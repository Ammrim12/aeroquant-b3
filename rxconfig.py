"""Configuração do Reflex para o AeroQuant (estética Dark Glassmorphism sobre Wallpaper)."""

import reflex as rx
from reflex_base.plugins.sitemap import SitemapPlugin

config = rx.Config(
    app_name="aeroquant",
    default_color_mode="dark",
    disable_plugins=[SitemapPlugin],
    plugins=[
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="inherit",
                accent_color="jade",
                gray_color="sage",
                radius="large",
                scaling="100%",
            )
        ),
    ],
)
