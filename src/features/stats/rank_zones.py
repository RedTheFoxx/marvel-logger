"""
Paliers RS majeurs pour le graphique d'évolution (Tracker.gg Rank Score).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

RS_PER_SUBDIVISION = 100
"""Points RS entre deux divisions adjacentes (ex. Diamond I → Grandmaster III)."""

# Bronze III = 3 000 ; Diamond I = 4 400 ; Grandmaster III = 4 500 ; Celestial I = 5 000.
BRONZE_III_RS = 3000
GRANDMASTER_III_RS = 4500

_SUBDIVISIONS_PER_MAJOR = 3

_MAJOR_RANK_ORDER = (
    "bronze",
    "silver",
    "gold",
    "platinum",
    "diamond",
    "grandmaster",
    "celestial",
    "eternity",
    "one_above_all",
)

_MAJOR_LABELS: dict[str, str] = {
    "bronze": "Bronze",
    "silver": "Silver",
    "gold": "Gold",
    "platinum": "Platinum",
    "diamond": "Diamond",
    "grandmaster": "Grandmaster",
    "celestial": "Celestial",
    "eternity": "Eternity",
    "one_above_all": "One Above All",
}

_MAJOR_COLORS: dict[str, str] = {
    "bronze": "#B87333",
    "silver": "#A8B4C0",
    "gold": "#E8B923",
    "platinum": "#4FD1C5",
    "diamond": "#1680FF",
    "grandmaster": "#A855F7",
    "celestial": "#F97316",
    "eternity": "#FF4F4D",
    "one_above_all": "#FBBF24",
}

_TIER_ALIASES: dict[str, str] = {
    "bronze": "bronze",
    "silver": "silver",
    "gold": "gold",
    "platinum": "platinum",
    "plat": "platinum",
    "diamond": "diamond",
    "grandmaster": "grandmaster",
    "gm": "grandmaster",
    "celestial": "celestial",
    "eternity": "eternity",
    "one above all": "one_above_all",
    "oneaboveall": "one_above_all",
    "oaa": "one_above_all",
}


@dataclass(frozen=True, slots=True)
class RankZone:
    key: str
    label: str
    rs_min: int
    rs_max: int | None
    color: str


def _major_rank_rs_bounds() -> list[tuple[str, int, int | None]]:
    """Bornes [rs_min, rs_max) par rang principal (rs_max exclusif sauf sommet)."""
    bounds: list[tuple[str, int, int | None]] = []
    for index, key in enumerate(_MAJOR_RANK_ORDER):
        if key in ("eternity", "one_above_all"):
            continue
        rs_min = BRONZE_III_RS + index * _SUBDIVISIONS_PER_MAJOR * RS_PER_SUBDIVISION
        rs_max = rs_min + _SUBDIVISIONS_PER_MAJOR * RS_PER_SUBDIVISION
        bounds.append((key, rs_min, rs_max))

    # Après Celestial I (5 000) : Eternity puis One Above All (+100 RS par palier).
    celestial_end = BRONZE_III_RS + 7 * _SUBDIVISIONS_PER_MAJOR * RS_PER_SUBDIVISION
    bounds.append(("eternity", celestial_end, celestial_end + RS_PER_SUBDIVISION))
    bounds.append(("one_above_all", celestial_end + RS_PER_SUBDIVISION, None))
    return bounds


def _build_major_rank_zones() -> tuple[RankZone, ...]:
    return tuple(
        RankZone(
            key,
            _MAJOR_LABELS[key],
            rs_min,
            rs_max,
            _MAJOR_COLORS[key],
        )
        for key, rs_min, rs_max in _major_rank_rs_bounds()
    )


# Seuils RS par rang principal (rs_max exclusif, sauf One Above All ouvert).
MAJOR_RANK_ZONES: tuple[RankZone, ...] = _build_major_rank_zones()
# Bronze 3000–3300, Silver 3300–3600, …, Diamond 4200–4500, Grandmaster 4500–4800,
# Celestial 4800–5100, Eternity 5100–5200, One Above All 5200+.


def rs_for_subdivision_index(index: int) -> int:
    """RS plancher de la sous-division ``index`` (0 = Bronze III)."""
    return BRONZE_III_RS + index * RS_PER_SUBDIVISION


def major_rank_key(tier_name: str | None) -> str | None:
    """Normalise un libellé Tracker (ex. « Diamond III ») vers une clé majeure."""
    if not tier_name:
        return None
    cleaned = tier_name.strip().lower()
    cleaned = re.sub(r"\s+(iii|ii|i|3|2|1)\s*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    if cleaned in _TIER_ALIASES:
        return _TIER_ALIASES[cleaned]
    for alias, key in _TIER_ALIASES.items():
        if cleaned.startswith(alias):
            return key
    return None


def zones_intersecting(rs_lo: float, rs_hi: float) -> list[RankZone]:
    """Retourne les paliers dont la bande RS chevauche [rs_lo, rs_hi]."""
    if rs_hi < rs_lo:
        rs_lo, rs_hi = rs_hi, rs_lo
    visible: list[RankZone] = []
    for zone in MAJOR_RANK_ZONES:
        top = zone.rs_max if zone.rs_max is not None else float("inf")
        if top <= rs_lo or zone.rs_min >= rs_hi:
            continue
        visible.append(zone)
    return visible


def rank_bounds_from_stat_metadata(metadata: dict[str, Any] | None) -> tuple[int, int | None] | None:
    """Extrait des bornes RS si Tracker les ajoute un jour dans les métadonnées."""
    if not metadata:
        return None
    for lo_key, hi_key in (
        ("tierMin", "tierMax"),
        ("min", "max"),
        ("lowerBound", "upperBound"),
        ("minValue", "maxValue"),
    ):
        lo = metadata.get(lo_key)
        hi = metadata.get(hi_key)
        if lo is None and hi is None:
            continue
        try:
            rs_min = int(float(lo)) if lo is not None else 0
            rs_max = int(float(hi)) if hi is not None else None
            return rs_min, rs_max
        except (TypeError, ValueError):
            continue
    return None


def zone_for_rs(rs: int) -> RankZone | None:
    for zone in MAJOR_RANK_ZONES:
        top = zone.rs_max if zone.rs_max is not None else float("inf")
        if zone.rs_min <= rs < top:
            return zone
    return MAJOR_RANK_ZONES[-1] if rs >= MAJOR_RANK_ZONES[-1].rs_min else None
