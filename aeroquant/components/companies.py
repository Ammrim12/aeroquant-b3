"""Diretório Completo de Empresas & Ativos da B3 (~1.637 papéis: Ações, FIIs, ETFs, BDRs e Favoritos).

Painel de filtros unificado em vidro translúcido (sem barras de rolagem horizontais),
pílulas de alto contraste, expansão inteligente dos 20 segmentos econômicos, busca
instantânea e alternância entre Grade de Cards, Tabela Completa e Mapa de Calor.
"""

from __future__ import annotations

import reflex as rx

from ..state import State
from .kpi_cards import heatmap_tile_cell
from .styles import (
    INTERACTIVE_CARD,
    PRIMARY_PILL_BTN,
    ROW_HOVER,
    SECONDARY_PILL_BTN,
    SUBSURFACE_BOX,
    SURFACE_CARD,
    filter_pill_style,
)

SORT_OPTIONS = [
    "Valor de Mercado",
    "Volume Negociado",
    "Maiores Altas",
    "Maiores Baixas",
    "Ordem Alfabética",
]

ASSET_CLASS_TABS = [
    ("acao", "building-2", "Ações"),
    ("favoritos", "star", "Favoritos"),
    ("fii", "landmark", "FIIs"),
    ("etf", "layers", "ETFs"),
    ("bdr", "globe", "BDRs"),
    ("todos", "sparkles", "Todos na B3"),
]


def _counter_pill(count_text, is_active) -> rx.Component:
    """Badge numérica interna com alto contraste tanto no estado ativo quanto inativo."""
    return rx.box(
        rx.text(
            count_text,
            size="1",
            weight="bold",
            style={
                "color": rx.cond(is_active, "#A7F3D0", "var(--aq-text-muted)"),
                "fontSize": "0.72rem",
            },
        ),
        padding="0.1rem 0.48rem",
        border_radius="999px",
        background=rx.cond(
            is_active,
            "rgba(6, 18, 12, 0.45)",
            "rgba(255, 255, 255, 0.08)",
        ),
        border=rx.cond(
            is_active,
            "1px solid rgba(167, 243, 208, 0.35)",
            "1px solid rgba(255, 255, 255, 0.08)",
        ),
    )


def _asset_class_tab(key: str, icon_name: str, label: str) -> rx.Component:
    is_active = State.selected_asset_class == key
    return rx.hstack(
        rx.icon(
            icon_name,
            size=15,
            color=rx.cond(is_active, "#A7F3D0", "var(--aq-text-muted)"),
        ),
        rx.text(label, size="2", weight=rx.cond(is_active, "bold", "medium")),
        _counter_pill(State.class_counts[key], is_active),
        align="center",
        spacing="2",
        on_click=State.set_asset_class(key),
        **filter_pill_style(is_active),
    )


def _sector_pill(pill: dict[str, str]) -> rx.Component:
    is_active = State.selected_sector == pill["key"]
    return rx.hstack(
        rx.text(pill["label"], size="2", weight=rx.cond(is_active, "bold", "medium")),
        _counter_pill(pill["count"], is_active),
        align="center",
        spacing="2",
        on_click=State.set_sector_filter(pill["key"]),
        **filter_pill_style(is_active),
    )


def unified_filter_panel() -> rx.Component:
    """Painel de filtros unificado fixo no topo (sem barras de rolagem horizontais)."""
    return rx.box(
        rx.vstack(
            # Linha 1: Abas de Classes de Ativos + Busca + Ordenação + Alternador de Visão
            rx.flex(
                rx.hstack(
                    *[_asset_class_tab(k, ic, lbl) for k, ic, lbl in ASSET_CLASS_TABS],
                    spacing="1",
                    wrap="wrap",
                    align="center",
                ),
                rx.hstack(
                    rx.hstack(
                        rx.icon("layout-grid", size=14),
                        rx.text("Grade", size="2"),
                        spacing="1",
                        align="center",
                        on_click=State.set_view_mode("cards"),
                        **filter_pill_style(State.view_mode == "cards"),
                    ),
                    rx.hstack(
                        rx.icon("table-2", size=14),
                        rx.text("Tabela", size="2"),
                        spacing="1",
                        align="center",
                        on_click=State.set_view_mode("tabela"),
                        **filter_pill_style(State.view_mode == "tabela"),
                    ),
                    rx.hstack(
                        rx.icon("flame", size=14),
                        rx.text("Mapa de Calor", size="2"),
                        spacing="1",
                        align="center",
                        on_click=State.set_view_mode("heatmap"),
                        **filter_pill_style(State.view_mode == "heatmap"),
                    ),
                    spacing="1",
                    wrap="wrap",
                    align="center",
                ),
                direction=rx.breakpoints(initial="column", xl="row"),
                justify="between",
                align=rx.breakpoints(initial="start", xl="center"),
                gap="0.5rem",
                width="100%",
            ),
            # Linha 2: Barra de Busca + Ordenação + Contador + Limpar Filtros
            rx.flex(
                rx.box(
                    rx.input(
                        rx.input.slot(rx.icon("search", size=15, color="#6EE7B7")),
                        rx.cond(
                            State.search_query != "",
                            rx.input.slot(
                                rx.icon(
                                    "x",
                                    size=14,
                                    color="var(--aq-text-muted)",
                                    cursor="pointer",
                                    on_click=State.set_search_query(""),
                                )
                            ),
                        ),
                        value=State.search_query,
                        on_change=State.set_search_query,
                        placeholder="Filtrar por código (PETR4, VALE3, HGLG11, BOVA11...), nome da empresa ou subsetor...",
                        size="2",
                        width="100%",
                        radius="full",
                    ),
                    flex="1",
                    width="100%",
                ),
                rx.hstack(
                    rx.badge(
                        State.filtered_count,
                        " ativos exibidos",
                        color_scheme="jade",
                        variant="soft",
                        radius="full",
                        size="2",
                    ),
                    rx.hstack(
                        rx.icon("arrow-up-down", size=14, color="var(--aq-text-muted)"),
                        rx.select(
                            SORT_OPTIONS,
                            value=State.sort_by,
                            on_change=State.set_sort_by,
                            size="2",
                            radius="full",
                        ),
                        align="center",
                        spacing="2",
                    ),
                    rx.cond(
                        State.has_active_filters,
                        rx.button(
                            rx.icon("rotate-ccw", size=13),
                            "Limpar",
                            size="2",
                            on_click=State.clear_filters,
                            **SECONDARY_PILL_BTN,
                        ),
                    ),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                direction=rx.breakpoints(initial="column", lg="row"),
                justify="between",
                align=rx.breakpoints(initial="stretch", lg="center"),
                gap="0.5rem",
                width="100%",
            ),
            # Linha 3: Segmentos Econômicos (expansível em múltiplas linhas, zero scrollbar horizontal!)
            rx.cond(
                State.selected_asset_class == "acao",
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.hstack(
                                rx.icon("layers-3", size=13, color="#F5B851"),
                                rx.text(
                                    "Segmentos da B3:",
                                    size="1",
                                    weight="bold",
                                    color="var(--aq-text-muted)",
                                ),
                                align="center",
                                spacing="1",
                            ),
                            rx.spacer(),
                            rx.hstack(
                                rx.icon(
                                    rx.cond(State.show_all_sectors, "chevron-up", "chevron-down"),
                                    size=14,
                                    color="#6EE7B7",
                                ),
                                rx.text(
                                    rx.cond(
                                        State.show_all_sectors,
                                        "Recolher setores",
                                        "Ver todos os 20 setores",
                                    ),
                                    size="1",
                                    weight="bold",
                                    color="#6EE7B7",
                                ),
                                align="center",
                                spacing="1",
                                cursor="pointer",
                                on_click=State.toggle_all_sectors,
                            ),
                            width="100%",
                            align="center",
                        ),
                        rx.box(
                            rx.hstack(
                                rx.foreach(State.visible_sector_options, _sector_pill),
                                spacing="1",
                                wrap="wrap",
                                width="100%",
                            ),
                            max_height="108px",
                            overflow_y="auto",
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    background="var(--aq-subsurface)",
                    border="1px solid var(--aq-border)",
                    border_radius="12px",
                    padding="0.5rem 0.75rem",
                    width="100%",
                ),
            ),
            spacing="2",
            width="100%",
        ),
        background="var(--aq-surface)",
        border="1px solid var(--aq-border)",
        border_radius="16px",
        padding="0.65rem 0.9rem",
        box_shadow="var(--aq-shadow)",
        width="100%",
    )


def _company_card(stock: dict[str, str]) -> rx.Component:
    """Card de empresa estilo 'Directory' (0:56 do vídeo Coffra)."""
    return rx.box(
        rx.vstack(
            # Topo: Avatar/Logo à esquerda + Estrela de Favorito + Badge de variação à direita
            rx.hstack(
                rx.avatar(
                    src=stock["logo"],
                    fallback=stock["initials"],
                    size="3",
                    radius="medium",
                    color_scheme="jade",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.tooltip(
                        rx.center(
                            rx.icon(
                                "star",
                                size=14,
                                color=rx.cond(stock["is_favorite"] == "1", "#F5B851", "var(--aq-text-soft)"),
                            ),
                            width="28px",
                            height="28px",
                            border_radius="999px",
                            background="var(--aq-subsurface)",
                            border="1px solid var(--aq-border)",
                            on_click=State.toggle_favorite(stock["ticker"]).stop_propagation,
                        ),
                        content="Adicionar / remover dos Favoritos",
                    ),
                    rx.badge(
                        rx.icon(stock["arrow"], size=12),
                        stock["change"],
                        color_scheme=stock["tone"],
                        variant="soft",
                        radius="full",
                        size="2",
                    ),
                    align="center",
                    spacing="2",
                ),
                width="100%",
                align="center",
            ),
            # Nome e Ticker
            rx.vstack(
                rx.hstack(
                    rx.heading(stock["ticker"], size="4", weight="bold"),
                    rx.text("·", color="var(--aq-text-soft)"),
                    rx.text(stock["price"], size="3", weight="bold", color="#6EE7B7"),
                    align="center",
                    spacing="2",
                ),
                rx.text(
                    stock["name"],
                    size="2",
                    color="var(--aq-text-muted)",
                    style={
                        "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "whiteSpace": "nowrap",
                        "maxWidth": "100%",
                    },
                ),
                spacing="0",
                align="start",
                width="100%",
            ),
            # Rodapé: Setor + Valor de Mercado + Volume
            rx.hstack(
                rx.badge(
                    stock["sector_short"],
                    variant="surface",
                    color_scheme="gray",
                    radius="full",
                    size="1",
                ),
                rx.spacer(),
                rx.text(
                    "VM: ",
                    stock["market_cap"],
                    size="1",
                    color="var(--aq-text-muted)",
                ),
                width="100%",
                align="center",
            ),
            rx.text(
                stock["subsector"],
                size="1",
                color="var(--aq-text-soft)",
                style={
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                    "maxWidth": "100%",
                },
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        on_click=State.open_stock_drawer(stock),
        class_name="aq-fade-in",
        **INTERACTIVE_CARD,
    )


def _company_table_row(stock: dict[str, str]) -> rx.Component:
    """Linha de empresa na visão em tabela (estilo 'Agreements' em 1:05 do vídeo)."""
    return rx.table.row(
        rx.table.row_header_cell(
            rx.hstack(
                rx.avatar(
                    src=stock["logo"],
                    fallback=stock["initials"],
                    size="2",
                    radius="medium",
                    color_scheme="jade",
                ),
                rx.vstack(
                    rx.text(stock["ticker"], size="2", weight="bold"),
                    rx.text(stock["name"], size="1", color="var(--aq-text-muted)"),
                    spacing="0",
                    align="start",
                ),
                align="center",
                spacing="3",
            )
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(stock["sector_short"], size="2", weight="medium"),
                rx.text(stock["subsector"], size="1", color="var(--aq-text-muted)"),
                spacing="0",
                align="start",
            )
        ),
        rx.table.cell(rx.text(stock["price"], weight="bold"), align="right"),
        rx.table.cell(
            rx.badge(
                stock["change"],
                color_scheme=stock["tone"],
                variant="soft",
                radius="full",
            ),
            align="right",
        ),
        rx.table.cell(stock["volume"], align="right"),
        rx.table.cell(stock["market_cap"], align="right"),
        on_click=State.open_stock_drawer(stock),
        style=ROW_HOVER,
    )


def companies_explorer() -> rx.Component:
    """Área central rolável com os cards, tabela ou mapa de calor das empresas da B3."""
    return rx.vstack(
        # Visão principal: Grade de cards | Mapa de Calor | Tabela completa
        rx.cond(
            State.view_mode == "cards",
            rx.grid(
                rx.foreach(State.visible_stocks, _company_card),
                columns=rx.breakpoints(initial="1", sm="2", lg="3", xl="4"),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                State.view_mode == "heatmap",
                rx.box(
                    rx.grid(
                        rx.foreach(State.visible_stocks, heatmap_tile_cell),
                        columns=rx.breakpoints(initial="2", sm="3", md="4", lg="6"),
                        spacing="2",
                        width="100%",
                    ),
                    **SURFACE_CARD,
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Ativo"),
                                rx.table.column_header_cell("Segmento & Subsetor"),
                                rx.table.column_header_cell("Cotação", align="right"),
                                rx.table.column_header_cell("Variação Dia", align="right"),
                                rx.table.column_header_cell("Volume", align="right"),
                                rx.table.column_header_cell("Valor de Mercado", align="right"),
                            )
                        ),
                        rx.table.body(rx.foreach(State.visible_stocks, _company_table_row)),
                        width="100%",
                        variant="ghost",
                    ),
                    overflow_x="auto",
                    **SURFACE_CARD,
                ),
            ),
        ),
        # 3. Controles de paginação ("Carregar mais 80" / "Exibir todos")
        rx.cond(
            State.has_more_stocks,
            rx.center(
                rx.hstack(
                    rx.button(
                        rx.icon("chevron-down", size=15),
                        "Carregar mais 80 ativos",
                        size="2",
                        on_click=State.show_more_stocks,
                        **SECONDARY_PILL_BTN,
                    ),
                    rx.button(
                        rx.icon("layers", size=15),
                        "Exibir todos os ",
                        State.filtered_count,
                        " ativos",
                        size="2",
                        on_click=State.show_all_stocks,
                        **PRIMARY_PILL_BTN,
                    ),
                    spacing="3",
                    wrap="wrap",
                ),
                width="100%",
                padding_y="0.75rem",
            ),
        ),
        spacing="4",
        width="100%",
    )
