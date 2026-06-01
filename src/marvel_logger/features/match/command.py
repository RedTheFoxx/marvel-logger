import logging
import time

import discord
from discord import app_commands

from marvel_logger.db import RegistrationStore
from marvel_logger.features.match.embed import (
    build_error_embed,
    build_match_picker_embed,
    build_no_matches_embed,
    build_no_registration_embed,
)
from marvel_logger.features.match.view import MatchPickerView
from marvel_logger.tracker.client import (
    ProfileNotFoundError,
    TrackerRateLimitError,
    TrackerScraper,
    TrackerScraperError,
)
from marvel_logger.utils import validate_tracker_username

logger = logging.getLogger(__name__)


async def _resolve_username(
    interaction: discord.Interaction,
    username: str | None,
    store: RegistrationStore,
) -> str | None:
    if username is not None:
        username = username.strip()
        validation_error = validate_tracker_username(username)
        if validation_error:
            await interaction.response.send_message(
                embed=build_error_embed(validation_error),
                ephemeral=True,
            )
            return None
        return username

    linked = await store.list_for_user(interaction.user.id)
    if not linked:
        await interaction.response.send_message(
            embed=build_no_registration_embed(),
            ephemeral=True,
        )
        return None
    return linked[0]


def register_match_command(
    tree: app_commands.CommandTree,
    tracker: TrackerScraper,
    store: RegistrationStore,
) -> None:
    @tree.command(
        name="match",
        description="Consulte le détail d'un de vos derniers matchs classés (Tracker.gg)",
    )
    @app_commands.describe(
        username="Pseudo Tracker.gg (optionnel si enregistré via /register)",
    )
    async def match(
        interaction: discord.Interaction,
        username: str | None = None,
    ) -> None:
        started = time.monotonic()
        requester = interaction.user.display_name
        logger.info(
            "[bold magenta]/match[/] demandé par [cyan]%s[/] (username=%s)",
            requester,
            username or "(défaut register)",
        )

        resolved = await _resolve_username(interaction, username, store)
        if resolved is None:
            return

        await interaction.response.defer()
        logger.info("Réponse différée, récupération des matchs pour %s…", resolved)

        try:
            bundle = await tracker.fetch_match_bundle(resolved)
            if not bundle.entries:
                await interaction.followup.send(
                    embed=build_no_matches_embed(resolved),
                    ephemeral=True,
                )
                return

            embed = build_match_picker_embed(bundle)
            view = MatchPickerView(bundle)
            await interaction.followup.send(embed=embed, view=view)
            logger.info(
                "[green]/match OK[/] pour %s (%d matchs, %d détails) — %.1fs",
                resolved,
                len(bundle.entries),
                len(bundle.details),
                time.monotonic() - started,
            )
        except ProfileNotFoundError as exc:
            logger.warning(
                "/match profil introuvable : %s (%.1fs)",
                resolved,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(str(exc)),
                ephemeral=True,
            )
        except TrackerRateLimitError as exc:
            logger.warning(
                "/match cooldown pour %s : %.0fs (%.1fs)",
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
                "/match échec scraper pour %s : %s (%.1fs)",
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
                "/match erreur inattendue pour %s (%.1fs)",
                resolved,
                time.monotonic() - started,
            )
            await interaction.followup.send(
                embed=build_error_embed(
                    "Une erreur inattendue s'est produite. Réessayez plus tard."
                ),
                ephemeral=True,
            )
