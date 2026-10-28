"""Ponto de entrada do AeroQuant: registro das 5 rotas e folhas de estilo."""

from __future__ import annotations

import reflex as rx

from .pages.calendar import calendar_page
from .pages.companies import companies_page
from .pages.market import market_page
from .pages.news import news_page
from .pages.portfolio import portfolio_page
from .state import State

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
