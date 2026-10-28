"""Página '/' — Visão Geral do Mercado (fiel à tela 'Overview — Coffra' do vídeo)."""

from __future__ import annotations

import reflex as rx

from ..components.chart import price_chart
from ..components.kpi_cards import b3_heatmap_card, kpi_cards, sector_xray_card
from ..components.layout import page_layout
from ..components.table import movers_table
from ..state import State


def market_page() -> rx.Component:
    # Linha executiva dinâmica idêntica a "Monday, October 26 · $490,268 across four accounts..."
    summary_line = rx.text(
        State.today_label,
        " · ",
        rx.text.strong(State.breadth["total_stocks"], " empresas"),
        " em ",
        rx.text.strong(State.breadth["total_sectors"], " segmentos"),
        " da B3 (",
        rx.text.strong(State.class_counts["todos"], " ativos"),
        " incluindo FIIs, ETFs e BDRs) · Ibovespa em ",
        rx.text.strong(State.ibov_quote["price"]),
        " (",
        State.ibov_quote["change"],
        ") e Dólar a ",
        rx.text.strong(State.usd_quote["price"]),
        ".",
        size="2",
        color="var(--aq-text-muted)",
    )
    return page_layout(
        "Visão Geral",
        rx.text(State.greeting_text, ", Investidor"),
        summary_line,
        price_chart(),
        sector_xray_card(),
        kpi_cards(),
        b3_heatmap_card(),
        movers_table(),
    )
