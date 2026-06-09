from typing import Any

from config import TRACKER_PROFILE_URL
from tracker.models import (
    HeroStats,
    PlayerProfile,
    RankInfo,
    RoleStats,
    StatValue,
)


def _segment(
    segments: list[dict[str, Any]],
    seg_type: str,
    season: int,
    mode: str = "all",
) -> dict[str, Any] | None:
    for seg in segments:
        attrs = seg.get("attributes") or {}
        if seg.get("type") != seg_type:
            continue
        if seg_type == "ranked-peaks":
            return seg
        if attrs.get("season") == season and attrs.get("mode", "all") == mode:
            return seg
    return None


def _stat(segment: dict[str, Any] | None, key: str) -> dict[str, Any] | None:
    if not segment:
        return None
    return (segment.get("stats") or {}).get(key)


def _display(stat: dict[str, Any] | None) -> str | None:
    if not stat:
        return None
    return stat.get("displayValue") or str(stat.get("value", ""))


def _percentile(stat: dict[str, Any] | None) -> float | None:
    if not stat:
        return None
    p = stat.get("percentile")
    return float(p) if p is not None else None


def _stat_value(stat: dict[str, Any] | None) -> StatValue | None:
    if not stat:
        return None
    display = _display(stat)
    if not display:
        return None
    return StatValue(display=display, percentile=_percentile(stat))


def _rank_from_stat(stat: dict[str, Any] | None, season_label: str | None = None) -> RankInfo | None:
    if not stat:
        return None
    meta = stat.get("metadata") or {}
    tier = meta.get("tierName") or stat.get("displayName") or ""
    if not tier:
        return None
    rs = _display(stat) or ""
    return RankInfo(
        tier_name=tier,
        tier_short=meta.get("tierShortName") or tier,
        rs=rs,
        icon_url=meta.get("iconUrl"),
        color=meta.get("color"),
        season_label=season_label
        or meta.get("seasonShortName")
        or meta.get("seasonName"),
    )


def _rank_from_peak_entry(entry: dict[str, Any]) -> RankInfo | None:
    meta = entry.get("metadata") or {}
    tier = meta.get("tierName")
    if not tier:
        return None
    value = entry.get("value")
    rs = f"{int(value):,}" if isinstance(value, (int, float)) else str(value or "")
    return RankInfo(
        tier_name=tier,
        tier_short=meta.get("tierShortName") or tier,
        rs=rs,
        icon_url=meta.get("iconUrl"),
        color=meta.get("color"),
        season_label=meta.get("seasonShortName") or meta.get("seasonName"),
    )


def _combat_line(segment: dict[str, Any] | None) -> tuple[str, str, str]:
    kills = _display(_stat(segment, "kills")) or "0"
    deaths = _display(_stat(segment, "deaths")) or "0"
    assists = _display(_stat(segment, "assists")) or "0"
    return kills, deaths, assists


def _hero_record(segment: dict[str, Any] | None) -> str:
    wins_stat = _stat(segment, "matchesWon")
    played_stat = _stat(segment, "matchesPlayed")
    if not wins_stat or not played_stat:
        return "—"
    wins = int(wins_stat.get("value") or 0)
    played = int(round(float(played_stat.get("value") or 0)))
    losses = max(played - wins, 0)
    return f"{wins}W / {losses}L"


def parse_profile(raw: dict[str, Any], username: str) -> PlayerProfile:
    data = raw["data"]
    metadata = data.get("metadata") or {}
    season_id = int(metadata.get("currentSeason") or metadata.get("defaultSeason") or 0)

    season_name = ""
    for s in metadata.get("seasons") or []:
        if s.get("id") == season_id:
            season_name = s.get("name") or s.get("shortName") or ""
            break

    segments = data.get("segments") or []
    overview = _segment(segments, "overview", season_id)
    peaks_seg = _segment(segments, "ranked-peaks", season_id)

    platform = data.get("platformInfo") or {}
    handle = platform.get("platformUserHandle") or username

    current_rank = _rank_from_stat(_stat(overview, "ranked"))
    season_peak = _rank_from_stat(_stat(overview, "peakRanked"))
    lifetime_stat = _stat(peaks_seg, "lifetimePeakRanked")
    lifetime_meta = (lifetime_stat or {}).get("metadata") or {}
    lifetime_peak = _rank_from_stat(
        lifetime_stat,
        season_label=lifetime_meta.get("seasonShortName")
        or lifetime_meta.get("seasonName"),
    )

    season_peaks: list[RankInfo] = []
    peak_tiers_stat = _stat(peaks_seg, "peakTiers")
    if peak_tiers_stat:
        tiers = peak_tiers_stat.get("value") or []
        if isinstance(tiers, list):
            for entry in tiers[:4]:
                rank = _rank_from_peak_entry(entry)
                if rank:
                    season_peaks.append(rank)

    roles: list[RoleStats] = []
    for seg in segments:
        if seg.get("type") != "hero-role":
            continue
        attrs = seg.get("attributes") or {}
        if attrs.get("season") != season_id or attrs.get("mode", "all") != "all":
            continue
        meta = seg.get("metadata") or {}
        name = meta.get("name") or attrs.get("roleId", "Unknown")
        kills, deaths, assists = _combat_line(seg)
        roles.append(
            RoleStats(
                name=name,
                win_pct=_display(_stat(seg, "matchesWinPct")) or "—",
                wins=_display(_stat(seg, "matchesWon")) or "—",
                kda=_display(_stat(seg, "kdaRatio")) or "—",
                kills=kills,
                deaths=deaths,
                assists=assists,
            )
        )

    heroes_raw: list[tuple[float, HeroStats]] = []
    for seg in segments:
        if seg.get("type") != "hero":
            continue
        attrs = seg.get("attributes") or {}
        if attrs.get("season") != season_id or attrs.get("mode", "all") != "all":
            continue
        meta = seg.get("metadata") or {}
        name = meta.get("name")
        if not name:
            continue
        played_stat = _stat(seg, "matchesPlayed")
        played = float(played_stat.get("value") or 0) if played_stat else 0.0
        if played < 0.5:
            continue
        kills, deaths, assists = _combat_line(seg)
        heroes_raw.append(
            (
                played,
                HeroStats(
                    name=name,
                    image_url=meta.get("imageUrl"),
                    win_pct=_display(_stat(seg, "matchesWinPct")) or "—",
                    record=_hero_record(seg),
                    kda=_display(_stat(seg, "kdaRatio")) or "—",
                    kills=kills,
                    deaths=deaths,
                    assists=assists,
                    matches_played=played,
                ),
            )
        )

    heroes_raw.sort(key=lambda x: x[0], reverse=True)
    top_heroes = [h for _, h in heroes_raw[:3]]

    embed_color = None
    if current_rank and current_rank.color:
        try:
            embed_color = int(current_rank.color.lstrip("#"), 16)
        except ValueError:
            embed_color = None

    profile_url = TRACKER_PROFILE_URL.format(username=handle) + f"?season={season_id}"

    return PlayerProfile(
        username=handle,
        avatar_url=platform.get("avatarUrl"),
        profile_url=profile_url,
        season_id=season_id,
        season_name=season_name,
        matches_played=_display(_stat(overview, "matchesPlayed")) or "—",
        time_played=_display(_stat(overview, "timePlayed")) or "—",
        current_rank=current_rank,
        season_peak=season_peak,
        lifetime_peak=lifetime_peak,
        season_peaks=season_peaks,
        kda=_stat_value(_stat(overview, "kdaRatio")),
        win_pct=_stat_value(_stat(overview, "matchesWinPct")),
        wins=_stat_value(_stat(overview, "matchesWon")),
        mvp_pct=_stat_value(_stat(overview, "totalMvpPct")),
        kd_ratio=_display(_stat(overview, "kdRatio")),
        kills=_display(_stat(overview, "kills")),
        deaths=_display(_stat(overview, "deaths")),
        assists=_display(_stat(overview, "assists")),
        last_kills=_display(_stat(overview, "lastKills")),
        svp_pct=_display(_stat(overview, "totalSvpPct")),
        damage=_display(_stat(overview, "totalHeroDamage")),
        healing=_display(_stat(overview, "totalHeroHeal")),
        damage_blocked=_display(_stat(overview, "totalDamageTaken")),
        max_kill_streak=_display(_stat(overview, "maxSurvivalKills")),
        mvps=_display(_stat(overview, "totalMvp")),
        svps=_stat_value(_stat(overview, "totalSvp")),
        roles=roles,
        top_heroes=top_heroes,
        embed_color=embed_color,
    )
