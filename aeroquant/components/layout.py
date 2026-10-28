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
) -> rx.Component:
    return rx.flex(
        rx.script(_KEYBOARD_SHORTCUT_JS),
        splash_intro_overlay(),
        sidebar(),
        rx.box(
            mobile_nav(),
            ticker_tape_bar(),
            rx.vstack(
                top_utility_bar(section_label),
                page_hero(hero_title, summary_line, show_market_actions=show_market_actions),
                _error_banner(),
                *content,
                spacing="5",
                width="100%",
                max_width="1240px",
                margin_x="auto",
                padding_x=rx.breakpoints(initial="0.9rem", sm="1.25rem", md="2.25rem"),
                padding_top=rx.breakpoints(initial="0.9rem", md="1.5rem"),
                padding_bottom=rx.breakpoints(initial="5.5rem", md="2.5rem"),
            ),
            mobile_bottom_bar(),
            stock_detail_drawer(),
            command_palette_modal(),
            trade_modal(),
            flex="1",
            min_width="0",
        ),
        width="100%",
        min_height="100vh",
        class_name=State.canvas_class,
    )
