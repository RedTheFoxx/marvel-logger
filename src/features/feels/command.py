import asyncio
import io
import logging
import time

import discord
from discord import app_commands

from config import FEELS_MATCH_LIMIT
from db import FeelsStore, RegistrationStore
from features.feels.chart import render_feels_chart
from features.feels.embed import (
    build_error_embed,
    build_feels_no_matches_embed,
    build_feels_no_registration_embed,
    build_feels_overview_embed,
    build_feels_unknown_username_embed,
)
from features.feels.view import FeelsRatingView
from tracker.client import (
    ProfileNotFoundError,
    TrackerRateLimitError,
    TrackerScraper,
    TrackerScraperError,
)

logger = logging.getLogger(__name__)


async def _resolve_registered_username(
    interaction: discord.Interaction,
    username: str | None,
    store: RegistrationStore,
) -> str | None:
    """La notation est personnelle : le pseudo doit être lié via /register."""
    linked = await store.list_for_user(interaction.user.id)
    if not linked:
        await interaction.response.send_message(
            embed=build_feels_no_registration_embed(),
            ephemeral=True,
        )
        return None

    if username is None:
        return linked[0]

    username = username.strip()
    for candidate in linked:
        if candidate.lower() == username.lower():
            return candidate

    await interaction.response.send_message(
        embed=build_feels_unknown_username_embed(username, linked),
        ephemeral=True,
    )
    return None


def register_feels_command(
    tree: app_commands.CommandTree,
    tracker: TrackerScraper,
    store: RegistrationStore,
    feels_store: FeelsStore,
) -> None:
    @tree.command(
        name="feels",
        description=(
            "Notez le ressenti (1-10) de vos derniers matchs classés de la saison"
        ),
    )
    @app_commands.describe(
        username="Pseudo lié via /register (optionnel, premier pseudo par défaut)",
    )
    async def feels(
        interaction: discord.Interaction,
        username: str | None = None,
    ) -> None:
        started = time.monotonic()
        requester = interaction.user.display_name
        logger.info(
            "[bold magenta]/feels[/] demandé par [cyan]%s[/] (username=%s)",
            requester,
            username or "(défaut register)",
        )

        resolved = await _resolve_registered_username(interaction, username, store)
        if resolved is None:
            return

        await interaction.response.defer()
        logger.info("Réponse différée, récupération des matchs pour %s…", resolved)

        try:
            bundle = await tracker.fetch_match_bundle(
                resolved, limit=FEELS_MATCH_LIMIT
            )
            if not bundle.entries:
                await interaction.followup.send(
                    embed=build_feels_no_matches_embed(resolved),
                    ephemeral=True,
                )
                return

            normalized = bundle.username.lower()
            rated_ids = await feels_store.rated_match_ids(
                interaction.user.id, normalized, bundle.season_id
            )
            season_records = await feels_store.list_for_season(
                interaction.user.id, normalized, bundle.season_id
            )

            files: list[discord.File] = []
            if season_records:
                png_bytes = await asyncio.to_thread(
                    render_feels_chart, season_records
                )
                files = [
                    discord.File(
                        io.BytesIO(png_bytes), filename="feels_chart.png"
                    )
                ]

            embed = build_feels_overview_embed(bundle, rated_ids, season_records)
            unrated = [
                e for e in bundle.entries if e.match_id not in rated_ids
            ]
            view = (
                FeelsRatingView(bundle, unrated, feels_store, interaction.user.id)
                if unrated
                else discord.utils.MISSING
            )
            message = await interaction.followup.send(
                embed=embed,
                files=files,
                view=view,
                wait=True,
            )
            if isinstance(view, FeelsRatingView):
                view.message = message
            logger.info(
                "[green]/feels OK[/] pour %s (%d matchs, %d notés, %d à noter) — %.1fs",
                resolved,
                len(bundle.entries),
                len(rated_ids & {e.match_id for e in bundle.entries}),
                len(unrated),
                time.monotonic() - started,
            )
        except ProfileNotFoundError as exc:
            logger.warning(
                "/feels profil introuvable : %s (%.1fs)",
                resolved,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerRateLimitError as exc:
            logger.warning(
                "/feels cooldown pour %s : %.0fs (%.1fs)",
                resolved,
                exc.retry_after_seconds,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerScraperError as exc:
            logger.exception(
                "/feels échec scraper pour %s : %s (%.1fs)",
                resolved,
                exc,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except Exception:
            logger.exception(
                "/feels erreur inattendue pour %s (%.1fs)",
                resolved,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(
                    "Une erreur inattendue s'est produite. Réessayez plus tard."
                ),
                ephemeral=True,
            )
