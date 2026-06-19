import logging

import discord
from discord import app_commands

from config import DISCORD_GUILD_ID, DISCORD_TOKEN
from db import FeelsStore, RegistrationStore
from features.feels import register_feels_command
from features.match import register_match_command
from features.register import register_register_command
from features.stats import register_stats_command
from features.unregister import register_unregister_command
from logging_setup import configure_logging
from tracker import TrackerScraper

logger = logging.getLogger(__name__)


class MarvelLoggerBot(discord.Client):
    def __init__(
        self,
        tracker: TrackerScraper,
        registrations: RegistrationStore,
        feels: FeelsStore,
    ) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tracker = tracker
        self.registrations = registrations
        self.feels = feels
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.registrations.init()
        await self.feels.init()
        await self.tracker.start()
        register_stats_command(self.tree, self.tracker)
        register_register_command(self.tree, self.tracker, self.registrations)
        register_unregister_command(self.tree, self.registrations, self.feels)
        register_match_command(self.tree, self.tracker, self.registrations)
        register_feels_command(
            self.tree, self.tracker, self.registrations, self.feels
        )
        if DISCORD_GUILD_ID:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info(
                "[green]✓[/] Commandes synchronisées sur la guilde [bold]%s[/]",
                DISCORD_GUILD_ID,
            )
        else:
            await self.tree.sync()
            logger.info("[green]✓[/] Commandes synchronisées [bold]globalement[/]")

    async def close(self) -> None:
        await self.tracker.close()
        await super().close()

    async def on_ready(self) -> None:
        logger.info(
            "[bold green]Connecté[/] en tant que [cyan]%s[/] [dim](%s)[/]",
            self.user,
            self.user.id,
        )


def main() -> None:
    configure_logging()

    if not DISCORD_TOKEN:
        raise SystemExit(
            "DISCORD_TOKEN manquant. Copiez .env.example vers .env et renseignez le token."
        )

    tracker = TrackerScraper()
    registrations = RegistrationStore()
    feels = FeelsStore()
    bot = MarvelLoggerBot(tracker, registrations, feels)
    # log_handler=None : pas de StreamHandler discord.py (format YYYY-MM-DD séparé)
    bot.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
