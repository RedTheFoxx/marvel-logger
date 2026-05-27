from dataclasses import dataclass, field


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
