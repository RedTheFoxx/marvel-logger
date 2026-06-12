from __future__ import annotations

import asyncio
import dataclasses
import io
import json
import logging
import sqlite3

import discord

from db import FeelsStore, MatchFeelsRecord
from features.feels.chart import render_feels_chart
from features.feels.embed import (
    build_feels_rating_prompt_embed,
    build_feels_saved_embed,
)
from tracker.models import MatchBundle, MatchListEntry

logger = logging.getLogger(__name__)

_VIEW_TIMEOUT = 180.0

_RATING_LABELS = {
    1: "Horrible",
    2: "Très mauvais",
    3: "Mauvais",
    4: "Décevant",
    5: "Moyen",
    6: "Correct",
    7: "Bien",
    8: "Très bien",
    9: "Excellent",
    10: "Incroyable",
}


def _build_raw_snapshot(bundle: MatchBundle, entry: MatchListEntry) -> str:
    raw_detail = bundle.details_raw.get(entry.match_id)
    if raw_detail is not None:
        payload = {"source": "tracker_match_detail", "data": raw_detail}
    else:
        payload = {
            "source": "match_list_entry",
            "data": dataclasses.asdict(entry),
        }
    return json.dumps(payload, ensure_ascii=False, default=str)


def build_feels_record(
    bundle: MatchBundle,
    entry: MatchListEntry,
    *,
    discord_user_id: int,
    rating: int,
) -> MatchFeelsRecord:
    rank = entry.rank
    return MatchFeelsRecord(
        discord_user_id=discord_user_id,
        tracker_username=bundle.username,
        match_id=entry.match_id,
        season_id=bundle.season_id,
        rating=rating,
        played_at=entry.played_at,
        hero_name=entry.hero.name,
        map_name=entry.map_name,
        game_mode=entry.game_mode,
        outcome=entry.outcome,
        score=entry.score,
        kills=entry.kills,
        deaths=entry.deaths,
        assists=entry.assists,
        kda_ratio=entry.kda_ratio,
        rs=rank.rs if rank else None,
        rs_delta=rank.rs_delta if rank else None,
        raw_snapshot_json=_build_raw_snapshot(bundle, entry),
    )


class FeelsRatingView(discord.ui.View):
    """Sélection d'un match non noté puis d'une note de 1 à 10."""

    def __init__(
        self,
        bundle: MatchBundle,
        unrated_entries: list[MatchListEntry],
        feels_store: FeelsStore,
        author_id: int,
    ) -> None:
        super().__init__(timeout=_VIEW_TIMEOUT)
        self._bundle = bundle
        self._feels_store = feels_store
        self._author_id = author_id
        self._entries_by_id = {e.match_id: e for e in unrated_entries}
        self._selected_entry: MatchListEntry | None = None

        options: list[discord.SelectOption] = []
        for index, entry in enumerate(unrated_entries, start=1):
            outcome = "V" if entry.outcome == "win" else "D"
            label = f"#{index} {outcome} {entry.score} · {entry.map_name}"
            if len(label) > 100:
                label = label[:97] + "..."
            description = (
                f"{entry.hero.name} · KDA {entry.kda_ratio} · {entry.game_mode}"
            )
            if len(description) > 100:
                description = description[:97] + "..."
            options.append(
                discord.SelectOption(
                    label=label,
                    description=description,
                    value=entry.match_id,
                )
            )

        match_select = discord.ui.Select(
            placeholder="Choisir un match à noter…",
            options=options,
            min_values=1,
            max_values=1,
        )
        match_select.callback = self._on_match_select
        self.add_item(match_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id == self._author_id:
            return True
        await interaction.response.send_message(
            "Seul l'auteur de la commande peut noter ces matchs.",
            ephemeral=True,
        )
        return False

    async def _on_match_select(self, interaction: discord.Interaction) -> None:
        match_id = interaction.data["values"][0]  # type: ignore[index]
        entry = self._entries_by_id.get(match_id)
        if entry is None:
            await interaction.response.send_message(
                "Match introuvable.", ephemeral=True
            )
            return

        self._selected_entry = entry
        self.clear_items()
        rating_select = discord.ui.Select(
            placeholder="Choisir une note de 1 à 10…",
            options=[
                discord.SelectOption(
                    label=f"{value} — {_RATING_LABELS[value]}",
                    value=str(value),
                )
                for value in range(1, 11)
            ],
            min_values=1,
            max_values=1,
        )
        rating_select.callback = self._on_rating_select
        self.add_item(rating_select)

        await interaction.response.edit_message(
            embed=build_feels_rating_prompt_embed(entry),
            attachments=[],
            view=self,
        )

    async def _on_rating_select(self, interaction: discord.Interaction) -> None:
        entry = self._selected_entry
        if entry is None:
            await interaction.response.send_message(
                "Aucun match sélectionné.", ephemeral=True
            )
            return
        rating = int(interaction.data["values"][0])  # type: ignore[index]

        await interaction.response.defer()

        record = build_feels_record(
            self._bundle,
            entry,
            discord_user_id=self._author_id,
            rating=rating,
        )
        try:
            await self._feels_store.add_rating(record)
        except sqlite3.IntegrityError:
            logger.warning(
                "Note déjà existante pour le match %s (user %s)",
                entry.match_id,
                self._author_id,
            )

        season_records = await self._feels_store.list_for_season(
            self._author_id,
            self._bundle.username.lower(),
            self._bundle.season_id,
        )
        png_bytes = await asyncio.to_thread(render_feels_chart, season_records)
        files = [discord.File(io.BytesIO(png_bytes), filename="feels_chart.png")]

        self.stop()
        await interaction.edit_original_response(
            embed=build_feels_saved_embed(entry, rating, season_records),
            attachments=files,
            view=None,
        )
        logger.info(
            "Note %d/10 enregistrée : match %s, %s (user %s)",
            rating,
            entry.match_id,
            self._bundle.username,
            interaction.user.display_name,
        )

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        if self.message is not None:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
