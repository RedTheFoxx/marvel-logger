import os

from dotenv import load_dotenv

load_dotenv()


def _env_bool(key: str, default: bool) -> bool:
    value = os.getenv(key, "").strip().lower()
    if not value:
        return default
    return value in ("1", "true", "yes", "on")


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "")

TRACKER_PROFILE_URL = (
    "https://tracker.gg/marvel-rivals/profile/ign/{username}/overview"
)
TRACKER_PROFILE_API_PATH = (
    "/api/v2/marvel-rivals/standard/profile/ign/{username}"
)

DEBUG = _env_bool("DEBUG", False)

CACHE_TTL_SECONDS = 90
TRACKER_REQUEST_COOLDOWN_SECONDS = int(
    os.getenv("TRACKER_REQUEST_COOLDOWN_SECONDS", "300")
)
SCRAPE_TIMEOUT_MS = int(os.getenv("SCRAPE_TIMEOUT_MS", "60000"))
SCRAPE_HEADLESS = _env_bool("SCRAPE_HEADLESS", True)
SCRAPE_SOLVE_CLOUDFLARE = _env_bool("SCRAPE_SOLVE_CLOUDFLARE", False)
SCRAPE_MAX_PAGES = int(os.getenv("SCRAPE_MAX_PAGES", "2"))

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

DEFAULT_EMBED_COLOR = 0xF4C430

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/registrations.db")
MAX_REGISTRATIONS_PER_USER = 3
