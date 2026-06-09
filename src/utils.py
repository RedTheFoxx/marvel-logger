import re

TRACKER_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,32}$")


def validate_tracker_username(username: str) -> str | None:
    """Retourne un message d'erreur ou None si le pseudo est valide."""
    if not username:
        return "Le pseudo ne peut pas être vide."
    if not TRACKER_USERNAME_PATTERN.match(username):
        return (
            "Pseudo invalide. Utilisez uniquement lettres, chiffres, "
            "tirets, underscores ou points (max 32 caractères)."
        )
    return None
