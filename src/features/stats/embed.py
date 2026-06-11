import datetime

import discord

from config import DEFAULT_EMBED_COLOR
from tracker.models import HeroStats, PlayerProfile, RankInfo, RoleStats, StatValue

_BLANK = "\u200b"
_SECTION_SEPARATOR = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


def _add_section_separator(embed: discord.Embed) -> None:
    embed.add_field(name=_BLANK, value=_SECTION_SEPARATOR, inline=False)


_ROLE_EMOJIS = {
    "vanguard": "🛡️",
    "duelist": "⚔️",
    "strategist": "💉",
}

_MEDALS = ["🥇", "🥈", "🥉"]


def _role_emoji(name: str) -> str:
    return _ROLE_EMOJIS.get(name.strip().lower(), "🎮")


def _percentile_badge(stat: StatValue | None) -> str:
    """Petit badge de percentile sur la même ligne (ex : `Top 4.2%`)."""
    if not stat or stat.percentile is None:
        return ""
    p = stat.percentile
    if p > 50:
        return f"\n-# Top {100.0 - p:.1f}%"
    return f"\n-# Bottom {p:.1f}%"


def _rank_line(rank: RankInfo, *, with_season: bool = False) -> str:
    parts = [f"**{rank.tier_name}**"]
    if rank.rs:
        parts.append(f"{rank.rs} RS")
    line = " · ".join(parts)
    if with_season and rank.season_label:
        line += f"\n-# {rank.season_label}"
    return line


def _rating_chart_summary(profile: PlayerProfile) -> str:
    parts = [f"📈 **{len(profile.rating_chart)}** parties classées"]
    delta = profile.rating_chart_delta
    if delta is not None:
        if delta > 0:
            parts.append(f"🔺 **+{delta} RS**")
        elif delta < 0:
            parts.append(f"🔻 **{delta} RS**")
        else:
            parts.append("➖ **±0 RS**")
    if profile.current_rank and profile.current_rank.rs:
        parts.append(f"🎯 **{profile.current_rank.rs} RS** actuels")
    return " · ".join(parts)


def _role_field_value(role: RoleStats) -> str:
    return (
        f"🏆 WR **{role.win_pct}** · {role.wins} wins\n"
        f"⚖️ KDA **{role.kda}**\n"
        f"-# {role.kills} / {role.deaths} / {role.assists}"
    )


def _hero_field_value(hero: HeroStats) -> str:
    return (
        f"🏆 WR **{hero.win_pct}** · {hero.record}\n"
        f"⚖️ KDA **{hero.kda}**\n"
        f"-# {hero.kills} / {hero.deaths} / {hero.assists}"
    )


def _pad_inline_row(embed: discord.Embed, used: int) -> None:
    """Complète une rangée inline pour garder l'alignement en colonnes de 3."""
    for _ in range((3 - used % 3) % 3):
        embed.add_field(name=_BLANK, value=_BLANK, inline=True)


def build_stats_embed(profile: PlayerProfile) -> discord.Embed:
    color = profile.embed_color or DEFAULT_EMBED_COLOR
    embed = discord.Embed(
        title=f"{profile.username} — Marvel Rivals Overview",
        url=profile.profile_url,
        color=color,
    )

    author_icon = None
    if profile.current_rank and profile.current_rank.icon_url:
        author_icon = profile.current_rank.icon_url
    elif profile.avatar_url:
        author_icon = profile.avatar_url

    if author_icon:
        embed.set_author(name=profile.username, icon_url=author_icon)
    else:
        embed.set_author(name=profile.username)

    if profile.avatar_url:
        embed.set_thumbnail(url=profile.avatar_url)

    summary = (
        f"🎮 **{profile.matches_played}** matchs · "
        f"⏱️ **{profile.time_played}** de jeu"
    )
    if profile.season_name:
        summary += f"\n-# {profile.season_name}"
    embed.description = summary

    # ── Performance clé (3 colonnes) ──
    key_stats = 0
    if profile.kda:
        embed.add_field(
            name="⚖️ KDA Ratio",
            value=f"**{profile.kda.display}**{_percentile_badge(profile.kda)}",
            inline=True,
        )
        key_stats += 1
    if profile.win_pct:
        embed.add_field(
            name="🏆 Win %",
            value=f"**{profile.win_pct.display}**{_percentile_badge(profile.win_pct)}",
            inline=True,
        )
        key_stats += 1
    if profile.wins:
        embed.add_field(
            name="✅ Wins",
            value=f"**{profile.wins.display}**{_percentile_badge(profile.wins)}",
            inline=True,
        )
        key_stats += 1
    _pad_inline_row(embed, key_stats)

    # ── Rang (3 colonnes) ──
    has_rank_section = bool(
        profile.current_rank
        or profile.season_peak
        or profile.lifetime_peak
        or profile.season_peaks
    )
    if has_rank_section:
        _add_section_separator(embed)

    rank_fields = 0
    if profile.current_rank:
        embed.add_field(
            name="🏅 Rang actuel",
            value=_rank_line(profile.current_rank),
            inline=True,
        )
        rank_fields += 1
    if profile.season_peak:
        embed.add_field(
            name="📈 Peak saison",
            value=_rank_line(profile.season_peak),
            inline=True,
        )
        rank_fields += 1
    if profile.lifetime_peak:
        embed.add_field(
            name="👑 All-time best",
            value=_rank_line(profile.lifetime_peak, with_season=True),
            inline=True,
        )
        rank_fields += 1
    _pad_inline_row(embed, rank_fields)

    if profile.season_peaks:
        peaks_text = " · ".join(
            f"{p.season_label} **{p.tier_short}**"
            for p in profile.season_peaks
            if p.season_label
        )
        if peaks_text:
            embed.add_field(
                name="🗓️ Rangs précédents",
                value=f"-# {peaks_text}",
                inline=False,
            )

    # ── Combat (colonnes thématiques) ──
    combat_lines = []
    if profile.kd_ratio:
        combat_lines.append(f"K/D **{profile.kd_ratio}**")
    if profile.kills:
        combat_lines.append(f"Kills **{profile.kills}**")
    if profile.deaths:
        combat_lines.append(f"Deaths **{profile.deaths}**")
    if profile.assists:
        combat_lines.append(f"Assists **{profile.assists}**")
    if profile.last_kills:
        combat_lines.append(f"Last Kills **{profile.last_kills}**")
    if profile.max_kill_streak:
        combat_lines.append(f"Kill Streak **{profile.max_kill_streak}**")

    impact_lines = []
    if profile.damage:
        impact_lines.append(f"Damage **{profile.damage}**")
    if profile.healing:
        impact_lines.append(f"Healing **{profile.healing}**")
    if profile.damage_blocked:
        impact_lines.append(f"Blocked **{profile.damage_blocked}**")

    honors_lines = []
    if profile.mvps is not None:
        honors_lines.append(f"MVPs **{profile.mvps}**")
    if profile.mvp_pct:
        honors_lines.append(f"MVP % **{profile.mvp_pct.display}**")
    if profile.svps:
        honors_lines.append(f"SVPs **{profile.svps.display}**")
    if profile.svp_pct:
        honors_lines.append(f"SVP % **{profile.svp_pct}**")

    has_detail_section = bool(combat_lines or impact_lines or honors_lines)
    if has_detail_section:
        _add_section_separator(embed)

    detail_fields = 0
    if combat_lines:
        embed.add_field(name="⚔️ Combat", value="\n".join(combat_lines), inline=True)
        detail_fields += 1
    if impact_lines:
        embed.add_field(name="💥 Impact", value="\n".join(impact_lines), inline=True)
        detail_fields += 1
    if honors_lines:
        embed.add_field(
            name="🌟 Distinctions", value="\n".join(honors_lines), inline=True
        )
        detail_fields += 1
    _pad_inline_row(embed, detail_fields)

    # ── Rôles (côte à côte) ──
    if profile.roles:
        _add_section_separator(embed)
        for role in profile.roles[:3]:
            embed.add_field(
                name=f"{_role_emoji(role.name)} {role.name}",
                value=_role_field_value(role),
                inline=True,
            )
        _pad_inline_row(embed, min(len(profile.roles), 3))

    # ── Top héros (côte à côte, avec podium) ──
    if profile.top_heroes:
        _add_section_separator(embed)
        for i, hero in enumerate(profile.top_heroes[:3]):
            medal = _MEDALS[i] if i < len(_MEDALS) else "🎖️"
            embed.add_field(
                name=f"{medal} {hero.name}",
                value=_hero_field_value(hero),
                inline=True,
            )
        _pad_inline_row(embed, min(len(profile.top_heroes), 3))

    # ── Courbe de rating ──
    if profile.rating_chart:
        _add_section_separator(embed)
        embed.add_field(
            name="📊 Évolution du rating",
            value=_rating_chart_summary(profile),
            inline=False,
        )
        embed.set_image(url="attachment://rating_chart.png")

    footer = "Tracker.gg · Marvel Rivals"
    if profile.season_name:
        footer = f"{profile.season_name} · {footer}"
    embed.set_footer(text=footer)
    embed.timestamp = datetime.datetime.now(datetime.timezone.utc)

    return embed


def build_error_embed(message: str) -> discord.Embed:
    return discord.Embed(
        title="Erreur",
        description=message,
        color=discord.Color.red(),
    )
