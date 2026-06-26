import discord

from config import DEFAULT_EMBED_COLOR, MAX_REGISTRATIONS_PER_USER


def build_not_registered_embed(username: str) -> discord.Embed:
    return discord.Embed(
        title="Pseudo introuvable",
        description=(
            f"**{username}** n'est pas lié à votre compte Discord.\n"
            "Vérifiez l'orthographe ou utilisez `/register` pour l'ajouter."
        ),
        color=discord.Color.orange(),
    )


def build_unregister_success_embed(
    removed_username: str,
    remaining_usernames: list[str],
    feels_deleted: int,
) -> discord.Embed:
    if remaining_usernames:
        lines = "\n".join(f"• **{name}**" for name in remaining_usernames)
        remaining_text = (
            f"**Vos pseudos restants ({len(remaining_usernames)}/{MAX_REGISTRATIONS_PER_USER})**\n{lines}"
        )
    else:
        remaining_text = "Vous n'avez plus aucun pseudo lié. Utilisez `/register` pour en ajouter un."

    feels_text = (
        f"\n\n*{feels_deleted} ressenti(s) supprimé(s) associé(s) à ce pseudo.*"
        if feels_deleted > 0
        else ""
    )

    return discord.Embed(
        title="Pseudo retiré",
        description=(
            f"**{removed_username}** a été dissocié de votre compte Discord.{feels_text}\n\n"
            f"{remaining_text}"
        ),
        color=DEFAULT_EMBED_COLOR,
    )


def build_unregister_error_embed(message: str) -> discord.Embed:
    return discord.Embed(
        title="Erreur",
        description=message,
        color=discord.Color.red(),
    )
