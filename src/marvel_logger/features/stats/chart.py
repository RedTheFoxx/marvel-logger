from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from marvel_logger.features.stats.rank_zones import (
    RankZone,
    major_rank_key,
    zones_intersecting,
)
from marvel_logger.tracker.models import RatingChartPoint

_BG = "#0a0e14"
_PANEL = "#0d1117"
_LINE = "#3b82f6"
_FILL = "#3b82f6"
_GRID = "#1f2937"
_TEXT = "#9ca3af"
_LABEL = "#e5e7eb"
_WIN = "#22c55e"
_LOSS = "#ef4444"
_ZONE_LINE = "#4b5563"
_ZONE_LABEL = "#6b7280"
_ZONE_HIGHLIGHT = "#d1d5db"


def _zone_top_rs(zone: RankZone, rs_hi: float) -> float:
    if zone.rs_max is not None:
        return float(zone.rs_max)
    return rs_hi


def _draw_rank_zones(
    ax: plt.Axes,
    rs_lo: float,
    rs_hi: float,
    *,
    highlight_key: str | None,
    dense: bool,
) -> None:
    zones = zones_intersecting(rs_lo, rs_hi)
    if not zones:
        return

    label_zones: list[RankZone]
    if highlight_key:
        label_zones = [z for z in zones if z.key == highlight_key]
    elif len(zones) <= 3:
        label_zones = zones
    else:
        label_zones = []

    line_w = 0.7 if dense else 0.9
    span_alpha = 0.05 if dense else 0.07
    highlight_alpha = 0.11 if dense else 0.14

    for zone in zones:
        is_highlight = zone.key == highlight_key
        color = zone.color
        top = _zone_top_rs(zone, rs_hi)
        bottom = max(float(zone.rs_min), rs_lo)
        top_clamped = min(top, rs_hi)
        if top_clamped > bottom:
            ax.axhspan(
                bottom,
                top_clamped,
                facecolor=color,
                alpha=highlight_alpha if is_highlight else span_alpha,
                zorder=0,
                linewidth=0,
            )

        ax.axhline(
            zone.rs_min,
            color=color if is_highlight else _ZONE_LINE,
            linewidth=line_w + (0.2 if is_highlight else 0),
            alpha=0.75 if is_highlight else 0.5,
            zorder=1,
        )
        if zone.rs_max is not None:
            ax.axhline(
                zone.rs_max,
                color=color if is_highlight else _ZONE_LINE,
                linewidth=line_w,
                alpha=0.6 if is_highlight else 0.4,
                linestyle=(0, (4, 4)),
                zorder=1,
            )

    label_size = 6 if dense else 7
    for zone in label_zones:
        bottom = max(float(zone.rs_min), rs_lo)
        top = min(_zone_top_rs(zone, rs_hi), rs_hi)
        y_mid = (bottom + top) / 2.0
        is_highlight = zone.key == highlight_key
        ax.text(
            1.01,
            y_mid,
            zone.label,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="center",
            color=_ZONE_HIGHLIGHT if is_highlight else _ZONE_LABEL,
            fontsize=label_size + (1 if is_highlight else 0),
            fontweight="bold" if is_highlight else "normal",
            clip_on=False,
            zorder=2,
        )


def _catmull_rom_1d(p0: float, p1: float, p2: float, p3: float, t: float) -> float:
    t2 = t * t
    t3 = t2 * t
    return 0.5 * (
        (2 * p1)
        + (-p0 + p2) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * t3
    )


def _smooth_series(
    x: list[float] | list[int],
    y: list[int],
    *,
    samples_per_segment: int,
) -> tuple[np.ndarray, np.ndarray]:
    x_arr = np.asarray(x, dtype=np.float64)
    y_arr = np.asarray(y, dtype=np.float64)
    n = len(x_arr)
    if n < 2:
        return x_arr, y_arr
    if n == 2:
        t = np.linspace(0.0, 1.0, samples_per_segment + 1)
        return np.interp(t, [0.0, 1.0], x_arr), np.interp(t, [0.0, 1.0], y_arr)

    t = np.arange(n, dtype=np.float64)
    y_pad = np.concatenate([[y_arr[0]], y_arr, [y_arr[-1]]])
    t_smooth_list: list[float] = []
    y_smooth_list: list[float] = []

    for i in range(n - 1):
        y0, y1, y2, y3 = y_pad[i : i + 4]
        for ti in np.linspace(0.0, 1.0, samples_per_segment, endpoint=False):
            t_smooth_list.append(i + float(ti))
            y_smooth_list.append(_catmull_rom_1d(y0, y1, y2, y3, float(ti)))

    t_smooth_list.append(float(n - 1))
    y_smooth_list.append(float(y_arr[-1]))
    t_smooth = np.asarray(t_smooth_list)
    y_smooth = np.asarray(y_smooth_list)
    x_smooth = np.interp(t_smooth, t, x_arr)
    return x_smooth, y_smooth


def render_rating_chart(
    points: list[RatingChartPoint],
    *,
    total_delta: int | None = None,
    current_tier_name: str | None = None,
) -> bytes:
    if not points:
        raise ValueError("points must not be empty")

    rs_values = [p.rs for p in points]
    has_dates = all(p.played_at is not None for p in points)
    if has_dates:
        x_values = [p.played_at for p in points]
        x_label = None
    else:
        x_values = list(range(1, len(points) + 1))
        x_label = "Partie"

    n = len(points)
    dense = n > 40
    fig_width = 11 if dense else 9
    line_width = 1.4 if dense else 2.2
    base_marker = 3.0 if dense else 5.0
    outcome_marker = 4.0 if dense else 7.0
    marker_edge = 0.8 if dense else 1.2

    fig, ax = plt.subplots(figsize=(fig_width, 3.4), dpi=100)
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_PANEL)

    y_min, y_max = min(rs_values), max(rs_values)
    padding = max(25, int((y_max - y_min) * 0.15) or 25)
    y_lo = y_min - padding
    y_hi = y_max + padding
    ax.set_ylim(y_lo, y_hi)

    highlight_key = major_rank_key(current_tier_name)
    visible_zones = zones_intersecting(y_lo, y_hi)
    _draw_rank_zones(
        ax,
        y_lo,
        y_hi,
        highlight_key=highlight_key,
        dense=dense,
    )
    show_zone_labels = bool(
        highlight_key or len(visible_zones) <= 3
    )

    samples_per_segment = 8 if dense else 14
    if has_dates:
        x_numeric = mdates.date2num(x_values)
        x_line_num, y_line = _smooth_series(
            list(x_numeric), rs_values, samples_per_segment=samples_per_segment
        )
        x_line = mdates.num2date(x_line_num)
    else:
        x_line, y_line = _smooth_series(
            x_values, rs_values, samples_per_segment=samples_per_segment
        )

    fill_base = min(rs_values) - 40
    ax.fill_between(x_line, y_line, fill_base, color=_FILL, alpha=0.12)
    ax.plot(
        x_line,
        y_line,
        color=_LINE,
        linewidth=line_width,
        solid_capstyle="round",
        solid_joinstyle="round",
        zorder=3,
    )
    ax.plot(
        x_values,
        rs_values,
        linestyle="none",
        marker="o",
        markersize=base_marker,
        markerfacecolor=_LINE,
        markeredgecolor=_BG,
        markeredgewidth=marker_edge,
        zorder=3,
    )

    for x, y, point in zip(x_values, rs_values, points):
        if point.outcome == "win":
            color = _WIN
        elif point.outcome == "loss":
            color = _LOSS
        else:
            continue
        ax.plot(
            x,
            y,
            marker="o",
            markersize=outcome_marker,
            markerfacecolor=color,
            markeredgecolor=_BG,
            markeredgewidth=marker_edge,
            zorder=4,
        )

    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _p: f"{int(v):,}".replace(",", " "))
    )
    ax.tick_params(colors=_TEXT, labelsize=8)
    ax.grid(True, color=_GRID, linewidth=0.6, alpha=0.85)
    for spine in ax.spines.values():
        spine.set_color(_GRID)

    if has_dates:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        fig.autofmt_xdate(rotation=0, ha="center")
    elif x_label:
        ax.set_xlabel(x_label, color=_TEXT, fontsize=9)

    ax.set_ylabel("RS", color=_TEXT, fontsize=9)

    delta = total_delta
    if delta is None:
        deltas = [p.rs_delta for p in points if p.rs_delta is not None]
        if deltas:
            delta = sum(deltas)
        elif len(rs_values) > 1:
            delta = rs_values[-1] - rs_values[0]
        else:
            delta = 0

    sign = "+" if delta > 0 else ""
    ax.text(
        0.99,
        0.96,
        f"{sign}{delta} RS",
        transform=ax.transAxes,
        ha="right",
        va="top",
        color=_LABEL,
        fontsize=14,
        fontweight="bold",
    )
    ax.text(
        0.99,
        0.82,
        f"{len(points)} parties classées",
        transform=ax.transAxes,
        ha="right",
        va="top",
        color=_TEXT,
        fontsize=8,
    )

    if show_zone_labels:
        fig.subplots_adjust(right=0.88)
    else:
        plt.tight_layout(pad=0.8)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()
