import asyncio
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from config import DATABASE_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS match_feels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER NOT NULL,
    tracker_username TEXT NOT NULL,
    tracker_username_normalized TEXT NOT NULL,
    match_id TEXT NOT NULL,
    season_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 10),
    rated_at TEXT NOT NULL,
    played_at TEXT,
    hero_name TEXT,
    map_name TEXT,
    game_mode TEXT,
    outcome TEXT,
    score TEXT,
    kills TEXT,
    deaths TEXT,
    assists TEXT,
    kda_ratio TEXT,
    rs TEXT,
    rs_delta TEXT,
    raw_snapshot_json TEXT,
    UNIQUE(discord_user_id, tracker_username_normalized, match_id)
);
CREATE INDEX IF NOT EXISTS idx_match_feels_user_season
    ON match_feels(discord_user_id, tracker_username_normalized, season_id);
"""


@dataclass
class MatchFeelsRecord:
    """Note de ressenti + snapshot des stats du match au moment de la notation."""

    discord_user_id: int
    tracker_username: str
    match_id: str
    season_id: int
    rating: int
    played_at: datetime | None = None
    hero_name: str | None = None
    map_name: str | None = None
    game_mode: str | None = None
    outcome: str | None = None
    score: str | None = None
    kills: str | None = None
    deaths: str | None = None
    assists: str | None = None
    kda_ratio: str | None = None
    rs: str | None = None
    rs_delta: str | None = None
    raw_snapshot_json: str | None = None
    rated_at: datetime | None = None


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _row_to_record(row: sqlite3.Row) -> MatchFeelsRecord:
    return MatchFeelsRecord(
        discord_user_id=row["discord_user_id"],
        tracker_username=row["tracker_username"],
        match_id=row["match_id"],
        season_id=row["season_id"],
        rating=row["rating"],
        played_at=_parse_dt(row["played_at"]),
        hero_name=row["hero_name"],
        map_name=row["map_name"],
        game_mode=row["game_mode"],
        outcome=row["outcome"],
        score=row["score"],
        kills=row["kills"],
        deaths=row["deaths"],
        assists=row["assists"],
        kda_ratio=row["kda_ratio"],
        rs=row["rs"],
        rs_delta=row["rs_delta"],
        raw_snapshot_json=row["raw_snapshot_json"],
        rated_at=_parse_dt(row["rated_at"]),
    )


class FeelsStore:
    def __init__(self, path: str | None = None) -> None:
        self._path = path or DATABASE_PATH

    async def init(self) -> None:
        await asyncio.to_thread(self._init_sync)

    def _init_sync(self) -> None:
        db_path = Path(self._path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        try:
            conn.executescript(_SCHEMA)
            conn.commit()
        finally:
            conn.close()

    async def add_rating(self, record: MatchFeelsRecord) -> None:
        await asyncio.to_thread(self._add_rating_sync, record)

    def _add_rating_sync(self, record: MatchFeelsRecord) -> None:
        rated_at = (record.rated_at or datetime.now(timezone.utc)).isoformat()
        played_at = record.played_at.isoformat() if record.played_at else None
        conn = sqlite3.connect(self._path)
        try:
            conn.execute(
                """
                INSERT INTO match_feels (
                    discord_user_id,
                    tracker_username,
                    tracker_username_normalized,
                    match_id,
                    season_id,
                    rating,
                    rated_at,
                    played_at,
                    hero_name,
                    map_name,
                    game_mode,
                    outcome,
                    score,
                    kills,
                    deaths,
                    assists,
                    kda_ratio,
                    rs,
                    rs_delta,
                    raw_snapshot_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.discord_user_id,
                    record.tracker_username,
                    record.tracker_username.lower(),
                    record.match_id,
                    record.season_id,
                    record.rating,
                    rated_at,
                    played_at,
                    record.hero_name,
                    record.map_name,
                    record.game_mode,
                    record.outcome,
                    record.score,
                    record.kills,
                    record.deaths,
                    record.assists,
                    record.kda_ratio,
                    record.rs,
                    record.rs_delta,
                    record.raw_snapshot_json,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def list_for_season(
        self,
        discord_user_id: int,
        tracker_username_normalized: str,
        season_id: int,
    ) -> list[MatchFeelsRecord]:
        return await asyncio.to_thread(
            self._list_for_season_sync,
            discord_user_id,
            tracker_username_normalized,
            season_id,
        )

    def _list_for_season_sync(
        self,
        discord_user_id: int,
        tracker_username_normalized: str,
        season_id: int,
    ) -> list[MatchFeelsRecord]:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                """
                SELECT * FROM match_feels
                WHERE discord_user_id = ?
                  AND tracker_username_normalized = ?
                  AND season_id = ?
                ORDER BY COALESCE(played_at, rated_at) ASC
                """,
                (discord_user_id, tracker_username_normalized, season_id),
            ).fetchall()
            return [_row_to_record(row) for row in rows]
        finally:
            conn.close()

    async def rated_match_ids(
        self,
        discord_user_id: int,
        tracker_username_normalized: str,
        season_id: int,
    ) -> set[str]:
        return await asyncio.to_thread(
            self._rated_match_ids_sync,
            discord_user_id,
            tracker_username_normalized,
            season_id,
        )

    def _rated_match_ids_sync(
        self,
        discord_user_id: int,
        tracker_username_normalized: str,
        season_id: int,
    ) -> set[str]:
        conn = sqlite3.connect(self._path)
        try:
            rows = conn.execute(
                """
                SELECT match_id FROM match_feels
                WHERE discord_user_id = ?
                  AND tracker_username_normalized = ?
                  AND season_id = ?
                """,
                (discord_user_id, tracker_username_normalized, season_id),
            ).fetchall()
            return {row[0] for row in rows}
        finally:
            conn.close()
