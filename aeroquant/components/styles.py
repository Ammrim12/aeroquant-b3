"""Tokens de estilo reutilizáveis (estética Glassmorphism Escuro sobre Wallpaper)."""

from __future__ import annotations

import reflex as rx

_GLASS_FILTER = {
    "backdropFilter": "blur(20px) saturate(155%)",
    "WebkitBackdropFilter": "blur(20px) saturate(155%)",
}

# Card principal translúcido (vidro escuro com desfoque sobre o wallpaper).
SURFACE_CARD = {
    "background": "var(--aq-surface)",
    "border": "1px solid var(--aq-border)",
    "border_radius": "18px",
    "box_shadow": "var(--aq-shadow)",
    "padding": rx.breakpoints(initial="1rem", md="1.5rem"),
    "width": "100%",
    "style": _GLASS_FILTER,
}

# Card clicável translúcido (empresas, posições, notícias, agenda) com brilho de borda no hover.
INTERACTIVE_CARD = {
    "background": "var(--aq-surface)",
    "border": "1px solid var(--aq-border)",
    "border_radius": "16px",
    "box_shadow": "var(--aq-shadow)",
    "padding": "1.1rem",
    "width": "100%",
    "cursor": "pointer",
    "style": _GLASS_FILTER,
    "transition": "all 0.22s cubic-bezier(0.32, 0.72, 0, 1)",
    "_hover": {
        "transform": "translateY(-2px)",
        "border_color": "var(--aq-border-strong)",
        "box_shadow": "var(--aq-shadow-hover)",
    },
}

# Caixa interna translúcida (quadros internos de métricas nos gráficos e na carteira).
SUBSURFACE_BOX = {
    "background": "var(--aq-subsurface)",
    "border": "1px solid var(--aq-border)",
    "border_radius": "14px",
    "padding": "0.95rem 1.1rem",
    "width": "100%",
    "style": {
        "backdropFilter": "blur(14px)",
        "WebkitBackdropFilter": "blur(14px)",
    },
}

# Botão primário verde-esmeralda translúcido.
PRIMARY_PILL_BTN = {
    "background": "var(--aq-primary)",
    "color": "var(--aq-primary-fg)",
    "border": "1px solid rgba(110, 231, 183, 0.42)",
    "border_radius": "999px",
    "padding_x": "1rem",
    "font_weight": "600",
    "cursor": "pointer",
    "style": {
        "backdropFilter": "blur(14px)",
        "WebkitBackdropFilter": "blur(14px)",
    },
    "transition": "all 0.18s ease",
    "_hover": {"background": "var(--aq-primary-hover)", "transform": "translateY(-1px)"},
    "_active": {"transform": "scale(0.97)"},
}

# Botão secundário de vidro escuro com borda sutil.
SECONDARY_PILL_BTN = {
    "background": "var(--aq-surface-elevated)",
    "color": "var(--aq-text)",
    "border": "1px solid var(--aq-border)",
    "border_radius": "999px",
    "padding_x": "1rem",
    "font_weight": "500",
    "cursor": "pointer",
    "box_shadow": "var(--aq-shadow)",
    "style": {
        "backdropFilter": "blur(16px)",
        "WebkitBackdropFilter": "blur(16px)",
    },
    "transition": "all 0.18s ease",
    "_hover": {"border_color": "var(--aq-border-strong)", "transform": "translateY(-1px)"},
}

ROW_HOVER = {
    "transition": "background-color 0.15s ease",
    "cursor": "pointer",
    "_hover": {"background_color": "var(--aq-subsurface)"},
}


def filter_pill_style(is_active) -> dict:
    """Estilo das pílulas de filtro translúcidas com alto contraste quando selecionadas."""
    return {
        "background": rx.cond(is_active, "var(--aq-pill-active-bg)", "var(--aq-pill-bg)"),
        "color": rx.cond(is_active, "var(--aq-pill-active-fg)", "var(--aq-pill-fg)"),
        "border": rx.cond(
            is_active,
            "1px solid var(--aq-pill-active-border)",
            "1px solid var(--aq-border)",
        ),
        "box_shadow": rx.cond(
            is_active,
            "0 4px 16px rgba(46, 124, 86, 0.38), inset 0 1px 0 rgba(255, 255, 255, 0.25)",
            "none",
        ),
        "border_radius": "999px",
        "padding": "0.42rem 0.9rem",
        "font_size": "0.82rem",
        "font_weight": rx.cond(is_active, "600", "500"),
        "cursor": "pointer",
        "white_space": "nowrap",
        "style": {
            "backdropFilter": "blur(14px)",
            "WebkitBackdropFilter": "blur(14px)",
        },
        "transition": "all 0.16s ease",
        "_hover": {"border_color": "var(--aq-border-strong)", "transform": "translateY(-1px)"},
    }


def tinted_card_style(tint: str) -> dict:
    """Estilo dos 4 cards translúcidos coloridos inferiores (mint, rose, sand, lemon)."""
    return {
        "background": f"var(--aq-tint-{tint})",
        "border": f"1px solid var(--aq-tint-{tint}-border)",
        "border_radius": "16px",
        "padding": "1.1rem 1.25rem",
        "width": "100%",
        "box_shadow": "var(--aq-shadow)",
        "style": _GLASS_FILTER,
        "transition": "all 0.2s ease",
        "_hover": {
            "transform": "translateY(-2px)",
            "border_color": "var(--aq-border-strong)",
            "box_shadow": "var(--aq-shadow-hover)",
        },
    }
