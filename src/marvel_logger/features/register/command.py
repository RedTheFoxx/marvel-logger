import logging
import time

import discord
from discord import app_commands

from marvel_logger.config import MAX_REGISTRATIONS_PER_USER
from marvel_logger.db.store import RegistrationStore
from marvel_logger.features.register.embed import (
    build_already_linked_embed,
    build_error_embed,
    build_quota_reached_embed,
    build_register_success_embed,
)
from marvel_logger.tracker.client import (
    ProfileNotFoundError,
    TrackerRateLimitError,
    TrackerScraper,
    TrackerScraperError,
)
from marvel_logger.utils import validate_tracker_username

logger = logging.getLogger(__name__)


def register_register_command(
    tree: app_commands.CommandTree,
    tracker: TrackerScraper,
    store: RegistrationStore,
) -> None:
    @tree.command(
        name="register",
        description="Lie votre compte Discord à un pseudo Tracker.gg (max 3)",
    )
    @app_commands.describe(
        username="Pseudo IGN du joueur sur Tracker.gg",
    )
    async def register(interaction: discord.Interaction, username: str) -> None:
        started = time.monotonic()
        requester = interaction.user.display_name
        discord_user_id = interaction.user.id
        username = username.strip()
        logger.info(
            "[bold magenta]/register[/] demandé par [cyan]%s[/] pour « [bold]%s[/] »",
            requester,
            username,
        )

        validation_error = validate_tracker_username(username)
        if validation_error:
            await interaction.response.send_message(
                embed=build_error_embed(validation_error),
                ephemeral=True,
            )
            return

        normalized = username.lower()
        if await store.has_user_pseudo(discord_user_id, normalized):
            linked = await store.list_for_user(discord_user_id)
            await interaction.response.send_message(
                embed=build_already_linked_embed(linked),
                ephemeral=True,
            )
            return

        if await store.count_for_user(discord_user_id) >= MAX_REGISTRATIONS_PER_USER:
            linked = await store.list_for_user(discord_user_id)
            await interaction.response.send_message(
                embed=build_quota_reached_embed(linked),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        logger.info("Réponse différée, vérification du profil Tracker.gg…")

        try:
            profile = await tracker.fetch_profile(username)
            await store.add(discord_user_id, profile.username)
            all_usernames = await store.list_for_user(discord_user_id)
            await interaction.followup.send(
                embed=build_register_success_embed(profile, all_usernames),
                ephemeral=True,
            )
            logger.info(
                "[green]/register OK[/] %s lié pour %s (%d/%d) — %.1fs",
                profile.username,
                requester,
                len(all_usernames),
                MAX_REGISTRATIONS_PER_USER,
                time.monotonic() - started,
            )
        except ProfileNotFoundError as exc:
            logger.warning(
                "/register profil introuvable : %s (%.1fs)",
                username,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerRateLimitError as exc:
            logger.warning(
                "/register cooldown Tracker.gg pour %s : %.0fs restantes (%.1fs)",
                username,
                exc.retry_after_seconds,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerScraperError as exc:
            logger.exception(
                "/register échec scraper pour %s : %s (%.1fs)",
                username,
                exc,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except Exception:
            logger.exception(
                "/register erreur inattendue pour %s (%.1fs)",
                username,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(
                    "Une erreur inattendue s'est produite. Réessayez plus tard."
                ),
                ephemeral=True,
            )
