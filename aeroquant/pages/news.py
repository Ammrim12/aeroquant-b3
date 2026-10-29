"""Página '/noticias' — Central de Notícias Financeiras em Português."""

from __future__ import annotations

import reflex as rx

from ..components.layout import page_layout
from ..components.news import news_feed, news_filter_bar
from ..state import State


def news_page() -> rx.Component:
    summary_line = rx.text(
        "Manchetes em português dos principais veículos econômicos do Brasil · Atualizado às ",
        rx.text.strong(State.last_update),
        ".",
        size="2",
        color="var(--aq-text-muted)",
    )
    return page_layout(
        "Notícias",
        "Central de Notícias — Brasil",
        summary_line,
        news_feed(),
        fixed_filter=news_filter_bar(),
    )
