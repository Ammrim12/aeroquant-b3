"""Card 'Raio-X Setorial da B3' (estilo 'Cash on hand') + Mapa de Calor + 4 Cards Pastéis de KPIs."""

from __future__ import annotations

import reflex as rx

from ..state import State
from .styles import ROW_HOVER, SURFACE_CARD, tinted_card_style


def _sector_bar_segment(sec: dict[str, str]) -> rx.Component:
    """Segmento proporcional da barra horizontal de setores (estilo 'Cash on hand')."""
    return rx.tooltip(
        rx.box(
            height="10px",
            width=sec["share_width"],
            background=sec["color"],
            border_radius="999px",
            cursor="pointer",
            on_click=State.filter_by_sector_and_navigate(sec["key"]),
            transition="opacity 0.15s ease",
            _hover={"opacity": "0.82"},
        ),
        content=f"{sec['short']}: {sec['share_label']} ({sec['market_cap']})",
    )


def _sector_row(sec: dict[str, str]) -> rx.Component:
    """Linha clicável de um segmento econômico da B3."""
    return rx.hstack(
        rx.box(
            width="10px",
            height="10px",
            border_radius="3px",
            background=sec["color"],
            flex_shrink="0",
        ),
        rx.vstack(
            rx.hstack(
                rx.text(sec["label"], size="2", weight="bold", color="var(--aq-text)"),
                rx.badge(
                    sec["count_label"],
                    variant="surface",
                    color_scheme="gray",
                    radius="full",
                    size="1",
                ),
                align="center",
                spacing="2",
                wrap="wrap",
            ),
            rx.text(
                "Líderes: ",
                sec["leaders"],
                " · ",
                sec["up_ratio"],
                size="1",
                color="var(--aq-text-muted)",
            ),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.hstack(
            rx.badge(
                sec["avg_change"],
                color_scheme=sec["tone"],
                variant="soft",
                radius="full",
                size="1",
            ),
            rx.vstack(
                rx.text(sec["market_cap"], size="2", weight="bold", color="var(--aq-text)"),
                rx.text(sec["share_label"], " da B3", size="1", color="var(--aq-text-muted)"),
                spacing="0",
                align="end",
            ),
            align="center",
            spacing="3",
        ),
        width="100%",
        align="center",
        padding="0.55rem 0.65rem",
        border_radius="10px",
        on_click=State.filter_by_sector_and_navigate(sec["key"]),
        **ROW_HOVER,
    )


def sector_xray_card() -> rx.Component:
    """Card 'Valor de Mercado & Raio-X Setorial da B3' (inspirado em 'Cash on hand')."""
    b = State.breadth
    return rx.box(
        rx.vstack(
            # Cabeçalho com botão circular de seta no canto direito
            rx.hstack(
                rx.vstack(
                    rx.heading("Valor de Mercado & Segmentos da B3", size="4", weight="bold"),
                    rx.text(
                        "Todas as empresas brasileiras listadas por setor (bancos, fábricas, lojas, energia, saúde...)",
                        size="2",
                        color="var(--aq-text-muted)",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.tooltip(
                    rx.link(
                        rx.center(
                            rx.icon("arrow-up-right", size=16, color="var(--aq-text)"),
                            width="34px",
                            height="34px",
                            border_radius="999px",
                            background="var(--aq-subsurface)",
                            border="1px solid var(--aq-border)",
                        ),
                        href="/empresas",
                        underline="none",
                    ),
                    content="Abrir diretório completo de empresas",
                ),
                width="100%",
                align="center",
            ),
            # Valor total + badge de amplitude
            rx.hstack(
                rx.heading(
                    b["total_market_cap"],
                    size="8",
                    weight="bold",
                    letter_spacing="-0.03em",
                ),
                rx.badge(
                    b["up_pct"],
                    " das ações em alta",
                    color_scheme="green",
                    variant="soft",
                    radius="full",
                    size="2",
                ),
                align="center",
                spacing="3",
                wrap="wrap",
            ),
            rx.text(
                b["total_stocks"],
                " ações negociadas · ",
                b["total_sectors"],
                " segmentos econômicos monitorados em tempo real",
                size="1",
                color="var(--aq-text-muted)",
            ),
            # Termômetro de Sentimento do Pregão (Força Compradora vs. Vendedora)
            rx.vstack(
                rx.hstack(
                    rx.text(
                        "Termômetro do Pregão: ",
                        rx.text.strong(b["sentiment_label"]),
                        size="1",
                        color="var(--aq-text)",
                    ),
                    rx.spacer(),
                    rx.text(
                        b["up_count"],
                        " altas (",
                        b["up_pct"],
                        ") · ",
                        b["down_count"],
                        " baixas",
                        size="1",
                        color="var(--aq-text-muted)",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.hstack(
                    rx.box(
                        height="7px",
                        width=b["up_width"],
                        background="#4ADE80",
                        border_radius="999px",
                    ),
                    rx.box(
                        height="7px",
                        width=b["flat_width"],
                        background="rgba(255, 255, 255, 0.25)",
                        border_radius="999px",
                    ),
                    rx.box(
                        height="7px",
                        width=b["down_width"],
                        background="#E89565",
                        border_radius="999px",
                    ),
                    spacing="1",
                    width="100%",
                ),
                spacing="1",
                width="100%",
                padding_y="0.2rem",
            ),
            # Barra proporcional segmentada
            rx.hstack(
                rx.foreach(State.top_sectors, _sector_bar_segment),
                spacing="1",
                width="100%",
                padding_y="0.25rem",
            ),
            # Lista dos 6 maiores segmentos
            rx.vstack(
                rx.foreach(State.top_sectors, _sector_row),
                spacing="1",
                width="100%",
            ),
            rx.divider(),
            rx.hstack(
                rx.icon("sparkles", size=14, color="var(--aq-primary)"),
                rx.text(
                    "Clique em qualquer segmento acima para filtrar todas as empresas daquele setor",
                    size="1",
                    color="var(--aq-text-muted)",
                ),
                rx.spacer(),
                rx.link(
                    rx.text("Ver todos os 20 setores →", size="1", weight="bold", color="var(--aq-primary)"),
                    href="/empresas",
                    underline="none",
                ),
                width="100%",
                align="center",
                wrap="wrap",
            ),
            spacing="3",
            width="100%",
        ),
        class_name="aq-fade-in",
        **SURFACE_CARD,
    )


def heatmap_tile_cell(tile: dict[str, str]) -> rx.Component:
    """Célula colorida do Mapa de Calor (inspirada na matriz 'Timesheets' em 0:51 do vídeo Coffra)."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(
                    tile["ticker"],
                    size="2",
                    weight="bold",
                    style={"color": tile["heat_fg"]},
                ),
                rx.spacer(),
                rx.text(
                    tile["change"],
                    size="1",
                    weight="bold",
                    style={"color": tile["heat_fg"]},
                ),
                width="100%",
                align="center",
            ),
            rx.text(
                tile["name"],
                size="1",
                style={
                    "color": tile["heat_fg"],
                    "opacity": "0.82",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "whiteSpace": "nowrap",
                    "maxWidth": "100%",
                },
            ),
            rx.hstack(
                rx.text(
                    tile["price"],
                    size="1",
                    weight="medium",
                    style={"color": tile["heat_fg"]},
                ),
                rx.spacer(),
                rx.text(
                    tile["market_cap"],
                    size="1",
                    style={"color": tile["heat_fg"], "opacity": "0.75"},
                ),
                width="100%",
                align="center",
            ),
            spacing="1",
            align="start",
            width="100%",
        ),
        background=tile["heat_bg"],
        border="1px solid var(--aq-border)",
        border_radius="12px",
        padding="0.7rem 0.85rem",
        cursor="pointer",
        style={
            "backdropFilter": "blur(14px)",
            "WebkitBackdropFilter": "blur(14px)",
        },
        transition="transform 0.14s ease, box-shadow 0.14s ease",
        _hover={"transform": "translateY(-2px)"},
        on_click=State.open_stock_drawer(tile),
        width="100%",
    )


def b3_heatmap_card() -> rx.Component:
    """Card 'Mapa de Calor da B3' (matriz cromática inspirada na tela 'Timesheets' do Coffra)."""
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading("Mapa de Calor da B3 (Top 24 Blue Chips)", size="4", weight="bold"),
                        rx.badge("Tempo Real", color_scheme="jade", variant="soft", radius="full", size="1"),
                        align="center",
                        spacing="2",
                        wrap="wrap",
                    ),
                    rx.text(
                        "Intensidade de alta (verde sálvia) e baixa (terracota) das maiores empresas em valor de mercado · Clique em qualquer bloco para abrir o Raio-X",
                        size="2",
                        color="var(--aq-text-muted)",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.hstack(
                    rx.hstack(
                        rx.box(width="10px", height="10px", border_radius="3px", background="#B8E0CE"),
                        rx.text("Alta > +2%", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.box(width="10px", height="10px", border_radius="3px", background="#EBF4EE"),
                        rx.text("Alta leve", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.box(width="10px", height="10px", border_radius="3px", background="#FBECE8"),
                        rx.text("Baixa leve", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="1",
                    ),
                    rx.hstack(
                        rx.box(width="10px", height="10px", border_radius="3px", background="#F2C8BE"),
                        rx.text("Baixa < -2%", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="1",
                    ),
                    spacing="3",
                    wrap="wrap",
                ),
                direction=rx.breakpoints(initial="column", lg="row"),
                justify="between",
                align=rx.breakpoints(initial="start", lg="center"),
                gap="0.75rem",
                width="100%",
            ),
            rx.grid(
                rx.foreach(State.heatmap_tiles, heatmap_tile_cell),
                columns=rx.breakpoints(initial="2", sm="3", md="4", lg="6"),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        class_name="aq-fade-in",
        **SURFACE_CARD,
    )


def kpi_cards() -> rx.Component:
    """Grade 2x2 de cards pastéis (mint, rose, sand, lemon — idênticos ao vídeo Coffra)."""
    b = State.breadth
    return rx.grid(
        # 1. Mint: Ações em Alta Hoje
        rx.link(
            rx.vstack(
                rx.hstack(
                    rx.icon("trending-up", size=15, color="#2D5A43"),
                    rx.text("Ações em alta hoje na B3", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(b["up_count"], size="6", weight="bold"),
                rx.hstack(
                    rx.badge(
                        b["top_gainer_ticker"],
                        " ",
                        b["top_gainer_change"],
                        color_scheme="green",
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.text("maior alta do pregão", size="1", color="var(--aq-text-muted)"),
                    rx.spacer(),
                    rx.icon("arrow-right", size=14, color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                spacing="2",
                align="start",
                **tinted_card_style("mint"),
            ),
            href="/empresas",
            underline="none",
            width="100%",
        ),
        # 2. Rose: Ações em Baixa Hoje
        rx.link(
            rx.vstack(
                rx.hstack(
                    rx.icon("trending-down", size=15, color="#B85C4E"),
                    rx.text("Ações em baixa hoje na B3", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(b["down_count"], size="6", weight="bold"),
                rx.hstack(
                    rx.badge(
                        b["top_loser_ticker"],
                        " ",
                        b["top_loser_change"],
                        color_scheme="tomato",
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.text("maior recuo do pregão", size="1", color="var(--aq-text-muted)"),
                    rx.spacer(),
                    rx.icon("arrow-right", size=14, color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                spacing="2",
                align="start",
                **tinted_card_style("rose"),
            ),
            href="/empresas",
            underline="none",
            width="100%",
        ),
        # 3. Sand: Dólar Comercial + Bitcoin
        rx.vstack(
            rx.hstack(
                rx.icon("dollar-sign", size=15, color="#9C6B3B"),
                rx.text("Dólar Comercial (USD/BRL)", size="1", weight="medium", color="var(--aq-text-muted)"),
                align="center",
                spacing="2",
            ),
            rx.heading(State.usd_quote["price"], size="6", weight="bold"),
            rx.hstack(
                rx.badge(
                    State.usd_quote["change"],
                    color_scheme=State.usd_quote["color"],
                    variant="soft",
                    radius="full",
                    size="1",
                ),
                rx.text(
                    "Bitcoin: ",
                    State.btc_quote["price"],
                    " (",
                    State.btc_quote["change"],
                    ")",
                    size="1",
                    color="var(--aq-text-muted)",
                ),
                align="center",
                spacing="2",
                wrap="wrap",
            ),
            spacing="2",
            align="start",
            on_click=State.select_benchmark("USDBRL=X", "Dólar", "USD/BRL · Câmbio Comercial"),
            cursor="pointer",
            **tinted_card_style("sand"),
        ),
        # 4. Lemon: Volume Total Negociado na B3
        rx.link(
            rx.vstack(
                rx.hstack(
                    rx.icon("bar-chart-3", size=15, color="#7A7234"),
                    rx.text("Volume negociado hoje (ações)", size="1", weight="medium", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(b["total_volume"], size="6", weight="bold"),
                rx.hstack(
                    rx.badge(
                        b["most_active_ticker"],
                        color_scheme="amber",
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.text(
                        "líder de liquidez (",
                        b["most_active_volume"],
                        ")",
                        size="1",
                        color="var(--aq-text-muted)",
                    ),
                    rx.spacer(),
                    rx.icon("arrow-right", size=14, color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                    width="100%",
                ),
                spacing="2",
                align="start",
                **tinted_card_style("lemon"),
            ),
            href="/empresas",
            underline="none",
            width="100%",
        ),
        columns=rx.breakpoints(initial="1", sm="2"),
        spacing="4",
        width="100%",
    )
