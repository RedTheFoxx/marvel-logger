from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

from features.stats.rank_zones import (
    RankZone,
    major_rank_key,
    zones_intersecting,
)
from tracker.models import RatingChartPoint

_DEFAULT_ACCENT = "#3b82f6"
_BG = "#0a0e14"
_PANEL = "#0d1117"
_GRID = "#1f2937"
_TEXT = "#9ca3af"
_LABEL = "#e5e7eb"
_WIN = "#22c55e"
_LOSS = "#ef4444"
_ZONE_LINE = "#4b5563"
_CHART_DPI = 150
_FILL_LAYERS = 10


def _discord_color_to_hex(color: int | None) -> str:
    if color is None:
        return _DEFAULT_ACCENT
    return f"#{color & 0xFFFFFF:06x}"


def _configure_chart_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [
                "Segoe UI",
                "Inter",
                "Helvetica Neue",
                "DejaVu Sans",
                "sans-serif",
            ],
        }
    )


def _zone_top_rs(zone: RankZone, rs_hi: float) -> float:
    if zone.rs_max is not None:
        return float(zone.rs_max)
    return rs_hi


def _label_zones_for(zones: list[RankZone], highlight_key: str | None) -> list[RankZone]:
    if len(zones) <= 3:
        return zones
    if highlight_key:
        return [z for z in zones if z.key == highlight_key]
    return []


def _zone_label_y(
    zone: RankZone,
    rs_lo: float,
    rs_hi: float,
    *,
    avoid_y: float | None = None,
    min_gap: float = 55,
) -> float:
    bottom = max(float(zone.rs_min), rs_lo)
    top = min(_zone_top_rs(zone, rs_hi), rs_hi)
    if top <= bottom:
        return bottom
    y_mid = (bottom + top) / 2.0
    if avoid_y is None or abs(y_mid - avoid_y) >= min_gap:
        return y_mid
    if avoid_y < y_mid:
        return max(bottom + 8, top - min_gap * 0.35)
    return min(top - 8, bottom + min_gap * 0.35)


def _draw_zone_span(
    ax: plt.Axes,
    zone: RankZone,
    rs_lo: float,
    rs_hi: float,
    *,
    is_highlight: bool,
    span_alpha: float,
    highlight_alpha: float,
) -> None:
    top = min(_zone_top_rs(zone, rs_hi), rs_hi)
    bottom = max(float(zone.rs_min), rs_lo)
    if top <= bottom:
        return
    color = zone.color
    ax.axhspan(
        bottom,
        top,
        facecolor=color,
        alpha=highlight_alpha if is_highlight else span_alpha,
        edgecolor=color if is_highlight else "none",
        linewidth=1.2 if is_highlight else 0,
        zorder=0,
    )


def _draw_zone_boundaries(
    ax: plt.Axes,
    zone: RankZone,
    *,
    is_highlight: bool,
    line_w: float,
) -> None:
    color = zone.color
    line_color = color if is_highlight else _ZONE_LINE
    ax.axhline(
        zone.rs_min,
        color=line_color,
        linewidth=line_w + (0.35 if is_highlight else 0),
        alpha=0.9 if is_highlight else 0.5,
        zorder=1,
    )
    if zone.rs_max is None:
        return
    ax.axhline(
        zone.rs_max,
        color=line_color,
        linewidth=line_w + (0.15 if is_highlight else 0),
        alpha=0.75 if is_highlight else 0.4,
        linestyle=(0, (4, 4)),
        zorder=1,
    )


def _draw_zone_label(
    ax: plt.Axes,
    zone: RankZone,
    rs_lo: float,
    rs_hi: float,
    *,
    is_highlight: bool,
    label_size: int,
    avoid_y: float | None = None,
) -> None:
    y_mid = _zone_label_y(zone, rs_lo, rs_hi, avoid_y=avoid_y)
    ax.text(
        1.01,
        y_mid,
        zone.label,
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        color=zone.color,
        fontsize=label_size + (1 if is_highlight else 0),
        fontweight="bold" if is_highlight else "normal",
        clip_on=False,
        zorder=2,
    )


def _draw_rank_zones(
    ax: plt.Axes,
    rs_lo: float,
    rs_hi: float,
    *,
    highlight_key: str | None,
    dense: bool,
    avoid_y: float | None = None,
) -> None:
    zones = zones_intersecting(rs_lo, rs_hi)
    if not zones:
        return

    label_zones = _label_zones_for(zones, highlight_key)
    line_w = 0.7 if dense else 0.9
    span_alpha = 0.05 if dense else 0.07
    highlight_alpha = 0.16 if dense else 0.2

    for zone in zones:
        is_highlight = zone.key == highlight_key
        _draw_zone_span(
            ax,
            zone,
            rs_lo,
            rs_hi,
            is_highlight=is_highlight,
            span_alpha=span_alpha,
            highlight_alpha=highlight_alpha,
        )
        _draw_zone_boundaries(ax, zone, is_highlight=is_highlight, line_w=line_w)

    label_size = 6 if dense else 7
    for zone in label_zones:
        _draw_zone_label(
            ax,
            zone,
            rs_lo,
            rs_hi,
            is_highlight=zone.key == highlight_key,
            label_size=label_size,
            avoid_y=avoid_y,
        )


def _fill_gradient(
    ax: plt.Axes,
    x_values: list,
    y_values: list[int],
    *,
    fill_base: float,
    color: str,
) -> None:
    n = len(y_values)
    if n == 0:
        return
    for layer in range(_FILL_LAYERS):
        t0 = layer / _FILL_LAYERS
        t1 = (layer + 1) / _FILL_LAYERS
        y_lower = [fill_base + (y - fill_base) * t0 for y in y_values]
        y_upper = [fill_base + (y - fill_base) * t1 for y in y_values]
        alpha = 0.018 * (1.0 - t0 * 0.55)
        ax.fill_between(
            x_values,
            y_lower,
            y_upper,
            color=color,
            alpha=alpha,
            linewidth=0,
            zorder=2,
        )


def _format_rs(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def _chart_axis_data(
    points: list[RatingChartPoint],
) -> tuple[list[int], list, str | None, bool]:
    rs_values = [p.rs for p in points]
    has_dates = all(p.played_at is not None for p in points)
    if has_dates:
        return rs_values, [p.played_at for p in points], None, True
    return rs_values, list(range(1, len(points) + 1)), "Partie", False


def _outcome_color(outcome: str | None) -> str | None:
    if outcome == "win":
        return _WIN
    if outcome == "loss":
        return _LOSS
    return None


def _plot_base_line(
    ax: plt.Axes,
    x_values: list,
    rs_values: list[int],
    *,
    line_color: str,
    line_width: float,
    dense: bool,
    base_marker: float,
    marker_edge: float,
) -> None:
    ax.plot(
        x_values,
        rs_values,
        color=line_color,
        linewidth=line_width,
        solid_capstyle="round",
        solid_joinstyle="miter",
        zorder=3,
    )
    if dense:
        return
    ax.plot(
        x_values,
        rs_values,
        linestyle="none",
        marker="o",
        markersize=base_marker,
        markerfacecolor=line_color,
        markeredgecolor=_BG,
        markeredgewidth=marker_edge,
        zorder=3,
    )


def _plot_outcome_markers(
    ax: plt.Axes,
    x_values: list,
    rs_values: list[int],
    points: list[RatingChartPoint],
    *,
    outcome_marker: float,
    marker_edge: float,
) -> bool:
    has_outcomes = False
    for x, y, point in zip(x_values, rs_values, points):
        color = _outcome_color(point.outcome)
        if color is None:
            continue
        has_outcomes = True
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
    return has_outcomes


def _plot_last_point(
    ax: plt.Axes,
    x_values: list,
    rs_values: list[int],
    points: list[RatingChartPoint],
    *,
    line_color: str,
    outcome_marker: float,
) -> None:
    last_x, last_rs = x_values[-1], rs_values[-1]
    last_marker_color = _outcome_color(points[-1].outcome) or line_color
    ax.plot(
        last_x,
        last_rs,
        marker="o",
        markersize=outcome_marker + 1.5,
        markerfacecolor=last_marker_color,
        markeredgecolor=_LABEL,
        markeredgewidth=1.4,
        zorder=5,
    )
    ax.annotate(
        _format_rs(last_rs),
        xy=(last_x, last_rs),
        xytext=(-10, 0),
        textcoords="offset points",
        ha="right",
        va="center",
        color=_LABEL,
        fontsize=9,
        fontweight="bold",
        zorder=5,
    )


def _add_outcome_legend(ax: plt.Axes, *, marker_edge: float) -> None:
    legend = ax.legend(
        handles=[
            Line2D(
                [],
                [],
                marker="o",
                linestyle="None",
                markerfacecolor=_WIN,
                markeredgecolor=_BG,
                markeredgewidth=marker_edge,
                markersize=6,
                label="Victoire",
            ),
            Line2D(
                [],
                [],
                marker="o",
                linestyle="None",
                markerfacecolor=_LOSS,
                markeredgecolor=_BG,
                markeredgewidth=marker_edge,
                markersize=6,
                label="Défaite",
            ),
        ],
        loc="lower left",
        frameon=True,
        facecolor=_PANEL,
        edgecolor=_GRID,
        labelcolor=_TEXT,
        fontsize=7,
        handlelength=1.2,
        handletextpad=0.6,
        borderpad=0.5,
    )
    legend.get_frame().set_alpha(0.92)


def _resolve_total_delta(
    total_delta: int | None,
    points: list[RatingChartPoint],
    rs_values: list[int],
) -> int:
    if total_delta is not None:
        return total_delta
    deltas = [p.rs_delta for p in points if p.rs_delta is not None]
    if deltas:
        return sum(deltas)
    if len(rs_values) > 1:
        return rs_values[-1] - rs_values[0]
    return 0


def _style_chart_axes(
    ax: plt.Axes,
    fig: plt.Figure,
    *,
    has_dates: bool,
    x_label: str | None,
) -> None:
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _p: _format_rs(int(v)))
    )
    ax.tick_params(colors=_TEXT, labelsize=8)
    ax.grid(True, axis="y", color=_GRID, linewidth=0.6, alpha=0.85)
    ax.grid(False, axis="x")
    for spine in ax.spines.values():
        spine.set_color(_GRID)

    if has_dates:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        fig.autofmt_xdate(rotation=0, ha="center")
    elif x_label:
        ax.set_xlabel(x_label, color=_TEXT, fontsize=9)

    ax.set_ylabel("RS", color=_TEXT, fontsize=9)


def render_rating_chart(
    points: list[RatingChartPoint],
    *,
    total_delta: int | None = None,
    current_tier_name: str | None = None,
    accent_color: int | None = None,
) -> bytes:
    if not points:
        raise ValueError("points must not be empty")

    _configure_chart_style()
    line_color = _discord_color_to_hex(accent_color)
    rs_values, x_values, x_label, has_dates = _chart_axis_data(points)

    n = len(points)
    dense = n > 40
    fig_width = 11 if dense else 9
    line_width = 1.4 if dense else 2.2
    base_marker = 3.0 if dense else 5.0
    outcome_marker = 4.0 if dense else 7.0
    marker_edge = 0.8 if dense else 1.2

    fig, ax = plt.subplots(figsize=(fig_width, 3.4), dpi=_CHART_DPI)
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_PANEL)

    y_min, y_max = min(rs_values), max(rs_values)
    padding = max(25, int((y_max - y_min) * 0.15) or 25)
    y_lo = y_min - padding
    y_hi = y_max + padding
    ax.set_ylim(y_lo, y_hi)

    highlight_key = major_rank_key(current_tier_name)
    visible_zones = zones_intersecting(y_lo, y_hi)
    last_rs = rs_values[-1]
    _draw_rank_zones(
        ax,
        y_lo,
        y_hi,
        highlight_key=highlight_key,
        dense=dense,
        avoid_y=last_rs,
    )
    show_zone_labels = bool(highlight_key or len(visible_zones) <= 3)

    fill_base = min(rs_values) - 40
    _fill_gradient(
        ax,
        x_values,
        rs_values,
        fill_base=fill_base,
        color=line_color,
    )
    _plot_base_line(
        ax,
        x_values,
        rs_values,
        line_color=line_color,
        line_width=line_width,
        dense=dense,
        base_marker=base_marker,
        marker_edge=marker_edge,
    )
    has_outcomes = _plot_outcome_markers(
        ax,
        x_values,
        rs_values,
        points,
        outcome_marker=outcome_marker,
        marker_edge=marker_edge,
    )
    _plot_last_point(
        ax,
        x_values,
        rs_values,
        points,
        line_color=line_color,
        outcome_marker=outcome_marker,
    )
    _style_chart_axes(ax, fig, has_dates=has_dates, x_label=x_label)

    if has_outcomes:
        _add_outcome_legend(ax, marker_edge=marker_edge)

    delta = _resolve_total_delta(total_delta, points, rs_values)
    sign = "+" if delta > 0 else ""
    ax.text(
        0.01,
        0.96,
        f"{sign}{delta} RS",
        transform=ax.transAxes,
        ha="left",
        va="top",
        color=_LABEL,
        fontsize=14,
        fontweight="bold",
    )
    ax.text(
        0.01,
        0.88,
        f"{len(points)} parties classées",
        transform=ax.transAxes,
        ha="left",
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
