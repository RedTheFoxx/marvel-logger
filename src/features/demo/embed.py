import discord

from config import DEFAULT_EMBED_COLOR


def build_demo_embed(index: int) -> discord.Embed:
    return discord.Embed(
        description=f"embed {index}",
        color=DEFAULT_EMBED_COLOR,
    )
