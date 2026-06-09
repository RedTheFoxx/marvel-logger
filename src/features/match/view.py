from __future__ import annotations

import logging

import discord

from features.match.embed import (
    build_match_detail_embed,
    build_match_detail_unavailable_embed,
)
from tracker.models import MatchBundle

logger = logging.getLogger(__name__)

_SELECT_TIMEOUT = 120.0


class MatchPickerView(discord.ui.View):
    def __init__(self, bundle: MatchBundle) -> None:
        super().__init__(timeout=_SELECT_TIMEOUT)
        self._bundle = bundle
        self._entries_by_id = {e.match_id: e for e in bundle.entries}

        options: list[discord.SelectOption] = []
        for index, entry in enumerate(bundle.entries, start=1):
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

        select = discord.ui.Select(
            placeholder="Choisir un match…",
            options=options,
            min_values=1,
            max_values=1,
        )
        select.callback = self._on_select
        self.add_item(select)

    async def _on_select(self, interaction: discord.Interaction) -> None:
        match_id = interaction.data["values"][0]  # type: ignore[index]
        entry = self._entries_by_id.get(match_id)
        detail = self._bundle.details.get(match_id)

        if detail is not None:
            embed = build_match_detail_embed(detail)
        elif entry is not None:
            embed = build_match_detail_unavailable_embed(
                entry, self._bundle.username
            )
        else:
            await interaction.response.send_message(
                "Match introuvable.", ephemeral=True
            )
            return

        await interaction.response.edit_message(embed=embed, view=None)
        logger.info(
            "Match sélectionné : %s pour %s par %s",
            match_id,
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
