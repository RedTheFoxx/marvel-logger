import logging
import re
import time

import discord
from discord import app_commands

logger = logging.getLogger(__name__)

from marvel_logger.features.check.embed import build_check_embed, build_error_embed
from marvel_logger.tracker.client import (
    ProfileNotFoundError,
    TrackerRateLimitError,
    TrackerScraper,
    TrackerScraperError,
)

_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,32}$")


def register_check_command(
    tree: app_commands.CommandTree,
    tracker: TrackerScraper,
) -> None:
    @tree.command(
        name="check",
        description="Affiche les statistiques Marvel Rivals d'un joueur (Tracker.gg)",
    )
    @app_commands.describe(
        username="Pseudo IGN du joueur sur Tracker.gg",
    )
    async def check(interaction: discord.Interaction, username: str) -> None:
        started = time.monotonic()
        requester = interaction.user.display_name
        username = username.strip()
        logger.info("/check demandé par %s pour « %s »", requester, username)

        if not username:
            await interaction.response.send_message(
                embed=build_error_embed("Le pseudo ne peut pas être vide."),
                ephemeral=True,
            )
            return
        if not _USERNAME_PATTERN.match(username):
            await interaction.response.send_message(
                embed=build_error_embed(
                    "Pseudo invalide. Utilisez uniquement lettres, chiffres, "
                    "tirets, underscores ou points (max 32 caractères)."
                ),
                ephemeral=True,
            )
            return

        await interaction.response.defer()
        logger.info("Réponse différée, récupération du profil…")

        try:
            profile = await tracker.fetch_profile(username)
            embed = build_check_embed(profile)
            await interaction.followup.send(embed=embed)
            logger.info(
                "/check OK pour %s (rang %s) — %.1fs total",
                username,
                profile.current_rank.tier_name if profile.current_rank else "—",
                time.monotonic() - started,
            )
        except ProfileNotFoundError as exc:
            logger.warning("/check profil introuvable : %s (%.1fs)", username, time.monotonic() - started)
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerRateLimitError as exc:
            logger.warning(
                "/check cooldown Tracker.gg pour %s : %.0fs restantes (%.1fs)",
                username,
                exc.retry_after_seconds,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerScraperError as exc:
            logger.error(
                "/check échec scraper pour %s : %s (%.1fs)",
                username,
                exc,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except Exception:
            logger.exception("/check erreur inattendue pour %s (%.1fs)", username, time.monotonic() - started)
            await interaction.followup.send(
                embed=build_error_embed(
                    "Une erreur inattendue s'est produite. Réessayez plus tard."
                ),
                ephemeral=True,
            )
