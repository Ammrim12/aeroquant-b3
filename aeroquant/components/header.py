"""Barra superior de utilidades (Ticker Tape B3, breadcrumb, Busca Rápida Ctrl+K, Seletor de Vidro, Alertas e Ações)."""

from __future__ import annotations

import reflex as rx
from reflex.style import toggle_color_mode

from ..state import State
from .styles import PRIMARY_PILL_BTN, SECONDARY_PILL_BTN

_ICON_CIRCLE = {
    "width": "36px",
    "height": "36px",
    "border_radius": "999px",
    "background": "var(--aq-surface-elevated)",
    "border": "1px solid var(--aq-border)",
    "cursor": "pointer",
    "box_shadow": "var(--aq-shadow)",
    "style": {
        "backdropFilter": "blur(16px)",
        "WebkitBackdropFilter": "blur(16px)",
    },
    "transition": "all 0.16s ease",
    "_hover": {"border_color": "var(--aq-border-strong)", "transform": "translateY(-1px)"},
}


def _ticker_tape_item(item: dict[str, str]) -> rx.Component:
    return rx.hstack(
        rx.text(item["ticker"], size="1", weight="bold", color="var(--aq-text)"),
        rx.text(item["price"], size="1", color="var(--aq-text-muted)"),
        rx.badge(
            item["change"],
            color_scheme=item["tone"],
            variant="soft",
            radius="full",
            size="1",
        ),
        rx.text("·", size="1", color="var(--aq-text-soft)"),
        align="center",
        spacing="2",
        padding_x="0.55rem",
        cursor="pointer",
        on_click=State.open_stock_drawer(item),
    )


def ticker_tape_bar() -> rx.Component:
    """Faixa horizontal deslizante de cotações ao vivo da B3 no topo do layout."""
    return rx.box(
        rx.box(
            rx.hstack(
                # Indicadores Macro fixos + Top Ações B3 (duplicados para loop contínuo)
                rx.hstack(
                    rx.text("IBOV", size="1", weight="bold", color="#F5B851"),
                    rx.text(State.ibov_quote["price"], size="1", color="var(--aq-text)"),
                    rx.badge(
                        State.ibov_quote["change"],
                        color_scheme=State.ibov_quote["color"],
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.text("·", size="1", color="var(--aq-text-soft)"),
                    align="center",
                    spacing="2",
                    padding_x="0.55rem",
                ),
                rx.hstack(
                    rx.text("USD/BRL", size="1", weight="bold", color="#F5B851"),
                    rx.text(State.usd_quote["price"], size="1", color="var(--aq-text)"),
                    rx.badge(
                        State.usd_quote["change"],
                        color_scheme=State.usd_quote["color"],
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.text("·", size="1", color="var(--aq-text-soft)"),
                    align="center",
                    spacing="2",
                    padding_x="0.55rem",
                ),
                rx.hstack(
                    rx.text("BTC", size="1", weight="bold", color="#F5B851"),
                    rx.text(State.btc_quote["price"], size="1", color="var(--aq-text)"),
                    rx.badge(
                        State.btc_quote["change"],
                        color_scheme=State.btc_quote["color"],
                        variant="soft",
                        radius="full",
                        size="1",
                    ),
                    rx.text("·", size="1", color="var(--aq-text-soft)"),
                    align="center",
                    spacing="2",
                    padding_x="0.55rem",
                ),
                rx.foreach(State.ticker_tape_items, _ticker_tape_item),
                rx.foreach(State.ticker_tape_items, _ticker_tape_item),
                spacing="1",
                align="center",
            ),
            class_name="aq-ticker-track",
        ),
        width="100%",
        overflow="hidden",
        padding_y="0.42rem",
        background="var(--aq-rail-bg)",
        border_bottom="1px solid var(--aq-border)",
        style={
            "backdropFilter": "blur(18px) saturate(150%)",
            "WebkitBackdropFilter": "blur(18px) saturate(150%)",
        },
    )


def _notifications_popover() -> rx.Component:
    return rx.popover.root(
        rx.popover.trigger(
            rx.box(
                rx.center(
                    rx.icon("bell", size=16, color="var(--aq-text)"),
                    **_ICON_CIRCLE,
                ),
                rx.center(
                    rx.text("3", size="1", weight="bold", color="#FFFFFF", font_size="10px"),
                    width="18px",
                    height="18px",
                    border_radius="999px",
                    background="var(--aq-primary)",
                    position="absolute",
                    top="-3px",
                    right="-3px",
                ),
                position="relative",
            )
        ),
        rx.popover.content(
            rx.vstack(
                rx.hstack(
                    rx.text("Radar do Pregão B3", size="2", weight="bold"),
                    rx.spacer(),
                    rx.text("Tempo real", size="1", color="var(--aq-text-muted)"),
                    width="100%",
                    align="center",
                ),
                rx.divider(),
                rx.hstack(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="999px",
                        background="#2D8A56",
                        margin_top="6px",
                        flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.text(
                            "Maior alta do dia: ",
                            rx.text.strong(State.breadth["top_gainer_ticker"]),
                            " (",
                            State.breadth["top_gainer_change"],
                            ")",
                            size="2",
                        ),
                        rx.text(
                            State.breadth["up_count"],
                            " ações operam no positivo na B3",
                            size="1",
                            color="var(--aq-text-muted)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                rx.hstack(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="999px",
                        background="#D98A5F",
                        margin_top="6px",
                        flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.text(
                            "Maior baixa do dia: ",
                            rx.text.strong(State.breadth["top_loser_ticker"]),
                            " (",
                            State.breadth["top_loser_change"],
                            ")",
                            size="2",
                        ),
                        rx.text(
                            State.breadth["down_count"],
                            " ações operam em queda na sessão",
                            size="1",
                            color="var(--aq-text-muted)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                rx.hstack(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="999px",
                        background="var(--aq-primary)",
                        margin_top="6px",
                        flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.text(
                            "Papel mais negociado: ",
                            rx.text.strong(State.breadth["most_active_ticker"]),
                            size="2",
                        ),
                        rx.text(
                            "Volume: ",
                            State.breadth["most_active_volume"],
                            " de ações hoje",
                            size="1",
                            color="var(--aq-text-muted)",
                        ),
                        spacing="0",
                        align="start",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                spacing="3",
                width="290px",
            ),
            style={
                "background": "var(--aq-surface-elevated)",
                "border": "1px solid var(--aq-border)",
                "borderRadius": "14px",
            },
        ),
    )


def top_utility_bar(section_label: str) -> rx.Component:
    """Faixa superior com trilha de navegação + Busca Rápida (Ctrl+K), Seletor de Vidro, Alertas e '+ Simular'."""
    return rx.flex(
        rx.box(
            rx.moment(interval=60000, on_change=State.tick_auto_refresh),
            display="none",
        ),
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.image(
                        src="/logo_aeroquant.jpg",
                        alt="AeroQuant B3",
                        class_name="aq-brand-dock-img",
                    ),
                    width="28px",
                    height="28px",
                    border_radius="8px",
                    overflow="hidden",
                    background="#0E1512",
                    border="1px solid rgba(110, 231, 183, 0.45)",
                    box_shadow="0 2px 8px rgba(0, 0, 0, 0.4)",
                    flex_shrink="0",
                ),
                rx.hstack(
                    rx.text("Aero", size="2", weight="bold", color="#FFFFFF"),
                    rx.text("Quant", size="2", weight="bold", color="#34D399"),
                    rx.text("B3", size="2", weight="bold", color="#F5B851"),
                    spacing="0",
                    align="center",
                ),
                spacing="2",
                align="center",
            ),
            rx.icon("chevron-right", size=14, color="var(--aq-text-soft)"),
            rx.text(section_label, size="2", weight="bold", color="var(--aq-text)"),
            rx.badge(
                rx.box(
                    width="6px",
                    height="6px",
                    border_radius="999px",
                    background=rx.cond(State.market_open, "#2D8A56", "#D98A5F"),
                ),
                State.market_status_label,
                " · ",
                State.last_update,
                variant="surface",
                color_scheme=rx.cond(State.market_open, "green", "gray"),
                radius="full",
                size="1",
            ),
            align="center",
            spacing="2",
            wrap="wrap",
        ),
        rx.hstack(
            # Botão de Busca Rápida Global (Command Palette) com atalho Ctrl+K
            rx.hstack(
                rx.icon("search", size=14, color="var(--aq-text-muted)"),
                rx.text("Buscar ativo na B3...", size="1", color="var(--aq-text-muted)"),
                rx.badge(
                    "Ctrl K",
                    size="1",
                    variant="surface",
                    color_scheme="gray",
                    radius="full",
                    display=rx.breakpoints(initial="none", sm="inline-flex"),
                ),
                rx.badge("1.600+", size="1", variant="soft", color_scheme="jade", radius="full"),
                id="aq-cmd-trigger",
                align="center",
                spacing="2",
                padding="0.38rem 0.75rem",
                border_radius="999px",
                background="var(--aq-surface-elevated)",
                border="1px solid var(--aq-border)",
                cursor="pointer",
                box_shadow="var(--aq-shadow)",
                style={
                    "backdropFilter": "blur(16px)",
                    "WebkitBackdropFilter": "blur(16px)",
                },
                on_click=State.set_command_palette_open(True),
                _hover={"border_color": "var(--aq-border-strong)"},
            ),
            # Seletor de Intensidade do Vidro (Cristal / Fumê / Obsidiana)
            rx.tooltip(
                rx.hstack(
                    rx.icon("sparkles", size=14, color="#F5B851"),
                    rx.text(State.glass_mode_label, size="1", weight="medium", color="var(--aq-text)"),
                    align="center",
                    spacing="2",
                    padding="0.38rem 0.75rem",
                    border_radius="999px",
                    background="var(--aq-surface-elevated)",
                    border="1px solid var(--aq-border)",
                    cursor="pointer",
                    box_shadow="var(--aq-shadow)",
                    style={
                        "backdropFilter": "blur(16px)",
                        "WebkitBackdropFilter": "blur(16px)",
                    },
                    on_click=State.cycle_glass_mode,
                    _hover={"border_color": "var(--aq-border-strong)"},
                ),
                content="Alternar transparência dos cards (Vidro Cristal · Vidro Fumê · Obsidiana)",
            ),
            rx.tooltip(
                rx.center(
                    rx.color_mode_cond(
                        light=rx.icon("moon", size=16, color="var(--aq-text)"),
                        dark=rx.icon("sun", size=16, color="var(--aq-text)"),
                    ),
                    on_click=toggle_color_mode,
                    **_ICON_CIRCLE,
                ),
                content="Alternar contraste do tema",
            ),
            _notifications_popover(),
            rx.button(
                rx.icon("plus", size=15),
                "Simular Aporte",
                size="2",
                on_click=State.set_trade_modal_open(True),
                **PRIMARY_PILL_BTN,
            ),
            align="center",
            spacing="2",
            wrap="wrap",
        ),
        justify="between",
        align="center",
        width="100%",
        wrap="wrap",
        gap="0.75rem",
    )


def page_hero(
    title: rx.Var | str,
    summary_line: rx.Component,
    show_market_actions: bool = True,
) -> rx.Component:
    return rx.flex(
        rx.vstack(
            rx.heading(
                title,
                size="6",
                weight="bold",
                letter_spacing="-0.03em",
                color="var(--aq-text)",
                class_name="aq-hero-title",
            ),
            summary_line,
            spacing="1",
            align="start",
        ),
        rx.cond(
            show_market_actions,
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.icon("building-2", size=15),
                        "Explorar B3 (",
                        State.breadth["total_assets"],
                        ")",
                        size="2",
                        **SECONDARY_PILL_BTN,
                    ),
                    href="/empresas",
                    underline="none",
                ),
                rx.button(
                    rx.icon(
                        "refresh-cw",
                        size=15,
                        class_name=rx.cond(State.is_loading, "aq-spin", ""),
                    ),
                    rx.cond(State.is_loading, "Atualizando...", "Atualizar Mercado"),
                    size="2",
                    on_click=State.manual_refresh,
                    disabled=State.is_loading,
                    **PRIMARY_PILL_BTN,
                ),
                spacing="2",
                wrap="wrap",
                flex_shrink="0",
            ),
        ),
        direction=rx.breakpoints(initial="column", md="row"),
        justify="between",
        align=rx.breakpoints(initial="start", md="center"),
        gap="0.65rem",
        width="100%",
    )
