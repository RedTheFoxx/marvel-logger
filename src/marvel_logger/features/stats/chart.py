from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

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

    y_min, y_max = min(rs_values), max(rs_values)
    padding = max(25, int((y_max - y_min) * 0.15) or 25)
    ax.set_ylim(y_min - padding, y_max + padding)

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

    plt.tight_layout(pad=0.8)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()
