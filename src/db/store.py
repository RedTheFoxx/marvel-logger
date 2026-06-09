import asyncio
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from config import DATABASE_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tracker_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_user_id INTEGER NOT NULL,
    tracker_username TEXT NOT NULL,
    tracker_username_normalized TEXT NOT NULL,
    registered_at TEXT NOT NULL,
    UNIQUE(discord_user_id, tracker_username_normalized)
);
CREATE INDEX IF NOT EXISTS idx_registrations_discord
    ON tracker_registrations(discord_user_id);
"""


class RegistrationStore:
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

    async def count_for_user(self, discord_user_id: int) -> int:
        return await asyncio.to_thread(self._count_for_user_sync, discord_user_id)

    def _count_for_user_sync(self, discord_user_id: int) -> int:
        conn = sqlite3.connect(self._path)
        try:
            row = conn.execute(
                "SELECT COUNT(*) FROM tracker_registrations WHERE discord_user_id = ?",
                (discord_user_id,),
            ).fetchone()
            return int(row[0]) if row else 0
        finally:
            conn.close()

    async def list_for_user(self, discord_user_id: int) -> list[str]:
        return await asyncio.to_thread(self._list_for_user_sync, discord_user_id)

    def _list_for_user_sync(self, discord_user_id: int) -> list[str]:
        conn = sqlite3.connect(self._path)
        try:
            rows = conn.execute(
                """
                SELECT tracker_username FROM tracker_registrations
                WHERE discord_user_id = ?
                ORDER BY registered_at ASC
                """,
                (discord_user_id,),
            ).fetchall()
            return [row[0] for row in rows]
        finally:
            conn.close()

    async def has_user_pseudo(self, discord_user_id: int, normalized: str) -> bool:
        return await asyncio.to_thread(
            self._has_user_pseudo_sync, discord_user_id, normalized
        )

    def _has_user_pseudo_sync(self, discord_user_id: int, normalized: str) -> bool:
        conn = sqlite3.connect(self._path)
        try:
            row = conn.execute(
                """
                SELECT 1 FROM tracker_registrations
                WHERE discord_user_id = ? AND tracker_username_normalized = ?
                LIMIT 1
                """,
                (discord_user_id, normalized),
            ).fetchone()
            return row is not None
        finally:
            conn.close()

    async def add(self, discord_user_id: int, tracker_username: str) -> None:
        await asyncio.to_thread(self._add_sync, discord_user_id, tracker_username)

    def _add_sync(self, discord_user_id: int, tracker_username: str) -> None:
        normalized = tracker_username.lower()
        registered_at = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(self._path)
        try:
            conn.execute(
                """
                INSERT INTO tracker_registrations (
                    discord_user_id,
                    tracker_username,
                    tracker_username_normalized,
                    registered_at
                ) VALUES (?, ?, ?, ?)
                """,
                (discord_user_id, tracker_username, normalized, registered_at),
            )
            conn.commit()
        finally:
            conn.close()
