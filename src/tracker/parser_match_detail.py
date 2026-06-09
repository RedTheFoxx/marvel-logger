from __future__ import annotations

from typing import Any

from config import TRACKER_MATCH_URL
from tracker.models import (
    MatchDetail,
    MatchHero,
    MatchOutcome,
    MatchPlayerRow,
    MatchTeam,
)
from tracker.parser import _display
from tracker.parser_matches import (
    _format_score,
    _normalize_outcome,
    _parse_timestamp,
    _rank_from_match_stats,
)

_PLAYER_SEGMENT_TYPES = frozenset({"player", "overview"})


def _match_root(raw: dict[str, Any]) -> dict[str, Any] | None:
    data = raw.get("data") or {}
    if isinstance(data.get("match"), dict):
        return data["match"]
    if data.get("attributes") or data.get("segments"):
        return data
    if raw.get("attributes") or raw.get("segments"):
        return raw
    return None


def _player_username(segment: dict[str, Any]) -> str | None:
    meta = segment.get("metadata") or {}
    platform = meta.get("platformInfo") or {}
    handle = platform.get("platformUserHandle") or platform.get(
        "platformUserIdentifier"
    )
    if handle:
        return str(handle)
    attrs = segment.get("attributes") or {}
    name = attrs.get("platformUserHandle") or attrs.get("platformUserIdentifier")
    return str(name) if name else None


def _team_key(segment: dict[str, Any]) -> str:
    meta = segment.get("metadata") or {}
    attrs = segment.get("attributes") or {}
    for key in ("teamId", "team", "side", "camp", "teamIndex"):
        val = meta.get(key)
        if val is None:
            val = attrs.get(key)
        if val is not None:
            return str(val)
    outcome = meta.get("outcome") or {}
    side = outcome.get("side") or outcome.get("team")
    if side is not None:
        return str(side)
    return "unknown"


def _parse_awards(meta: dict[str, Any]) -> tuple[bool, bool]:
    is_mvp = bool(meta.get("isMvp") or meta.get("mvp"))
    is_svp = bool(meta.get("isSvp") or meta.get("svp"))
    awards = meta.get("awards") or meta.get("badges") or []
    if isinstance(awards, list):
        for award in awards:
            label = str(award).lower() if not isinstance(award, dict) else str(
                award.get("name") or award.get("type") or ""
            ).lower()
            if "mvp" in label:
                is_mvp = True
            if "svp" in label:
                is_svp = True
    return is_mvp, is_svp


def _heroes_from_meta(meta: dict[str, Any]) -> list[MatchHero]:
    heroes_raw = meta.get("heroes") or []
    heroes: list[MatchHero] = []
    for hero in heroes_raw:
        if not isinstance(hero, dict):
            continue
        name = hero.get("name") or hero.get("heroName") or "Unknown"
        heroes.append(
            MatchHero(name=name, image_url=hero.get("imageUrl") or hero.get("image"))
        )
    return heroes


def _format_duration(meta: dict[str, Any]) -> str | None:
    display = meta.get("durationDisplay")
    if display:
        return str(display)
    raw = meta.get("duration")
    if raw is None:
        return None
    try:
        total = int(raw)
    except (TypeError, ValueError):
        return str(raw)
    minutes, seconds = divmod(total, 60)
    if minutes >= 60:
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"


def _solo_head_last(stats: dict[str, Any]) -> str | None:
    solo = _display(stats.get("soloKills"))
    head = _display(stats.get("headKills")) or _display(stats.get("headshots"))
    last = _display(stats.get("lastKills"))
    if solo or head or last:
        return f"{solo or '0'} / {head or '0'} / {last or '0'}"
    combined = _display(stats.get("soloHeadLastKills"))
    return combined


def _per_min(stat: dict[str, Any] | None) -> str | None:
    if not stat:
        return None
    meta = stat.get("metadata") or {}
    return meta.get("perMinuteDisplayValue") or meta.get("perMinuteValue")


def _parse_player_row(segment: dict[str, Any]) -> MatchPlayerRow | None:
    if segment.get("type") not in _PLAYER_SEGMENT_TYPES:
        return None
    if segment.get("metadata", {}).get("isBot"):
        return None
    username = _player_username(segment)
    if not username:
        return None

    meta = segment.get("metadata") or {}
    stats = segment.get("stats") or {}
    is_mvp, is_svp = _parse_awards(meta)

    outcome = _normalize_outcome(meta.get("result"))
    if outcome is None:
        outcome_meta = meta.get("outcome") or {}
        outcome = _normalize_outcome(outcome_meta.get("result"))

    damage_stat = (
        stats.get("totalHeroDamage")
        or stats.get("damageDone")
        or stats.get("damage")
    )
    blocked_stat = stats.get("totalDamageTaken") or stats.get("damageBlocked")
    healing_stat = stats.get("totalHeroHeal") or stats.get("healingDone")
    accuracy_stat = stats.get("sessionHitRate") or stats.get("accuracy")

    damage_per_min = _display(stats.get("totalHeroDamagePerMinute"))
    blocked_per_min = _display(stats.get("totalDamageTakenPerMinute"))
    healing_per_min = _display(stats.get("totalHeroHealPerMinute"))

    accuracy_display: str | None = None
    if accuracy_stat:
        acc = _display(accuracy_stat)
        if acc and "%" not in acc:
            try:
                pct = float(accuracy_stat.get("value", 0)) * 100
                acc = f"{pct:.1f}%"
            except (TypeError, ValueError):
                pass
        hits = _display(stats.get("shotsHit"))
        shots = _display(stats.get("shotsFired"))
        if acc and hits and shots:
            accuracy_display = f"{acc} ({hits} // {shots})"
        else:
            accuracy_display = acc

    return MatchPlayerRow(
        username=username,
        is_mvp=is_mvp,
        is_svp=is_svp,
        heroes=_heroes_from_meta(meta),
        rank=_rank_from_match_stats(stats),
        kda_ratio=_display(stats.get("kdaRatio")) or "—",
        kills=_display(stats.get("kills")) or "0",
        deaths=_display(stats.get("deaths")) or "0",
        assists=_display(stats.get("assists")) or "0",
        solo_head_last=_solo_head_last(stats),
        damage=_display(damage_stat),
        damage_per_min=damage_per_min or _per_min(damage_stat),
        blocked=_display(blocked_stat),
        blocked_per_min=blocked_per_min or _per_min(blocked_stat),
        healing=_display(healing_stat),
        healing_per_min=healing_per_min or _per_min(healing_stat),
        accuracy=accuracy_display,
        outcome=outcome,
    )


def _player_roster_sort_key(player: MatchPlayerRow) -> tuple[int, int]:
    if player.is_mvp:
        priority = 0
    elif player.is_svp:
        priority = 1
    else:
        priority = 2
    kills_raw = player.kills.replace(",", "")
    kills = -int(kills_raw) if kills_raw.isdigit() else 0
    return priority, kills


def _team_score_from_meta(
    match_meta: dict[str, Any], team_key: str, won: bool
) -> int | None:
    scores = match_meta.get("scores")
    if not isinstance(scores, list) or len(scores) < 2:
        return None
    try:
        if team_key in ("0", "1", "team0", "team1"):
            idx = int(team_key) if team_key.isdigit() else 0
            if idx < len(scores):
                return int(scores[idx])
        if won:
            return max(int(s) for s in scores)
        return min(int(s) for s in scores)
    except (TypeError, ValueError):
        return None


def _build_teams(
    players: list[tuple[str, MatchPlayerRow]],
    match_meta: dict[str, Any],
    scores_display: str,
) -> list[MatchTeam]:
    winning_team_id = match_meta.get("winningTeamId")
    by_team: dict[str, list[MatchPlayerRow]] = {}
    for team_key, row in players:
        by_team.setdefault(team_key, []).append(row)

    if len(by_team) == 1 and "unknown" in by_team:
        all_rows = by_team["unknown"]
        winners = [r for r in all_rows if r.outcome == "win"]
        losers = [r for r in all_rows if r.outcome == "loss"]
        if winners and losers:
            by_team = {"win": winners, "loss": losers}

    teams: list[MatchTeam] = []
    for team_key, roster in by_team.items():
        won = any(p.outcome == "win" for p in roster)
        lost = any(p.outcome == "loss" for p in roster)
        if winning_team_id is not None and str(team_key) == str(winning_team_id):
            label = "Équipe gagnante"
            won = True
        elif winning_team_id is not None and team_key not in ("win", "loss", "unknown"):
            label = "Équipe perdante"
            won = False
        elif won:
            label = "Équipe gagnante"
        elif lost:
            label = "Équipe perdante"
        else:
            label = f"Équipe {team_key}"

        roster.sort(key=_player_roster_sort_key)
        teams.append(
            MatchTeam(
                label=label,
                won=won and not lost,
                score=_team_score_from_meta(match_meta, team_key, won),
                players=roster,
            )
        )

    teams.sort(key=lambda t: (not t.won, t.label))
    if len(teams) == 2 and teams[0].won == teams[1].won:
        parts = scores_display.split(":")
        if len(parts) == 2:
            try:
                teams[0].score = int(parts[0].strip())
                teams[1].score = int(parts[1].strip())
            except ValueError:
                pass
    return teams


def parse_match_detail(raw: dict[str, Any], queried_username: str) -> MatchDetail:
    match = _match_root(raw)
    if not match:
        raise ValueError("Réponse match Tracker.gg invalide.")

    attrs = match.get("attributes") or {}
    meta = match.get("metadata") or {}
    match_id = attrs.get("id") or ""
    scores_display = _format_score(meta.get("scores"))

    players: list[tuple[str, MatchPlayerRow]] = []
    for segment in match.get("segments") or []:
        row = _parse_player_row(segment)
        if row:
            players.append((_team_key(segment), row))

    teams = _build_teams(players, meta, scores_display)
    queried_outcome: MatchOutcome | None = None
    key = queried_username.casefold()
    for team in teams:
        for player in team.players:
            if player.username.casefold() == key:
                queried_outcome = player.outcome
                break

    duration = _format_duration(meta)

    return MatchDetail(
        match_id=match_id,
        match_url=TRACKER_MATCH_URL.format(match_id=match_id) if match_id else "",
        game_mode=meta.get("modeName") or attrs.get("mode") or "Competitive",
        map_name=meta.get("mapName") or "—",
        map_location=meta.get("mapModeName") or "",
        score=scores_display,
        duration=duration,
        played_at=_parse_timestamp(meta.get("timestamp")),
        teams=teams,
        queried_username=queried_username,
        queried_outcome=queried_outcome,
    )
