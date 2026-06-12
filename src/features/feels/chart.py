from __future__ import annotations

import io

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from db import MatchFeelsRecord

_BG = "#0a0e14"
_PANEL = "#0d1117"
_GRID = "#1f2937"
_TEXT = "#9ca3af"
_LABEL = "#e5e7eb"
_WIN = "#22c55e"
_LOSS = "#ef4444"
_NEUTRAL = "#3b82f6"
_AVG_LINE = "#f4c430"
_CHART_DPI = 150


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


def _bar_color(outcome: str | None) -> str:
    if outcome == "win":
        return _WIN
    if outcome == "loss":
        return _LOSS
    return _NEUTRAL


def _bar_label(record: MatchFeelsRecord) -> str:
    parts: list[str] = []
    if record.hero_name:
        parts.append(record.hero_name)
    if record.played_at:
        parts.append(record.played_at.strftime("%d/%m"))
    if not parts:
        parts.append(record.match_id[:8])
    return "\n".join(parts)


def render_feels_chart(records: list[MatchFeelsRecord]) -> bytes:
    """Graphique en barres des notes de ressenti (1-10) par match noté."""
    if not records:
        raise ValueError("records must not be empty")

    _configure_chart_style()

    x_values = list(range(1, len(records) + 1))
    ratings = [r.rating for r in records]
    colors = [_bar_color(r.outcome) for r in records]
    average = sum(ratings) / len(ratings)

    fig_width = max(7.0, min(12.0, 1.0 + len(records) * 0.9))
    fig, ax = plt.subplots(figsize=(fig_width, 3.8), dpi=_CHART_DPI)
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_PANEL)

    bars = ax.bar(
        x_values,
        ratings,
        color=colors,
        width=0.62,
        edgecolor=_BG,
        linewidth=0.8,
        zorder=3,
    )
    for bar, rating in zip(bars, ratings):
        ax.annotate(
            str(rating),
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color=_LABEL,
            fontsize=9,
            fontweight="bold",
            zorder=4,
        )

    ax.axhline(
        average,
        color=_AVG_LINE,
        linewidth=1.2,
        linestyle=(0, (5, 3)),
        alpha=0.9,
        zorder=2,
    )
    ax.annotate(
        f"moyenne {average:.1f}",
        xy=(1.0, average),
        xycoords=("axes fraction", "data"),
        xytext=(-6, 4),
        textcoords="offset points",
        ha="right",
        va="bottom",
        color=_AVG_LINE,
        fontsize=8,
        fontweight="bold",
        zorder=4,
    )

    ax.set_ylim(0, 11)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.set_xlim(0.4, len(records) + 0.6)
    ax.set_xticks(x_values)
    ax.set_xticklabels(
        [_bar_label(r) for r in records],
        fontsize=7,
        color=_TEXT,
    )

    ax.tick_params(colors=_TEXT, labelsize=8)
    ax.grid(True, axis="y", color=_GRID, linewidth=0.6, alpha=0.85)
    ax.grid(False, axis="x")
    for spine in ax.spines.values():
        spine.set_color(_GRID)
    ax.set_ylabel("Note de ressenti", color=_TEXT, fontsize=9)

    ax.text(
        0.01,
        0.96,
        f"{len(records)} match{'s' if len(records) > 1 else ''} noté"
        f"{'s' if len(records) > 1 else ''}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        color=_LABEL,
        fontsize=10,
        fontweight="bold",
    )

    legend = ax.legend(
        handles=[
            Patch(facecolor=_WIN, label="Victoire"),
            Patch(facecolor=_LOSS, label="Défaite"),
            Line2D(
                [],
                [],
                color=_AVG_LINE,
                linewidth=1.2,
                linestyle=(0, (5, 3)),
                label="Moyenne",
            ),
        ],
        loc="upper right",
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

    plt.tight_layout(pad=0.8)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()
