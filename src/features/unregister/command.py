import logging
import time

import discord
from discord import app_commands

from db.feels_store import FeelsStore
from db.store import RegistrationStore
from features.unregister.embed import (
    build_not_registered_embed,
    build_unregister_error_embed,
    build_unregister_success_embed,
)

logger = logging.getLogger(__name__)


def register_unregister_command(
    tree: app_commands.CommandTree,
    store: RegistrationStore,
    feels: FeelsStore,
) -> None:
    @tree.command(
        name="unregister",
        description="Dissocie un pseudo Tracker.gg de votre compte Discord et supprime les données associées",
    )
    @app_commands.describe(
        username="Pseudo IGN à retirer",
    )
    async def unregister(interaction: discord.Interaction, username: str) -> None:
        started = time.monotonic()
        requester = interaction.user.display_name
        discord_user_id = interaction.user.id
        username = username.strip()
        logger.info(
            "[bold magenta]/unregister[/] demandé par [cyan]%s[/] pour « [bold]%s[/] »",
            requester,
            username,
        )

        normalized = username.lower()

        if not await store.has_user_pseudo(discord_user_id, normalized):
            await interaction.response.send_message(
                embed=build_not_registered_embed(username),
                ephemeral=True,
            )
            return

        try:
            feels_deleted = await feels.delete_for_username(discord_user_id, normalized)
            removed = await store.remove(discord_user_id, normalized)

            if not removed:
                # Ne devrait pas arriver (on a vérifié has_user_pseudo avant)
                await interaction.response.send_message(
                    embed=build_unregister_error_embed(
                        "Une erreur inattendue s'est produite lors de la suppression. Réessayez plus tard."
                    ),
                    ephemeral=True,
                )
                return

            remaining = await store.list_for_user(discord_user_id)
            await interaction.response.send_message(
                embed=build_unregister_success_embed(username, remaining, feels_deleted),
                ephemeral=True,
            )
            logger.info(
                "[green]/unregister OK[/] %s retiré pour %s (%d feels supprimés) — %.1fs",
                username,
                requester,
                feels_deleted,
                time.monotonic() - started,
            )
        except Exception:
            logger.exception(
                "/unregister erreur inattendue pour %s (%.1fs)",
                username,
                time.monotonic() - started,
            )
            await interaction.response.send_message(
                embed=build_unregister_error_embed(
                    "Une erreur inattendue s'est produite. Réessayez plus tard."
                ),
                ephemeral=True,
            )
