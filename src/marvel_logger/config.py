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
TRACKER_MATCHES_URL = (
    "https://tracker.gg/marvel-rivals/profile/ign/{username}/matches"
)
TRACKER_MATCHES_API_PATH = (
    "/api/v2/marvel-rivals/standard/matches/ign/{username}"
)
# Host réel servant l'API Tracker.gg (les appels XHR partent de api.tracker.gg)
TRACKER_API_BASE_URL = os.getenv("TRACKER_API_BASE_URL", "https://api.tracker.gg")
TRACKER_MATCH_URL = "https://tracker.gg/marvel-rivals/matches/{match_id}"

# 0 = toute la première page API (alignée overview) ; sinon plafond explicite
RATING_GRAPH_MATCH_LIMIT = int(os.getenv("RATING_GRAPH_MATCH_LIMIT", "0"))
# Nombre cible de matchs classés à accumuler via pagination de l'API matchs
RATING_GRAPH_MATCH_TARGET = int(os.getenv("RATING_GRAPH_MATCH_TARGET", "100"))
# Délai entre deux requêtes de pagination pour éviter un rate-limit
MATCHES_PAGE_FETCH_DELAY_SECONDS = float(
    os.getenv("MATCHES_PAGE_FETCH_DELAY_SECONDS", "0.4")
)
# Nombre maximum de pages à parcourir lors de la pagination
MATCHES_MAX_PAGES = int(os.getenv("MATCHES_MAX_PAGES", "8"))
MATCHES_CAPTURE_TIMEOUT_SECONDS = float(
    os.getenv("MATCHES_CAPTURE_TIMEOUT_SECONDS", "8")
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
