"""Barra lateral compacta de ícones (Desktop) + Topo e Barra Inferior Nativa (Mobile/Tablet)."""

from __future__ import annotations

import reflex as rx

from ..state import State

# (título para tooltip, rótulo curto mobile, rota, ícone Lucide)
NAV_ITEMS: tuple[tuple[str, str, str, str], ...] = (
    ("Visão Geral", "Início", "/", "house"),
    ("Empresas, FIIs, ETFs & BDRs", "Empresas", "/empresas", "building-2"),
    ("Minha Carteira & Benchmarks", "Carteira", "/carteira", "wallet"),
    ("Agenda do Mercado & Dividendos", "Agenda", "/calendario", "calendar-days"),
    ("Notícias do Mercado (Brasil)", "Notícias", "/noticias", "newspaper"),
)


def _brand_mark(size_px: str = "46px") -> rx.Component:
    """Logo oficial AeroQuant B3 onde a animação de abertura pousa após encolher."""
    return rx.link(
        rx.tooltip(
            rx.box(
                rx.image(
                    src="/logo_aeroquant.jpg",
                    alt="AeroQuant B3",
                    class_name="aq-brand-dock-img",
                ),
                width=size_px,
                height=size_px,
                class_name="aq-brand-dock-box",
                cursor="pointer",
            ),
            content="AeroQuant B3 · Terminal Financeiro",
            side="right",
        ),
        href="/",
        underline="none",
    )


def _rail_item(label: str, _short: str, href: str, icon_name: str) -> rx.Component:
    is_active = rx.State.router.page.path == href
    return rx.tooltip(
        rx.link(
            rx.center(
                rx.icon(
                    icon_name,
                    size=19,
                    color=rx.cond(is_active, "var(--aq-primary-fg)", "var(--aq-text-muted)"),
                ),
                width="40px",
                height="40px",
                border_radius="12px",
                background=rx.cond(is_active, "var(--aq-primary)", "transparent"),
                border=rx.cond(
                    is_active,
                    "1px solid rgba(110, 231, 183, 0.45)",
                    "1px solid transparent",
                ),
                _hover={
                    "background": rx.cond(
                        is_active, "var(--aq-primary-hover)", "var(--aq-primary-soft)"
                    )
                },
                transition="all 0.16s ease",
            ),
            href=href,
            underline="none",
        ),
        content=label,
        side="right",
    )


def sidebar() -> rx.Component:
    """Rail vertical estreito (68px) no desktop — fiel ao layout Coffra."""
    return rx.desktop_only(
        rx.vstack(
            _brand_mark(),
            rx.box(height="12px"),
            *[_rail_item(*item) for item in NAV_ITEMS],
            rx.spacer(),
            rx.tooltip(
                rx.center(
                    rx.icon("search", size=17, color="var(--aq-text-muted)"),
                    width="38px",
                    height="38px",
                    border_radius="10px",
                    cursor="pointer",
                    _hover={"background": "var(--aq-primary-soft)"},
                    on_click=State.set_command_palette_open(True),
                ),
                content="Busca Rápida Global (Ctrl+K)",
                side="right",
            ),
            rx.tooltip(
                rx.center(
                    rx.icon(
                        "refresh-cw",
                        size=17,
                        color="var(--aq-text-muted)",
                        class_name=rx.cond(State.is_loading, "aq-spin", ""),
                    ),
                    width="38px",
                    height="38px",
                    border_radius="10px",
                    cursor="pointer",
                    _hover={"background": "var(--aq-primary-soft)"},
                    on_click=State.manual_refresh,
                ),
                content="Atualizar cotações agora",
                side="right",
            ),
            rx.tooltip(
                rx.box(
                    rx.center(
                        rx.text("AQ", size="1", weight="bold", color="var(--aq-text)"),
                        width="38px",
                        height="38px",
                        border_radius="999px",
                        background="var(--aq-subsurface)",
                        border="1px solid var(--aq-border)",
                    ),
                    rx.box(
                        width="10px",
                        height="10px",
                        border_radius="999px",
                        background=rx.cond(State.auto_refresh, "#2D8A56", "#9AA59E"),
                        border="2px solid var(--aq-surface)",
                        position="absolute",
                        bottom="0px",
                        right="0px",
                    ),
                    position="relative",
                    cursor="pointer",
                    on_click=State.toggle_auto_refresh,
                ),
                content=rx.cond(
                    State.auto_refresh,
                    "Atualização online ativa (60s) · Clique para pausar",
                    "Atualização automática pausada · Clique para ativar",
                ),
                side="right",
            ),
            spacing="2",
            align="center",
            width="68px",
            height="100vh",
            padding_y="1.15rem",
            background="var(--aq-rail-bg)",
            border_right="1px solid var(--aq-border)",
            position="sticky",
            top="0",
            style={
                "backdropFilter": "blur(22px) saturate(160%)",
                "WebkitBackdropFilter": "blur(22px) saturate(160%)",
            },
        )
    )


def mobile_nav() -> rx.Component:
    """Cabeçalho compacto para Celular e Tablet."""
    return rx.mobile_and_tablet(
        rx.hstack(
            rx.hstack(
                _brand_mark(size_px="42px"),
                rx.vstack(
                    rx.hstack(
                        rx.text("Aero", size="3", weight="bold", color="#FFFFFF"),
                        rx.text("Quant", size="3", weight="bold", color="#34D399"),
                        rx.text("B3", size="3", weight="bold", color="#F5B851"),
                        spacing="1",
                        align="center",
                    ),
                    rx.text(State.market_status_label, size="1", color="#6EE7B7"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.center(
                    rx.icon("search", size=16, color="var(--aq-text)"),
                    width="36px",
                    height="36px",
                    border_radius="999px",
                    background="var(--aq-surface-elevated)",
                    border="1px solid var(--aq-border)",
                    on_click=State.set_command_palette_open(True),
                ),
                rx.center(
                    rx.icon("sparkles", size=16, color="#F5B851"),
                    width="36px",
                    height="36px",
                    border_radius="999px",
                    background="var(--aq-surface-elevated)",
                    border="1px solid var(--aq-border)",
                    on_click=State.cycle_glass_mode,
                ),
                rx.center(
                    rx.icon(
                        "refresh-cw",
                        size=16,
                        color="var(--aq-text)",
                        class_name=rx.cond(State.is_loading, "aq-spin", ""),
                    ),
                    width="36px",
                    height="36px",
                    border_radius="999px",
                    background="var(--aq-primary)",
                    border="1px solid rgba(110, 231, 183, 0.42)",
                    on_click=State.manual_refresh,
                ),
                spacing="2",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
            padding="0.65rem 1rem",
            background="var(--aq-rail-bg)",
            border_bottom="1px solid var(--aq-border)",
            style={
                "backdropFilter": "blur(22px) saturate(160%)",
                "WebkitBackdropFilter": "blur(22px) saturate(160%)",
            },
        )
    )


def mobile_bottom_bar() -> rx.Component:
    """Barra de navegação inferior fixa no celular (estilo app nativo iOS / Android)."""
    return rx.mobile_and_tablet(
        rx.hstack(
            *[
                rx.link(
                    rx.vstack(
                        rx.center(
                            rx.icon(
                                icon_name,
                                size=18,
                                color=rx.cond(
                                    rx.State.router.page.path == href,
                                    "#A7F3D0",
                                    "var(--aq-text-muted)",
                                ),
                            ),
                            width="44px",
                            height="28px",
                            border_radius="999px",
                            background=rx.cond(
                                rx.State.router.page.path == href,
                                "rgba(46, 124, 86, 0.55)",
                                "transparent",
                            ),
                        ),
                        rx.text(
                            short_label,
                            size="1",
                            weight=rx.cond(rx.State.router.page.path == href, "bold", "regular"),
                            color=rx.cond(
                                rx.State.router.page.path == href,
                                "#FFFFFF",
                                "var(--aq-text-muted)",
                            ),
                            style={"fontSize": "0.68rem"},
                        ),
                        spacing="1",
                        align="center",
                    ),
                    href=href,
                    underline="none",
                    flex="1",
                )
                for _full, short_label, href, icon_name in NAV_ITEMS
            ],
            justify="between",
            align="center",
            width="100%",
            padding="0.45rem 0.5rem 0.6rem",
            position="fixed",
            bottom="0",
            left="0",
            right="0",
            z_index="60",
            background="rgba(8, 13, 10, 0.86)",
            border_top="1px solid rgba(255, 255, 255, 0.16)",
            box_shadow="0 -8px 28px rgba(0, 0, 0, 0.55)",
            style={
                "backdropFilter": "blur(24px) saturate(170%)",
                "WebkitBackdropFilter": "blur(24px) saturate(170%)",
            },
        )
    )
