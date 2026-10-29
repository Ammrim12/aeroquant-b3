"""Ponto de entrada do AeroQuant: registro das 5 rotas, folhas de estilo e Keep-Alive anti-hibernação."""

from __future__ import annotations

import os
import threading
import time
import urllib.request

import reflex as rx

from .pages.calendar import calendar_page
from .pages.companies import companies_page
from .pages.market import market_page
from .pages.news import news_page
from .pages.portfolio import portfolio_page
from .state import State

_KEEPALIVE_STARTED = False


def _start_render_keepalive() -> None:
    """Envia ping externo periódico para evitar hibernação no Render Free Tier (timeout de 15 min)."""
    global _KEEPALIVE_STARTED
    if _KEEPALIVE_STARTED:
        return
    _KEEPALIVE_STARTED = True

    external_url = os.environ.get(
        "RENDER_EXTERNAL_URL", "https://aeroquant-b3.onrender.com"
    ).rstrip("/")

    def _loop() -> None:
        while True:
            time.sleep(540)  # A cada 9 minutos (antes do limite de 15 min do Render)
            try:
                req = urllib.request.Request(
                    f"{external_url}/ping",
                    headers={"User-Agent": "AeroQuant-KeepAlive/1.0"},
                )
                with urllib.request.urlopen(req, timeout=10):
                    pass
            except Exception:
                pass

    t = threading.Thread(target=_loop, name="aq-render-keepalive", daemon=True)
    t.start()


_start_render_keepalive()

app = rx.App(stylesheets=["/aeroquant.css"])

app.add_page(
    market_page,
    route="/",
    title="AeroQuant | Visão Geral — B3",
    on_load=State.refresh_all,
)
app.add_page(
    companies_page,
    route="/empresas",
    title="AeroQuant | Empresas & Ativos da B3",
    on_load=State.ensure_catalog_loaded,
)
app.add_page(
    portfolio_page,
    route="/carteira",
    title="AeroQuant | Minha Carteira",
    on_load=State.load_portfolio_page,
)
app.add_page(
    calendar_page,
    route="/calendario",
    title="AeroQuant | Agenda & Dividendos — B3",
    on_load=State.ensure_catalog_loaded,
)
app.add_page(
    news_page,
    route="/noticias",
    title="AeroQuant | Notícias do Mercado",
    on_load=State.load_news_page,
)
