import datetime

import discord

from config import DEFAULT_EMBED_COLOR
from tracker.models import PlayerProfile, StatValue

_SECTION_SEPARATOR = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"


def _add_section_separator(embed: discord.Embed) -> None:
    embed.add_field(name="\u200b", value=_SECTION_SEPARATOR, inline=False)


def _rating_chart_summary(profile: PlayerProfile) -> str:
    lines = [f"**{len(profile.rating_chart)}** parties classées"]
    delta = profile.rating_chart_delta
    if delta is not None:
        sign = "+" if delta > 0 else ""
        lines.append(f"Variation : **{sign}{delta} RS**")
    if profile.current_rank and profile.current_rank.rs:
        lines.append(f"RS actuel : **{profile.current_rank.rs}**")
    return "\n".join(lines)


def _percentile_suffix(stat: StatValue | None) -> str:
    if not stat or stat.percentile is None:
        return ""
    p = stat.percentile
    if p > 50:
        return f"\nTop {100.0 - p:.1f}%"
    return f"\nBottom {p:.1f}%"


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
        f"**{profile.matches_played}** matchs · **{profile.time_played}** de jeu"
    )
    if profile.season_name:
        summary += f"\nSaison : **{profile.season_name}**"
    embed.description = summary

    if profile.kda:
        embed.add_field(
            name="KDA Ratio",
            value=f"**{profile.kda.display}**{_percentile_suffix(profile.kda)}",
            inline=True,
        )
    if profile.win_pct:
        embed.add_field(
            name="Win %",
            value=f"**{profile.win_pct.display}**{_percentile_suffix(profile.win_pct)}",
            inline=True,
        )
    if profile.wins:
        embed.add_field(
            name="Wins",
            value=f"**{profile.wins.display}**{_percentile_suffix(profile.wins)}",
            inline=True,
        )

    rank_parts = []
    if profile.current_rank:
        rs = profile.current_rank.rs
        rank_parts.append(
            f"**Rang actuel** — {profile.current_rank.tier_name}"
            + (f" · {rs} RS" if rs else "")
        )
    if profile.season_peak:
        rank_parts.append(
            f"**Peak saison** — {profile.season_peak.tier_name}"
            + (f" · {profile.season_peak.rs} RS" if profile.season_peak.rs else "")
        )
    if profile.lifetime_peak:
        season = (
            f" // {profile.lifetime_peak.season_label}"
            if profile.lifetime_peak.season_label
            else ""
        )
        rank_parts.append(
            f"**All-time best** — {profile.lifetime_peak.tier_name}{season}"
            + (
                f" · {profile.lifetime_peak.rs} RS"
                if profile.lifetime_peak.rs
                else ""
            )
        )
    if rank_parts:
        _add_section_separator(embed)
        embed.add_field(name="Rang", value="\n".join(rank_parts), inline=False)

    if profile.rating_chart:
        _add_section_separator(embed)
        embed.add_field(
            name="Évolution du rating (parties classées)",
            value=_rating_chart_summary(profile),
            inline=False,
        )
        embed.set_image(url="attachment://rating_chart.png")

    if profile.season_peaks:
        peaks_text = " · ".join(
            f"{p.season_label} {p.tier_short}"
            for p in profile.season_peaks
            if p.season_label
        )
        if peaks_text:
            embed.add_field(
                name="Rangs précédents",
                value=peaks_text,
                inline=False,
            )

    detail_lines = []
    if profile.mvp_pct:
        detail_lines.append(f"MVP % · **{profile.mvp_pct.display}**")
    if profile.kd_ratio:
        detail_lines.append(f"K/D · **{profile.kd_ratio}**")
    if profile.kills:
        detail_lines.append(f"Kills · **{profile.kills}**")
    if profile.deaths:
        detail_lines.append(f"Deaths · **{profile.deaths}**")
    if profile.assists:
        detail_lines.append(f"Assists · **{profile.assists}**")
    if profile.last_kills:
        detail_lines.append(f"Last Kills · **{profile.last_kills}**")
    if profile.svp_pct:
        detail_lines.append(f"SVP % · **{profile.svp_pct}**")
    if profile.damage:
        detail_lines.append(f"Damage · **{profile.damage}**")
    if profile.healing:
        detail_lines.append(f"Healing · **{profile.healing}**")
    if profile.damage_blocked:
        detail_lines.append(f"Damage Blocked · **{profile.damage_blocked}**")
    if profile.max_kill_streak:
        detail_lines.append(f"Max Kill Streak · **{profile.max_kill_streak}**")
    if profile.mvps is not None:
        detail_lines.append(f"MVPs · **{profile.mvps}**")
    if profile.svps:
        svp_suffix = _percentile_suffix(profile.svps)
        detail_lines.append(f"SVPs · **{profile.svps.display}**{svp_suffix}")

    if detail_lines:
        _add_section_separator(embed)
        embed.add_field(
            name="Statistiques détaillées",
            value="\n".join(detail_lines),
            inline=False,
        )

    if profile.roles:
        _add_section_separator(embed)
        roles_text = "\n\n".join(
            f"**{r.name}** — WR **{r.win_pct}** ({r.wins} wins)\n"
            f"KDA **{r.kda}** · {r.kills} / {r.deaths} / {r.assists}"
            for r in profile.roles
        )
        embed.add_field(name="Rôles", value=roles_text, inline=False)

    if profile.top_heroes:
        _add_section_separator(embed)
        heroes_text = "\n\n".join(
            f"**{h.name}** — WR **{h.win_pct}** ({h.record})\n"
            f"KDA **{h.kda}** · {h.kills} / {h.deaths} / {h.assists}"
            for h in profile.top_heroes
        )
        embed.add_field(name="Top héros", value=heroes_text, inline=False)

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
