import discord

from config import DEFAULT_EMBED_COLOR, MAX_REGISTRATIONS_PER_USER
from features.stats.embed import build_error_embed
from tracker.models import PlayerProfile

__all__ = ["build_error_embed", "build_register_success_embed", "build_already_linked_embed"]


def build_already_linked_embed(usernames: list[str]) -> discord.Embed:
    lines = "\n".join(f"• **{name}**" for name in usernames) if usernames else "—"
    return discord.Embed(
        title="Pseudo déjà lié",
        description=(
            "Ce pseudo Tracker.gg est déjà associé à votre compte Discord.\n\n"
            f"**Vos pseudos ({len(usernames)}/{MAX_REGISTRATIONS_PER_USER})**\n{lines}"
        ),
        color=discord.Color.orange(),
    )


def build_quota_reached_embed(usernames: list[str]) -> discord.Embed:
    lines = "\n".join(f"• **{name}**" for name in usernames)
    return discord.Embed(
        title="Limite atteinte",
        description=(
            f"Vous avez déjà {MAX_REGISTRATIONS_PER_USER} pseudos liés "
            f"(maximum autorisé).\n\n"
            f"**Vos pseudos**\n{lines}\n\n"
            "Retirez un lien existant avant d'en ajouter un nouveau."
        ),
        color=discord.Color.red(),
    )


def build_register_success_embed(
    added_profile: PlayerProfile,
    all_usernames: list[str],
) -> discord.Embed:
    lines = "\n".join(f"• **{name}**" for name in all_usernames)
    count = len(all_usernames)
    embed = discord.Embed(
        title="Pseudo enregistré",
        description=(
            f"**{added_profile.username}** est maintenant lié à votre compte Discord.\n\n"
            f"**Vos pseudos ({count}/{MAX_REGISTRATIONS_PER_USER})**\n{lines}"
        ),
        color=DEFAULT_EMBED_COLOR,
        url=added_profile.profile_url,
    )
    embed.set_footer(text="Tracker.gg · Marvel Rivals")
    return embed
