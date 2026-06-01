import datetime

import discord

from marvel_logger.config import DEFAULT_EMBED_COLOR, TRACKER_MATCHES_URL
from marvel_logger.features.stats.embed import build_error_embed
from marvel_logger.tracker.models import (
    MatchBundle,
    MatchDetail,
    MatchListEntry,
    MatchPlayerRow,
)

__all__ = [
    "build_error_embed",
    "build_no_registration_embed",
    "build_no_matches_embed",
    "build_match_picker_embed",
    "build_match_detail_embed",
    "build_match_detail_unavailable_embed",
]

_SECTION_SEPARATOR = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


def build_no_registration_embed() -> discord.Embed:
    return discord.Embed(
        title="Aucun pseudo lié",
        description=(
            "Liez d'abord un pseudo Tracker.gg avec **/register**, "
            "ou précisez un `username` dans la commande."
        ),
        color=discord.Color.orange(),
    )


def build_no_matches_embed(username: str) -> discord.Embed:
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


def _format_played(entry: MatchListEntry) -> str:
    if entry.played_at:
        return entry.played_at.strftime("%d/%m/%Y %H:%M UTC")
    return "—"


def _match_field_value(entry: MatchListEntry) -> str:
    outcome = _outcome_label(entry.outcome)
    hero = entry.hero.name
    rank = entry.rank
    rs_part = f" · {rank.rs} RS" if rank and rank.rs else ""
    delta = f" ({rank.rs_delta})" if rank and rank.rs_delta else ""
    return (
        f"**{outcome}** · {entry.score}\n"
        f"{entry.game_mode} · **{entry.map_name}**"
        + (f" ({entry.map_location})" if entry.map_location else "")
        + f"\n{hero} · KDA **{entry.kda_ratio}** "
        f"({entry.kills}/{entry.deaths}/{entry.assists})"
        + f"{rs_part}{delta}\n"
        f"{_format_played(entry)}"
    )


def build_match_picker_embed(bundle: MatchBundle) -> discord.Embed:
    matches_url = TRACKER_MATCHES_URL.format(username=bundle.username)
    if bundle.season_id:
        matches_url += f"?season={bundle.season_id}"

    embed = discord.Embed(
        title=f"Derniers matchs classés — {bundle.username}",
        description=(
            "Choisissez un match dans le **menu déroulant** ci-dessous "
            "pour afficher le scoreboard détaillé."
        ),
        color=DEFAULT_EMBED_COLOR,
        url=matches_url,
    )
    for index, entry in enumerate(bundle.entries, start=1):
        embed.add_field(
            name=f"#{index} · {_outcome_label(entry.outcome)} · {entry.score}",
            value=_match_field_value(entry),
            inline=False,
        )
    embed.set_footer(text="Tracker.gg · Marvel Rivals")
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
    return embed


def _badge_prefix(player: MatchPlayerRow) -> str:
    if player.is_mvp:
        return "MVP "
    if player.is_svp:
        return "SVP "
    return ""


def _compact_player_line(player: MatchPlayerRow) -> str:
    parts = [
        f"{_badge_prefix(player)}**{player.username}**",
        f"{player.kda_ratio} KDA",
        f"{player.kills}/{player.deaths}/{player.assists}",
    ]
    if player.damage:
        parts.append(f"{player.damage} dmg")
    if player.rank and player.rank.rs_delta:
        parts.append(f"{player.rank.rs_delta} RS")
    elif player.rank and player.rank.rs:
        parts.append(f"{player.rank.rs} RS")
    line = " · ".join(parts)
    return line[:1024]


def _team_block(players: list[MatchPlayerRow]) -> str:
    lines = [_compact_player_line(p) for p in players]
    text = "\n".join(lines) if lines else "—"
    if len(text) > 1024:
        text = text[:1020] + "…"
    return text


def _player_detail_block(player: MatchPlayerRow) -> str:
    heroes = ", ".join(h.name for h in player.heroes) or "—"
    lines = [
        f"**{player.username}** · {heroes}",
        f"KDA **{player.kda_ratio}** · {player.kills} / {player.deaths} / {player.assists}",
    ]
    if player.solo_head_last:
        lines.append(f"Solo / Head / Last · {player.solo_head_last}")
    if player.damage:
        dmg = f"**{player.damage}**"
        if player.damage_per_min:
            dmg += f" ({player.damage_per_min}/min)"
        lines.append(f"Dégâts · {dmg}")
    if player.blocked:
        blk = f"**{player.blocked}**"
        if player.blocked_per_min:
            blk += f" ({player.blocked_per_min}/min)"
        lines.append(f"Bloqués · {blk}")
    if player.healing:
        heal = f"**{player.healing}**"
        if player.healing_per_min:
            heal += f" ({player.healing_per_min}/min)"
        lines.append(f"Soins · {heal}")
    if player.accuracy:
        lines.append(f"Précision · {player.accuracy}")
    if player.rank:
        rank_line = player.rank.tier_name
        if player.rank.rs:
            rank_line += f" · {player.rank.rs} RS"
        if player.rank.rs_delta:
            rank_line += f" ({player.rank.rs_delta})"
        lines.append(f"Rang · {rank_line}")
    return "\n".join(lines)


def build_match_detail_embed(detail: MatchDetail) -> discord.Embed:
    if detail.queried_outcome == "win":
        color = discord.Color.green()
    elif detail.queried_outcome == "loss":
        color = discord.Color.red()
    else:
        color = DEFAULT_EMBED_COLOR

    map_line = detail.map_name
    if detail.map_location:
        map_line += f" · {detail.map_location}"

    header = f"**{detail.game_mode}** · {map_line}\n"
    header += f"Score **{detail.score}**"
    if detail.duration:
        header += f" · {detail.duration}"
    if detail.played_at:
        header += f"\n{detail.played_at.strftime('%d/%m/%Y %H:%M UTC')}"

    embed = discord.Embed(
        title=f"Match — {detail.queried_username}",
        description=header,
        color=color,
        url=detail.match_url,
    )

    if detail.teams:
        embed.add_field(name="\u200b", value=_SECTION_SEPARATOR, inline=False)

    for team in detail.teams:
        score_suffix = f" ({team.score})" if team.score is not None else ""
        embed.add_field(
            name=f"{team.label}{score_suffix}",
            value=_team_block(team.players),
            inline=False,
        )

    queried: MatchPlayerRow | None = None
    key = detail.queried_username.casefold()
    for team in detail.teams:
        for player in team.players:
            if player.username.casefold() == key:
                queried = player
                break
        if queried:
            break

    if queried:
        embed.add_field(
            name="Votre performance",
            value=_player_detail_block(queried),
            inline=False,
        )

    embed.add_field(name="\u200b", value=_SECTION_SEPARATOR, inline=False)
    embed.set_footer(text="Tracker.gg · Marvel Rivals")
    if detail.played_at:
        embed.timestamp = detail.played_at
    return embed


def build_match_detail_unavailable_embed(
    entry: MatchListEntry,
    username: str,
) -> discord.Embed:
    return discord.Embed(
        title=f"Détail indisponible — {username}",
        description=(
            f"Impossible de charger le scoreboard pour **{username}**.\n"
            f"[Voir sur Tracker.gg]({entry.match_url})"
        ),
        color=discord.Color.orange(),
        url=entry.match_url,
    )
