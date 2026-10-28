"""Card analítico principal da Visão Geral (inspirado no card 'Cash flow' do vídeo Coffra)."""

from __future__ import annotations

import reflex as rx

from ..services.market_data import BENCHMARK_PILLS, PERIOD_OPTIONS
from ..state import State
from .styles import SUBSURFACE_BOX, SURFACE_CARD, filter_pill_style

_AXIS_FMT = "(value) => value >= 1000 ? (value/1000).toFixed(0) + 'k' : value.toFixed(0)"
_PCT_FMT = "(value) => (value > 0 ? '+' : '') + value.toFixed(1).replace('.', ',') + '%'"


def _pill_button(item: dict[str, str]) -> rx.Component:
    is_active = State.chart_symbol == item["symbol"]
    return rx.box(
        item["label"],
        on_click=State.select_benchmark(item["symbol"], item["label"], item["subtitle"]),
        **filter_pill_style(is_active),
    )


def _summary_strip() -> rx.Component:
    """Faixa interna de 3 colunas (estilo 'September 2026: Money in / Money out / Net')."""
    s = State.chart_summary
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(
                    State.chart_label,
                    " · Resumo de ",
                    State.chart_period,
                    size="2",
                    weight="bold",
                    color="var(--aq-text)",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.badge(
                        "IFR-14: ",
                        s["rsi_value"],
                        " · ",
                        s["rsi_status"],
                        variant="soft",
                        color_scheme=s["rsi_tone"],
                        radius="full",
                        size="1",
                    ),
                    rx.badge(
                        "Vol: ",
                        s["volatility"],
                        variant="surface",
                        color_scheme="gray",
                        radius="full",
                        size="1",
                    ),
                    rx.badge(
                        "MM20: ",
                        s["mm20_label"],
                        variant="surface",
                        color_scheme="amber",
                        radius="full",
                        size="1",
                    ),
                    rx.text(s["sessions"], size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                width="100%",
                align="center",
            ),
            rx.grid(
                # Coluna 1: Cotação atual
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="8px",
                            height="8px",
                            border_radius="999px",
                            background="#2D5A43",
                        ),
                        rx.text("Cotação atual", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="2",
                    ),
                    rx.heading(s["current"], size="6", weight="bold", letter_spacing="-0.02em"),
                    rx.text(s["range_sub"], size="1", color="var(--aq-text-muted)"),
                    spacing="1",
                    align="start",
                ),
                # Coluna 2: Variação no período
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            width="8px",
                            height="8px",
                            border_radius="999px",
                            background="#D98A5F",
                        ),
                        rx.text("Resultado no período", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="2",
                    ),
                    rx.heading(s["period_diff"], size="6", weight="bold", letter_spacing="-0.02em"),
                    rx.hstack(
                        rx.badge(
                            s["period_change"],
                            color_scheme=s["tone"],
                            variant="soft",
                            radius="full",
                            size="1",
                        ),
                        rx.text("vs. início (", s["first"], ")", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="2",
                        wrap="wrap",
                    ),
                    spacing="1",
                    align="start",
                ),
                # Coluna 3: Liquidez / Volume médio
                rx.vstack(
                    rx.hstack(
                        rx.text("—", size="2", weight="bold", color="var(--aq-text)"),
                        rx.text("Volume diário médio", size="1", color="var(--aq-text-muted)"),
                        align="center",
                        spacing="2",
                    ),
                    rx.heading(s["avg_volume"], size="6", weight="bold", letter_spacing="-0.02em"),
                    rx.text("Negociação média por pregão", size="1", color="var(--aq-text-muted)"),
                    spacing="1",
                    align="start",
                ),
                columns=rx.breakpoints(initial="1", sm="3"),
                spacing="4",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        **SUBSURFACE_BOX,
    )


def _composed_flow_chart(with_mm20: bool = True) -> rx.Component:
    """Gráfico híbrido Coffra: barras de ganho/perda diária + curva de fechamento + MM20."""
    children = [
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3", stroke="rgba(120, 140, 128, 0.18)", vertical=False
        ),
        rx.recharts.bar(
            data_key="ganho",
            name="Alta diária (%)",
            y_axis_id="pct",
            fill="#4E8768",
            radius=[4, 4, 0, 0],
            animation_duration=900,
        ),
        rx.recharts.bar(
            data_key="perda",
            name="Baixa diária (%)",
            y_axis_id="pct",
            fill="#D98A5F",
            radius=[0, 0, 4, 4],
            animation_duration=900,
        ),
        rx.recharts.line(
            data_key="close",
            name="Fechamento",
            y_axis_id="price",
            type_="monotone",
            stroke="#6EE7B7",
            stroke_width=2.4,
            dot={"r": 2, "fill": "#34D399"},
            active_dot={"r": 5, "fill": "#34D399", "stroke": "#FFFFFF"},
            animation_duration=1000,
        ),
    ]
    if with_mm20:
        children.append(
            rx.recharts.line(
                data_key="mm20",
                name="Média Móvel 20p (MM20)",
                y_axis_id="price",
                type_="monotone",
                stroke="#F5B851",
                stroke_width=1.9,
                stroke_dasharray="5 4",
                dot=False,
                animation_duration=900,
            )
        )
    children.extend(
        [
            rx.recharts.x_axis(
                data_key="date",
                tick_line=False,
                axis_line=False,
                min_tick_gap=22,
            ),
            rx.recharts.y_axis(
                y_axis_id="pct",
                tick_line=False,
                axis_line=False,
                width=48,
                tick_formatter=_PCT_FMT,
            ),
            rx.recharts.y_axis(
                y_axis_id="price",
                orientation="right",
                domain=["auto", "auto"],
                tick_line=False,
                axis_line=False,
                width=56,
                tick_formatter=_AXIS_FMT,
            ),
            rx.recharts.graphing_tooltip(
                content_style={
                    "background": "var(--aq-surface-elevated)",
                    "border": "1px solid var(--aq-border-strong)",
                    "borderRadius": "12px",
                },
            ),
        ]
    )
    return rx.recharts.composed_chart(
        *children,
        data=State.chart_data,
        height=290,
        width="100%",
    )


def _smooth_area_chart(with_mm20: bool = True) -> rx.Component:
    """Gráfico de área contínuo (estilo 'Rainy day balance' do vídeo) + linha MM20."""
    children = [
        rx.el.svg.defs(
            rx.el.svg.linear_gradient(
                rx.el.svg.stop(stop_color="#34D399", offset="5%", stop_opacity=0.45),
                rx.el.svg.stop(stop_color="#34D399", offset="95%", stop_opacity=0.0),
                id="mainSageGradient",
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
            stroke_width=2.5,
            fill="url(#mainSageGradient)",
            dot=False,
            active_dot={"r": 5, "fill": "#34D399", "stroke": "#FFFFFF"},
            animation_duration=1000,
        ),
    ]
    if with_mm20:
        children.append(
            rx.recharts.line(
                data_key="mm20",
                name="Média Móvel 20p (MM20)",
                type_="monotone",
                stroke="#F5B851",
                stroke_width=1.9,
                stroke_dasharray="5 4",
                dot=False,
                animation_duration=900,
            )
        )
    children.extend(
        [
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
                    "borderRadius": "12px",
                },
            ),
        ]
    )
    return rx.recharts.composed_chart(
        *children,
        data=State.chart_data,
        height=290,
        width="100%",
    )


def price_chart() -> rx.Component:
    """Card principal de Fluxo e Desempenho do Mercado."""
    return rx.box(
        rx.vstack(
            # Cabeçalho do card + seletores de janela temporal + MM20
            rx.flex(
                rx.vstack(
                    rx.heading("Fluxo e Desempenho do Mercado", size="4", weight="bold"),
                    rx.text(
                        State.chart_subtitle,
                        " · Selecione qualquer ativo ou clique numa empresa abaixo",
                        size="2",
                        color="var(--aq-text-muted)",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.hstack(
                    rx.hstack(
                        rx.box(
                            "Barras & Linha",
                            on_click=State.set_chart_mode("fluxo"),
                            **filter_pill_style(State.chart_mode == "fluxo"),
                        ),
                        rx.box(
                            "Curva de Área",
                            on_click=State.set_chart_mode("area"),
                            **filter_pill_style(State.chart_mode == "area"),
                        ),
                        rx.box(
                            "MM20",
                            on_click=State.toggle_mm20,
                            **filter_pill_style(State.show_mm20),
                        ),
                        spacing="1",
                    ),
                    rx.hstack(
                        *[
                            rx.box(
                                label,
                                on_click=State.set_chart_period(label),
                                **filter_pill_style(State.chart_period == label),
                            )
                            for label in PERIOD_OPTIONS
                        ],
                        spacing="1",
                        wrap="wrap",
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
            # Pílulas de ativos em destaque (estilo "All gyms | Foundry | Quarry | Ridgeline")
            rx.hstack(
                *[_pill_button(item) for item in BENCHMARK_PILLS],
                spacing="2",
                width="100%",
                wrap="wrap",
                padding_bottom="2px",
            ),
            # Quadro interno de resumo do período
            _summary_strip(),
            # Área do gráfico
            rx.cond(
                State.chart_loading,
                rx.skeleton(height="290px", width="100%", border_radius="12px"),
                rx.cond(
                    State.chart_data.length() > 0,
                    rx.cond(
                        State.chart_mode == "fluxo",
                        rx.cond(
                            State.show_mm20,
                            _composed_flow_chart(True),
                            _composed_flow_chart(False),
                        ),
                        rx.cond(
                            State.show_mm20,
                            _smooth_area_chart(True),
                            _smooth_area_chart(False),
                        ),
                    ),
                    rx.center(
                        rx.text("Sem dados históricos disponíveis.", color="var(--aq-text-muted)"),
                        height="290px",
                        width="100%",
                    ),
                ),
            ),
            # Legenda inferior estilo Coffra
            rx.hstack(
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="999px", background="#4E8768"),
                    rx.text("Pregões em alta (%)", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.hstack(
                    rx.box(width="8px", height="8px", border_radius="999px", background="#D98A5F"),
                    rx.text("Pregões em baixa (%)", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="2",
                ),
                rx.hstack(
                    rx.text("—", size="2", weight="bold", color="var(--aq-text)"),
                    rx.text("Cotação de fechamento", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="1",
                ),
                rx.hstack(
                    rx.text("- -", size="2", weight="bold", color="#B8863B"),
                    rx.text("Média Móvel 20 pregões (MM20)", size="1", color="var(--aq-text-muted)"),
                    align="center",
                    spacing="1",
                ),
                spacing="4",
                wrap="wrap",
            ),
            spacing="4",
            width="100%",
        ),
        class_name="aq-fade-in",
        **SURFACE_CARD,
    )
