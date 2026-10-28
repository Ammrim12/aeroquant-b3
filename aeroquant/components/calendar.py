"""Componente 'Agenda do Mercado & Dividendos B3' (inspirado na tela 'Calendar' em 1:18 do vídeo Coffra)."""

from __future__ import annotations

import reflex as rx

from ..state import State
from .styles import filter_pill_style, tinted_card_style

CALENDAR_CATEGORIES = [
    ("Todos", "calendar-days", "Todos os Eventos"),
    ("Copom & Macro Brasil", "landmark", "Copom & Macro Brasil"),
    ("Dividendos & JCP B3", "coins", "Dividendos & JCP B3"),
    ("Temporada de Balanços", "file-spreadsheet", "Temporada de Balanços"),
    ("Vencimentos B3", "clock", "Vencimentos B3"),
]


def _category_pill(cat_key: str, icon_name: str, label: str) -> rx.Component:
    is_active = State.calendar_category == cat_key
    return rx.hstack(
        rx.icon(
            icon_name,
            size=14,
            color=rx.cond(is_active, "#FFFFFF", "var(--aq-text-muted)"),
        ),
        rx.text(label, size="2", weight="medium"),
        align="center",
        spacing="2",
        on_click=State.set_calendar_category(cat_key),
        **filter_pill_style(is_active),
    )


def _calendar_event_card(ev: dict[str, str]) -> rx.Component:
    """Card de evento estilo 'Calendar' (1:18 do vídeo Coffra) com bloco de dia/horário lateral."""
    return rx.box(
        rx.hstack(
            # Bloco lateral de Dia e Horário estilo calendário Coffra
            rx.vstack(
                rx.text(ev["day"], size="2", weight="bold", style={"color": ev["color"]}),
                rx.heading(ev["date"], size="4", weight="bold", letter_spacing="-0.02em"),
                rx.text("BRT", size="1", color="var(--aq-text-muted)"),
                spacing="0",
                align="center",
                justify="center",
                width="74px",
                min_width="74px",
                height="74px",
                border_radius="14px",
                background="var(--aq-surface)",
                border="1px solid var(--aq-border)",
            ),
            # Conteúdo principal do evento
            rx.vstack(
                rx.hstack(
                    rx.badge(
                        ev["badge"],
                        color_scheme="jade",
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.badge(
                        ev["ticker"],
                        variant="surface",
                        color_scheme="gray",
                        radius="full",
                        size="1",
                    ),
                    rx.spacer(),
                    rx.text(ev["category"], size="1", weight="medium", color="var(--aq-text-muted)"),
                    width="100%",
                    align="center",
                    wrap="wrap",
                ),
                rx.heading(ev["title"], size="3", weight="bold", color="var(--aq-text)"),
                rx.text(ev["subtitle"], size="2", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                width="100%",
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        background=ev["bg"],
        border=f"1px solid {ev['border']}",
        border_radius="16px",
        padding="1.1rem 1.25rem",
        box_shadow="var(--aq-shadow)",
        style={
            "backdropFilter": "blur(20px) saturate(155%)",
            "WebkitBackdropFilter": "blur(20px) saturate(155%)",
        },
        class_name="aq-fade-in",
        width="100%",
    )


def calendar_view() -> rx.Component:
    """Visão completa da página Agenda do Mercado & Dividendos B3."""
    return rx.vstack(
        # 1. Resumo superior em 4 cartões pastéis (estilo Coffra)
        rx.grid(
            rx.vstack(
                rx.hstack(
                    rx.icon("coins", size=15, color="#2D5A43"),
                    rx.text("Proventos & Data-Com", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading("Dividendos & JCP", size="5", weight="bold"),
                rx.text("PETR4, BBAS3, WEGE3 e FIIs no radar", size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                **tinted_card_style("mint"),
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("file-spreadsheet", size=15, color="#7A7234"),
                    rx.text("Temporada de Balanços", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading("Resultados B3", size="5", weight="bold"),
                rx.text("ITUB4, VALE3, MGLU3 e LREN3 divulgam balanços", size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                **tinted_card_style("lemon"),
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("landmark", size=15, color="#B85C4E"),
                    rx.text("Política Monetária & Inflação", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading("Copom & IPCA-15", size="5", weight="bold"),
                rx.text("Boletim Focus, IPCA-15 (IBGE) e Super Quarta", size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                **tinted_card_style("rose"),
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("clock", size=15, color="#9C6B3B"),
                    rx.text("Derivativos & Exercícios", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading("Vencimentos B3", size="5", weight="bold"),
                rx.text("Opções sobre Ações e Índice Ibovespa", size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                **tinted_card_style("sand"),
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            width="100%",
        ),
        # 2. Pílulas de filtro por tipo de evento
        rx.hstack(
            *[_category_pill(k, ic, lbl) for k, ic, lbl in CALENDAR_CATEGORIES],
            spacing="2",
            width="100%",
            wrap="wrap",
            padding_bottom="4px",
        ),
        # 3. Grade cronológica de eventos (2 colunas em telas grandes)
        rx.grid(
            rx.foreach(State.calendar_events, _calendar_event_card),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )
