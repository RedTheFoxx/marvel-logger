import asyncio
import io
import logging
import time

import discord
from discord import app_commands

logger = logging.getLogger(__name__)

from marvel_logger.features.stats.chart import render_rating_chart
from marvel_logger.features.stats.embed import build_stats_embed, build_error_embed
from marvel_logger.tracker.client import (
    ProfileNotFoundError,
    TrackerRateLimitError,
    TrackerScraper,
    TrackerScraperError,
)
from marvel_logger.utils import validate_tracker_username


def register_stats_command(
    tree: app_commands.CommandTree,
    tracker: TrackerScraper,
) -> None:
    @tree.command(
        name="stats",
        description="Affiche les statistiques Marvel Rivals d'un joueur (Tracker.gg)",
    )
    @app_commands.describe(
        username="Pseudo IGN du joueur sur Tracker.gg",
    )
    async def stats(interaction: discord.Interaction, username: str) -> None:
        started = time.monotonic()
        requester = interaction.user.display_name
        username = username.strip()
        logger.info(
            "[bold magenta]/stats[/] demandé par [cyan]%s[/] pour « [bold]%s[/] »",
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

        await interaction.response.defer()
        logger.info("Réponse différée, récupération du profil…")

        try:
            profile = await tracker.fetch_profile(username)
            embed = build_stats_embed(profile)
            files: list[discord.File] | None = None
            if profile.rating_chart:
                png_bytes = await asyncio.to_thread(
                    render_rating_chart,
                    profile.rating_chart,
                    total_delta=profile.rating_chart_delta,
                )
                files = [
                    discord.File(
                        io.BytesIO(png_bytes),
                        filename="rating_chart.png",
                    )
                ]
            await interaction.followup.send(embed=embed, files=files)
            logger.info(
                "[green]/stats OK[/] pour %s (rang %s, %d pts rating) — %.1fs total",
                username,
                profile.current_rank.tier_name if profile.current_rank else "—",
                len(profile.rating_chart),
                time.monotonic() - started,
            )
        except ProfileNotFoundError as exc:
            logger.warning("/stats profil introuvable : %s (%.1fs)", username, time.monotonic() - started)
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerRateLimitError as exc:
            logger.warning(
                "/stats cooldown Tracker.gg pour %s : %.0fs restantes (%.1fs)",
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
                "/stats échec scraper pour %s : %s (%.1fs)",
                username,
                exc,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except Exception:
            logger.exception("/stats erreur inattendue pour %s (%.1fs)", username, time.monotonic() - started)
            await interaction.followup.send(
                embed=build_error_embed(
                    "Une erreur inattendue s'est produite. Réessayez plus tard."
                ),
                ephemeral=True,
            )
