import discord
from discord import app_commands

from config import MAX_DEMONSTRATION_EMBED
from features.demo.embed import build_demo_embed


def register_demo_command(tree: app_commands.CommandTree) -> None:
    @tree.command(name="demo", description="Affiche des embeds de démonstration")
    async def demo(interaction: discord.Interaction) -> None:
        embeds = [
            build_demo_embed(i) for i in range(1, MAX_DEMONSTRATION_EMBED + 1)
        ]
        await interaction.response.send_message(embeds=embeds)
