import datetime
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class StatValue:
    display: str
    percentile: float | None = None


@dataclass
class RankInfo:
    tier_name: str
    tier_short: str
    rs: str
    icon_url: str | None = None
    color: str | None = None
    season_label: str | None = None


@dataclass
class RoleStats:
    name: str
    win_pct: str
    wins: str
    kda: str
    kills: str
    deaths: str
    assists: str


@dataclass
class HeroStats:
    name: str
    image_url: str | None
    win_pct: str
    record: str
    kda: str
    kills: str
    deaths: str
    assists: str
    matches_played: float = 0.0


MatchOutcome = Literal["win", "loss"]


@dataclass
class MatchHero:
    """Héros joué pendant le match (icône + nom)."""

    name: str
    image_url: str | None = None


@dataclass
class MatchRankSnapshot:
    """Rang du joueur au moment du match (liste ou détail)."""

    tier_name: str
    tier_short: str
    rs: str
    rs_delta: str | None = None
    icon_url: str | None = None


@dataclass
class RatingChartPoint:
    """Point RS après une partie classée (courbe d'évolution)."""

    rs: int
    rs_delta: int | None
    outcome: MatchOutcome | None
    played_at: datetime.datetime | None
    match_id: str


@dataclass
class MatchPlayerRow:
    """Joueur dans le scoreboard détaillé d'un match."""

    username: str
    is_mvp: bool = False
    is_svp: bool = False
    heroes: list[MatchHero] = field(default_factory=list)
    rank: MatchRankSnapshot | None = None
    kda_ratio: str = "—"
    kills: str = "0"
    deaths: str = "0"
    assists: str = "0"
    solo_head_last: str | None = None
    damage: str | None = None
    damage_per_min: str | None = None
    blocked: str | None = None
    blocked_per_min: str | None = None
    healing: str | None = None
    healing_per_min: str | None = None
    accuracy: str | None = None
    outcome: MatchOutcome | None = None


@dataclass
class MatchTeam:
    """Équipe dans un match (jusqu'à 6 joueurs)."""

    label: str
    won: bool
    score: int | None = None
    players: list[MatchPlayerRow] = field(default_factory=list)


@dataclass
class MatchDetail:
    """Détail complet d'un match (scoreboard des deux équipes)."""

    match_id: str
    match_url: str
    game_mode: str
    map_name: str
    map_location: str
    score: str
    duration: str | None
    played_at: datetime.datetime | None
    teams: list[MatchTeam]
    queried_username: str
    queried_outcome: MatchOutcome | None = None


@dataclass
class MatchListEntry:
    """Résumé d'un match tel qu'affiché dans la liste (/matches?season=…)."""

    match_id: str
    match_url: str
    outcome: MatchOutcome
    played_ago: str
    game_mode: str
    map_name: str
    map_location: str
    score: str
    hero: MatchHero
    rank: MatchRankSnapshot
    kills: str
    deaths: str
    assists: str
    kda_ratio: str
    played_at: datetime.datetime | None = None
    season_id: int | None = None


@dataclass
class MatchBundle:
    """Résultat de fetch_match_bundle : aperçu + détails préchargés."""

    username: str
    season_id: int
    entries: list[MatchListEntry]
    details: dict[str, MatchDetail]
    details_raw: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class PlayerProfile:
    username: str
    avatar_url: str | None
    profile_url: str
    season_id: int
    season_name: str
    matches_played: str
    time_played: str
    current_rank: RankInfo | None
    season_peak: RankInfo | None
    lifetime_peak: RankInfo | None
    season_peaks: list[RankInfo] = field(default_factory=list)
    kda: StatValue | None = None
    win_pct: StatValue | None = None
    wins: StatValue | None = None
    mvp_pct: StatValue | None = None
    kd_ratio: str | None = None
    kills: str | None = None
    deaths: str | None = None
    assists: str | None = None
    last_kills: str | None = None
    svp_pct: str | None = None
    damage: str | None = None
    healing: str | None = None
    damage_blocked: str | None = None
    max_kill_streak: str | None = None
    mvps: str | None = None
    svps: StatValue | None = None
    roles: list[RoleStats] = field(default_factory=list)
    top_heroes: list[HeroStats] = field(default_factory=list)
    embed_color: int | None = None
    rating_chart: list[RatingChartPoint] = field(default_factory=list)
    rating_chart_delta: int | None = None
