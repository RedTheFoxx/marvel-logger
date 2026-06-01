import datetime
import re
from typing import Any

from marvel_logger.config import (
    RATING_GRAPH_MATCH_LIMIT,
    RATING_GRAPH_MATCH_TARGET,
    TRACKER_MATCH_URL,
)
from marvel_logger.tracker.models import (
    MatchHero,
    MatchListEntry,
    MatchOutcome,
    MatchRankSnapshot,
    PlayerProfile,
    RatingChartPoint,
)
from marvel_logger.tracker.parser import _display

_RANKED_MODES = frozenset({"competitive", "ranked"})


def _parse_timestamp(value: str | None) -> datetime.datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=datetime.timezone.utc)
        return parsed
    except ValueError:
        return None


def _parse_rs_int(rs: str | None) -> int | None:
    if not rs:
        return None
    cleaned = re.sub(r"[^\d-]", "", rs)
    if not cleaned or cleaned == "-":
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


def _parse_delta_int(delta_display: str | None, delta_value: Any = None) -> int | None:
    if delta_value is not None:
        try:
            return int(round(float(delta_value)))
        except (TypeError, ValueError):
            pass
    if not delta_display:
        return None
    cleaned = delta_display.strip().replace(",", "")
    if not cleaned:
        return None
    try:
        return int(round(float(cleaned)))
    except ValueError:
        return None


def _normalize_outcome(result: str | None) -> MatchOutcome | None:
    if not result:
        return None
    key = result.strip().lower()
    if key in ("win", "w"):
        return "win"
    if key in ("loss", "lose", "l"):
        return "loss"
    return None


def _rank_from_match_stats(stats: dict[str, Any]) -> MatchRankSnapshot | None:
    ranked = stats.get("ranked")
    if not ranked:
        return None
    meta = ranked.get("metadata") or {}
    tier = meta.get("tierName") or ranked.get("displayName") or ""
    if not tier:
        return None
    rs = _display(ranked) or ""
    delta_stat = stats.get("rankedDelta")
    delta_display = _display(delta_stat)
    delta_value = delta_stat.get("value") if delta_stat else None
    delta_str: str | None = None
    if delta_display is not None:
        delta_int = _parse_delta_int(delta_display, delta_value)
        if delta_int is not None:
            sign = "+" if delta_int > 0 else ""
            delta_str = f"{sign}{delta_int}"
    return MatchRankSnapshot(
        tier_name=tier,
        tier_short=meta.get("tierShortName") or tier,
        rs=rs,
        rs_delta=delta_str,
        icon_url=meta.get("iconUrl"),
    )


def _find_player_segment(
    segments: list[dict[str, Any]], username: str
) -> dict[str, Any] | None:
    key = username.casefold()
    for seg in segments:
        if seg.get("type") != "overview":
            continue
        meta = seg.get("metadata") or {}
        platform = meta.get("platformInfo") or {}
        handle = platform.get("platformUserHandle") or platform.get(
            "platformUserIdentifier"
        )
        if handle and str(handle).casefold() == key:
            return seg
    return None


def _format_score(scores: list[Any] | None) -> str:
    if not scores or len(scores) < 2:
        return "—"
    return f"{scores[0]} : {scores[1]}"


def parse_recent_matches(
    raw: dict[str, Any],
    username: str,
    season_id: int,
    limit: int | None = None,
) -> list[MatchListEntry]:
    matches_raw = (raw.get("data") or {}).get("matches") or []
    if not isinstance(matches_raw, list):
        return []

    entries: list[MatchListEntry] = []
    for match in matches_raw:
        attrs = match.get("attributes") or {}
        meta = match.get("metadata") or {}
        mode = (attrs.get("mode") or "").lower()
        if mode not in _RANKED_MODES and not meta.get("isRanked"):
            continue

        segment = _find_player_segment(match.get("segments") or [], username)
        if not segment:
            continue

        seg_meta = segment.get("metadata") or {}
        stats = segment.get("stats") or {}
        rank = _rank_from_match_stats(stats)
        if not rank or _parse_rs_int(rank.rs) is None:
            continue

        match_id = attrs.get("id") or ""
        if not match_id:
            continue

        heroes = seg_meta.get("heroes") or []
        hero_name = "Unknown"
        hero_url: str | None = None
        if heroes:
            first = heroes[0]
            hero_name = first.get("name") or hero_name
            hero_url = first.get("imageUrl")

        outcome = _normalize_outcome(seg_meta.get("result"))
        if outcome is None:
            outcome_meta = seg_meta.get("outcome") or {}
            outcome = _normalize_outcome(outcome_meta.get("result"))

        if outcome is None:
            continue

        played_at = _parse_timestamp(meta.get("timestamp"))
        entries.append(
            MatchListEntry(
                match_id=match_id,
                match_url=TRACKER_MATCH_URL.format(match_id=match_id),
                outcome=outcome,
                played_ago="",
                game_mode=meta.get("modeName") or attrs.get("mode") or "Competitive",
                map_name=meta.get("mapName") or "—",
                map_location=meta.get("mapModeName") or "",
                score=_format_score(meta.get("scores")),
                hero=MatchHero(name=hero_name, image_url=hero_url),
                rank=rank,
                kills=_display(stats.get("kills")) or "0",
                deaths=_display(stats.get("deaths")) or "0",
                assists=_display(stats.get("assists")) or "0",
                kda_ratio=_display(stats.get("kdaRatio")) or "—",
                played_at=played_at,
                season_id=season_id,
            )
        )

    entries.sort(
        key=lambda e: e.played_at or datetime.datetime.min.replace(
            tzinfo=datetime.timezone.utc
        )
    )
    if limit is not None and limit > 0 and len(entries) > limit:
        entries = entries[-limit:]
    return entries


def build_rating_chart(matches: list[MatchListEntry]) -> list[RatingChartPoint]:
    points: list[RatingChartPoint] = []
    for entry in matches:
        rs = _parse_rs_int(entry.rank.rs)
        if rs is None:
            continue
        delta_stat_val = None
        if entry.rank.rs_delta:
            delta_stat_val = _parse_delta_int(entry.rank.rs_delta)
        points.append(
            RatingChartPoint(
                rs=rs,
                rs_delta=delta_stat_val,
                outcome=entry.outcome,
                played_at=entry.played_at,
                match_id=entry.match_id,
            )
        )

    caps = [v for v in (RATING_GRAPH_MATCH_TARGET, RATING_GRAPH_MATCH_LIMIT) if v > 0]
    if caps:
        cap = min(caps)
        if len(points) > cap:
            points = points[-cap:]

    return points


def _chart_delta_total(points: list[RatingChartPoint]) -> int | None:
    deltas = [p.rs_delta for p in points if p.rs_delta is not None]
    if not deltas:
        if len(points) >= 2:
            return points[-1].rs - points[0].rs
        return None
    return sum(deltas)


def apply_rating_chart(
    profile: PlayerProfile,
    matches_raw: dict[str, Any] | None,
) -> None:
    if not matches_raw:
        profile.rating_chart = []
        profile.rating_chart_delta = None
        return

    entries = parse_recent_matches(
        matches_raw, profile.username, profile.season_id
    )
    profile.rating_chart = build_rating_chart(entries)
    profile.rating_chart_delta = _chart_delta_total(profile.rating_chart)
