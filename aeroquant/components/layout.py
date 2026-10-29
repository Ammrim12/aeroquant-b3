"""Layout base compartilhado por todas as páginas do AeroQuant (Desktop + Mobile Nativo)."""

from __future__ import annotations

import reflex as rx

from ..state import State
from .drawer import command_palette_modal, stock_detail_drawer, trade_modal
from .header import page_hero, ticker_tape_bar, top_utility_bar
from .sidebar import mobile_bottom_bar, mobile_nav, sidebar

_KEYBOARD_SHORTCUT_JS = """
window.__aqDisableSplash = function() {
  document.documentElement.classList.add("aq-intro-done");
  if (document.body) document.body.classList.add("aq-intro-done");
  if (!document.getElementById("aq-kill-splash")) {
    var st = document.createElement("style");
    st.id = "aq-kill-splash";
    st.textContent = ".aq-splash-root, .aq-splash-backdrop, .aq-splash-logo-flyer, .aq-splash-meta { display: none !important; opacity: 0 !important; visibility: hidden !important; animation: none !important; } .aq-brand-dock-box { animation: none !important; }";
    document.head.appendChild(st);
  }
};

if (window.__aqIntroPlayed) {
  window.__aqDisableSplash();
} else {
  window.__aqIntroPlayed = true;
  setTimeout(function() {
    window.__aqDisableSplash();
  }, 2650);
}

if (!window.__aqKeybound) {
  window.__aqKeybound = true;
  window.addEventListener("keydown", function(e) {
    var tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : "";
    var isInput = tag === "input" || tag === "textarea" || (e.target && e.target.isContentEditable);
    if (((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") || (!isInput && e.key === "/")) {
      e.preventDefault();
      var btn = document.getElementById("aq-cmd-trigger");
      if (btn) btn.click();
    }
  });
  document.addEventListener("click", function(e) {
    var link = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (link) {
      window.__aqDisableSplash();
    }
  }, true);
}
"""


def splash_intro_overlay() -> rx.Component:
    """Tela de abertura animada: exibe a logo AeroQuant B3 no centro e depois a encolhe até o topo esquerdo."""
    return rx.box(
        rx.box(id="aq-splash-backdrop", class_name="aq-splash-backdrop"),
        rx.box(
            rx.image(
                src="/logo_aeroquant.jpg",
                alt="Logo Oficial AeroQuant B3",
            ),
            id="aq-splash-flyer",
            class_name="aq-splash-logo-flyer",
        ),
        rx.box(
            rx.box(
                rx.box(id="aq-splash-bar", class_name="aq-splash-progress-bar"),
                class_name="aq-splash-progress-track",
            ),
            rx.text(
                "TERMINAL QUANTITATIVO B3 · TEMPO REAL",
                size="1",
                weight="bold",
                letter_spacing="0.14em",
                color="#A7F3D0",
                style={"fontSize": "0.68rem", "textShadow": "0 2px 10px rgba(0,0,0,0.8)"},
            ),
            id="aq-splash-meta",
            class_name="aq-splash-meta",
        ),
        id="aq-splash-root",
        class_name="aq-splash-root",
    )


def _error_banner() -> rx.Component:
    return rx.cond(
        State.has_error,
        rx.callout(
            State.error_message,
            icon="triangle-alert",
            color_scheme="amber",
            variant="surface",
            width="100%",
        ),
    )


def page_layout(
    section_label: str,
    hero_title: rx.Var | str,
    summary_line: rx.Component,
    *content: rx.Component,
    show_market_actions: bool = True,
    fixed_filter: rx.Component | None = None,
) -> rx.Component:
    """Layout App-Shell: Barra lateral, cabeçalho e filtros fixos; apenas o conteúdo central rola."""
    fixed_header_children: list[rx.Component] = [
        top_utility_bar(section_label),
        page_hero(hero_title, summary_line, show_market_actions=show_market_actions),
    ]
    if fixed_filter is not None:
        fixed_header_children.append(fixed_filter)

    return rx.flex(
        rx.script(_KEYBOARD_SHORTCUT_JS),
        splash_intro_overlay(),
        sidebar(),
        rx.flex(
            # 1. Bloco Superior Fixo (Mobile Nav + Ticker Tape + Cabeçalho + Filtros da Página)
            rx.box(
                mobile_nav(),
                ticker_tape_bar(),
                rx.vstack(
                    *fixed_header_children,
                    spacing="2",
                    width="100%",
                    max_width="1240px",
                    margin_x="auto",
                    padding_x=rx.breakpoints(initial="0.9rem", sm="1.25rem", md="2.25rem"),
                    padding_top=rx.breakpoints(initial="0.6rem", md="0.8rem"),
                    padding_bottom=rx.breakpoints(initial="0.6rem", md="0.75rem"),
                ),
                width="100%",
                flex_shrink="0",
                z_index="35",
                background="rgba(8, 12, 10, 0.72)",
                border_bottom="1px solid var(--aq-border)",
                box_shadow="0 8px 24px rgba(0, 0, 0, 0.35)",
                style={
                    "backdropFilter": "blur(22px) saturate(160%)",
                    "WebkitBackdropFilter": "blur(22px) saturate(160%)",
                },
            ),
            # 2. Área Central Rolável (somente os cards/tabelas/gráficos centrais descem)
            rx.box(
                rx.vstack(
                    _error_banner(),
                    *content,
                    spacing="5",
                    width="100%",
                    max_width="1240px",
                    margin_x="auto",
                    padding_x=rx.breakpoints(initial="0.9rem", sm="1.25rem", md="2.25rem"),
                    padding_top="1.1rem",
                    padding_bottom=rx.breakpoints(initial="5.5rem", md="2.5rem"),
                ),
                flex="1",
                width="100%",
                min_height="0",
                overflow_y="auto",
                overflow_x="hidden",
                class_name="aq-central-scroll",
            ),
            mobile_bottom_bar(),
            stock_detail_drawer(),
            command_palette_modal(),
            trade_modal(),
            direction="column",
            flex="1",
            height="100vh",
            max_height="100vh",
            min_width="0",
            overflow="hidden",
        ),
        width="100%",
        height="100vh",
        max_height="100vh",
        overflow="hidden",
        class_name=State.canvas_class,
    )
