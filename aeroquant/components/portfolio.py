"""Componentes da página 'Minha Carteira' (inspirada nas telas 'Cards' 0:18 e 'Balances' 0:28 do Coffra)."""

from __future__ import annotations

import reflex as rx

from ..state import State
from .styles import (
    PRIMARY_PILL_BTN,
    ROW_HOVER,
    SECONDARY_PILL_BTN,
    SUBSURFACE_BOX,
    SURFACE_CARD,
    filter_pill_style,
)

_AXIS_FMT = "(value) => 'R$ ' + value.toFixed(0)"
_PCT_FMT = "(value) => (value > 0 ? '+' : '') + value.toFixed(1).replace('.', ',') + '%'"


def _strategy_vault_card(card: dict[str, str]) -> rx.Component:
    """Cartão visual de cofre/estratégia (inspirado na tela 'Cards' em 0:18 do vídeo Coffra)."""
    return rx.box(
        rx.vstack(
            # Topo do cartão: Título da estratégia + Código B3
            rx.hstack(
                rx.vstack(
                    rx.text(
                        card["title"],
                        size="3",
                        weight="bold",
                        style={"color": "#FFFFFF"},
                    ),
                    rx.text(
                        card["subtitle"],
                        size="1",
                        style={"color": "rgba(255, 255, 255, 0.78)"},
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.box(
                    rx.text(
                        card["ticker"],
                        size="1",
                        weight="bold",
                        style={"color": "#FFFFFF"},
                    ),
                    padding="0.22rem 0.6rem",
                    border_radius="999px",
                    border="1px solid rgba(255, 255, 255, 0.28)",
                    background="rgba(255, 255, 255, 0.14)",
                ),
                width="100%",
                align="start",
            ),
            # Valor total do cofre + retorno percentual
            rx.hstack(
                rx.heading(
                    card["total"],
                    size="6",
                    weight="bold",
                    letter_spacing="-0.02em",
                    style={"color": "#FFFFFF"},
                ),
                rx.text(
                    card["pnl_pct"],
                    size="2",
                    weight="bold",
                    style={"color": "#B8E0CE"},
                ),
                align="baseline",
                spacing="2",
                padding_top="0.35rem",
            ),
            # Barra de participação na carteira (estilo Spending Limit do Coffra)
            rx.vstack(
                rx.hstack(
                    rx.text(
                        "Participação: ",
                        card["weight"],
                        " · ",
                        card["cost"],
                        size="1",
                        style={"color": "rgba(255, 255, 255, 0.84)"},
                    ),
                    rx.spacer(),
                    rx.text(
                        card["code"],
                        size="1",
                        weight="medium",
                        style={"color": "rgba(255, 255, 255, 0.75)"},
                    ),
                    width="100%",
                    align="center",
                ),
                rx.box(
                    rx.box(
                        width=card["weight_width"],
                        height="6px",
                        border_radius="999px",
                        background="#B8E0CE",
                    ),
                    width="100%",
                    height="6px",
                    border_radius="999px",
                    background="rgba(255, 255, 255, 0.22)",
                    overflow="hidden",
                ),
                spacing="1",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        background=card["bg"],
        border="1px solid rgba(255, 255, 255, 0.18)",
        border_radius="18px",
        padding="1.15rem 1.3rem",
        box_shadow="var(--aq-shadow)",
        cursor="pointer",
        style={
            "backdropFilter": "blur(20px) saturate(155%)",
            "WebkitBackdropFilter": "blur(20px) saturate(155%)",
        },
        on_click=State.select_position_card(card["ticker"]),
        transition="transform 0.16s ease",
        _hover={"transform": "translateY(-2px)"},
        width="100%",
    )


def _position_card(row: dict[str, str]) -> rx.Component:
    """Card selecionável de uma posição (estilo 'Operating | Payroll | Rainy day' em 0:28 do vídeo)."""
    is_selected = State.selected_position_ticker == row["ticker"]
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    width="9px",
                    height="9px",
                    border_radius="3px",
                    background=row["color"],
                ),
                rx.text(row["ticker"], size="2", weight="bold", color="var(--aq-text)"),
                rx.text("·", size="1", color="var(--aq-text-soft)"),
                rx.text(row["sector"], size="1", color="var(--aq-text-muted)"),
                rx.spacer(),
                rx.text(row["weight"], size="1", color="var(--aq-text-muted)"),
                width="100%",
                align="center",
            ),
            rx.hstack(
                rx.heading(row["total"], size="6", weight="bold", letter_spacing="-0.02em"),
                rx.badge(
                    row["pnl_pct"],
                    color_scheme=row["tone"],
                    variant="soft",
                    radius="full",
                    size="1",
                ),
                align="center",
                spacing="2",
            ),
            rx.hstack(
                rx.text(
                    row["quantity"],
                    " ações · PM ",
                    row["avg_price"],
                    " → Atual ",
                    row["price"],
                    size="1",
                    color="var(--aq-text-muted)",
                ),
                rx.spacer(),
                rx.text(row["pnl"], size="1", weight="bold", color="var(--aq-text)"),
                width="100%",
                align="center",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        on_click=State.select_position_card(row["ticker"]),
        background="var(--aq-surface)",
        border=rx.cond(
            is_selected,
            "2px solid var(--aq-border-strong)",
            "1px solid var(--aq-border)",
        ),
        border_radius="16px",
        padding="1.1rem 1.25rem",
        cursor="pointer",
        box_shadow="var(--aq-shadow)",
        style={
            "backdropFilter": "blur(20px) saturate(155%)",
            "WebkitBackdropFilter": "blur(20px) saturate(155%)",
        },
        transition="all 0.18s ease",
        _hover={"transform": "translateY(-2px)"},
        width="100%",
    )


def _benchmark_comparator_section() -> rx.Component:
    """Gráfico comparativo de rentabilidade acumulada: Carteira vs. Ibovespa vs. CDI (90 dias)."""
    bs = State.benchmark_summary
    return rx.vstack(
        rx.grid(
            rx.vstack(
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="999px", background="#2D5A43"),
                    rx.text("Minha Carteira (90d)", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(bs["carteira"], size="5", weight="bold"),
                spacing="1",
                align="start",
                **SUBSURFACE_BOX,
            ),
            rx.vstack(
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="999px", background="#B8863B"),
                    rx.text("Ibovespa (^BVSP)", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(bs["ibovespa"], size="5", weight="bold"),
                spacing="1",
                align="start",
                **SUBSURFACE_BOX,
            ),
            rx.vstack(
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="999px", background="#6E7F74"),
                    rx.text("CDI Referencial", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(bs["cdi"], size="5", weight="bold"),
                spacing="1",
                align="start",
                **SUBSURFACE_BOX,
            ),
            rx.vstack(
                rx.text("Alpha sobre o Ibovespa", size="1", color="var(--aq-text-muted)"),
                rx.hstack(
                    rx.heading(bs["alpha"], size="4", weight="bold"),
                    rx.badge("90 dias", color_scheme=bs["tone"], variant="soft", radius="full", size="1"),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                spacing="1",
                align="start",
                **SUBSURFACE_BOX,
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="3",
            width="100%",
        ),
        rx.recharts.line_chart(
            rx.recharts.cartesian_grid(
                stroke_dasharray="3 3", stroke="rgba(120, 140, 128, 0.18)", vertical=False
            ),
            rx.recharts.line(
                data_key="carteira",
                name="Minha Carteira (%)",
                type_="monotone",
                stroke="#2D5A43",
                stroke_width=2.6,
                dot=False,
                animation_duration=800,
            ),
            rx.recharts.line(
                data_key="ibovespa",
                name="Ibovespa (%)",
                type_="monotone",
                stroke="#B8863B",
                stroke_width=2.0,
                dot=False,
                animation_duration=800,
            ),
            rx.recharts.line(
                data_key="cdi",
                name="CDI Acumulado (%)",
                type_="monotone",
                stroke="#6E7F74",
                stroke_width=1.8,
                stroke_dasharray="5 4",
                dot=False,
                animation_duration=800,
            ),
            rx.recharts.x_axis(data_key="date", tick_line=False, axis_line=False, min_tick_gap=22),
            rx.recharts.y_axis(
                domain=["auto", "auto"],
                tick_line=False,
                axis_line=False,
                width=58,
                tick_formatter=_PCT_FMT,
            ),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": "var(--aq-surface-elevated)",
                    "border": "1px solid var(--aq-border-strong)",
                    "borderRadius": "10px",
                },
            ),
            rx.recharts.legend(),
            data=State.benchmark_chart,
            height=240,
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def _selected_position_detail_card() -> rx.Component:
    """Card com alternador entre Evolução da Posição e Comparador vs. Ibovespa/CDI."""
    sel = State.selected_position_row
    cs = State.position_chart_summary
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.heading(
                            rx.cond(
                                State.portfolio_chart_mode == "comparador",
                                "Desempenho Comparado — Carteira vs. Ibovespa vs. CDI",
                                f"Evolução da Posição — {sel['ticker']}",
                            ),
                            size="4",
                            weight="bold",
                        ),
                        rx.badge(sel["name"], variant="surface", color_scheme="gray", radius="full"),
                        align="center",
                        spacing="2",
                        wrap="wrap",
                    ),
                    rx.text(
                        "Alterne entre a curva individual do ativo e o comparativo contra os benchmarks brasileiros",
                        size="1",
                        color="var(--aq-text-muted)",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            "Comparador vs. Ibovespa & CDI",
                            on_click=State.set_portfolio_chart_mode("comparador"),
                            **filter_pill_style(State.portfolio_chart_mode == "comparador"),
                        ),
                        rx.box(
                            "Curva do Ativo",
                            on_click=State.set_portfolio_chart_mode("ativo"),
                            **filter_pill_style(State.portfolio_chart_mode == "ativo"),
                        ),
                        spacing="1",
                        wrap="wrap",
                    ),
                    rx.button(
                        rx.icon("download", size=14),
                        "Exportar CSV",
                        size="2",
                        on_click=State.download_portfolio_csv,
                        **SECONDARY_PILL_BTN,
                    ),
                    rx.button(
                        rx.icon("plus", size=15),
                        "Novo Aporte / Ativo",
                        size="2",
                        on_click=State.set_trade_modal_open(True),
                        **PRIMARY_PILL_BTN,
                    ),
                    spacing="2",
                    wrap="wrap",
                ),
                direction=rx.breakpoints(initial="column", lg="row"),
                justify="between",
                align=rx.breakpoints(initial="start", lg="center"),
                gap="0.75rem",
                width="100%",
            ),
            rx.cond(
                State.portfolio_chart_mode == "comparador",
                _benchmark_comparator_section(),
                rx.vstack(
                    # 4 caixas internas (como 'Now | 365 days ago | Low point | In · out this month' em 0:30)
                    rx.grid(
                        rx.vstack(
                            rx.text("Posição atualizada", size="1", color="var(--aq-text-muted)"),
                            rx.heading(sel["total"], size="5", weight="bold"),
                            spacing="1",
                            align="start",
                            **SUBSURFACE_BOX,
                        ),
                        rx.vstack(
                            rx.text("Custo investido", size="1", color="var(--aq-text-muted)"),
                            rx.heading(sel["cost"], size="5", weight="bold"),
                            spacing="1",
                            align="start",
                            **SUBSURFACE_BOX,
                        ),
                        rx.vstack(
                            rx.text("Resultado (P&L)", size="1", color="var(--aq-text-muted)"),
                            rx.hstack(
                                rx.heading(sel["pnl"], size="5", weight="bold"),
                                rx.badge(sel["pnl_pct"], color_scheme="green", variant="soft", radius="full", size="1"),
                                align="center",
                                spacing="2",
                                wrap="wrap",
                            ),
                            spacing="1",
                            align="start",
                            **SUBSURFACE_BOX,
                        ),
                        rx.vstack(
                            rx.text("Amplitude 90 dias", size="1", color="var(--aq-text-muted)"),
                            rx.text(cs["range_sub"], size="2", weight="bold"),
                            spacing="1",
                            align="start",
                            **SUBSURFACE_BOX,
                        ),
                        columns=rx.breakpoints(initial="1", sm="2", lg="4"),
                        spacing="3",
                        width="100%",
                    ),
                    rx.cond(
                        State.position_chart_loading,
                        rx.skeleton(height="230px", width="100%", border_radius="12px"),
                        rx.recharts.area_chart(
                            rx.el.svg.defs(
                                rx.el.svg.linear_gradient(
                                    rx.el.svg.stop(stop_color="#2D5A43", offset="5%", stop_opacity=0.36),
                                    rx.el.svg.stop(stop_color="#2D5A43", offset="95%", stop_opacity=0.0),
                                    id="pfSageGrad",
                                    x1=0,
                                    x2=0,
                                    y1=0,
                                    y2=1,
                                )
                            ),
                            rx.recharts.cartesian_grid(
                                stroke_dasharray="3 3", stroke="rgba(120, 140, 128, 0.18)", vertical=False
                            ),
                            rx.recharts.area(
                                data_key="close",
                                name="Cotação (R$)",
                                type_="monotone",
                                stroke="#2D5A43",
                                stroke_width=2.2,
                                fill="url(#pfSageGrad)",
                                dot=False,
                                animation_duration=800,
                            ),
                            rx.recharts.x_axis(data_key="date", tick_line=False, axis_line=False, min_tick_gap=22),
                            rx.recharts.y_axis(
                                domain=["auto", "auto"],
                                tick_line=False,
                                axis_line=False,
                                width=58,
                                tick_formatter=_AXIS_FMT,
                            ),
                            rx.recharts.graphing_tooltip(
                                content_style={
                                    "background": "var(--aq-surface-elevated)",
                                    "border": "1px solid var(--aq-border-strong)",
                                    "borderRadius": "10px",
                                },
                            ),
                            data=State.position_chart,
                            height=230,
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
        ),
        **SURFACE_CARD,
    )


def _table_row(row: dict[str, str]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(
            rx.hstack(
                rx.avatar(
                    src=row["logo"],
                    fallback=row["ticker"],
                    size="2",
                    radius="medium",
                    color_scheme="jade",
                ),
                rx.vstack(
                    rx.text(row["ticker"], size="2", weight="bold"),
                    rx.text(row["name"], size="1", color="var(--aq-text-muted)"),
                    spacing="0",
                    align="start",
                ),
                align="center",
                spacing="3",
            )
        ),
        rx.table.cell(row["quantity"], align="right"),
        rx.table.cell(row["avg_price"], align="right"),
        rx.table.cell(
            rx.hstack(
                rx.text(row["price"], weight="medium"),
                rx.badge(row["day_change"], color_scheme=row["day_tone"], variant="soft", radius="full", size="1"),
                justify="end",
                align="center",
                spacing="2",
            ),
            align="right",
        ),
        rx.table.cell(rx.text(row["total"], weight="bold"), align="right"),
        rx.table.cell(
            rx.hstack(
                rx.text(row["pnl"], size="2", weight="medium"),
                rx.badge(row["pnl_pct"], color_scheme=row["tone"], variant="soft", radius="full", size="1"),
                justify="end",
                align="center",
                spacing="2",
            ),
            align="right",
        ),
        rx.table.cell(
            rx.vstack(
                rx.text(row["annual_div"], size="2", weight="bold", color="#6EE7B7"),
                rx.text("DY ", row["dy_label"], size="1", color="var(--aq-text-muted)"),
                spacing="0",
                align="end",
            ),
            align="right",
        ),
        rx.table.cell(
            rx.tooltip(
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    size="1",
                    variant="ghost",
                    color_scheme="gray",
                    cursor="pointer",
                    on_click=State.remove_position(row["ticker"]),
                ),
                content="Remover ativo da carteira",
            ),
            align="right",
        ),
        style=ROW_HOVER,
    )


def _dividend_income_card() -> rx.Component:
    """Card de Projeção de Dividendos & Renda Passiva Mensal Isenta de IR."""
    s = State.portfolio_summary
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.vstack(
                    rx.hstack(
                        rx.icon("coins", size=18, color="#F5B851"),
                        rx.heading("Projeção de Dividendos & Renda Passiva (Isenta de IR)", size="4", weight="bold"),
                        rx.badge("DY Médio ", s["portfolio_dy"], color_scheme="amber", variant="soft", radius="full"),
                        align="center",
                        spacing="2",
                        wrap="wrap",
                    ),
                    rx.text(
                        "Estimativa anual e mensal de proventos (Dividendos + JCP líquidos) gerados pelas posições atuais da carteira",
                        size="2",
                        color="var(--aq-text-muted)",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.hstack(
                    rx.vstack(
                        rx.text("Renda Mensal Estimada", size="1", color="var(--aq-text-muted)"),
                        rx.heading(s["monthly_dividends"], "/mês", size="5", weight="bold", color="#6EE7B7"),
                        spacing="0",
                        align="end",
                    ),
                    rx.divider(orientation="vertical", size="2"),
                    rx.vstack(
                        rx.text("Proventos Anuais", size="1", color="var(--aq-text-muted)"),
                        rx.heading(s["annual_dividends"], "/ano", size="5", weight="bold", color="#F5B851"),
                        spacing="0",
                        align="end",
                    ),
                    spacing="4",
                    align="center",
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                justify="between",
                align=rx.breakpoints(initial="start", md="center"),
                gap="1rem",
                width="100%",
            ),
            rx.vstack(
                rx.hstack(
                    rx.text(
                        "Meta de Liberdade Financeira Inicial (R$ 1.000,00/mês em dividendos):",
                        size="1",
                        color="var(--aq-text-muted)",
                    ),
                    rx.spacer(),
                    rx.text(s["income_goal_pct"], " atingido", size="1", weight="bold", color="#6EE7B7"),
                    width="100%",
                    align="center",
                ),
                rx.box(
                    rx.box(
                        width=s["income_goal_width"],
                        height="8px",
                        border_radius="999px",
                        background="linear-gradient(90deg, #34D399 0%, #F5B851 100%)",
                    ),
                    width="100%",
                    height="8px",
                    border_radius="999px",
                    background="rgba(255, 255, 255, 0.12)",
                    overflow="hidden",
                ),
                spacing="1",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        **SURFACE_CARD,
    )


def portfolio_view() -> rx.Component:
    """Visão completa da página Minha Carteira."""
    return rx.vstack(
        # 1. Cofres de Estratégia (estilo tela 'Cards' em 0:18 do vídeo Coffra)
        rx.grid(
            rx.foreach(State.strategy_cards, _strategy_vault_card),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            width="100%",
        ),
        # 2. Card de Projeção de Dividendos & Renda Passiva Mensal
        _dividend_income_card(),
        # 3. Cards interativos das posições individuais (estilo 'Balances' em 0:28)
        rx.grid(
            rx.foreach(State.portfolio_rows, _position_card),
            columns=rx.breakpoints(initial="1", sm="2"),
            spacing="4",
            width="100%",
        ),
        # 4. Card analítico (Comparador vs. Ibovespa/CDI ou Evolução da Posição)
        _selected_position_detail_card(),
        # 5. Tabela detalhada + Rosca de alocação
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.heading("Alocação da Carteira", size="4", weight="bold"),
                    rx.recharts.pie_chart(
                        rx.recharts.pie(
                            data=State.portfolio_slices,
                            data_key="value",
                            name_key="name",
                            inner_radius=62,
                            outer_radius=95,
                            padding_angle=3,
                            stroke="var(--aq-surface)",
                        ),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        height=260,
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                **SURFACE_CARD,
            ),
            rx.box(
                rx.vstack(
                    rx.flex(
                        rx.vstack(
                            rx.heading("Demonstrativo de Posições", size="4", weight="bold"),
                            rx.text(
                                "Persistência automática ativa em data/portfolio.json",
                                size="1",
                                color="var(--aq-text-muted)",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        rx.button(
                            rx.icon("rotate-ccw", size=13),
                            "Restaurar Carteira Padrão",
                            size="1",
                            on_click=State.reset_default_portfolio,
                            **SECONDARY_PILL_BTN,
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                        wrap="wrap",
                        gap="0.5rem",
                    ),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Ativo"),
                                rx.table.column_header_cell("Qtd", align="right"),
                                rx.table.column_header_cell("Preço Médio", align="right"),
                                rx.table.column_header_cell("Cotação Hoje", align="right"),
                                rx.table.column_header_cell("Valor Atual", align="right"),
                                rx.table.column_header_cell("Retorno (P&L)", align="right"),
                                rx.table.column_header_cell("Proventos / Ano", align="right"),
                                rx.table.column_header_cell("", align="right"),
                            )
                        ),
                        rx.table.body(rx.foreach(State.portfolio_rows, _table_row)),
                        width="100%",
                        variant="ghost",
                    ),
                    spacing="3",
                    width="100%",
                ),
                grid_column=rx.breakpoints(initial="auto", lg="span 2"),
                overflow_x="auto",
                **SURFACE_CARD,
            ),
            columns=rx.breakpoints(initial="1", lg="3"),
            spacing="4",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )
