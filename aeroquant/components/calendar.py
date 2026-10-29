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
    """Card de evento conectado em tempo real (BCB + Yahoo Finance + Catálogo B3). Clicável para abrir Raio-X."""
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
                height="78px",
                border_radius="14px",
                background="var(--aq-surface)",
                border="1px solid var(--aq-border)",
            ),
            # Conteúdo principal do evento + Pílula de Dados Ao Vivo
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
                rx.hstack(
                    rx.box(
                        width="7px",
                        height="7px",
                        border_radius="999px",
                        background="#34D399",
                        box_shadow="0 0 8px rgba(52, 211, 153, 0.85)",
                    ),
                    rx.text(
                        ev["live_metric"],
                        size="1",
                        weight="bold",
                        color="#A7F3D0",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.text("Abrir Raio-X", size="1", color="var(--aq-text-muted)"),
                        rx.icon("chevron-right", size=13, color="#6EE7B7"),
                        spacing="1",
                        align="center",
                    ),
                    align="center",
                    spacing="2",
                    width="100%",
                    padding="0.32rem 0.65rem",
                    margin_top="0.2rem",
                    border_radius="10px",
                    background="rgba(10, 18, 14, 0.55)",
                    border="1px solid rgba(110, 231, 183, 0.28)",
                ),
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
        padding="1.05rem 1.2rem",
        box_shadow="var(--aq-shadow)",
        cursor="pointer",
        on_click=State.open_calendar_ticker(ev["primary_ticker"]),
        style={
            "backdropFilter": "blur(20px) saturate(155%)",
            "WebkitBackdropFilter": "blur(20px) saturate(155%)",
        },
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": "var(--aq-shadow-hover)",
            "border_color": "rgba(110, 231, 183, 0.65)",
        },
        transition="all 0.18s ease",
        class_name="aq-fade-in",
        width="100%",
    )


def calendar_filter_bar() -> rx.Component:
    """Barra de filtro fixa no cabeçalho da Agenda."""
    return rx.hstack(
        *[_category_pill(k, ic, lbl) for k, ic, lbl in CALENDAR_CATEGORIES],
        spacing="2",
        width="100%",
        wrap="wrap",
        padding_top="2px",
    )


def calendar_view() -> rx.Component:
    """Visão completa da página Agenda do Mercado & Dividendos B3 (conectada ao BCB, Yahoo Finance e B3)."""
    return rx.vstack(
        # 1. Resumo superior em 4 cartões conectados em tempo real
        rx.grid(
            rx.vstack(
                rx.hstack(
                    rx.icon("coins", size=15, color="#6EE7B7"),
                    rx.text("Proventos Reais Apurados (B3)", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(State.calendar_summary["div_headline"], size="4", weight="bold"),
                rx.text(State.calendar_summary["div_sub"], size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                cursor="pointer",
                on_click=State.open_calendar_ticker("PETR4"),
                **tinted_card_style("mint"),
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("file-spreadsheet", size=15, color="#F5B851"),
                    rx.text("Balanços & Consenso Receita", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(State.calendar_summary["earn_headline"], size="4", weight="bold"),
                rx.text(State.calendar_summary["earn_sub"], size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                cursor="pointer",
                on_click=State.open_calendar_ticker("ITUB4"),
                **tinted_card_style("lemon"),
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("landmark", size=15, color="#FCA5A5"),
                    rx.text("Taxas Oficiais BCB (Ao Vivo)", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(State.calendar_summary["macro_headline"], size="4", weight="bold"),
                rx.text(State.calendar_summary["macro_sub"], size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                cursor="pointer",
                on_click=State.open_calendar_ticker("BOVA11"),
                **tinted_card_style("rose"),
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("clock", size=15, color="#FCD34D"),
                    rx.text("Calendário Oficial de Opções B3", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(State.calendar_summary["exp_headline"], size="4", weight="bold"),
                rx.text(State.calendar_summary["exp_sub"], size="1", color="var(--aq-text-muted)"),
                spacing="1",
                align="start",
                cursor="pointer",
                on_click=State.open_calendar_ticker("BOVA11"),
                **tinted_card_style("sand"),
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            width="100%",
        ),
        # 2. Grade cronológica de eventos conectados (2 colunas em telas grandes)
        rx.grid(
            rx.foreach(State.calendar_events, _calendar_event_card),
            columns=rx.breakpoints(initial="1", lg="2"),
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )
