"""Painel lateral deslizante (Drawer), Modal 'Simular Aporte' e Busca Rápida Global."""

from __future__ import annotations

import reflex as rx

from ..services.market_data import PERIOD_OPTIONS
from ..state import State
from .styles import (
    PRIMARY_PILL_BTN,
    ROW_HOVER,
    SECONDARY_PILL_BTN,
    SUBSURFACE_BOX,
    filter_pill_style,
)

_AXIS_FMT = "(value) => value.toFixed(2).replace('.', ',')"
_TOOLTIP_BRL = rx.Var(
    '(value) => [new Intl.NumberFormat("pt-BR", {style: "currency", currency: "BRL"}).format(value), "Fechamento"]'
)


def _drawer_chart() -> rx.Component:
    return rx.recharts.composed_chart(
        rx.el.svg.defs(
            rx.el.svg.linear_gradient(
                rx.el.svg.stop(stop_color="#34D399", offset="5%", stop_opacity=0.45),
                rx.el.svg.stop(stop_color="#34D399", offset="95%", stop_opacity=0.0),
                id="drawerSageGrad",
                x1=0,
                x2=0,
                y1=0,
                y2=1,
            )
        ),
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3", stroke="rgba(255, 255, 255, 0.10)", vertical=False
        ),
        rx.recharts.area(
            data_key="close",
            name="Fechamento",
            type_="monotone",
            stroke="#6EE7B7",
            stroke_width=2.2,
            fill="url(#drawerSageGrad)",
            dot=False,
            animation_duration=700,
        ),
        rx.recharts.line(
            data_key="mm20",
            name="MM20",
            type_="monotone",
            stroke="#F5B851",
            stroke_width=1.8,
            stroke_dasharray="4 4",
            dot=False,
            animation_duration=700,
        ),
        rx.recharts.x_axis(data_key="date", tick_line=False, axis_line=False, min_tick_gap=24),
        rx.recharts.y_axis(
            domain=["auto", "auto"],
            tick_line=False,
            axis_line=False,
            width=52,
            tick_formatter=_AXIS_FMT,
        ),
        rx.recharts.graphing_tooltip(
            custom_attrs={"formatter": _TOOLTIP_BRL},
            content_style={
                "background": "var(--aq-surface-elevated)",
                "border": "1px solid var(--aq-border-strong)",
                "borderRadius": "10px",
            },
        ),
        data=State.drawer_chart,
        height=200,
        width="100%",
    )


def _detail_line(label: str, value) -> rx.Component:
    return rx.hstack(
        rx.text(label, size="2", color="var(--aq-text-muted)"),
        rx.spacer(),
        rx.text(value, size="2", weight="medium", color="var(--aq-text)"),
        width="100%",
        padding_y="0.35rem",
        border_bottom="1px solid var(--aq-border)",
    )


def stock_detail_drawer() -> rx.Component:
    """Folha lateral deslizante à direita (inspirada em 0:20 e 0:58 do vídeo Coffra)."""
    stock = State.selected_stock
    summary = State.drawer_summary
    return rx.drawer.root(
        rx.drawer.overlay(style={"background": "rgba(12, 20, 16, 0.36)", "backdropFilter": "blur(4px)"}),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.hstack(
                        rx.avatar(
                            src=stock["logo"],
                            fallback=stock["initials"],
                            size="3",
                            radius="medium",
                            color_scheme="jade",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.heading(stock["ticker"], size="5", weight="bold"),
                                rx.badge(
                                    stock["change"],
                                    color_scheme=stock["tone"],
                                    variant="soft",
                                    radius="full",
                                ),
                                align="center",
                                spacing="2",
                            ),
                            rx.text(stock["name"], size="2", color="var(--aq-text-muted)"),
                            spacing="0",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon(
                                    "star",
                                    size=16,
                                    color=rx.cond(State.is_drawer_favorite, "#F5B851", "var(--aq-text-muted)"),
                                ),
                                variant="soft",
                                color_scheme=rx.cond(State.is_drawer_favorite, "amber", "gray"),
                                radius="full",
                                cursor="pointer",
                                on_click=State.toggle_drawer_favorite,
                            ),
                            content="Favoritar / remover dos Favoritos",
                        ),
                        rx.drawer.close(
                            rx.icon_button(
                                rx.icon("x", size=16),
                                variant="ghost",
                                color_scheme="gray",
                                radius="full",
                                cursor="pointer",
                            )
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.vstack(
                                rx.text("Cotação atual na B3", size="1", color="var(--aq-text-muted)"),
                                rx.heading(stock["price"], size="6", weight="bold"),
                                spacing="0",
                                align="start",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.text("Valor de mercado", size="1", color="var(--aq-text-muted)"),
                                rx.text(stock["market_cap"], size="3", weight="bold"),
                                spacing="0",
                                align="end",
                            ),
                            width="100%",
                            align="center",
                        ),
                        rx.text(summary["range_sub"], size="1", color="var(--aq-text-muted)"),
                        # Barra visual de posição entre Mínima e Máxima de 52 Semanas
                        rx.vstack(
                            rx.hstack(
                                rx.text("Mín 52s: ", summary["low_52w"], size="1", color="var(--aq-text-soft)"),
                                rx.spacer(),
                                rx.text(summary["pos_52w_label"], size="1", weight="bold", color="#6EE7B7"),
                                rx.spacer(),
                                rx.text("Máx 52s: ", summary["high_52w"], size="1", color="var(--aq-text-soft)"),
                                width="100%",
                                align="center",
                            ),
                            rx.box(
                                rx.box(
                                    width=summary["pos_52w_pct"],
                                    height="6px",
                                    border_radius="999px",
                                    background="linear-gradient(90deg, #E89565 0%, #F5B851 50%, #4ADE80 100%)",
                                ),
                                width="100%",
                                height="6px",
                                border_radius="999px",
                                background="rgba(255, 255, 255, 0.14)",
                                overflow="hidden",
                            ),
                            spacing="1",
                            width="100%",
                            padding_top="0.25rem",
                        ),
                        spacing="2",
                        **SUBSURFACE_BOX,
                    ),
                    rx.hstack(
                        rx.text("Evolução + MM20", size="2", weight="bold"),
                        rx.spacer(),
                        rx.hstack(
                            *[
                                rx.box(
                                    label,
                                    on_click=State.set_drawer_period(label),
                                    **filter_pill_style(State.drawer_period == label),
                                )
                                for label in PERIOD_OPTIONS
                            ],
                            spacing="1",
                        ),
                        width="100%",
                        align="center",
                        wrap="wrap",
                    ),
                    rx.cond(
                        State.drawer_loading,
                        rx.skeleton(height="200px", width="100%"),
                        _drawer_chart(),
                    ),
                    rx.vstack(
                        rx.text(
                            "FICHA DO ATIVO",
                            size="1",
                            weight="bold",
                            color="var(--aq-text-soft)",
                            letter_spacing="0.08em",
                        ),
                        _detail_line("Segmento B3", stock["sector"]),
                        _detail_line("Subsetor / Classe", stock["subsector"]),
                        _detail_line("Média Móvel (MM20)", summary["mm20_label"]),
                        _detail_line("IFR-14 (RSI Técnico)", f"{summary['rsi_value']} · {summary['rsi_status']}"),
                        _detail_line("Volatilidade Anualizada", summary["volatility"]),
                        _detail_line("Retorno no período", summary["period_change"]),
                        _detail_line("Variação em R$", summary["period_diff"]),
                        _detail_line("Volume do dia (cotas)", stock["volume"]),
                        _detail_line("Volume médio no período", summary["avg_volume"]),
                        spacing="1",
                        width="100%",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.button(
                            rx.icon("chart-line", size=15),
                            "Ver no Gráfico Principal",
                            size="2",
                            on_click=State.promote_drawer_stock_to_main_chart,
                            **SECONDARY_PILL_BTN,
                        ),
                        rx.button(
                            rx.icon("plus", size=15),
                            "Simular na Carteira",
                            size="2",
                            on_click=State.open_trade_modal_for_drawer_stock,
                            **PRIMARY_PILL_BTN,
                        ),
                        spacing="2",
                        width="100%",
                        justify="end",
                        wrap="wrap",
                    ),
                    spacing="4",
                    height="100%",
                    width="100%",
                ),
                style={
                    "background": "var(--aq-surface)",
                    "borderLeft": "1px solid var(--aq-border)",
                    "padding": "1.5rem",
                    "width": "min(440px, 94vw)",
                    "height": "100vh",
                    "marginLeft": "auto",
                    "overflowY": "auto",
                },
            )
        ),
        direction="right",
        open=State.drawer_open,
        on_open_change=State.set_drawer_open,
    )


def _palette_row(stock: dict) -> rx.Component:
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
                rx.badge(stock["sector_short"], size="1", variant="surface", color_scheme="gray", radius="full"),
                align="center",
                spacing="2",
            ),
            rx.text(stock["name"], size="1", color="var(--aq-text-muted)"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.hstack(
            rx.text(stock["price"], size="2", weight="bold", color="var(--aq-text)"),
            rx.badge(stock["change"], color_scheme=stock["tone"], variant="soft", radius="full", size="1"),
            rx.icon("arrow-right", size=14, color="var(--aq-text-soft)"),
            align="center",
            spacing="2",
        ),
        width="100%",
        align="center",
        padding="0.55rem 0.7rem",
        border_radius="10px",
        on_click=State.select_from_palette(stock),
        **ROW_HOVER,
    )


def command_palette_modal() -> rx.Component:
    """Modal de Busca Rápida Global em todos os ~1.600 ativos da B3 (Ações, FIIs, ETFs, BDRs)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("search", size=18, color="var(--aq-primary)"),
                    rx.dialog.title("Busca Rápida na B3", size="4", margin_bottom="0"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            color_scheme="gray",
                            radius="full",
                            cursor="pointer",
                        )
                    ),
                    width="100%",
                    align="center",
                ),
                rx.input(
                    rx.input.slot(rx.icon("sparkles", size=15, color="var(--aq-primary)")),
                    value=State.palette_query,
                    on_change=State.set_palette_query,
                    placeholder="Digite o código ou nome (ex.: PETR4, MXRF11, BOVA11, ROXO34, WEGE3)...",
                    size="3",
                    width="100%",
                    radius="full",
                    auto_focus=True,
                ),
                rx.text(
                    "Clique em qualquer ativo abaixo para abrir a ficha completa e o gráfico histórico:",
                    size="1",
                    color="var(--aq-text-muted)",
                ),
                rx.vstack(
                    rx.foreach(State.palette_results, _palette_row),
                    spacing="1",
                    width="100%",
                    max_height="340px",
                    overflow_y="auto",
                ),
                spacing="3",
                width="100%",
            ),
            style={
                "background": "var(--aq-surface)",
                "border": "1px solid var(--aq-border)",
                "borderRadius": "18px",
                "maxWidth": "520px",
            },
        ),
        open=State.command_palette_open,
        on_open_change=State.set_command_palette_open,
    )


def trade_modal() -> rx.Component:
    """Modal 'Simular Aporte / Posição' (inspirado no modal 'Move money' em 0:06 do vídeo)."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.dialog.title("Simular Aporte na Carteira", margin_bottom="0"),
                        rx.text(
                            "Adicione qualquer Ação, FII, ETF ou BDR da B3; sua carteira fica salva automaticamente.",
                            size="2",
                            color="var(--aq-text-muted)",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            color_scheme="gray",
                            radius="full",
                            cursor="pointer",
                        )
                    ),
                    width="100%",
                    align="start",
                ),
                rx.vstack(
                    rx.text("Código na B3 (ex.: PETR4, VALE3, MXRF11, BOVA11, WEGE3)", size="2", weight="medium"),
                    rx.input(
                        value=State.form_ticker,
                        on_change=State.set_form_ticker,
                        placeholder="Ex.: BBAS3",
                        size="3",
                        width="100%",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text("Quantidade de cotas/ações", size="2", weight="medium"),
                        rx.input(
                            value=State.form_qty,
                            on_change=State.set_form_qty,
                            placeholder="Ex.: 200",
                            size="3",
                            width="100%",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("Preço médio de compra (R$)", size="2", weight="medium"),
                        rx.input(
                            value=State.form_price,
                            on_change=State.set_form_price,
                            placeholder="Ex.: 28,50",
                            size="3",
                            width="100%",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Estratégia / Cofre", size="2", weight="medium"),
                    rx.input(
                        value=State.form_note,
                        on_change=State.set_form_note,
                        placeholder="Ex.: Dividendos & Renda Passiva",
                        size="3",
                        width="100%",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                rx.hstack(
                    rx.dialog.close(
                        rx.button("Cancelar", size="2", **SECONDARY_PILL_BTN),
                    ),
                    rx.button(
                        rx.icon("check", size=15),
                        "Salvar na Carteira",
                        size="2",
                        on_click=State.save_position,
                        **PRIMARY_PILL_BTN,
                    ),
                    justify="end",
                    spacing="2",
                    width="100%",
                    margin_top="0.5rem",
                ),
                spacing="4",
                width="100%",
            ),
            style={
                "background": "var(--aq-surface)",
                "border": "1px solid var(--aq-border)",
                "borderRadius": "18px",
                "maxWidth": "440px",
            },
        ),
        open=State.trade_modal_open,
        on_open_change=State.set_trade_modal_open,
    )
