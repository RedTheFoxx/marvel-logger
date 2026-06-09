"""Configuration Rich : logs colorés et barres de progression."""

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

console = Console()

# Loggers utilisés par discord.py (handlers retirés → propagation vers la racine Rich)
_DISCORD_LOGGERS = (
    "discord",
    "discord.client",
    "discord.gateway",
    "discord.http",
    "discord.webhook",
)


def _make_rich_handler() -> RichHandler:
    return RichHandler(
        console=console,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
        show_path=True,
        show_time=True,
        markup=True,
    )


def configure_logging(level: int = logging.INFO) -> None:
    """Branche RichHandler sur la racine (logs colorés, tracebacks lisibles)."""
    handler = _make_rich_handler()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(handler)

    for name in _DISCORD_LOGGERS:
        discord_logger = logging.getLogger(name)
        discord_logger.handlers.clear()
        discord_logger.propagate = True
        discord_logger.setLevel(level)


def scrape_progress() -> Progress:
    """Barre indéterminée (spinner) — idéal pour le fetch Scrapling."""
    return Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )
