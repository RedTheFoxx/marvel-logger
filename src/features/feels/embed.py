import datetime

import discord

from config import DEFAULT_EMBED_COLOR
from db import MatchFeelsRecord
from features.stats.embed import build_error_embed
from tracker.models import MatchBundle, MatchListEntry

__all__ = [
    "build_error_embed",
    "build_feels_no_registration_embed",
    "build_feels_unknown_username_embed",
    "build_feels_no_matches_embed",
    "build_feels_overview_embed",
    "build_feels_rating_prompt_embed",
    "build_feels_saved_embed",
]


def build_feels_no_registration_embed() -> discord.Embed:
    return discord.Embed(
        title="Aucun pseudo lié",
        description=(
            "La notation de ressenti est personnelle : liez d'abord "
            "votre pseudo Tracker.gg avec **/register** avant d'utiliser **/feels**."
        ),
        color=discord.Color.orange(),
    )


def build_feels_unknown_username_embed(
    username: str, linked: list[str]
) -> discord.Embed:
    linked_text = ", ".join(f"**{name}**" for name in linked) or "—"
    return discord.Embed(
        title="Pseudo non lié à votre compte",
        description=(
            f"**{username}** ne fait pas partie de vos pseudos enregistrés "
            f"({linked_text}).\n"
            "Vous ne pouvez noter que vos propres matchs : "
            "liez ce pseudo avec **/register** si c'est le vôtre."
        ),
        color=discord.Color.orange(),
    )


def build_feels_no_matches_embed(username: str) -> discord.Embed:
    return discord.Embed(
        title="Aucun match classé récent",
        description=(
            f"Aucune partie classée récente trouvée pour **{username}** "
            "sur la saison courante."
        ),
        color=discord.Color.orange(),
    )


def _outcome_label(outcome: str) -> str:
    return "Victoire" if outcome == "win" else "Défaite"


def _entry_line(index: int, entry: MatchListEntry, rated: bool) -> str:
    status = "✅ noté" if rated else "⬜ à noter"
    return (
        f"`#{index}` {status} · **{_outcome_label(entry.outcome)}** {entry.score} · "
        f"{entry.map_name} · {entry.hero.name} "
        f"(KDA {entry.kda_ratio})"
    )


def build_feels_overview_embed(
    bundle: MatchBundle,
    rated_ids: set[str],
    season_records: list[MatchFeelsRecord],
) -> discord.Embed:
    unrated_count = sum(1 for e in bundle.entries if e.match_id not in rated_ids)
    if unrated_count:
        description = (
            "Choisissez un match **à noter** dans le menu déroulant ci-dessous "
            "pour lui donner une note de ressenti de **1 à 10**."
        )
    else:
        description = (
            "Tous vos derniers matchs de la saison sont déjà notés. "
            "Revenez après vos prochaines parties !"
        )

    embed = discord.Embed(
        title=f"Ressenti des matchs — {bundle.username}",
        description=description,
        color=DEFAULT_EMBED_COLOR,
    )

    lines = [
        _entry_line(index, entry, entry.match_id in rated_ids)
        for index, entry in enumerate(bundle.entries, start=1)
    ]
    embed.add_field(
        name=f"Derniers matchs (saison courante) — {unrated_count} à noter",
        value="\n".join(lines)[:1024] or "—",
        inline=False,
    )

    if season_records:
        average = sum(r.rating for r in season_records) / len(season_records)
        embed.add_field(
            name="Notes sur la saison",
            value=(
                f"**{len(season_records)}** match"
                f"{'s' if len(season_records) > 1 else ''} noté"
                f"{'s' if len(season_records) > 1 else ''} · "
                f"moyenne **{average:.1f}/10**"
            ),
            inline=False,
        )
        embed.set_image(url="attachment://feels_chart.png")

    embed.set_footer(text="Tracker.gg · Marvel Rivals")
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
    return embed


def build_feels_rating_prompt_embed(entry: MatchListEntry) -> discord.Embed:
    embed = discord.Embed(
        title="Quelle note pour ce match ?",
        description=(
            f"**{_outcome_label(entry.outcome)}** {entry.score} · "
            f"{entry.game_mode} · **{entry.map_name}**\n"
            f"{entry.hero.name} · KDA **{entry.kda_ratio}** "
            f"({entry.kills}/{entry.deaths}/{entry.assists})\n\n"
            "Choisissez une note de **1** (horrible) à **10** (incroyable) "
            "dans le menu ci-dessous."
        ),
        color=DEFAULT_EMBED_COLOR,
        url=entry.match_url,
    )
    embed.set_footer(text="Tracker.gg · Marvel Rivals")
    return embed


def build_feels_saved_embed(
    entry: MatchListEntry,
    rating: int,
    season_records: list[MatchFeelsRecord],
) -> discord.Embed:
    average = sum(r.rating for r in season_records) / len(season_records)
    embed = discord.Embed(
        title=f"Note enregistrée : {rating}/10",
        description=(
            f"**{_outcome_label(entry.outcome)}** {entry.score} · "
            f"{entry.map_name} · {entry.hero.name}\n\n"
            f"**{len(season_records)}** match"
            f"{'s' if len(season_records) > 1 else ''} noté"
            f"{'s' if len(season_records) > 1 else ''} sur la saison · "
            f"moyenne **{average:.1f}/10**\n"
            "Relancez **/feels** pour noter un autre match."
        ),
        color=discord.Color.green(),
        url=entry.match_url,
    )
    embed.set_image(url="attachment://feels_chart.png")
    embed.set_footer(text="Tracker.gg · Marvel Rivals")
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
    return embed
