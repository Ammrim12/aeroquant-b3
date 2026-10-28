"""Página '/carteira' — Minha Carteira (inspirada em 'Balances · Accounts' do Coffra)."""

from __future__ import annotations

import reflex as rx

from ..components.layout import page_layout
from ..components.portfolio import portfolio_view
from ..state import State


def portfolio_page() -> rx.Component:
    s = State.portfolio_summary
    summary_line = rx.text(
        rx.text.strong(s["total_value"]),
        " distribuídos em ",
        rx.text.strong(s["positions"], " posições"),
        " na B3 · Retorno acumulado de ",
        rx.text.strong(s["pnl"]),
        " (",
        s["pnl_pct"],
        ") atualizado às ",
        State.last_update,
        ".",
        size="2",
        color="var(--aq-text-muted)",
    )
    return page_layout(
        "Minha Carteira",
        "Saldos & Posições",
        summary_line,
        portfolio_view(),
    )
