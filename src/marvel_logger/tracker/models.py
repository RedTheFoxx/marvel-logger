import datetime
from dataclasses import dataclass, field
from typing import Literal


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
MatchTeam = Literal["A", "B"]


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
class MatchCombatStats:
    """Statistiques de combat d'un participant (page détail match)."""

    kda_ratio: str
    kills: str
    deaths: str
    assists: str
    solo_kills: str | None = None
    headshot_kills: str | None = None
    last_kills: str | None = None
    damage: str | None = None
    damage_per_min: str | None = None
    damage_blocked: str | None = None
    damage_blocked_per_min: str | None = None
    healing: str | None = None
    healing_per_min: str | None = None
    accuracy_pct: str | None = None
    shots_hit: str | None = None
    shots_fired: str | None = None


@dataclass
class MatchParticipant:
    """Un joueur dans le détail d'un match (les 6 par équipe)."""

    username: str
    team: MatchTeam
    heroes: list[MatchHero] = field(default_factory=list)
    rank: MatchRankSnapshot | None = None
    stats: MatchCombatStats | None = None
    is_mvp: bool = False
    is_svp: bool = False


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
class Match:
    """
    Match complet (page /marvel-rivals/matches/{match_id}).

    Contient les métadonnées globales, les deux équipes et, optionnellement,
    le participant lié au profil Tracker surveillé.
    """

    match_id: str
    match_url: str
    game_mode: str
    map_name: str
    map_location: str
    score_team_a: int
    score_team_b: int
    winning_team: MatchTeam
    duration: str
    played_at: datetime.datetime | None = None
    duration_seconds: int | None = None
    season_id: int | None = None
    replay_id: str | None = None
    share_url: str | None = None
    team_a: list[MatchParticipant] = field(default_factory=list)
    team_b: list[MatchParticipant] = field(default_factory=list)
    tracked_username: str | None = None

    @property
    def score_display(self) -> str:
        return f"{self.score_team_a} : {self.score_team_b}"

    @property
    def map_display(self) -> str:
        if self.map_location:
            return f"{self.map_name} — {self.map_location}"
        return self.map_name

    @property
    def mode_and_map_display(self) -> str:
        return f"{self.game_mode} // {self.map_display}"

    @property
    def tracked_participant(self) -> MatchParticipant | None:
        if not self.tracked_username:
            return None
        key = self.tracked_username.casefold()
        for participant in self.team_a + self.team_b:
            if participant.username.casefold() == key:
                return participant
        return None

    @property
    def tracked_outcome(self) -> MatchOutcome | None:
        participant = self.tracked_participant
        if participant is None:
            return None
        if participant.team == self.winning_team:
            return "win"
        return "loss"


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
