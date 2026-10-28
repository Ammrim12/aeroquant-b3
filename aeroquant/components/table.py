"""Seção inferior da Visão Geral: Destaques do Pregão + Últimas Manchetes em Português."""

from __future__ import annotations

import reflex as rx

from ..state import State
from .styles import ROW_HOVER, SURFACE_CARD, filter_pill_style


def _mover_row(stock: dict) -> rx.Component:
    """Linha clicável de uma empresa nos rankings da Visão Geral (abre o Drawer)."""
    return rx.hstack(
        rx.avatar(
            src=stock["logo"],
            fallback=stock["initials"],
            size="2",
            radius="medium",
            color_scheme="jade",
        ),
        rx.vstack(
            rx.hstack(
                rx.text(stock["ticker"], size="2", weight="bold", color="var(--aq-text)"),
                rx.badge(
                    stock["sector_short"],
                    variant="surface",
                    color_scheme="gray",
                    radius="full",
                    size="1",
                ),
                align="center",
                spacing="2",
            ),
            rx.text(stock["name"], size="1", color="var(--aq-text-muted)"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.vstack(
            rx.text(stock["price"], size="2", weight="bold", color="var(--aq-text)"),
            rx.badge(
                stock["change"],
                color_scheme=stock["tone"],
                variant="soft",
                radius="full",
                size="1",
            ),
            spacing="1",
            align="end",
        ),
        rx.icon("chevron-right", size=15, color="var(--aq-text-soft)"),
        width="100%",
        align="center",
        spacing="3",
        padding="0.55rem 0.65rem",
        border_radius="10px",
        on_click=State.open_stock_drawer(stock),
        **ROW_HOVER,
    )


def _headline_row(item: dict) -> rx.Component:
    """Linha de notícia em português (estilo 'Latest mail' em 1:23 do vídeo)."""
    return rx.link(
        rx.hstack(
            rx.center(
                rx.text(item["initials"], size="1", weight="bold", color="var(--aq-primary)"),
                width="34px",
                height="34px",
                border_radius="999px",
                background="var(--aq-primary-soft)",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(item["publisher"], size="1", weight="bold", color="var(--aq-primary)"),
                    rx.text("·", size="1", color="var(--aq-text-soft)"),
                    rx.text(item["time"], size="1", color="var(--aq-text-muted)"),
                    rx.badge(
                        item["topic"],
                        variant="surface",
                        color_scheme="jade",
                        radius="full",
                        size="1",
                    ),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                rx.text(
                    item["title"],
                    size="2",
                    weight="medium",
                    color="var(--aq-text)",
                    line_height="1.35",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.icon("arrow-up-right", size=15, color="var(--aq-text-soft)"),
            width="100%",
            align="start",
            spacing="3",
            padding="0.6rem 0.65rem",
            border_radius="10px",
            **ROW_HOVER,
        ),
        href=item["url"],
        is_external=True,
        underline="none",
        width="100%",
    )


def movers_table() -> rx.Component:
    """Grade dupla inferior: Rankings de Ações (esquerda) + Manchetes do Dia (direita)."""
    return rx.grid(
        # Coluna esquerda: Rankings interativos da B3
        rx.box(
            rx.vstack(
                rx.flex(
                    rx.vstack(
                        rx.heading("Destaques do Pregão B3", size="4", weight="bold"),
                        rx.text(
                            "Clique em uma empresa para abrir a ficha completa ao lado",
                            size="1",
                            color="var(--aq-text-muted)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.hstack(
                        rx.box(
                            "Maiores Altas",
                            on_click=State.set_ranking_tab("altas"),
                            **filter_pill_style(State.ranking_tab == "altas"),
                        ),
                        rx.box(
                            "Maiores Baixas",
                            on_click=State.set_ranking_tab("baixas"),
                            **filter_pill_style(State.ranking_tab == "baixas"),
                        ),
                        rx.box(
                            "Mais Negociadas",
                            on_click=State.set_ranking_tab("volume"),
                            **filter_pill_style(State.ranking_tab == "volume"),
                        ),
                        spacing="1",
                        wrap="wrap",
                    ),
                    direction=rx.breakpoints(initial="column", sm="row"),
                    justify="between",
                    align=rx.breakpoints(initial="start", sm="center"),
                    gap="0.5rem",
                    width="100%",
                ),
                rx.vstack(
                    rx.foreach(State.active_ranking_rows, _mover_row),
                    spacing="1",
                    width="100%",
                ),
                rx.divider(),
                rx.hstack(
                    rx.text(
                        "Mostrando top 6 de ",
                        State.breadth["total_stocks"],
                        " ações listadas",
                        size="1",
                        color="var(--aq-text-muted)",
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.text("Explorar todas as empresas →", size="1", weight="bold", color="var(--aq-primary)"),
                        href="/empresas",
                        underline="none",
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            class_name="aq-fade-in",
            **SURFACE_CARD,
        ),
        # Coluna direita: Últimas manchetes em português (estilo 'Latest mail')
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Giro de Notícias (Brasil)", size="4", weight="bold"),
                        rx.text(
                            "Manchetes econômicas em português atualizadas ao vivo",
                            size="1",
                            color="var(--aq-text-muted)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.link(
                        rx.text("Todas →", size="2", weight="bold", color="var(--aq-primary)"),
                        href="/noticias",
                        underline="none",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.vstack(
                    rx.foreach(State.news[:5], _headline_row),
                    spacing="1",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            class_name="aq-fade-in",
            **SURFACE_CARD,
        ),
        columns=rx.breakpoints(initial="1", lg="2"),
        spacing="4",
        width="100%",
    )
