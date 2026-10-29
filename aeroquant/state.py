"""Estado global do AeroQuant (Reflex State).

Centraliza todas as informações exibidas nas cinco páginas:
- ``/`` (Visão Geral — estilo Coffra Overview + Mapa de Calor Setorial + Sentimento B3)
- ``/empresas`` (Diretório B3 — Ações, FIIs, ETFs, BDRs e Favoritos + Grade, Tabela e Mapa de Calor)
- ``/carteira`` (Minha Carteira — Cofres, Dividendos/Renda Passiva, Comparador vs. Ibovespa/CDI e CSV)
- ``/calendario`` (Agenda do Mercado — Copom, Inflação, Dividendos/JCP, Balanços e Vencimentos B3)
- ``/noticias`` (Notícias — Manchetes econômicas brasileiras em tempo real)
"""

from __future__ import annotations

import asyncio
from typing import Any

import reflex as rx

from .services import formatting as fmt
from .services import market_data as md


class State(rx.State):
    """Fonte única da verdade da interface."""

    # --- Cabeçalho, Tema de Vidro & Status Online -------------------------- #
    greeting_text: str = "Bom dia"
    today_label: str = ""
    market_open: bool = False
    market_status_label: str = "Verificando pregão..."
    last_update: str = "—"
    auto_refresh: bool = True
    is_loading: bool = True
    error_message: str = ""
    glass_mode: str = "fume"  # "cristal" | "fume" | "obsidiana"

    # --- Busca Rápida Global (Command Palette) ----------------------------- #
    command_palette_open: bool = False
    palette_query: str = ""

    # --- Indicadores Macro (Ibovespa, Dólar, Bitcoin) ---------------------- #
    kpis: list[dict[str, str]] = []

    # --- Gráfico Analítico Principal + MM20 + IFR-14 + Volatilidade -------- #
    chart_symbol: str = "^BVSP"
    chart_label: str = "Ibovespa"
    chart_subtitle: str = "Índice B3 · Pontos"
    chart_period: str = "90 dias"
    chart_mode: str = "fluxo"  # "fluxo" (barras + linha Coffra) ou "area"
    show_mm20: bool = True
    chart_loading: bool = True
    chart_data: list[dict[str, Any]] = []
    chart_summary: dict[str, str] = {
        "current": "—",
        "first": "—",
        "mm20_label": "—",
        "range_sub": "Carregando histórico...",
        "period_change": "0,00%",
        "period_diff": "—",
        "tone": "gray",
        "avg_volume": "—",
        "sessions": "—",
        "rsi_value": "50,0",
        "rsi_status": "Zona Neutra",
        "rsi_tone": "gray",
        "volatility": "—",
        "low_52w": "—",
        "high_52w": "—",
        "pos_52w_pct": "50%",
        "pos_52w_label": "—",
    }

    # --- Catálogo Completo da B3 (Backend-only para otimizar WebSocket) ---- #
    _all_stocks: list[dict[str, Any]] = []
    _all_assets: list[dict[str, Any]] = []
    sectors: list[dict[str, Any]] = []
    heatmap_tiles: list[dict[str, str]] = []
    ticker_tape_items: list[dict[str, str]] = []
    favorites: list[str] = md.load_watchlist()
    class_counts: dict[str, str] = {
        "acao": "385",
        "fii": "354",
        "etf": "232",
        "bdr": "655",
        "favoritos": "8",
        "todos": "1626",
    }
    breadth: dict[str, str] = {
        "total_stocks": "385",
        "total_assets": "1.626",
        "total_issuers": "300",
        "total_sectors": "20",
        "up_count": "—",
        "down_count": "—",
        "flat_count": "—",
        "up_pct": "—",
        "down_pct": "—",
        "up_width": "52%",
        "flat_width": "8%",
        "down_width": "40%",
        "sentiment_label": "Força Compradora Dominante",
        "total_market_cap": "—",
        "total_volume": "—",
        "top_gainer_ticker": "—",
        "top_gainer_change": "—",
        "top_loser_ticker": "—",
        "top_loser_change": "—",
        "most_active_ticker": "—",
        "most_active_volume": "—",
    }
    top_gainers: list[dict[str, str]] = []
    top_losers: list[dict[str, str]] = []
    most_active: list[dict[str, str]] = []
    ranking_tab: str = "altas"  # "altas" | "baixas" | "volume"

    # --- Filtros do Diretório B3 (/empresas) ------------------------------- #
    selected_asset_class: str = "acao"  # "acao" | "fii" | "etf" | "bdr" | "favoritos" | "todos"
    selected_sector: str = "Todos"
    show_all_sectors: bool = False
    search_query: str = ""
    sort_by: str = "Valor de Mercado"
    view_mode: str = "cards"  # "cards" | "tabela" | "heatmap"
    visible_limit: int = 48

    # --- Painel Lateral de Detalhes da Empresa (Slide-Over Drawer) --------- #
    drawer_open: bool = False
    drawer_loading: bool = False
    drawer_period: str = "90 dias"
    selected_stock: dict[str, str] = {
        "ticker": "PETR4",
        "yf_symbol": "PETR4.SA",
        "name": "Petrobras",
        "class_label": "Ação B3",
        "price": "R$ —",
        "change": "0,00%",
        "tone": "gray",
        "volume": "—",
        "market_cap": "—",
        "sector": "Petróleo, Gás e Combustíveis",
        "sector_short": "Petróleo & Gás",
        "subsector": "Petróleo e Gás Integrado",
        "logo": "",
        "initials": "PETR",
        "is_favorite": "1",
    }
    drawer_chart: list[dict[str, Any]] = []
    drawer_summary: dict[str, str] = {
        "current": "—",
        "first": "—",
        "mm20_label": "—",
        "range_sub": "—",
        "period_change": "0,00%",
        "period_diff": "—",
        "tone": "gray",
        "avg_volume": "—",
        "sessions": "—",
        "rsi_value": "50,0",
        "rsi_status": "Zona Neutra",
        "rsi_tone": "gray",
        "volatility": "—",
        "low_52w": "—",
        "high_52w": "—",
        "pos_52w_pct": "50%",
        "pos_52w_label": "—",
    }

    # --- Minha Carteira + Dividendos + Comparador Benchmarks --------------- #
    positions: list[dict[str, Any]] = md.load_saved_portfolio()
    portfolio_rows: list[dict[str, str]] = []
    portfolio_slices: list[dict[str, Any]] = []
    strategy_cards: list[dict[str, str]] = []
    portfolio_summary: dict[str, str] = {
        "total_value": "R$ —",
        "total_cost": "R$ —",
        "pnl": "R$ —",
        "pnl_pct": "0,00%",
        "tone": "gray",
        "arrow": "trending-up",
        "positions": "4",
        "annual_dividends": "R$ —",
        "monthly_dividends": "R$ —",
        "portfolio_dy": "—",
        "income_goal_pct": "0%",
        "income_goal_width": "10%",
    }
    portfolio_chart_mode: str = "comparador"  # "comparador" | "ativo"
    benchmark_chart: list[dict[str, Any]] = []
    benchmark_summary: dict[str, str] = {
        "carteira": "0,00%",
        "ibovespa": "0,00%",
        "cdi": "0,00%",
        "alpha": "0,00 p.p.",
        "tone": "gray",
    }
    selected_position_ticker: str = "PETR4"
    position_chart: list[dict[str, Any]] = []
    position_chart_summary: dict[str, str] = {
        "current": "—",
        "first": "—",
        "mm20_label": "—",
        "range_sub": "—",
        "period_change": "0,00%",
        "period_diff": "—",
        "tone": "gray",
        "avg_volume": "—",
        "sessions": "—",
    }
    position_chart_loading: bool = False
    trade_modal_open: bool = False
    form_ticker: str = "BBAS3"
    form_qty: str = "200"
    form_price: str = "28,50"
    form_note: str = "Bancos & Dividendos"

    # --- Agenda do Mercado (/calendario) ----------------------------------- #
    calendar_category: str = "Todos"

    # --- Notícias em Português (/noticias) --------------------------------- #
    news_topic: str = "Todas"
    news_loading: bool = False
    news: list[dict[str, str]] = []

    # ----------------------------------------------------------------------- #
    # Variáveis Computadas (@rx.var)
    # ----------------------------------------------------------------------- #
    @rx.var
    def has_error(self) -> bool:
        return self.error_message != ""

    @rx.var
    def canvas_class(self) -> str:
        return f"aq-canvas aq-glass-{self.glass_mode}"

    @rx.var
    def glass_mode_label(self) -> str:
        if self.glass_mode == "cristal":
            return "Vidro Cristal"
        if self.glass_mode == "obsidiana":
            return "Obsidiana"
        return "Vidro Fumê"

    @rx.var
    def is_drawer_favorite(self) -> bool:
        return self.selected_stock.get("ticker", "") in self.favorites

    @rx.var
    def ibov_quote(self) -> dict[str, str]:
        for k in self.kpis:
            if k.get("symbol") == "^BVSP":
                return k
        return {"price": "—", "change": "0,00%", "color": "gray"}

    @rx.var
    def usd_quote(self) -> dict[str, str]:
        for k in self.kpis:
            if k.get("symbol") == "USDBRL=X":
                return k
        return {"price": "R$ —", "change": "0,00%", "color": "gray"}

    @rx.var
    def btc_quote(self) -> dict[str, str]:
        for k in self.kpis:
            if k.get("symbol") == "BTC-USD":
                return k
        return {"price": "US$ —", "change": "0,00%", "color": "gray"}

    @rx.var
    def top_sectors(self) -> list[dict[str, str]]:
        return self.sectors[:6]

    @rx.var
    def active_ranking_rows(self) -> list[dict[str, str]]:
        if self.ranking_tab == "baixas":
            return self.top_losers
        if self.ranking_tab == "volume":
            return self.most_active
        return self.top_gainers

    @rx.var
    def sector_options(self) -> list[dict[str, str]]:
        total_st = len(self._all_stocks) or 385
        pills = [{"key": "Todos", "label": "Todos os Segmentos", "count": str(total_st)}]
        for sec in self.sectors:
            pills.append(
                {
                    "key": sec["key"],
                    "label": sec["short"],
                    "count": str(sec["count"]),
                }
            )
        return pills

    @rx.var
    def visible_sector_options(self) -> list[dict[str, str]]:
        all_opts = self.sector_options
        if self.show_all_sectors:
            return all_opts
        top = all_opts[:7]
        if self.selected_sector != "Todos" and not any(p["key"] == self.selected_sector for p in top):
            for p in all_opts[7:]:
                if p["key"] == self.selected_sector:
                    top.append(p)
                    break
        return top

    @rx.var
    def has_active_filters(self) -> bool:
        return (
            self.selected_sector != "Todos"
            or self.search_query.strip() != ""
            or self.selected_asset_class != "acao"
        )

    def _filtered_pool(self) -> list[dict[str, Any]]:
        """Filtra no servidor por classe de ativo, favoritos, setor, busca e ordenação."""
        pool = self._all_assets if self._all_assets else self._all_stocks
        fav_set = set(self.favorites)

        if self.selected_asset_class == "favoritos":
            items = [s for s in pool if s.get("ticker") in fav_set]
        elif self.selected_asset_class != "todos":
            items = [s for s in pool if s.get("asset_class") == self.selected_asset_class]
        else:
            items = list(pool)

        if self.selected_asset_class == "acao" and self.selected_sector != "Todos":
            items = [s for s in items if s.get("sector_key") == self.selected_sector]

        q = self.search_query.strip().lower()
        if q:
            items = [
                s
                for s in items
                if q in s.get("ticker", "").lower()
                or q in s.get("name", "").lower()
                or q in s.get("sector", "").lower()
                or q in s.get("subsector", "").lower()
            ]

        if self.sort_by == "Volume Negociado":
            items = sorted(items, key=lambda s: s.get("volume_raw", 0.0), reverse=True)
        elif self.sort_by == "Maiores Altas":
            items = sorted(items, key=lambda s: s.get("change_raw", 0.0), reverse=True)
        elif self.sort_by == "Maiores Baixas":
            items = sorted(items, key=lambda s: s.get("change_raw", 0.0))
        elif self.sort_by == "Ordem Alfabética":
            items = sorted(items, key=lambda s: s.get("ticker", ""))
        else:
            items = sorted(
                items,
                key=lambda s: (s.get("market_cap_raw", 0.0), s.get("volume_raw", 0.0)),
                reverse=True,
            )
        return items

    @rx.var
    def visible_stocks(self) -> list[dict[str, str]]:
        fav_set = set(self.favorites)
        out: list[dict[str, str]] = []
        for s in self._filtered_pool()[: self.visible_limit]:
            item = dict(s)
            item["is_favorite"] = "1" if item.get("ticker") in fav_set else "0"
            out.append(item)
        return out

    @rx.var
    def filtered_count(self) -> int:
        return len(self._filtered_pool())

    @rx.var
    def has_more_stocks(self) -> bool:
        return len(self._filtered_pool()) > self.visible_limit

    @rx.var
    def palette_results(self) -> list[dict[str, str]]:
        """Top 8 resultados instantâneos para o modal de Busca Rápida Global."""
        pool = self._all_assets if self._all_assets else self._all_stocks
        q = self.palette_query.strip().lower()
        if not q:
            return pool[:8]
        matched = [
            s
            for s in pool
            if q in s.get("ticker", "").lower()
            or q in s.get("name", "").lower()
            or q in s.get("sector_short", "").lower()
            or q in s.get("subsector", "").lower()
        ]
        return matched[:8]

    @rx.var
    def selected_position_row(self) -> dict[str, str]:
        for row in self.portfolio_rows:
            if row.get("ticker") == self.selected_position_ticker:
                return row
        if self.portfolio_rows:
            return self.portfolio_rows[0]
        return {
            "ticker": "PETR4",
            "name": "Petrobras",
            "total": "R$ —",
            "cost": "R$ —",
            "pnl": "R$ —",
            "pnl_pct": "0,00%",
            "dy_label": "13,8% a.a.",
            "annual_div": "R$ —",
            "avg_price": "R$ —",
            "price": "R$ —",
            "quantity": "0",
        }

    @rx.var
    def calendar_events(self) -> list[dict[str, str]]:
        # Depende de last_update para reavaliar automaticamente a cada ciclo de 60s
        _ = self.last_update
        return md.get_market_calendar(self.calendar_category)

    @rx.var
    def calendar_summary(self) -> dict[str, str]:
        _ = self.last_update
        bundle = md.fetch_live_calendar_bundle(force=False)
        return bundle.get(
            "summary",
            {
                "div_headline": "PETR4 · VALE3 · BBAS3",
                "div_sub": "Proventos reais B3 & FIIs",
                "earn_headline": "Balanços & Receita B3",
                "earn_sub": "ITUB4 · VALE3 · MGLU3",
                "macro_headline": "Selic & IPCA (BCB)",
                "macro_sub": "Taxas oficiais do Banco Central",
                "exp_headline": "Exercício de Opções B3",
                "exp_sub": "3ª sexta-feira do mês (15:00 BRT)",
            },
        )

    @rx.event
    async def open_calendar_ticker(self, ticker: str):
        """Ao clicar num card da Agenda, abre o Raio-X lateral do ativo correspondente."""
        tk = str(ticker).upper().strip()
        if not tk:
            return
        pool = self._all_assets if self._all_assets else self._all_stocks
        found = next((s for s in pool if s.get("ticker") == tk), None)
        if not found:
            found = {
                "ticker": tk,
                "name": tk,
                "price": "R$ —",
                "change": "0,00%",
                "tone": "gray",
                "sector": "Mercado B3",
                "sector_short": "B3",
                "subsector": "Ativo B3",
                "volume": "—",
                "market_cap": "—",
                "asset_class": "acao",
                "class_label": "Ativo B3",
            }
        async for _ in self.open_stock_drawer(found):
            yield

    # ----------------------------------------------------------------------- #
    # Eventos Principais de Atualização Online
    # ----------------------------------------------------------------------- #
    def _stamp_clock(self) -> None:
        now = fmt.now_brt()
        self.greeting_text = fmt.greeting(now)
        self.today_label = fmt.long_date(now)
        is_open, label = fmt.market_status(now)
        self.market_open = is_open
        self.market_status_label = label
        self.last_update = fmt.timestamp_now()

    @rx.event
    def cycle_glass_mode(self):
        """Alterna entre Vidro Cristal -> Vidro Fumê -> Obsidiana Profunda."""
        order = ("cristal", "fume", "obsidiana")
        idx = order.index(self.glass_mode) if self.glass_mode in order else 1
        self.glass_mode = order[(idx + 1) % len(order)]

    @rx.event
    def toggle_favorite(self, ticker: str):
        """Adiciona ou remove um ativo da lista de Favoritos (`data/watchlist.json`)."""
        t = str(ticker).upper().strip()
        if not t:
            return
        favs = list(self.favorites)
        if t in favs:
            favs.remove(t)
        else:
            favs.insert(0, t)
        self.favorites = favs
        md.save_watchlist(favs)
        counts = dict(self.class_counts)
        counts["favoritos"] = str(len(favs))
        self.class_counts = counts

    @rx.event
    def toggle_drawer_favorite(self):
        ticker = self.selected_stock.get("ticker", "")
        if ticker:
            self.toggle_favorite(ticker)

    @rx.event
    async def refresh_all(self, force_catalog: bool = False):
        """Atualiza em paralelo: catálogo B3 (~1.600 ativos), macro, gráfico, carteira e notícias."""
        self.is_loading = True
        self.chart_loading = True
        self.error_message = ""
        self.positions = md.load_saved_portfolio()
        self.favorites = md.load_watchlist()
        self._stamp_clock()
        yield

        days = md.PERIOD_OPTIONS.get(self.chart_period, 90)
        symbol = self.chart_symbol

        catalog, macros, chart_bundle, news_items = await asyncio.gather(
            asyncio.to_thread(md.fetch_b3_catalog, force_catalog),
            asyncio.to_thread(md.fetch_macro_quotes),
            asyncio.to_thread(md.fetch_chart_bundle, symbol, days),
            asyncio.to_thread(md.fetch_news_ptbr, self.news_topic),
        )

        if catalog.get("stocks"):
            self._all_stocks = catalog["stocks"]
            self._all_assets = catalog["all_assets"]
            self.sectors = catalog["sectors"]
            self.breadth = catalog["breadth"]
            self.top_gainers = catalog["top_gainers"]
            self.top_losers = catalog["top_losers"]
            self.most_active = catalog["most_active"]
            self.heatmap_tiles = catalog["heatmap_tiles"]
            self.ticker_tape_items = catalog.get("ticker_tape", catalog["stocks"][:12])
            counts = dict(catalog["class_counts"])
            counts["favoritos"] = str(len(self.favorites))
            self.class_counts = counts

        self.kpis = macros
        self.chart_data = chart_bundle["points"]
        self.chart_summary = chart_bundle["summary"]

        pf = await asyncio.to_thread(md.compute_portfolio, self.positions, self._all_assets)
        self.portfolio_rows = pf["rows"]
        self.portfolio_slices = pf["slices"]
        self.strategy_cards = pf["strategy_cards"]
        self.portfolio_summary = pf["summary"]

        if news_items:
            self.news = news_items

        if not self._all_stocks and not self.chart_data:
            self.error_message = (
                "Alguns serviços de cotação demoraram para responder. "
                "Clique em 'Atualizar Mercado' para tentar novamente."
            )

        self._stamp_clock()
        self.is_loading = False
        self.chart_loading = False

        # Pré-aquece os demais benchmarks e o bundle da Agenda em segundo plano
        asyncio.create_task(asyncio.to_thread(md.prewarm_benchmarks, days))
        asyncio.create_task(asyncio.to_thread(md.fetch_live_calendar_bundle, force_catalog))

    @rx.event
    async def manual_refresh(self):
        async for _ in self.refresh_all(force_catalog=True):
            yield

    @rx.event
    async def tick_auto_refresh(self, _value: str = ""):
        if not self.auto_refresh or self.is_loading:
            return
        async for _ in self.refresh_all(force_catalog=True):
            yield

    @rx.event
    def toggle_auto_refresh(self):
        self.auto_refresh = not self.auto_refresh

    # ----------------------------------------------------------------------- #
    # Eventos da Busca Rápida Global (Command Palette)
    # ----------------------------------------------------------------------- #
    @rx.event
    def set_command_palette_open(self, is_open: bool):
        self.command_palette_open = is_open
        if not is_open:
            self.palette_query = ""

    @rx.event
    def set_palette_query(self, query: str):
        self.palette_query = query

    @rx.event
    async def select_from_palette(self, stock: dict[str, Any]):
        """Ao clicar num ativo na Busca Rápida, fecha o modal e abre a ficha lateral."""
        self.command_palette_open = False
        self.palette_query = ""
        async for _ in self.open_stock_drawer(stock):
            yield

    # ----------------------------------------------------------------------- #
    # Eventos do Gráfico Analítico Principal + MM20
    # ----------------------------------------------------------------------- #
    @rx.event
    async def select_benchmark(self, symbol: str, label: str, subtitle: str):
        self.chart_symbol = symbol
        self.chart_label = label
        self.chart_subtitle = subtitle
        self.chart_loading = True
        yield
        days = md.PERIOD_OPTIONS.get(self.chart_period, 90)
        bundle = await asyncio.to_thread(md.fetch_chart_bundle, symbol, days)
        self.chart_data = bundle["points"]
        self.chart_summary = bundle["summary"]
        self.chart_loading = False

    @rx.event
    async def set_chart_period(self, period: str):
        self.chart_period = period
        self.chart_loading = True
        yield
        days = md.PERIOD_OPTIONS.get(period, 90)
        bundle = await asyncio.to_thread(md.fetch_chart_bundle, self.chart_symbol, days)
        self.chart_data = bundle["points"]
        self.chart_summary = bundle["summary"]
        self.chart_loading = False

    @rx.event
    def set_chart_mode(self, mode: str):
        self.chart_mode = mode

    @rx.event
    def toggle_mm20(self):
        self.show_mm20 = not self.show_mm20

    @rx.event
    def set_ranking_tab(self, tab: str):
        self.ranking_tab = tab

    # ----------------------------------------------------------------------- #
    # Eventos do Diretório de Empresas e Ativos B3 (/empresas)
    # ----------------------------------------------------------------------- #
    @rx.event
    async def ensure_catalog_loaded(self):
        if not self._all_stocks:
            async for _ in self.refresh_all(force_catalog=False):
                yield

    @rx.event
    def set_asset_class(self, asset_class: str):
        self.selected_asset_class = asset_class
        self.selected_sector = "Todos"
        self.visible_limit = 48

    @rx.event
    def set_sector_filter(self, sector_key: str):
        self.selected_asset_class = "acao"
        self.selected_sector = sector_key
        self.visible_limit = 48

    @rx.event
    def toggle_all_sectors(self):
        self.show_all_sectors = not self.show_all_sectors

    @rx.event
    def clear_filters(self):
        self.selected_asset_class = "acao"
        self.selected_sector = "Todos"
        self.search_query = ""
        self.sort_by = "Valor de Mercado"
        self.visible_limit = 48

    @rx.event
    def filter_by_sector_and_navigate(self, sector_key: str):
        self.selected_asset_class = "acao"
        self.selected_sector = sector_key
        self.visible_limit = 48
        return rx.redirect("/empresas")

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value
        self.visible_limit = 48

    @rx.event
    def set_sort_by(self, value: str):
        self.sort_by = value

    @rx.event
    def set_view_mode(self, mode: str):
        self.view_mode = mode
        if mode == "heatmap" and self.visible_limit < 80:
            self.visible_limit = 80

    @rx.event
    def show_more_stocks(self):
        self.visible_limit += 80

    @rx.event
    def show_all_stocks(self):
        self.visible_limit = 2000

    # ----------------------------------------------------------------------- #
    # Eventos do Drawer Lateral de Detalhes da Empresa
    # ----------------------------------------------------------------------- #
    @rx.event
    async def open_stock_drawer(self, stock: dict[str, Any]):
        self.selected_stock = stock
        self.drawer_open = True
        self.drawer_loading = True
        yield
        yf_symbol = stock.get("yf_symbol") or f"{stock.get('ticker', 'PETR4')}.SA"
        days = md.PERIOD_OPTIONS.get(self.drawer_period, 90)
        bundle = await asyncio.to_thread(md.fetch_chart_bundle, yf_symbol, days)
        self.drawer_chart = bundle["points"]
        self.drawer_summary = bundle["summary"]
        self.drawer_loading = False

    @rx.event
    def set_drawer_open(self, is_open: bool):
        self.drawer_open = is_open

    @rx.event
    async def set_drawer_period(self, period: str):
        self.drawer_period = period
        self.drawer_loading = True
        yield
        yf_symbol = self.selected_stock.get("yf_symbol") or f"{self.selected_stock.get('ticker', 'PETR4')}.SA"
        days = md.PERIOD_OPTIONS.get(period, 90)
        bundle = await asyncio.to_thread(md.fetch_chart_bundle, yf_symbol, days)
        self.drawer_chart = bundle["points"]
        self.drawer_summary = bundle["summary"]
        self.drawer_loading = False

    @rx.event
    async def promote_drawer_stock_to_main_chart(self):
        ticker = self.selected_stock.get("ticker", "PETR4")
        yf_symbol = self.selected_stock.get("yf_symbol") or f"{ticker}.SA"
        name = self.selected_stock.get("name", ticker)
        sector = self.selected_stock.get("sector_short", "B3")
        self.drawer_open = False
        self.chart_symbol = yf_symbol
        self.chart_label = ticker
        self.chart_subtitle = f"{name} · {sector}"
        self.chart_loading = True
        yield rx.redirect("/")
        days = md.PERIOD_OPTIONS.get(self.chart_period, 90)
        bundle = await asyncio.to_thread(md.fetch_chart_bundle, yf_symbol, days)
        self.chart_data = bundle["points"]
        self.chart_summary = bundle["summary"]
        self.chart_loading = False

    @rx.event
    def open_trade_modal_for_drawer_stock(self):
        self.form_ticker = str(self.selected_stock.get("ticker", "PETR4"))
        raw_px = self.selected_stock.get("price_raw", 30.0)
        self.form_price = fmt.format_number(float(raw_px or 30.0), 2)
        self.form_qty = "100"
        self.form_note = str(self.selected_stock.get("sector_short", "Aporte B3"))
        self.drawer_open = False
        self.trade_modal_open = True

    # ----------------------------------------------------------------------- #
    # Eventos da Página Minha Carteira (/carteira) + Comparador + CSV
    # ----------------------------------------------------------------------- #
    @rx.event
    async def load_portfolio_page(self):
        self.positions = md.load_saved_portfolio()
        if not self._all_stocks:
            async for _ in self.refresh_all(force_catalog=False):
                yield
        else:
            pf = await asyncio.to_thread(md.compute_portfolio, self.positions, self._all_assets)
            self.portfolio_rows = pf["rows"]
            self.portfolio_slices = pf["slices"]
            self.strategy_cards = pf["strategy_cards"]
            self.portfolio_summary = pf["summary"]

        self.position_chart_loading = True
        yield
        ticker = self.selected_position_ticker or (
            self.portfolio_rows[0]["ticker"] if self.portfolio_rows else "PETR4"
        )
        pos_bundle, bench_bundle = await asyncio.gather(
            asyncio.to_thread(md.fetch_chart_bundle, f"{ticker}.SA", 90),
            asyncio.to_thread(md.fetch_benchmark_comparison, self.positions, 90),
        )
        self.position_chart = pos_bundle["points"]
        self.position_chart_summary = pos_bundle["summary"]
        self.benchmark_chart = bench_bundle["points"]
        self.benchmark_summary = bench_bundle["summary"]
        self.position_chart_loading = False

    @rx.event
    async def select_position_card(self, ticker: str):
        self.selected_position_ticker = ticker
        self.portfolio_chart_mode = "ativo"
        self.position_chart_loading = True
        yield
        bundle = await asyncio.to_thread(md.fetch_chart_bundle, f"{ticker}.SA", 90)
        self.position_chart = bundle["points"]
        self.position_chart_summary = bundle["summary"]
        self.position_chart_loading = False

    @rx.event
    def set_portfolio_chart_mode(self, mode: str):
        self.portfolio_chart_mode = mode

    @rx.event
    def set_trade_modal_open(self, is_open: bool):
        self.trade_modal_open = is_open

    @rx.event
    def set_form_ticker(self, value: str):
        self.form_ticker = value.upper().strip()

    @rx.event
    def set_form_qty(self, value: str):
        self.form_qty = value

    @rx.event
    def set_form_price(self, value: str):
        self.form_price = value

    @rx.event
    def set_form_note(self, value: str):
        self.form_note = value

    @rx.event
    async def save_position(self):
        """Adiciona/atualiza posição, persiste em `data/portfolio.json` e recalcula benchmarks."""
        ticker = self.form_ticker.strip().upper().replace(".SA", "")
        try:
            qty = max(1, int(float(self.form_qty.replace(".", "").replace(",", "."))))
        except ValueError:
            qty = 100
        try:
            avg_price = max(0.01, float(self.form_price.replace("R$", "").replace(".", "").replace(",", ".").strip()))
        except ValueError:
            avg_price = 25.0

        updated: list[dict[str, Any]] = []
        found = False
        for pos in self.positions:
            if pos["ticker"] == ticker:
                updated.append(
                    {
                        "ticker": ticker,
                        "quantity": qty,
                        "avg_price": avg_price,
                        "note": self.form_note or pos.get("note", "B3"),
                    }
                )
                found = True
            else:
                updated.append(pos)
        if not found and ticker:
            updated.append(
                {
                    "ticker": ticker,
                    "quantity": qty,
                    "avg_price": avg_price,
                    "note": self.form_note or "Posição simulada",
                }
            )

        self.positions = updated
        md.save_portfolio_to_disk(updated)
        self.trade_modal_open = False
        self.selected_position_ticker = ticker

        pf, bench = await asyncio.gather(
            asyncio.to_thread(md.compute_portfolio, self.positions, self._all_assets),
            asyncio.to_thread(md.fetch_benchmark_comparison, self.positions, 90),
        )
        self.portfolio_rows = pf["rows"]
        self.portfolio_slices = pf["slices"]
        self.strategy_cards = pf["strategy_cards"]
        self.portfolio_summary = pf["summary"]
        self.benchmark_chart = bench["points"]
        self.benchmark_summary = bench["summary"]

    @rx.event
    async def remove_position(self, ticker: str):
        remaining = [p for p in self.positions if p["ticker"] != ticker]
        if not remaining:
            return
        self.positions = remaining
        md.save_portfolio_to_disk(remaining)
        pf, bench = await asyncio.gather(
            asyncio.to_thread(md.compute_portfolio, self.positions, self._all_assets),
            asyncio.to_thread(md.fetch_benchmark_comparison, self.positions, 90),
        )
        self.portfolio_rows = pf["rows"]
        self.portfolio_slices = pf["slices"]
        self.strategy_cards = pf["strategy_cards"]
        self.portfolio_summary = pf["summary"]
        self.benchmark_chart = bench["points"]
        self.benchmark_summary = bench["summary"]

    @rx.event
    async def reset_default_portfolio(self):
        """Restaura a carteira de demonstração inicial e salva em disco."""
        self.positions = [dict(item) for item in md.DEFAULT_PORTFOLIO]
        md.save_portfolio_to_disk(self.positions)
        pf, bench = await asyncio.gather(
            asyncio.to_thread(md.compute_portfolio, self.positions, self._all_assets),
            asyncio.to_thread(md.fetch_benchmark_comparison, self.positions, 90),
        )
        self.portfolio_rows = pf["rows"]
        self.portfolio_slices = pf["slices"]
        self.strategy_cards = pf["strategy_cards"]
        self.portfolio_summary = pf["summary"]
        self.benchmark_chart = bench["points"]
        self.benchmark_summary = bench["summary"]

    @rx.event
    def download_portfolio_csv(self):
        """Gera e baixa o arquivo CSV da carteira atual."""
        csv_data = md.export_portfolio_csv(self.portfolio_rows, self.portfolio_summary)
        return rx.download(data=csv_data, filename="aeroquant_carteira_b3.csv")

    # ----------------------------------------------------------------------- #
    # Eventos da Agenda (/calendario) & Notícias (/noticias)
    # ----------------------------------------------------------------------- #
    @rx.event
    def set_calendar_category(self, category: str):
        self.calendar_category = category

    @rx.event
    async def load_news_page(self):
        if not self.news:
            await self.select_news_topic(self.news_topic)

    @rx.event
    async def select_news_topic(self, topic: str):
        self.news_topic = topic
        self.news_loading = True
        yield
        items = await asyncio.to_thread(md.fetch_news_ptbr, topic)
        if items:
            self.news = items
            self._stamp_clock()
        self.news_loading = False
