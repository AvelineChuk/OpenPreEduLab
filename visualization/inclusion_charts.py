"""Academic visualisations for the inclusive education research prototype.

The charts display supplied dimension scores and descriptive support gaps.
They do not diagnose children or institutions and do not imply causal pathways.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import to_rgb

from models.inclusion import DIMENSION_LABELS, SCORE_COLUMNS


PALETTE = {
    "blue": "#496B7C",
    "green": "#3F7357",
    "sand": "#B98F62",
    "navy": "#1B2D35",
    "soft": "#E8EFEB",
}


def _relative_luminance(colour: Sequence[float]) -> float:
    """Return WCAG relative luminance for an RGB or RGBA colour."""
    channels = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in colour[:3]
    ]
    return (
        0.2126 * channels[0]
        + 0.7152 * channels[1]
        + 0.0722 * channels[2]
    )


def _contrast_ratio(first_luminance: float, second_luminance: float) -> float:
    """Return the WCAG contrast ratio between two relative luminances."""
    lighter = max(first_luminance, second_luminance)
    darker = min(first_luminance, second_luminance)
    return (lighter + 0.05) / (darker + 0.05)


def _contrast_text_color(background: Sequence[float]) -> str:
    """Choose the higher-contrast chart text colour for a background."""
    background_luminance = _relative_luminance(background)
    light_contrast = _contrast_ratio(background_luminance, 1.0)
    dark_luminance = _relative_luminance(to_rgb(PALETTE["navy"]))
    dark_contrast = _contrast_ratio(background_luminance, dark_luminance)
    return "white" if light_contrast > dark_contrast else PALETTE["navy"]


def _save(fig: plt.Figure, output_path: str | Path | None) -> None:
    """Save a figure at publication-oriented resolution when requested."""
    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")


def _validate_scores(scores: pd.DataFrame) -> None:
    """Validate the common five-dimension score table."""
    missing = sorted(set(SCORE_COLUMNS) - set(scores.columns))
    if missing:
        raise ValueError(f"Inclusive dimension scores are missing columns: {missing}")
    values = scores.loc[:, list(SCORE_COLUMNS)].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not values.apply(
        lambda column: column.between(0, 100)
    ).all().all():
        raise ValueError("Inclusive dimension scores must be complete values on the 0–100 scale.")


def plot_five_dimension_radar(
    scores: pd.DataFrame,
    institution_id: str | None = None,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot one institution or the sample mean across all five dimensions."""
    _validate_scores(scores)
    if institution_id is None:
        values = scores.loc[:, list(SCORE_COLUMNS)].mean()
        title = "Mean Five-Dimension Inclusive Education Profile"
    else:
        if "institution_id" not in scores.columns:
            raise ValueError("institution_id is required for an institution radar chart.")
        selected = scores.loc[scores["institution_id"] == institution_id]
        if selected.empty:
            raise ValueError(f"No inclusive education scores are available for '{institution_id}'.")
        values = selected.iloc[0].loc[list(SCORE_COLUMNS)]
        title = f"Five-Dimension Profile: {institution_id}"

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 7), subplot_kw={"projection": "polar"})
    else:
        fig = ax.figure
        if ax.name != "polar":
            raise ValueError("Five-dimension radar charts require polar axes.")
    angles = np.linspace(0, 2 * np.pi, len(SCORE_COLUMNS), endpoint=False).tolist()
    closed_angles = angles + angles[:1]
    closed_values = values.astype(float).tolist() + [float(values.iloc[0])]
    ax.plot(closed_angles, closed_values, color=PALETTE["green"], linewidth=2.2)
    ax.fill(closed_angles, closed_values, color=PALETTE["green"], alpha=0.14)
    ax.set_xticks(angles)
    ax.set_xticklabels([DIMENSION_LABELS[column] for column in SCORE_COLUMNS])
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_title(title, pad=28, color=PALETTE["navy"])
    _save(fig, output_path)
    return ax


def plot_support_pathway(
    scores: pd.DataFrame,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot mean Policy -> Resource -> Practice -> Participation -> Equity scores."""
    _validate_scores(scores)
    means = scores.loc[:, list(SCORE_COLUMNS)].mean()
    labels = [DIMENSION_LABELS[column] for column in SCORE_COLUMNS]
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, 4.8))
    else:
        fig = ax.figure
    x = np.arange(len(labels))
    ax.plot(x, means, color=PALETTE["blue"], marker="o", linewidth=2.3, markersize=9)
    ax.fill_between(x, means, alpha=0.08, color=PALETTE["blue"])
    for index, value in enumerate(means):
        ax.text(index, value + 3, f"{value:.1f}", ha="center", color=PALETTE["navy"])
        if index < len(labels) - 1:
            ax.annotate("", xy=(index + 0.88, means.iloc[index + 1]), xytext=(index + 0.12, value), arrowprops={"arrowstyle": "->", "color": "#9AACA6", "lw": 1})
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Mean score (0–100)")
    ax.set_title("Inclusive Education Research Pathway — Descriptive Profile")
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45)
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, output_path)
    return ax


def plot_support_gap_bars(
    gaps: pd.DataFrame,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot mean signed Resource→Practice and Practice→Participation gaps."""
    columns = ["gap_resource_practice", "gap_practice_participation"]
    missing = sorted(set(columns) - set(gaps.columns))
    if missing:
        raise ValueError(f"Support-gap data are missing columns: {missing}")
    means = gaps[columns].apply(pd.to_numeric, errors="coerce").mean()
    if means.isna().any():
        raise ValueError("Support-gap data must contain finite numeric values.")
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4.8))
    else:
        fig = ax.figure
    labels = ["Resource → Practice", "Practice → Participation"]
    colours = [PALETTE["sand"], PALETTE["green"]]
    bars = ax.bar(labels, means, color=colours, width=0.58)
    ax.axhline(0, color=PALETTE["navy"], linewidth=0.8)
    ax.bar_label(bars, fmt="%.1f", padding=4)
    ax.set_ylabel("Mean signed gap (score points)")
    ax.set_title("Support Conversion Gaps")
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.4)
    ax.set_axisbelow(True)
    _save(fig, output_path)
    return ax


def plot_institution_comparison(
    scores: pd.DataFrame,
    institutions: Sequence[str],
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Compare selected institutions across the five descriptive dimensions."""
    _validate_scores(scores)
    if "institution_id" not in scores.columns:
        raise ValueError("institution_id is required for institution comparison.")
    selected_ids = list(dict.fromkeys(institutions))
    if not selected_ids:
        raise ValueError("Select at least one institution for comparison.")
    selected = scores.loc[scores["institution_id"].isin(selected_ids)].copy()
    missing_ids = sorted(set(selected_ids) - set(selected["institution_id"]))
    if missing_ids:
        raise ValueError(f"No scores are available for institutions: {missing_ids}")
    if ax is None:
        fig, ax = plt.subplots(figsize=(11, max(4.8, len(selected) * 0.55)))
    else:
        fig = ax.figure
    matrix = selected.set_index("institution_id")[list(SCORE_COLUMNS)]
    matrix.plot(kind="barh", ax=ax, width=0.8, colormap="viridis")
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score (0–100)")
    ax.set_ylabel("Synthetic institution")
    ax.set_title("Institution Dimension Comparison")
    ax.legend([DIMENSION_LABELS[column] for column in SCORE_COLUMNS], bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    ax.grid(axis="x", linestyle="--", linewidth=0.6, alpha=0.4)
    _save(fig, output_path)
    return ax


def plot_dimension_heatmap(
    scores: pd.DataFrame,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot an institution-by-dimension score heatmap."""
    _validate_scores(scores)
    if "institution_id" not in scores.columns:
        raise ValueError("institution_id is required for the dimension heatmap.")
    matrix = scores.set_index("institution_id")[list(SCORE_COLUMNS)]
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, max(5, 0.45 * len(matrix))))
    else:
        fig = ax.figure
    image = ax.imshow(matrix.to_numpy(), aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
    ax.set_xticks(np.arange(len(SCORE_COLUMNS)), [DIMENSION_LABELS[column] for column in SCORE_COLUMNS], rotation=25, ha="right")
    ax.set_yticks(np.arange(len(matrix)), matrix.index)
    ax.set_title("Inclusive Education Dimension Heatmap")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = matrix.iat[row, column]
            background = image.cmap(image.norm(value))
            ax.text(
                column,
                row,
                f"{value:.0f}",
                ha="center",
                va="center",
                fontsize=8,
                color=_contrast_text_color(background),
            )
    colourbar = fig.colorbar(image, ax=ax, pad=0.02)
    colourbar.set_label("Score (0–100)")
    _save(fig, output_path)
    return ax
