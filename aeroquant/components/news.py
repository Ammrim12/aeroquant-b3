"""Feed de Notícias em Português (inspirado na tela 'All mail · Inbox' do vídeo Coffra)."""

from __future__ import annotations

import reflex as rx

from ..services.market_data import NEWS_QUERIES
from ..state import State
from .styles import ROW_HOVER, SURFACE_CARD, filter_pill_style


def _topic_pill(topic: str) -> rx.Component:
    is_active = State.news_topic == topic
    return rx.box(
        topic,
        on_click=State.select_news_topic(topic),
        **filter_pill_style(is_active),
    )


def _inbox_news_row(item: dict) -> rx.Component:
    """Linha de notícia estilo 'Inbox' (1:16 do vídeo Coffra)."""
    return rx.link(
        rx.hstack(
            rx.center(
                rx.text(item["initials"], size="1", weight="bold", color="var(--aq-primary)"),
                width="38px",
                height="38px",
                border_radius="999px",
                background="var(--aq-primary-soft)",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(item["publisher"], size="2", weight="bold", color="var(--aq-text)"),
                    rx.badge(
                        item["topic"],
                        variant="surface",
                        color_scheme="jade",
                        radius="full",
                        size="1",
                    ),
                    rx.text(item["date"], size="1", color="var(--aq-text-soft)"),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                rx.text(
                    item["title"],
                    size="3",
                    weight="medium",
                    color="var(--aq-text)",
                    line_height="1.4",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            rx.spacer(),
            rx.hstack(
                rx.text(item["time"], size="1", color="var(--aq-text-muted)", white_space="nowrap"),
                rx.icon("arrow-up-right", size=16, color="var(--aq-primary)"),
                align="center",
                spacing="2",
            ),
            width="100%",
            align="center",
            spacing="3",
            padding="0.85rem 1rem",
            border_bottom="1px solid var(--aq-border)",
            **ROW_HOVER,
        ),
        href=item["url"],
        is_external=True,
        underline="none",
        width="100%",
    )


def news_feed() -> rx.Component:
    """Feed completo de notícias em português com filtro por editoria."""
    return rx.vstack(
        rx.hstack(
            *[_topic_pill(topic) for topic in NEWS_QUERIES],
            spacing="2",
            width="100%",
            overflow_x="auto",
            padding_bottom="2px",
        ),
        rx.box(
            rx.cond(
                State.news_loading,
                rx.vstack(
                    *[rx.skeleton(height="64px", width="100%", border_radius="10px") for _ in range(6)],
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(State.news, _inbox_news_row),
                    spacing="0",
                    width="100%",
                ),
            ),
            **SURFACE_CARD,
        ),
        spacing="4",
        width="100%",
    )
