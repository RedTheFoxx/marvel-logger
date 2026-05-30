import asyncio
import logging
import math
import time
from typing import Any
from urllib.parse import urlparse

from playwright.async_api import Page, Response
from scrapling.fetchers import AsyncStealthySession

from marvel_logger.config import (
    CACHE_TTL_SECONDS,
    DEBUG,
    MATCHES_CAPTURE_TIMEOUT_SECONDS,
    MATCHES_MAX_PAGES,
    MATCHES_PAGE_FETCH_DELAY_SECONDS,
    RATING_GRAPH_MATCH_TARGET,
    SCRAPE_HEADLESS,
    SCRAPE_MAX_PAGES,
    SCRAPE_SOLVE_CLOUDFLARE,
    SCRAPE_TIMEOUT_MS,
    TRACKER_API_BASE_URL,
    TRACKER_MATCHES_API_PATH,
    TRACKER_MATCHES_URL,
    TRACKER_PROFILE_API_PATH,
    TRACKER_PROFILE_URL,
    TRACKER_REQUEST_COOLDOWN_SECONDS,
)
from marvel_logger.logging_setup import scrape_progress
from marvel_logger.tracker.models import PlayerProfile
from marvel_logger.tracker.parser import parse_profile
from marvel_logger.tracker.parser_matches import apply_rating_chart

logger = logging.getLogger(__name__)

_PROFILE_LOAD_ERROR = (
    "Impossible de charger le profil Tracker.gg. Réessayez dans quelques instants."
)


class TrackerScraperError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ProfileNotFoundError(TrackerScraperError):
    pass


class TrackerRateLimitError(TrackerScraperError):
    def __init__(self, retry_after_seconds: float):
        self.retry_after_seconds = retry_after_seconds
        total = max(1, math.ceil(retry_after_seconds))
        minutes, seconds = divmod(total, 60)
        if minutes:
            delay = f"{minutes} min {seconds:02d} s" if seconds else f"{minutes} min"
        else:
            delay = f"{seconds} s"
        super().__init__(
            f"Limite de requêtes Tracker.gg atteinte. Réessayez dans **{delay}**."
        )


class TrackerScraper:
    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._session: AsyncStealthySession | None = None
        self._last_scrape_at: float | None = None
        self._scrape_lock = asyncio.Lock()

    async def start(self) -> None:
        if self._session is not None:
            return
        logger.info(
            "Démarrage session Scrapling (headless=%s, cloudflare=%s, timeout=%dms)",
            SCRAPE_HEADLESS,
            SCRAPE_SOLVE_CLOUDFLARE,
            SCRAPE_TIMEOUT_MS,
        )
        self._session = AsyncStealthySession(
            headless=SCRAPE_HEADLESS,
            solve_cloudflare=SCRAPE_SOLVE_CLOUDFLARE,
            network_idle=False,
            timeout=SCRAPE_TIMEOUT_MS,
            max_pages=SCRAPE_MAX_PAGES,
            google_search=True,
        )
        await self._session.__aenter__()
        if DEBUG:
            logger.warning("DEBUG=true — cooldown Tracker.gg désactivé")
        else:
            logger.info(
                "Cooldown Tracker.gg : 1 requête toutes les %ds",
                TRACKER_REQUEST_COOLDOWN_SECONDS,
            )
        logger.info("Session Scrapling prête")

    async def close(self) -> None:
        if self._session is None:
            return
        logger.info("Fermeture session Scrapling")
        await self._session.__aexit__(None, None, None)
        self._session = None

    def _cache_get(self, username: str) -> dict[str, Any] | None:
        key = username.lower()
        entry = self._cache.get(key)
        if not entry:
            return None
        expires_at, payload = entry
        if time.monotonic() > expires_at:
            del self._cache[key]
            return None
        return payload

    def _cache_set(self, username: str, payload: dict[str, Any]) -> None:
        self._cache[username.lower()] = (
            time.monotonic() + CACHE_TTL_SECONDS,
            payload,
        )

    async def _acquire_scrape_slot(self) -> None:
        if DEBUG:
            return

        async with self._scrape_lock:
            now = time.monotonic()
            if self._last_scrape_at is not None:
                elapsed = now - self._last_scrape_at
                remaining = TRACKER_REQUEST_COOLDOWN_SECONDS - elapsed
                if remaining > 0:
                    logger.warning(
                        "Cooldown Tracker.gg actif — %.0fs restantes",
                        remaining,
                    )
                    raise TrackerRateLimitError(remaining)
            self._last_scrape_at = now
            logger.info("Slot Tracker.gg accordé")

    @staticmethod
    def _profile_api_path(username: str) -> str:
        return TRACKER_PROFILE_API_PATH.format(username=username).lower()

    @staticmethod
    def _matches_api_path(username: str) -> str:
        return TRACKER_MATCHES_API_PATH.format(username=username).lower()

    @staticmethod
    def _path_matches(response: Response, expected_path: str) -> bool:
        path = urlparse(response.url).path.lower().rstrip("/")
        return path == expected_path.rstrip("/")

    @staticmethod
    def _is_matches_api(response: Response, username: str) -> bool:
        path = urlparse(response.url).path.lower()
        expected = TrackerScraper._matches_api_path(username)
        return path == expected.rstrip("/") or (
            "/matches/ign/" in path and username.lower() in path
        )

    @staticmethod
    def _normalize_bundle(payload: dict[str, Any]) -> dict[str, Any]:
        if "profile" in payload:
            return payload
        return {"profile": payload, "matches": None}

    @staticmethod
    def _season_id_from_profile(profile_payload: dict[str, Any]) -> int:
        metadata = (profile_payload.get("data") or {}).get("metadata") or {}
        return int(metadata.get("currentSeason") or metadata.get("defaultSeason") or 0)

    @staticmethod
    def _matches_list(matches_payload: dict[str, Any] | None) -> list[Any]:
        data = (matches_payload or {}).get("data") or {}
        matches = data.get("matches")
        return matches if isinstance(matches, list) else []

    @staticmethod
    def _next_cursor(matches_payload: dict[str, Any] | None) -> str | None:
        data = (matches_payload or {}).get("data") or {}
        meta = data.get("metadata") or {}
        cursor = meta.get("next")
        return str(cursor) if cursor else None

    @staticmethod
    def _ranked_match_count(matches_payload: dict[str, Any] | None) -> int:
        count = 0
        for match in TrackerScraper._matches_list(matches_payload):
            attrs = match.get("attributes") or {}
            meta = match.get("metadata") or {}
            mode = (attrs.get("mode") or "").lower()
            if mode in ("competitive", "ranked") or meta.get("isRanked"):
                count += 1
        return count

    async def _paginate_matches(
        self,
        page: Page,
        username: str,
        season_id: int,
        first_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Accumule plusieurs pages de l'API matchs via le curseur ``next``."""
        accumulated = list(self._matches_list(first_payload))
        next_cursor = self._next_cursor(first_payload)
        api_path = self._matches_api_path(username)
        seen_cursors: set[str] = set()
        pages_fetched = 1

        while (
            next_cursor
            and next_cursor not in seen_cursors
            and pages_fetched < MATCHES_MAX_PAGES
            and self._ranked_match_count({"data": {"matches": accumulated}})
            < RATING_GRAPH_MATCH_TARGET
        ):
            seen_cursors.add(next_cursor)
            base = f"{TRACKER_API_BASE_URL.rstrip('/')}{api_path}"
            try:
                payload = await page.evaluate(
                    """async ({ base, season, cursor }) => {
                        const url = new URL(base);
                        url.searchParams.set('season', season);
                        url.searchParams.set('next', cursor);
                        try {
                            const res = await fetch(url.toString(), {
                                headers: { accept: 'application/json' },
                                credentials: 'include',
                            });
                            if (!res.ok) return { __status: res.status };
                            return await res.json();
                        } catch (e) {
                            return { __error: String(e) };
                        }
                    }""",
                    {"base": base, "season": str(season_id), "cursor": next_cursor},
                )
            except Exception as exc:
                logger.warning(
                    "Échec fetch pagination matchs (page %d) : %s",
                    pages_fetched + 1,
                    exc,
                )
                break

            if not isinstance(payload, dict) or payload.get("__error"):
                logger.warning(
                    "Erreur fetch pagination (page %d) : %s",
                    pages_fetched + 1,
                    payload.get("__error") if isinstance(payload, dict) else "réponse inattendue",
                )
                break
            if payload.get("__status"):
                logger.warning(
                    "Réponse pagination invalide (page %d, HTTP %s)",
                    pages_fetched + 1,
                    payload.get("__status"),
                )
                break

            new_matches = self._matches_list(payload)
            if not new_matches:
                break
            accumulated.extend(new_matches)
            pages_fetched += 1
            next_cursor = self._next_cursor(payload)
            logger.info(
                "Page matchs %d récupérée (+%d → %d matchs, %d classés)",
                pages_fetched,
                len(new_matches),
                len(accumulated),
                self._ranked_match_count({"data": {"matches": accumulated}}),
            )
            if next_cursor:
                await asyncio.sleep(MATCHES_PAGE_FETCH_DELAY_SECONDS)

        merged = dict(first_payload)
        data = dict(merged.get("data") or {})
        data["matches"] = accumulated
        merged["data"] = data
        return merged

    @staticmethod
    def _validate_profile_payload(payload: dict[str, Any], username: str) -> None:
        if payload.get("errors"):
            message = payload["errors"][0].get("message", "Profil introuvable.")
            raise ProfileNotFoundError(
                f"Profil introuvable : **{username}**\n{message}",
                status_code=404,
            )
        if "data" not in payload:
            raise TrackerScraperError("Réponse Tracker.gg invalide.")

    def _make_page_action(self, username: str, capture: dict[str, Any]):
        profile_path = self._profile_api_path(username)
        wait_seconds = max((SCRAPE_TIMEOUT_MS - 20_000) / 1000, 20.0)
        profile_done = asyncio.Event()
        matches_done = asyncio.Event()

        async def on_response(response: Response) -> None:
            if self._path_matches(response, profile_path):
                if capture.get("profile") is not None:
                    return
                capture["profile_status"] = response.status
                logger.info(
                    "Réponse API profil interceptée : HTTP %d (%s)",
                    response.status,
                    response.url,
                )
                if response.status == 404:
                    profile_done.set()
                    return
                try:
                    capture["profile"] = await response.json()
                    profile_done.set()
                except Exception:
                    logger.warning("Impossible de parser le JSON de la réponse profil")
                return

            if not self._is_matches_api(response, username):
                return
            if capture.get("matches") is not None:
                return
            capture["matches_status"] = response.status
            logger.info(
                "Réponse API matchs interceptée : HTTP %d (%s)",
                response.status,
                response.url,
            )
            if response.status != 200:
                return
            try:
                capture["matches"] = await response.json()
                matches_done.set()
            except Exception:
                logger.warning("Impossible de parser le JSON de la réponse matchs")

        async def _wait_profile() -> None:
            try:
                await asyncio.wait_for(profile_done.wait(), timeout=wait_seconds)
            except TimeoutError:
                body = ""
                if capture.get("_page") is not None:
                    page_content = await capture["_page"].content()
                    body = page_content.lower()
                if "profile not found" in body or "page-not-found" in body:
                    raise ProfileNotFoundError(
                        f"Profil introuvable : **{username}**",
                        status_code=404,
                    )
                if capture.get("profile") is None:
                    raise TrackerScraperError(_PROFILE_LOAD_ERROR)

        async def _wait_matches_optional() -> None:
            if capture.get("matches") is not None:
                return
            try:
                await asyncio.wait_for(
                    matches_done.wait(), timeout=MATCHES_CAPTURE_TIMEOUT_SECONDS
                )
            except TimeoutError:
                logger.info(
                    "Pas de réponse API matchs sur l'overview après %.0fs",
                    MATCHES_CAPTURE_TIMEOUT_SECONDS,
                )

        async def page_action(page: Page) -> None:
            capture["_page"] = page
            page.on("response", on_response)
            logger.debug("Rechargement overview pour déclencher les appels API")
            await page.reload(wait_until="domcontentloaded")
            await _wait_profile()
            await _wait_matches_optional()

            if capture.get("matches") is None and capture.get("profile"):
                season_id = self._season_id_from_profile(capture["profile"])
                matches_url = (
                    TRACKER_MATCHES_URL.format(username=username)
                    + f"?season={season_id}"
                )
                logger.info(
                    "Fallback navigation matchs → %s",
                    matches_url,
                )
                await page.goto(matches_url, wait_until="domcontentloaded")
                try:
                    await asyncio.wait_for(matches_done.wait(), timeout=wait_seconds)
                except TimeoutError:
                    logger.warning(
                        "API matchs non reçue après fallback pour %s",
                        username,
                    )

            if capture.get("matches") is not None and capture.get("profile"):
                season_id = self._season_id_from_profile(capture["profile"])
                ranked = self._ranked_match_count(capture["matches"])
                has_cursor = self._next_cursor(capture["matches"]) is not None
                if ranked < RATING_GRAPH_MATCH_TARGET and has_cursor:
                    logger.info(
                        "Pagination matchs : %d classés < cible %d, curseur présent",
                        ranked,
                        RATING_GRAPH_MATCH_TARGET,
                    )
                    try:
                        capture["matches"] = await self._paginate_matches(
                            page, username, season_id, capture["matches"]
                        )
                    except Exception:
                        logger.warning("Pagination matchs interrompue, page 1 conservée")
                elif ranked < RATING_GRAPH_MATCH_TARGET and not has_cursor:
                    logger.info(
                        "Pas de curseur 'next' — repli clic « Load more »",
                    )
                    await self._load_more_via_ui(
                        page, username, season_id, capture, wait_seconds
                    )

        return page_action

    async def _load_more_via_ui(
        self,
        page: Page,
        username: str,
        season_id: int,
        capture: dict[str, Any],
        wait_seconds: float,
    ) -> None:
        """Repli : navigue vers /matches et clique « Load more » jusqu'à la cible."""
        accumulated = list(self._matches_list(capture.get("matches")))
        page_responses: list[dict[str, Any]] = []

        async def on_more(response: Response) -> None:
            if not self._is_matches_api(response, username) or response.status != 200:
                return
            try:
                page_responses.append(await response.json())
            except Exception:
                pass

        matches_url = (
            TRACKER_MATCHES_URL.format(username=username) + f"?season={season_id}"
        )
        try:
            page.on("response", on_more)
            await page.goto(matches_url, wait_until="domcontentloaded")
            clicks = 0
            while (
                self._ranked_match_count({"data": {"matches": accumulated}})
                < RATING_GRAPH_MATCH_TARGET
                and clicks < MATCHES_MAX_PAGES
            ):
                button = page.locator(
                    "button:has-text('Load more'), button:has-text('Load More'), "
                    "[class*='load-more'] button, button[class*='load-more']"
                ).first
                try:
                    if await button.count() == 0 or not await button.is_visible():
                        break
                    page_responses.clear()
                    await button.click()
                    await asyncio.sleep(MATCHES_PAGE_FETCH_DELAY_SECONDS)
                    try:
                        await page.wait_for_load_state(
                            "networkidle", timeout=int(wait_seconds * 1000)
                        )
                    except Exception:
                        pass
                except Exception:
                    break
                for payload in page_responses:
                    accumulated.extend(self._matches_list(payload))
                clicks += 1
                logger.info(
                    "« Load more » clic %d → %d matchs (%d classés)",
                    clicks,
                    len(accumulated),
                    self._ranked_match_count({"data": {"matches": accumulated}}),
                )
        finally:
            page.remove_listener("response", on_more)

        if accumulated:
            base = capture.get("matches") or {"data": {}}
            merged = dict(base)
            data = dict(merged.get("data") or {})
            data["matches"] = accumulated
            merged["data"] = data
            capture["matches"] = merged

    async def _scrape_json(self, username: str) -> dict[str, Any]:
        if self._session is None:
            raise TrackerScraperError(
                "Le scraper n'est pas démarré. Relancez le bot."
            )

        profile_url = TRACKER_PROFILE_URL.format(username=username)
        logger.info("Scraping profil %s → %s", username, profile_url)
        started = time.monotonic()
        capture: dict[str, Any] = {}
        page_action = self._make_page_action(username, capture)

        try:
            with scrape_progress() as progress:
                progress.add_task(
                    f"[cyan]Scraping[/] [bold]{username}[/] sur Tracker.gg…",
                    total=None,
                )
                await self._session.fetch(
                    profile_url,
                    page_action=page_action,
                    network_idle=False,
                    solve_cloudflare=SCRAPE_SOLVE_CLOUDFLARE,
                    timeout=SCRAPE_TIMEOUT_MS,
                )
        except ProfileNotFoundError:
            logger.warning(
                "Profil introuvable après %.1fs : %s", time.monotonic() - started, username
            )
            raise
        except TrackerScraperError:
            raise
        except Exception as exc:
            logger.exception(
                "Erreur Scrapling après %.1fs pour %s",
                time.monotonic() - started,
                username,
            )
            raise TrackerScraperError(_PROFILE_LOAD_ERROR) from exc
        finally:
            capture.pop("_page", None)

        elapsed = time.monotonic() - started
        status = capture.get("profile_status")
        profile_payload = capture.get("profile")
        matches_payload = capture.get("matches")
        logger.info(
            "Page chargée en %.1fs (profil HTTP %s, matchs %s)",
            elapsed,
            status or "?",
            "oui" if matches_payload else "non",
        )

        if status == 404:
            raise ProfileNotFoundError(
                f"Profil introuvable : **{username}**",
                status_code=404,
            )
        if status == 403:
            raise TrackerScraperError(
                "Accès refusé par Tracker.gg. Réessayez dans quelques instants.",
                status_code=403,
            )
        if not profile_payload:
            raise TrackerScraperError(_PROFILE_LOAD_ERROR)

        self._validate_profile_payload(profile_payload, username)
        segments = len((profile_payload.get("data") or {}).get("segments") or [])
        match_count = len((matches_payload or {}).get("data", {}).get("matches") or [])
        logger.info(
            "Données valides (%d segments profil, %d matchs API) en %.1fs",
            segments,
            match_count,
            elapsed,
        )
        return {"profile": profile_payload, "matches": matches_payload}

    async def fetch_raw(self, username: str) -> dict[str, Any]:
        cached = self._cache_get(username)
        if cached is not None:
            logger.info("[green]Cache hit[/] pour %s", username)
            return self._normalize_bundle(cached)

        logger.info("[yellow]Cache miss[/] pour %s — lancement du scrape", username)
        await self._acquire_scrape_slot()
        payload = await self._scrape_json(username)
        self._cache_set(username, payload)
        logger.info("Profil %s mis en cache (%ds)", username, CACHE_TTL_SECONDS)
        return payload

    async def fetch_profile(self, username: str) -> PlayerProfile:
        started = time.monotonic()
        raw = self._normalize_bundle(await self.fetch_raw(username))
        profile = parse_profile(raw["profile"], username)
        apply_rating_chart(profile, raw.get("matches"))
        logger.info(
            "Profil parsé : %s (saison %s, %d points rating) en %.1fs",
            profile.username,
            profile.season_name or "?",
            len(profile.rating_chart),
            time.monotonic() - started,
        )
        return profile


# Alias rétrocompatibilité interne
TrackerClient = TrackerScraper
TrackerAPIError = TrackerScraperError
