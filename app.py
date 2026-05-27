import logging
import sys

import discord
from discord import app_commands

from marvel_logger.config import DISCORD_GUILD_ID, DISCORD_TOKEN
from marvel_logger.features.check import register_check_command
from marvel_logger.tracker import TrackerScraper


class MarvelLoggerBot(discord.Client):
    def __init__(self, tracker: TrackerScraper) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tracker = tracker
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tracker.start()
        register_check_command(self.tree, self.tracker)
        if DISCORD_GUILD_ID:
            guild = discord.Object(id=int(DISCORD_GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Commandes synchronisées sur la guilde {DISCORD_GUILD_ID}")
        else:
            await self.tree.sync()
            print("Commandes synchronisées globalement")

    async def close(self) -> None:
        await self.tracker.close()
        await super().close()

    async def on_ready(self) -> None:
        print(f"Connecté en tant que {self.user}")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


def main() -> None:
    _configure_logging()

    if not DISCORD_TOKEN:
        raise SystemExit(
            "DISCORD_TOKEN manquant. Copiez .env.example vers .env et renseignez le token."
        )

    tracker = TrackerScraper()
    bot = MarvelLoggerBot(tracker)
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
