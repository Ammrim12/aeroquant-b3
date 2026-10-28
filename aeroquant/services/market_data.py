"""Camada de dados do AeroQuant (B3 completa: Ações, FIIs, ETFs, BDRs + Benchmarks + Agenda).

Fontes utilizadas (100% gratuitas e online):
- **brapi.dev** (`/api/quote/list`): lista ~1.600 ativos da B3 (todas as ~385 ações
  de empresas em 20 segmentos + FIIs + ETFs + BDRs) em uma única chamada rápida.
- **Yahoo Finance (`yfinance`)**: indicadores macro (`^BVSP`, `USDBRL=X`, `BTC-USD`),
  séries históricas com Média Móvel de 20 pregões (`MM20`) e comparativo normalizado
  **Sua Carteira vs. Ibovespa vs. CDI**.
- **Google News RSS Brasil (`hl=pt-BR&gl=BR`)**: manchetes em português em tempo real.
- **Persistência local (`data/portfolio.json`)**: salva automaticamente as posições
  simuladas pelo usuário em disco e gera exportação em CSV.
"""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request
import warnings
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

from .formatting import (
    format_compact,
    format_number,
    format_percent,
    format_signed,
    relative_time,
    tone,
)

logger = logging.getLogger("aeroquant.market_data")
warnings.filterwarnings("ignore", module="yfinance")

REQUEST_TIMEOUT = 12
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AeroQuant/3.0"

# Diretório para persistência local da carteira simulada e favoritos (watchlist).
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
DEFAULT_WATCHLIST: list[str] = [
    "PETR4",
    "VALE3",
    "ITUB4",
    "WEGE3",
    "BBAS3",
    "HGLG11",
    "BOVA11",
    "NVDC34",
]

# Cache em memória para o catálogo da B3 e séries históricas (evita rate-limit e acelera cliques).
_CATALOG_CACHE: dict[str, Any] = {"timestamp": 0.0, "data": None}
_CATALOG_TTL_SECONDS = 45
_CHART_CACHE: dict[tuple[str, int], tuple[float, dict[str, Any]]] = {}
_CHART_TTL_SECONDS = 120.0


def load_watchlist() -> list[str]:
    """Carrega a lista de ativos favoritos salva em `data/watchlist.json`."""
    try:
        if WATCHLIST_FILE.exists():
            data = json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return [str(x).upper().strip() for x in data if str(x).strip()]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao carregar watchlist: %s", exc)
    return list(DEFAULT_WATCHLIST)


def save_watchlist(tickers: list[str]) -> None:
    """Persiste a lista de ativos favoritos em `data/watchlist.json`."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        unique = list(dict.fromkeys(str(t).upper().strip() for t in tickers if str(t).strip()))
        WATCHLIST_FILE.write_text(json.dumps(unique, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao salvar watchlist: %s", exc)


# --------------------------------------------------------------------------- #
# Tradução e metadados dos 20 setores da B3 + Classes de Ativos
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SectorMeta:
    """Metadados visuais de um segmento econômico da B3."""

    key: str
    label: str
    short: str
    icon: str
    color: str


SECTOR_MAP: dict[str, SectorMeta] = {
    "Finance": SectorMeta(
        "Finance", "Bancos, Finanças e Seguros", "Bancos & Finanças", "landmark", "#2D5A43"
    ),
    "Energy Minerals": SectorMeta(
        "Energy Minerals", "Petróleo, Gás e Combustíveis", "Petróleo & Gás", "flame", "#3E7B5C"
    ),
    "Utilities": SectorMeta(
        "Utilities", "Energia Elétrica e Saneamento", "Energia & Água", "zap", "#589474"
    ),
    "Non-Energy Minerals": SectorMeta(
        "Non-Energy Minerals", "Mineração e Siderurgia", "Mineração & Aço", "pickaxe", "#78AD90"
    ),
    "Producer Manufacturing": SectorMeta(
        "Producer Manufacturing", "Fábricas, Máquinas e Indústria", "Fábricas & Indústria", "factory", "#D98A5F"
    ),
    "Retail Trade": SectorMeta(
        "Retail Trade", "Lojas, Varejo e E-commerce", "Lojas & Varejo", "shopping-bag", "#E29D73"
    ),
    "Consumer Non-Durables": SectorMeta(
        "Consumer Non-Durables", "Alimentos, Bebidas e Consumo", "Alimentos & Consumo", "utensils", "#C97A53"
    ),
    "Process Industries": SectorMeta(
        "Process Industries", "Química, Papel, Celulose e Agro", "Química, Papel & Agro", "trees", "#4B8366"
    ),
    "Consumer Durables": SectorMeta(
        "Consumer Durables", "Construção Civil, Imóveis e Bens Duráveis", "Construção & Bens", "building-2", "#8AB89E"
    ),
    "Transportation": SectorMeta(
        "Transportation", "Transporte, Aviação e Logística", "Transporte & Logística", "plane", "#36694E"
    ),
    "Health Services": SectorMeta(
        "Health Services", "Hospitais, Laboratórios e Saúde", "Saúde & Hospitais", "heart-pulse", "#B86B52"
    ),
    "Health Technology": SectorMeta(
        "Health Technology", "Farmacêuticas e Biotecnologia", "Farmácia & Biotech", "pill", "#D18669"
    ),
    "Technology Services": SectorMeta(
        "Technology Services", "Tecnologia, Software e TI", "Tecnologia & TI", "cpu", "#2F6B55"
    ),
    "Communications": SectorMeta(
        "Communications", "Telecomunicações e Mídia", "Telecom & Mídia", "radio-tower", "#649E80"
    ),
    "Commercial Services": SectorMeta(
        "Commercial Services", "Serviços Empresariais e Pagamentos", "Serviços", "briefcase", "#7CA68D"
    ),
    "Consumer Services": SectorMeta(
        "Consumer Services", "Educação, Turismo e Redes", "Educação & Lazer", "graduation-cap", "#DDA06D"
    ),
    "Industrial Services": SectorMeta(
        "Industrial Services", "Engenharia, Concessões e Infraestrutura", "Infraestrutura", "hard-hat", "#517F67"
    ),
    "Distribution Services": SectorMeta(
        "Distribution Services", "Atacado e Distribuição", "Distribuição", "truck", "#93BCA5"
    ),
    "Electronic Technology": SectorMeta(
        "Electronic Technology", "Eletrônicos, Hardware e Automação", "Eletrônicos", "microchip", "#43755B"
    ),
    "Miscellaneous": SectorMeta(
        "Miscellaneous", "Holdings e Participações", "Holdings", "layers", "#A3B8AA"
    ),
}

DEFAULT_SECTOR = SectorMeta(
    "Other", "Outros Segmentos", "Outros", "building", "#8CA896"
)

# Seletores rápidos de ativos para o gráfico principal da Visão Geral.
BENCHMARK_PILLS: tuple[dict[str, str], ...] = (
    {"symbol": "^BVSP", "label": "Ibovespa", "subtitle": "Índice B3 · Pontos", "unit": "pts"},
    {"symbol": "PETR4.SA", "label": "Petrobras", "subtitle": "PETR4 · Petróleo & Gás", "unit": "BRL"},
    {"symbol": "VALE3.SA", "label": "Vale", "subtitle": "VALE3 · Mineração", "unit": "BRL"},
    {"symbol": "ITUB4.SA", "label": "Itaú", "subtitle": "ITUB4 · Bancos", "unit": "BRL"},
    {"symbol": "WEGE3.SA", "label": "WEG", "subtitle": "WEGE3 · Fábricas & Indústria", "unit": "BRL"},
    {"symbol": "MGLU3.SA", "label": "Magalu", "subtitle": "MGLU3 · Lojas & Varejo", "unit": "BRL"},
    {"symbol": "USDBRL=X", "label": "Dólar", "subtitle": "USD/BRL · Câmbio Comercial", "unit": "BRL"},
)

PERIOD_OPTIONS: dict[str, int] = {
    "30 dias": 30,
    "90 dias": 90,
    "6 meses": 180,
    "12 meses": 365,
}


# --------------------------------------------------------------------------- #
# Cores do Mapa de Calor (Heatmap estilo Coffra Timesheets)
# --------------------------------------------------------------------------- #
def _heatmap_colors(change: float) -> tuple[str, str]:
    """Retorna (cor_de_fundo_translucida, cor_do_texto) para o bloco do Mapa de Calor."""
    if change >= 3.0:
        return ("rgba(28, 98, 64, 0.68)", "#F7FCF9")
    if change >= 1.2:
        return ("rgba(44, 124, 84, 0.54)", "#F7FCF9")
    if change > 0.15:
        return ("rgba(72, 152, 110, 0.38)", "#F2F9F5")
    if change >= -0.15:
        return ("rgba(255, 255, 255, 0.07)", "var(--aq-text)")
    if change >= -1.2:
        return ("rgba(218, 122, 74, 0.38)", "#FDF6F2")
    if change >= -3.0:
        return ("rgba(196, 84, 54, 0.54)", "#FFFFFF")
    return ("rgba(164, 48, 34, 0.68)", "#FFFFFF")


# --------------------------------------------------------------------------- #
# 1. Catálogo Completo da B3 (Ações + FIIs + ETFs + BDRs)
# --------------------------------------------------------------------------- #
def _clean_company_name(raw_name: str, ticker: str) -> str:
    name = (raw_name or ticker).strip()
    name = re.sub(r"\s*-\s*EM RECUPERA[ÇC][ÃA]O JUDICIAL.*$", "", name, flags=re.I)
    name = re.sub(r"\s*-\s*RESPONSABILIDADE LIMITADA.*$", "", name, flags=re.I)
    if name.isupper() and len(name) > 4:
        name = name.title()
        for acronym in ("S.A.", "S/A", "B3", "Fii", "Etf", "Bdr", "Cia", "Cpfl", "Csn", "Jbs", "Mrv", "Brf"):
            name = re.sub(rf"\b{re.escape(acronym.title())}\b", acronym.upper(), name)
    return name


def _classify_asset(item: dict[str, Any]) -> tuple[str, str, SectorMeta]:
    """Classifica o ativo em ('acao' | 'fii' | 'etf' | 'bdr', rótulo_classe, SectorMeta)."""
    raw_type = str(item.get("type") or "stock").lower()
    sub_type = str(item.get("subType") or "").lower()
    sector_key = str(item.get("sector") or "Other")

    if raw_type == "bdr":
        meta = SECTOR_MAP.get(sector_key, SectorMeta("BDR", "BDRs Internacionais", "BDR Global", "globe", "#3D7058"))
        return ("bdr", "BDR Internacional", meta)
    if raw_type == "fund":
        if sub_type == "etf":
            meta = SectorMeta("ETF", "ETFs de Índices e Renda Fixa", "ETF de Índice", "layers", "#4B8366")
            return ("etf", "ETF de Índice", meta)
        meta = SectorMeta("FII", "Fundos Imobiliários, Fiagro e Infra", "Fundo Imobiliário", "building", "#D98A5F")
        return ("fii", "Fundo Imobiliário (FII)", meta)

    meta = SECTOR_MAP.get(sector_key, DEFAULT_SECTOR)
    return ("acao", "Ação B3", meta)


def fetch_b3_catalog(force: bool = False) -> dict[str, Any]:
    """Busca todos os ativos negociados na B3 (Ações, FIIs, ETFs e BDRs)."""
    now = time.time()
    if not force and _CATALOG_CACHE["data"] and (now - _CATALOG_CACHE["timestamp"] < _CATALOG_TTL_SECONDS):
        return _CATALOG_CACHE["data"]

    url = "https://brapi.dev/api/quote/list?limit=3000"
    token = os.environ.get("BRAPI_TOKEN", "").strip()
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            payload = json.load(resp)
        raw_items = payload.get("stocks") or []
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao consultar catálogo da B3 na brapi.dev: %s", exc)
        return _CATALOG_CACHE["data"] or {
            "stocks": [],
            "all_assets": [],
            "sectors": [],
            "breadth": {},
            "top_gainers": [],
            "top_losers": [],
            "most_active": [],
            "heatmap_tiles": [],
            "class_counts": {"acao": "0", "fii": "0", "etf": "0", "bdr": "0", "todos": "0"},
        }

    all_assets: list[dict[str, Any]] = []
    stocks_only: list[dict[str, Any]] = []
    issuer_mcap: dict[str, tuple[str, float]] = {}
    class_counter = {"acao": 0, "fii": 0, "etf": 0, "bdr": 0}

    for item in raw_items:
        ticker = str(item.get("stock") or "").strip().upper()
        # Ignora mercado fracionário (terminado em dígito + F, ex.: PETR4F).
        if not ticker or re.search(r"\dF$", ticker):
            continue

        close = float(item.get("close") or 0.0)
        change = float(item.get("change") or 0.0)
        volume = float(item.get("volume") or 0.0)
        mcap = float(item.get("market_cap") or 0.0)
        asset_class, class_label, meta = _classify_asset(item)
        sector_key = meta.key if asset_class != "acao" else str(item.get("sector") or "Other")
        subsector = str(item.get("subsector") or class_label)
        raw_name = str(item.get("name") or ticker)
        clean_name = _clean_company_name(raw_name, ticker)
        heat_bg, heat_fg = _heatmap_colors(change)

        class_counter[asset_class] = class_counter.get(asset_class, 0) + 1

        if asset_class == "acao":
            issuer_key = raw_name.strip().upper()
            _, prev_mcap = issuer_mcap.get(issuer_key, (sector_key, 0.0))
            if mcap >= prev_mcap:
                issuer_mcap[issuer_key] = (sector_key, mcap)

        entry = {
            "ticker": ticker,
            "yf_symbol": f"{ticker}.SA",
            "name": clean_name,
            "raw_name": raw_name,
            "asset_class": asset_class,
            "class_label": class_label,
            "price_raw": close,
            "price": f"R$ {format_number(close)}",
            "change_raw": change,
            "change": format_percent(change),
            "tone": tone(change),
            "arrow": "trending-up" if change >= 0 else "trending-down",
            "volume_raw": volume,
            "volume": format_compact(volume),
            "market_cap_raw": mcap,
            "market_cap": format_compact(mcap, "R$ ") if mcap > 0 else "—",
            "sector_key": sector_key,
            "sector": meta.label,
            "sector_short": meta.short,
            "sector_icon": meta.icon,
            "sector_color": meta.color,
            "subsector": subsector,
            "logo": str(item.get("logo") or ""),
            "initials": ticker[:4],
            "heat_bg": heat_bg,
            "heat_fg": heat_fg,
        }
        all_assets.append(entry)
        if asset_class == "acao":
            stocks_only.append(entry)

    stocks_only.sort(key=lambda s: (s["market_cap_raw"], s["volume_raw"]), reverse=True)
    all_assets.sort(key=lambda s: (s["market_cap_raw"], s["volume_raw"]), reverse=True)

    # Agregação por setor (apenas ações de empresas, sem dupla contagem ON/PN).
    sector_mcap_map: dict[str, float] = {}
    for sec_key, mcap in issuer_mcap.values():
        sector_mcap_map[sec_key] = sector_mcap_map.get(sec_key, 0.0) + mcap

    total_b3_mcap = sum(sector_mcap_map.values()) or 1.0
    by_sector: dict[str, list[dict[str, Any]]] = {}
    for st in stocks_only:
        by_sector.setdefault(st["sector_key"], []).append(st)

    sectors: list[dict[str, Any]] = []
    for sec_key, group in by_sector.items():
        meta = SECTOR_MAP.get(sec_key, DEFAULT_SECTOR)
        sec_mcap = sector_mcap_map.get(sec_key, 0.0)
        share_pct = (sec_mcap / total_b3_mcap) * 100 if total_b3_mcap else 0.0
        avg_change = sum(x["change_raw"] for x in group) / max(1, len(group))
        leaders = ", ".join(x["ticker"] for x in group[:3])
        up_count = sum(1 for x in group if x["change_raw"] > 0)
        sectors.append(
            {
                "key": sec_key,
                "label": meta.label,
                "short": meta.short,
                "icon": meta.icon,
                "color": meta.color,
                "count": len(group),
                "count_label": f"{len(group)} {'ações' if len(group) != 1 else 'ação'}",
                "leaders": leaders,
                "subtitle": f"{len(group)} ações · Líderes: {leaders}",
                "market_cap_raw": sec_mcap,
                "market_cap": format_compact(sec_mcap, "R$ "),
                "share_raw": round(share_pct, 2),
                "share_width": f"{max(2.5, round(share_pct, 1))}%",
                "share_label": f"{format_number(share_pct, 1)}%",
                "avg_change_raw": avg_change,
                "avg_change": format_percent(avg_change),
                "tone": tone(avg_change),
                "up_ratio": f"{up_count}/{len(group)} em alta",
            }
        )

    sectors.sort(key=lambda s: s["market_cap_raw"], reverse=True)

    liquid = [s for s in stocks_only if s["volume_raw"] >= 50_000 and s["price_raw"] >= 1.0]
    if len(liquid) < 15:
        liquid = stocks_only
    top_gainers = sorted(liquid, key=lambda s: s["change_raw"], reverse=True)[:6]
    top_losers = sorted(liquid, key=lambda s: s["change_raw"])[:6]
    most_active = sorted(stocks_only, key=lambda s: s["volume_raw"], reverse=True)[:6]

    # 36 maiores empresas por valor de mercado/liquidez para o Mapa de Calor da Visão Geral.
    heatmap_tiles = stocks_only[:36]

    up_total = sum(1 for s in stocks_only if s["change_raw"] > 0.005)
    down_total = sum(1 for s in stocks_only if s["change_raw"] < -0.005)
    flat_total = len(stocks_only) - up_total - down_total
    total_volume = sum(s["volume_raw"] for s in stocks_only)
    denom = max(1, len(stocks_only))
    up_ratio_pct = (up_total / denom) * 100.0
    down_ratio_pct = (down_total / denom) * 100.0
    flat_ratio_pct = max(0.0, 100.0 - up_ratio_pct - down_ratio_pct)
    if up_ratio_pct >= 55.0:
        sentiment_label = "Força Compradora Dominante"
    elif up_ratio_pct <= 45.0:
        sentiment_label = "Pressão Vendedora no Pregão"
    else:
        sentiment_label = "Pregão em Equilíbrio Técnico"

    breadth = {
        "total_stocks": str(len(stocks_only)),
        "total_assets": str(len(all_assets)),
        "total_issuers": str(len(issuer_mcap)),
        "total_sectors": str(len(sectors)),
        "up_count": str(up_total),
        "down_count": str(down_total),
        "flat_count": str(flat_total),
        "up_pct": f"{format_number(up_ratio_pct, 0)}%",
        "down_pct": f"{format_number(down_ratio_pct, 0)}%",
        "up_width": f"{max(8.0, round(up_ratio_pct, 1))}%",
        "flat_width": f"{max(2.0, round(flat_ratio_pct, 1))}%",
        "down_width": f"{max(8.0, round(down_ratio_pct, 1))}%",
        "sentiment_label": sentiment_label,
        "total_market_cap": format_compact(total_b3_mcap, "R$ "),
        "total_volume": format_compact(total_volume),
        "top_gainer_ticker": top_gainers[0]["ticker"] if top_gainers else "—",
        "top_gainer_change": top_gainers[0]["change"] if top_gainers else "—",
        "top_loser_ticker": top_losers[0]["ticker"] if top_losers else "—",
        "top_loser_change": top_losers[0]["change"] if top_losers else "—",
        "most_active_ticker": most_active[0]["ticker"] if most_active else "—",
        "most_active_volume": most_active[0]["volume"] if most_active else "—",
    }

    fav_set = set(load_watchlist())
    for item_entry in all_assets:
        item_entry["is_favorite"] = "1" if item_entry["ticker"] in fav_set else "0"

    class_counts = {
        "acao": str(class_counter["acao"]),
        "fii": str(class_counter["fii"]),
        "etf": str(class_counter["etf"]),
        "bdr": str(class_counter["bdr"]),
        "favoritos": str(sum(1 for a in all_assets if a["ticker"] in fav_set)),
        "todos": str(len(all_assets)),
    }

    ticker_tape = stocks_only[:12]

    result = {
        "stocks": stocks_only,
        "all_assets": all_assets,
        "sectors": sectors,
        "breadth": breadth,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "most_active": most_active,
        "heatmap_tiles": heatmap_tiles,
        "ticker_tape": ticker_tape,
        "class_counts": class_counts,
    }
    _CATALOG_CACHE["timestamp"] = now
    _CATALOG_CACHE["data"] = result
    return result


# --------------------------------------------------------------------------- #
# 2. Cotações Macro + Séries Históricas com Média Móvel MM20 (yfinance)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Asset:
    symbol: str
    name: str
    prefix: str
    suffix: str
    icon: str


OVERVIEW_ASSETS: tuple[Asset, ...] = (
    Asset("^BVSP", "Ibovespa", "", " pts", "chart-candlestick"),
    Asset("USDBRL=X", "Dólar Comercial", "R$ ", "", "dollar-sign"),
    Asset("BTC-USD", "Bitcoin (USD)", "US$ ", "", "bitcoin"),
)


def _fetch_history(symbol: str, period: str = "6mo") -> pd.DataFrame:
    return yf.Ticker(symbol).history(
        period=period, interval="1d", auto_adjust=True, timeout=REQUEST_TIMEOUT
    )


def fetch_quote(asset: Asset) -> dict[str, str] | None:
    try:
        closes = _fetch_history(asset.symbol, "7d")["Close"].dropna()
        if len(closes) < 2:
            raise ValueError("histórico insuficiente")
        price, previous = float(closes.iloc[-1]), float(closes.iloc[-2])
        change_pct = (price / previous - 1) * 100
        decimals = 0 if asset.symbol == "^BVSP" else 2
        return {
            "symbol": asset.symbol,
            "name": asset.name,
            "icon": asset.icon,
            "price": f"{asset.prefix}{format_number(price, decimals)}{asset.suffix}",
            "change": format_percent(change_pct),
            "change_raw": f"{change_pct:.2f}",
            "arrow": "trending-up" if change_pct >= 0 else "trending-down",
            "color": tone(change_pct),
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao buscar cotação de %s: %s", asset.symbol, exc)
        return None


def unavailable_quote(asset: Asset) -> dict[str, str]:
    return {
        "symbol": asset.symbol,
        "name": asset.name,
        "icon": asset.icon,
        "price": "Indisponível",
        "change": "0,00%",
        "change_raw": "0",
        "arrow": "minus",
        "color": "gray",
    }


def fetch_chart_bundle(symbol: str, days: int = 90, force: bool = False) -> dict[str, Any]:
    """Retorna a série histórica com MM20, IFR-14 (RSI), Volatilidade Anualizada e Faixa de 52s."""
    cache_key = (symbol, int(days))
    now_ts = time.time()
    if not force and cache_key in _CHART_CACHE:
        cached_at, cached_bundle = _CHART_CACHE[cache_key]
        if (now_ts - cached_at) < _CHART_TTL_SECONDS:
            return cached_bundle

    yf_period = "2y" if days > 180 else "1y"
    is_points = symbol == "^BVSP"
    prefix = "" if is_points else "R$ "
    suffix = " pts" if is_points else ""
    decimals = 0 if is_points else 2

    try:
        frame = _fetch_history(symbol, yf_period).dropna(subset=["Close"])
        if frame.empty:
            raise ValueError("sem dados históricos")

        # Calcula a Média Móvel Simples de 20 pregões + IFR-14 (RSI) + Volatilidade Anualizada.
        frame = frame.copy()
        frame["MM20"] = frame["Close"].rolling(window=20, min_periods=1).mean()

        delta = frame["Close"].diff()
        gain = delta.clip(lower=0.0).rolling(window=14, min_periods=1).mean()
        loss = (-delta.clip(upper=0.0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss.replace(0.0, 1e-9)
        rsi_series = 100.0 - (100.0 / (1.0 + rs))
        last_rsi = float(rsi_series.iloc[-1]) if not rsi_series.empty else 50.0
        last_rsi = max(5.0, min(95.0, last_rsi))

        if last_rsi >= 70.0:
            rsi_status = "Sobrecompra (>70)"
            rsi_tone = "amber"
        elif last_rsi <= 30.0:
            rsi_status = "Sobrevenda (<30)"
            rsi_tone = "jade"
        else:
            rsi_status = "Zona Neutra"
            rsi_tone = "gray"

        daily_ret = frame["Close"].pct_change().dropna()
        ann_vol = float(daily_ret.tail(60).std() * (252 ** 0.5) * 100.0) if len(daily_ret) > 5 else 18.5

        year_slice = frame.tail(252)
        low_52w = float(year_slice["Close"].min())
        high_52w = float(year_slice["Close"].max())

        cutoff = frame.index.max() - pd.Timedelta(days=days)
        sliced = frame[frame.index >= cutoff]
        if len(sliced) < 2:
            sliced = frame.tail(min(len(frame), 30))

        points: list[dict[str, Any]] = []
        prev_close = float(sliced["Close"].iloc[0])
        for idx, row in sliced.iterrows():
            close = float(row["Close"])
            mm20 = float(row["MM20"])
            vol = float(row.get("Volume", 0.0) or 0.0)
            var_dia = ((close / prev_close) - 1) * 100 if prev_close else 0.0
            prev_close = close
            points.append(
                {
                    "date": idx.strftime("%d/%m"),
                    "full_date": idx.strftime("%d/%m/%Y"),
                    "close": round(close, 2),
                    "mm20": round(mm20, 2),
                    "ganho": round(max(0.0, var_dia), 2),
                    "perda": round(min(0.0, var_dia), 2),
                    "volume": round(vol / 1e6, 2),
                }
            )

        first_close = float(sliced["Close"].iloc[0])
        last_close = float(sliced["Close"].iloc[-1])
        last_mm20 = float(sliced["MM20"].iloc[-1])
        high_period = float(sliced["Close"].max())
        low_period = float(sliced["Close"].min())
        period_change = ((last_close / first_close) - 1) * 100 if first_close else 0.0
        avg_vol = float(sliced["Volume"].mean()) if "Volume" in sliced else 0.0

        span_52w = max(0.01, high_52w - low_52w)
        pos_52w = max(4.0, min(98.0, ((last_close - low_52w) / span_52w) * 100.0))

        summary = {
            "current": f"{prefix}{format_number(last_close, decimals)}{suffix}",
            "first": f"{prefix}{format_number(first_close, decimals)}{suffix}",
            "mm20_label": f"{prefix}{format_number(last_mm20, decimals)}{suffix}",
            "range_sub": f"Mín {prefix}{format_number(low_period, decimals)} · Máx {prefix}{format_number(high_period, decimals)}",
            "period_change": format_percent(period_change),
            "period_diff": format_signed(last_close - first_close, prefix=prefix, suffix=suffix),
            "tone": tone(period_change),
            "avg_volume": format_compact(avg_vol) if avg_vol > 0 else "Índice B3",
            "sessions": f"{len(points)} pregões · MM20 {prefix}{format_number(last_mm20, decimals)}",
            "rsi_value": format_number(last_rsi, 1),
            "rsi_status": rsi_status,
            "rsi_tone": rsi_tone,
            "volatility": f"{format_number(ann_vol, 1)}% a.a.",
            "low_52w": f"{prefix}{format_number(low_52w, decimals)}{suffix}",
            "high_52w": f"{prefix}{format_number(high_52w, decimals)}{suffix}",
            "pos_52w_pct": f"{round(pos_52w, 1)}%",
            "pos_52w_label": f"{format_number(pos_52w, 0)}% do topo de 52s",
        }
        bundle_out = {"points": points, "summary": summary}
        _CHART_CACHE[cache_key] = (now_ts, bundle_out)
        return bundle_out
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao buscar série de %s: %s", symbol, exc)
        return {
            "points": [],
            "summary": {
                "current": "—",
                "first": "—",
                "mm20_label": "—",
                "range_sub": "Sem dados no período",
                "period_change": "0,00%",
                "period_diff": "—",
                "tone": "gray",
                "avg_volume": "—",
                "sessions": "0 pregões",
                "rsi_value": "50,0",
                "rsi_status": "Zona Neutra",
                "rsi_tone": "gray",
                "volatility": "—",
                "low_52w": "—",
                "high_52w": "—",
                "pos_52w_pct": "50%",
                "pos_52w_label": "—",
            },
        }


def prewarm_benchmarks(days: int = 90) -> None:
    """Pré-aquece o cache de gráficos dos principais benchmarks da Visão Geral em background."""
    symbols = [b["symbol"] for b in BENCHMARK_PILLS[:4]]
    with ThreadPoolExecutor(max_workers=len(symbols)) as pool:
        list(pool.map(lambda s: fetch_chart_bundle(s, days), symbols))


# --------------------------------------------------------------------------- #
# 3. Carteira Simulada + Persistência em Disco + Comparador vs. Ibovespa & CDI
# --------------------------------------------------------------------------- #
DEFAULT_PORTFOLIO: list[dict[str, Any]] = [
    {"ticker": "PETR4", "quantity": 500, "avg_price": 42.00, "note": "Dividendos & Petróleo"},
    {"ticker": "VALE3", "quantity": 200, "avg_price": 60.50, "note": "Mineração & Exportação"},
    {"ticker": "ITUB4", "quantity": 400, "avg_price": 34.80, "note": "Bancos & Finanças"},
    {"ticker": "WEGE3", "quantity": 300, "avg_price": 39.20, "note": "Fábricas & Indústria"},
]

_SLICE_PALETTE = ("#4ADE80", "#F5B851", "#E89565", "#38BDF8", "#A78BFA", "#34D399")
_CARD_THEMES = (
    {"bg": "linear-gradient(135deg, rgba(28, 76, 54, 0.62), rgba(48, 114, 80, 0.54))", "fg": "#FFFFFF", "tag": "VAULT · 01"},
    {"bg": "linear-gradient(135deg, rgba(158, 88, 44, 0.62), rgba(204, 124, 68, 0.54))", "fg": "#FFFFFF", "fg_sub": "#FCEEE6", "tag": "VAULT · 02"},
    {"bg": "linear-gradient(135deg, rgba(24, 36, 30, 0.66), rgba(46, 68, 58, 0.56))", "fg": "#FFFFFF", "tag": "VAULT · 03"},
    {"bg": "linear-gradient(135deg, rgba(52, 98, 74, 0.60), rgba(84, 144, 112, 0.52))", "fg": "#FFFFFF", "tag": "VAULT · 04"},
)


def load_saved_portfolio() -> list[dict[str, Any]]:
    """Carrega a carteira persistida em `data/portfolio.json` (ou retorna a padrão)."""
    try:
        if PORTFOLIO_FILE.exists():
            data = json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("Não foi possível ler %s: %s", PORTFOLIO_FILE, exc)
    return [dict(item) for item in DEFAULT_PORTFOLIO]


def save_portfolio_to_disk(positions: list[dict[str, Any]]) -> None:
    """Persiste as posições simuladas em `data/portfolio.json`."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        PORTFOLIO_FILE.write_text(
            json.dumps(positions, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Não foi possível salvar %s: %s", PORTFOLIO_FILE, exc)


def export_portfolio_csv(rows: list[dict[str, Any]], summary: dict[str, str]) -> str:
    """Gera o conteúdo CSV (UTF-8 com BOM para Excel) da carteira atual."""
    buf = io.StringIO()
    buf.write("\ufeff")
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(
        ["Ativo", "Empresa", "Segmento", "Quantidade", "Preço Médio", "Cotação Atual", "Valor Atual", "Retorno (R$)", "Retorno (%)", "Participação"]
    )
    for r in rows:
        writer.writerow(
            [
                r.get("ticker", ""),
                r.get("name", ""),
                r.get("sector", ""),
                r.get("quantity", ""),
                r.get("avg_price", ""),
                r.get("price", ""),
                r.get("total", ""),
                r.get("pnl", ""),
                r.get("pnl_pct", ""),
                r.get("weight", ""),
            ]
        )
    writer.writerow([])
    writer.writerow(["PATRIMÔNIO TOTAL", summary.get("total_value", ""), "CUSTO TOTAL", summary.get("total_cost", ""), "RESULTADO", summary.get("pnl", ""), summary.get("pnl_pct", "")])
    return buf.getvalue()


_REFERENCE_DY: dict[str, float] = {
    "PETR4": 13.8,
    "PETR3": 13.2,
    "VALE3": 9.4,
    "ITUB4": 8.1,
    "BBDC4": 8.6,
    "BBAS3": 10.2,
    "SANB11": 7.8,
    "WEGE3": 2.4,
    "TAEE11": 10.6,
    "EGIE3": 8.9,
    "CMIG4": 11.4,
    "CPLE6": 8.5,
    "BBSE3": 9.8,
    "CXSE3": 8.7,
    "HGLG11": 9.6,
    "KNCR11": 11.2,
    "MXRF11": 11.8,
    "XPML11": 9.9,
}


def _estimate_dividend_yield(ticker: str, sector_short: str, asset_class: str = "acao") -> float:
    if ticker in _REFERENCE_DY:
        return _REFERENCE_DY[ticker]
    if asset_class == "fii" or ticker.endswith("11"):
        return 10.4
    low = sector_short.lower()
    if any(k in low for k in ("petróleo", "energia", "banco", "mineração")):
        return 8.8
    if any(k in low for k in ("indústria", "fábrica", "consumo", "alimento")):
        return 4.6
    return 6.2


def compute_portfolio(
    positions: list[dict[str, Any]],
    catalog_assets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Calcula patrimônio, P&L, dividendos estimados, fatias e cartões de estratégia."""
    if catalog_assets is None:
        catalog_assets = fetch_b3_catalog().get("all_assets", [])
    by_ticker = {s["ticker"]: s for s in catalog_assets}

    rows: list[dict[str, Any]] = []
    slices: list[dict[str, Any]] = []
    strategy_cards: list[dict[str, str]] = []
    total_value = 0.0
    total_cost = 0.0
    total_annual_div = 0.0

    for idx, pos in enumerate(positions):
        ticker = str(pos.get("ticker") or "").upper().replace(".SA", "")
        qty = int(pos.get("quantity") or 0)
        avg = float(pos.get("avg_price") or 0.0)
        if not ticker or qty <= 0 or avg <= 0:
            continue

        info = by_ticker.get(ticker)
        price = float(info["price_raw"]) if info else avg
        day_change = float(info["change_raw"]) if info else 0.0
        name = info["name"] if info else ticker
        sector = info["sector_short"] if info else "B3"
        asset_cls = info.get("asset_class", "acao") if info else "acao"
        logo = info["logo"] if info else ""

        value = qty * price
        cost = qty * avg
        pnl = value - cost
        pnl_pct = ((price / avg) - 1) * 100 if avg else 0.0
        dy_pct = _estimate_dividend_yield(ticker, sector, asset_cls)
        annual_div = value * (dy_pct / 100.0)

        total_value += value
        total_cost += cost
        total_annual_div += annual_div
        color = _SLICE_PALETTE[idx % len(_SLICE_PALETTE)]

        rows.append(
            {
                "ticker": ticker,
                "yf_symbol": f"{ticker}.SA",
                "name": name,
                "sector": sector,
                "note": str(pos.get("note") or sector),
                "logo": logo,
                "quantity": format_number(qty, 0),
                "avg_price": f"R$ {format_number(avg)}",
                "price": f"R$ {format_number(price)}",
                "day_change": format_percent(day_change),
                "day_tone": tone(day_change),
                "value_raw": value,
                "total": f"R$ {format_number(value)}",
                "cost": f"R$ {format_number(cost)}",
                "pnl": format_signed(pnl, "R$ "),
                "pnl_pct": format_percent(pnl_pct),
                "dy_label": f"{format_number(dy_pct, 1)}% a.a.",
                "annual_div": f"R$ {format_number(annual_div)}",
                "tone": tone(pnl),
                "color": color,
            }
        )
        slices.append({"name": ticker, "value": round(value, 2), "fill": color})

    for idx, row in enumerate(rows):
        share = (row["value_raw"] / total_value * 100) if total_value else 0.0
        row["weight"] = f"{format_number(share, 1)}%"
        row["weight_width"] = f"{max(4.0, min(100.0, round(share, 1)))}%"
        theme = _CARD_THEMES[idx % len(_CARD_THEMES)]
        strategy_cards.append(
            {
                "ticker": row["ticker"],
                "title": row["note"],
                "subtitle": f"{row['name']} · {row['quantity']} cotas",
                "code": f"B3 •• {1040 + idx * 117}",
                "total": row["total"],
                "cost": f"DY {row['dy_label']} · {row['annual_div']}/ano",
                "pnl_pct": row["pnl_pct"],
                "weight": row["weight"],
                "weight_width": row["weight_width"],
                "bg": theme["bg"],
            }
        )

    total_pnl = total_value - total_cost
    total_pct = ((total_value / total_cost) - 1) * 100 if total_cost else 0.0
    monthly_div = total_annual_div / 12.0
    portfolio_dy = (total_annual_div / total_value * 100.0) if total_value else 0.0
    goal_pct = min(100.0, (monthly_div / 1000.0) * 100.0)

    summary = {
        "total_value": f"R$ {format_number(total_value)}",
        "total_cost": f"R$ {format_number(total_cost)}",
        "pnl": format_signed(total_pnl, "R$ "),
        "pnl_pct": format_percent(total_pct),
        "tone": tone(total_pnl),
        "arrow": "trending-up" if total_pnl >= 0 else "trending-down",
        "positions": str(len(rows)),
        "annual_dividends": f"R$ {format_number(total_annual_div)}",
        "monthly_dividends": f"R$ {format_number(monthly_div)}",
        "portfolio_dy": f"{format_number(portfolio_dy, 1)}% a.a.",
        "income_goal_pct": f"{format_number(goal_pct, 0)}%",
        "income_goal_width": f"{max(6.0, round(goal_pct, 1))}%",
    }
    return {
        "rows": rows,
        "slices": slices,
        "strategy_cards": strategy_cards,
        "summary": summary,
    }


def fetch_benchmark_comparison(positions: list[dict[str, Any]], days: int = 90) -> dict[str, Any]:
    """Compara o retorno acumulado (%) da Carteira vs. Ibovespa vs. CDI nos últimos ``days`` dias."""
    try:
        ibov_df = _fetch_history("^BVSP", "6mo")["Close"].dropna()
        if ibov_df.empty:
            raise ValueError("sem histórico do Ibovespa")
        cutoff = ibov_df.index.max() - pd.Timedelta(days=days)
        ibov_df = ibov_df[ibov_df.index >= cutoff]

        # Busca fechamentos das posições da carteira em paralelo.
        tickers = [f"{str(p['ticker']).upper().replace('.SA', '')}.SA" for p in positions[:6]]
        weights = [float(p.get("quantity", 100)) * float(p.get("avg_price", 20.0)) for p in positions[:6]]
        total_w = sum(weights) or 1.0
        norm_weights = [w / total_w for w in weights]

        def _get_close(sym: str) -> pd.Series:
            try:
                s = _fetch_history(sym, "6mo")["Close"].dropna()
                return s[s.index >= cutoff]
            except Exception:  # noqa: BLE001
                return pd.Series(dtype=float)

        with ThreadPoolExecutor(max_workers=max(1, len(tickers))) as pool:
            series_list = list(pool.map(_get_close, tickers))

        # Taxa diária equivalente a ~11,25% a.a. (252 dias úteis) para o CDI de referência.
        cdi_daily = (1.1125 ** (1 / 252)) - 1.0
        ibov_start = float(ibov_df.iloc[0])

        # Prepara preço inicial de cada ativo da carteira
        starts = [float(s.iloc[0]) if not s.empty else 0.0 for s in series_list]

        points: list[dict[str, Any]] = []
        for i, (dt, ibov_val) in enumerate(ibov_df.items()):
            ibov_pct = ((float(ibov_val) / ibov_start) - 1.0) * 100.0 if ibov_start else 0.0
            cdi_pct = (((1.0 + cdi_daily) ** i) - 1.0) * 100.0

            pf_pct = 0.0
            valid_w = 0.0
            for s, w, st0 in zip(series_list, norm_weights, starts):
                if st0 > 0 and not s.empty:
                    sub = s[s.index <= dt]
                    if not sub.empty:
                        cur = float(sub.iloc[-1])
                        pf_pct += w * (((cur / st0) - 1.0) * 100.0)
                        valid_w += w
            if valid_w > 0:
                pf_pct = pf_pct / valid_w
            else:
                pf_pct = ibov_pct

            points.append(
                {
                    "date": dt.strftime("%d/%m"),
                    "carteira": round(pf_pct, 2),
                    "ibovespa": round(ibov_pct, 2),
                    "cdi": round(cdi_pct, 2),
                }
            )

        last = points[-1] if points else {"carteira": 0.0, "ibovespa": 0.0, "cdi": 0.0}
        alpha_ibov = last["carteira"] - last["ibovespa"]
        return {
            "points": points,
            "summary": {
                "carteira": format_percent(last["carteira"]),
                "ibovespa": format_percent(last["ibovespa"]),
                "cdi": format_percent(last["cdi"]),
                "alpha": format_signed(alpha_ibov, suffix=" p.p. vs Ibov"),
                "tone": tone(alpha_ibov),
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao calcular comparativo de benchmarks: %s", exc)
        return {
            "points": [],
            "summary": {
                "carteira": "0,00%",
                "ibovespa": "0,00%",
                "cdi": "0,00%",
                "alpha": "0,00 p.p.",
                "tone": "gray",
            },
        }


# --------------------------------------------------------------------------- #
# 4. Agenda do Mercado Financeiro & Proventos B3 (/calendario)
# --------------------------------------------------------------------------- #
CALENDAR_CATEGORIES = (
    "Todos",
    "Copom & Macro Brasil",
    "Dividendos & JCP B3",
    "Temporada de Balanços",
    "Vencimentos B3",
)


def get_market_calendar(category: str = "Todos") -> list[dict[str, str]]:
    """Retorna o cronograma de eventos econômicos, dividendos e balanços da B3."""
    events = [
        {
            "day": "SEG",
            "date": "08:25",
            "title": "Boletim Focus — Banco Central do Brasil",
            "subtitle": "Projeções atualizadas do mercado para Selic, IPCA, PIB e Câmbio",
            "category": "Copom & Macro Brasil",
            "badge": "Macro BCB",
            "ticker": "SELIC / IPCA",
            "color": "#2D5A43",
            "bg": "var(--aq-tint-mint)",
            "border": "var(--aq-tint-mint-border)",
        },
        {
            "day": "SEG",
            "date": "18:00",
            "title": "Divulgação de Resultados Trimestrais — Itaú Unibanco (ITUB4)",
            "subtitle": "Balanço consolidado após o fechamento do pregão + teleconferência",
            "category": "Temporada de Balanços",
            "badge": "Balanço B3",
            "ticker": "ITUB4",
            "color": "#3E7B5C",
            "bg": "var(--aq-tint-lemon)",
            "border": "var(--aq-tint-lemon-border)",
        },
        {
            "day": "TER",
            "date": "09:00",
            "title": "IPCA-15 / Prévia da Inflação Oficial — IBGE",
            "subtitle": "Impacto direto na curva de juros DI Futuro e nos FIIs de tijolo/papel",
            "category": "Copom & Macro Brasil",
            "badge": "Inflação IBGE",
            "ticker": "DI1 / NTN-B",
            "color": "#2D5A43",
            "bg": "var(--aq-tint-mint)",
            "border": "var(--aq-tint-mint-border)",
        },
        {
            "day": "TER",
            "date": "10:00",
            "title": "Pagamento de Dividendos e JCP — Petrobras (PETR4 / PETR3)",
            "subtitle": "Crédito em conta corretora para acionistas posicionados na data-com",
            "category": "Dividendos & JCP B3",
            "badge": "Proventos R$",
            "ticker": "PETR4",
            "color": "#9C6B3B",
            "bg": "var(--aq-tint-sand)",
            "border": "var(--aq-tint-sand-border)",
        },
        {
            "day": "QUA",
            "date": "18:30",
            "title": "Super Quarta — Decisão da Taxa Selic (Copom / BCB)",
            "subtitle": "Comunicado oficial do Comitê de Política Monetária sobre a taxa básica",
            "category": "Copom & Macro Brasil",
            "badge": "Decisão Copom",
            "ticker": "SELIC",
            "color": "#2D5A43",
            "bg": "var(--aq-tint-mint)",
            "border": "var(--aq-tint-mint-border)",
        },
        {
            "day": "QUA",
            "date": "19:00",
            "title": "Relatório de Produção e Vendas — Vale S.A. (VALE3)",
            "subtitle": "Desempenho operacional de minério de ferro em Carajás e pelotas",
            "category": "Temporada de Balanços",
            "badge": "Operacional",
            "ticker": "VALE3",
            "color": "#3E7B5C",
            "bg": "var(--aq-tint-lemon)",
            "border": "var(--aq-tint-lemon-border)",
        },
        {
            "day": "QUI",
            "date": "10:00",
            "title": "Data-Com de Juros sobre Capital Próprio — WEG (WEGE3) & Banco do Brasil (BBAS3)",
            "subtitle": "Último pregão para negociar ações com direito ao recebimento do provento",
            "category": "Dividendos & JCP B3",
            "badge": "Data-Com B3",
            "ticker": "WEGE3 · BBAS3",
            "color": "#9C6B3B",
            "bg": "var(--aq-tint-sand)",
            "border": "var(--aq-tint-sand-border)",
        },
        {
            "day": "QUI",
            "date": "18:15",
            "title": "Resultados Trimestrais — Magazine Luiza (MGLU3) & Lojas Renner (LREN3)",
            "subtitle": "Indicadores de vendas no varejo físico, e-commerce (GMV) e margens",
            "category": "Temporada de Balanços",
            "badge": "Varejo B3",
            "ticker": "MGLU3 · LREN3",
            "color": "#3E7B5C",
            "bg": "var(--aq-tint-lemon)",
            "border": "var(--aq-tint-lemon-border)",
        },
        {
            "day": "SEX",
            "date": "10:00",
            "title": "Rendimentos Mensais de Fundos Imobiliários (FIIs — MXRF11, HGLG11, KNRI11)",
            "subtitle": "Distribuição mensal isenta de IR para pessoas físicas nos principais FIIs",
            "category": "Dividendos & JCP B3",
            "badge": "Proventos FIIs",
            "ticker": "IFIX / FIIs",
            "color": "#9C6B3B",
            "bg": "var(--aq-tint-sand)",
            "border": "var(--aq-tint-sand-border)",
        },
        {
            "day": "SEX",
            "date": "15:00",
            "title": "Vencimento de Opções sobre Ações e Índice Ibovespa na B3",
            "subtitle": "Aumento de volume e liquidez no encerramento das séries mensais da B3",
            "category": "Vencimentos B3",
            "badge": "Exercício B3",
            "ticker": "IBOV / OPÇÕES",
            "color": "#B85C4E",
            "bg": "var(--aq-tint-rose)",
            "border": "var(--aq-tint-rose-border)",
        },
    ]
    if category and category != "Todos":
        return [e for e in events if e["category"] == category]
    return events


# --------------------------------------------------------------------------- #
# 5. Notícias Financeiras 100% em Português (Google News RSS Brasil)
# --------------------------------------------------------------------------- #
NEWS_QUERIES: dict[str, str] = {
    "Todas": "Ibovespa OR B3 OR mercado financeiro ações Brasil",
    "Ibovespa & B3": "Ibovespa OR bolsa de valores B3 pregão",
    "Empresas & Balanços": "Petrobras OR Vale OR Itaú OR WEG OR Magazine Luiza ações",
    "Dólar & Juros": "Dólar comercial OR Selic Banco Central Copom inflação",
    "Indústria & Varejo": "indústria brasileira OR varejo empresas fábricas economia Brasil",
}


def fetch_news_ptbr(topic: str = "Todas", limit: int = 16) -> list[dict[str, str]]:
    """Busca manchetes reais e atuais em português via Google News RSS (BR)."""
    query = NEWS_QUERIES.get(topic, NEWS_QUERIES["Todas"])
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            xml_bytes = resp.read()
        root = ET.fromstring(xml_bytes)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao buscar RSS de notícias (%s): %s", topic, exc)
        return []

    parsed_items: list[tuple[float, dict[str, str]]] = []
    seen_titles: set[str] = set()

    for item in root.findall(".//item"):
        raw_title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        source = (item.findtext("source") or "Imprensa Econômica").strip()
        pub_raw = (item.findtext("pubDate") or "").strip()

        if not raw_title or not link:
            continue

        suffix = f" - {source}"
        title = raw_title[: -len(suffix)].strip() if raw_title.endswith(suffix) else raw_title
        norm_key = title.lower()[:80]
        if norm_key in seen_titles:
            continue
        seen_titles.add(norm_key)

        try:
            dt = parsedate_to_datetime(pub_raw)
            ts = dt.timestamp()
            when = relative_time(dt)
            date_str = dt.strftime("%d/%m · %H:%M")
        except Exception:  # noqa: BLE001
            ts = 0.0
            when = "Recente"
            date_str = ""

        low = title.lower()
        if any(k in low for k in ("dólar", "cambio", "câmbio", "selic", "copom", "juro", "inflação", "ipca")):
            tag = "Macro & Juros"
        elif any(k in low for k in ("petrobras", "petr", "petróleo", "energia", "elétrica", "aneel")):
            tag = "Energia & Petróleo"
        elif any(k in low for k in ("vale", "minério", "siderurgia", "csn", "gerdau")):
            tag = "Mineração & Aço"
        elif any(k in low for k in ("itaú", "bradesco", "banco", "santander", "btg", "nubank")):
            tag = "Bancos & Finanças"
        elif any(k in low for k in ("varejo", "magazine", "loja", "consumo", "fábrica", "indústria", "weg", "embraer")):
            tag = "Indústria & Varejo"
        else:
            tag = "Ibovespa & B3"

        parsed_items.append(
            (
                ts,
                {
                    "title": title,
                    "publisher": source,
                    "time": when,
                    "date": date_str,
                    "url": link,
                    "topic": tag,
                    "initials": "".join(w[0] for w in source.split()[:2]).upper() or "BR",
                },
            )
        )

    parsed_items.sort(key=lambda pair: pair[0], reverse=True)
    return [entry for _, entry in parsed_items[:limit]]


def fetch_macro_quotes() -> list[dict[str, str]]:
    """Busca Ibovespa, Dólar e Bitcoin em paralelo."""
    with ThreadPoolExecutor(max_workers=len(OVERVIEW_ASSETS)) as pool:
        results = list(pool.map(fetch_quote, OVERVIEW_ASSETS))
    return [q or unavailable_quote(a) for a, q in zip(OVERVIEW_ASSETS, results)]
