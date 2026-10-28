"""Utilitários de formatação e de tempo (padrão brasileiro, fuso de Brasília)."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

# O Brasil não adota horário de verão desde 2019: UTC-3 fixo dispensa o pacote tzdata.
BRT = timezone(timedelta(hours=-3), "BRT")

_WEEKDAYS = (
    "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira",
    "sexta-feira", "sábado", "domingo",
)  # fmt: skip
_MONTHS = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)  # fmt: skip


def format_number(value: float, decimals: int = 2) -> str:
    """Formata um número no padrão pt-BR (1.234,56), sem depender do locale do SO."""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def format_compact(value: float, prefix: str = "") -> str:
    """Formata valores grandes por extenso curto: ``R$ 1,2 tri``, ``80,6 mi``."""
    for limit, label in ((1e12, "tri"), (1e9, "bi"), (1e6, "mi"), (1e3, "mil")):
        if abs(value) >= limit:
            return f"{prefix}{format_number(value / limit, 1)} {label}"
    return f"{prefix}{format_number(value, 0)}"


def format_signed(value: float, prefix: str = "", suffix: str = "") -> str:
    """Formata com sinal explícito: ``+R$ 1.234,00`` / ``-R$ 56,00``."""
    sign = "+" if value >= 0 else "-"
    return f"{sign}{prefix}{format_number(abs(value))}{suffix}"


def format_percent(value: float) -> str:
    """Variação percentual com sinal: ``+2,19%``."""
    return format_signed(value, suffix="%")


def tone(value: float, threshold: float = 0.005) -> str:
    """Cor semântica de uma variação: 'green' (alta), 'tomato' (baixa) ou 'gray'."""
    if value > threshold:
        return "green"
    if value < -threshold:
        return "tomato"
    return "gray"


def now_brt() -> datetime:
    """Data/hora atual em Brasília."""
    return datetime.now(BRT)


def timestamp_now() -> str:
    """Horário da última atualização, para exibição."""
    return now_brt().strftime("%H:%M:%S")


def greeting(now: datetime | None = None) -> str:
    """Saudação conforme a hora do dia."""
    hour = (now or now_brt()).hour
    if hour < 12:
        return "Bom dia"
    return "Boa tarde" if hour < 18 else "Boa noite"


def long_date(now: datetime | None = None) -> str:
    """Ex.: ``terça-feira, 28 de outubro de 2026``."""
    now = now or now_brt()
    return f"{_WEEKDAYS[now.weekday()]}, {now.day} de {_MONTHS[now.month - 1]} de {now.year}"


def market_status(now: datetime | None = None) -> tuple[bool, str]:
    """Estado do pregão da B3 (seg–sex, 10h00–17h55; feriados não considerados)."""
    now = now or now_brt()
    is_open = now.weekday() < 5 and time(10, 0) <= now.time() <= time(17, 55)
    return is_open, "Pregão aberto" if is_open else "Pregão fechado"


def relative_time(moment: datetime) -> str:
    """Tempo decorrido: 'Há 15 min', 'Há 3 h', 'Há 2 d'."""
    seconds = max(0, int((datetime.now(timezone.utc) - moment).total_seconds()))
    if seconds < 3600:
        return f"Há {max(1, seconds // 60)} min"
    if seconds < 86400:
        return f"Há {seconds // 3600} h"
    return f"Há {seconds // 86400} d"
