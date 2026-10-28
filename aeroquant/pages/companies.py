"""Página '/empresas' — Diretório de todas as empresas e classes de ativos da B3."""

from __future__ import annotations

import reflex as rx

from ..components.companies import companies_explorer
from ..components.layout import page_layout
from ..state import State


def companies_page() -> rx.Component:
    summary = rx.text(
        rx.text.strong(State.class_counts["todos"], " ativos negociados na B3"),
        ": ",
        rx.text.strong(State.breadth["total_stocks"], " ações de empresas"),
        " em ",
        rx.text.strong(State.breadth["total_sectors"], " segmentos"),
        " (bancos, lojas, fábricas, energia, mineração, saúde, tecnologia e construção), além de ",
        rx.text.strong(State.class_counts["fii"], " FIIs"),
        ", ",
        rx.text.strong(State.class_counts["etf"], " ETFs"),
        " e ",
        rx.text.strong(State.class_counts["bdr"], " BDRs"),
        ". Clique em qualquer ativo para abrir o Raio-X lateral.",
        size="2",
        color="var(--aq-text-muted)",
    )
    return page_layout(
        "Empresas da B3",
        "Diretório de Empresas & Ativos — B3",
        summary,
        companies_explorer(),
    )
