"""Página '/calendario' — Agenda do Mercado, Dividendos, Balanços e Copom na B3."""

from __future__ import annotations

import reflex as rx

from ..components.calendar import calendar_filter_bar, calendar_view
from ..components.layout import page_layout
from ..state import State


def calendar_page() -> rx.Component:
    summary = rx.text(
        "Cronograma corporativo e macroeconômico do mercado brasileiro: ",
        rx.text.strong("Data-Com de Dividendos & JCP"),
        ", ",
        rx.text.strong("Temporada de Balanços da B3"),
        ", ",
        rx.text.strong("Reuniões do Copom & IPCA"),
        " e ",
        rx.text.strong("Rendimentos de FIIs"),
        " · Atualizado em ",
        State.today_label,
        ".",
        size="2",
        color="var(--aq-text-muted)",
    )
    return page_layout(
        "Agenda & Dividendos",
        "Agenda do Mercado & Proventos — B3",
        summary,
        calendar_view(),
        fixed_filter=calendar_filter_bar(),
    )

