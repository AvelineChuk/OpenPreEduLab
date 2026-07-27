"""Reusable visualisations for Preschool Resource Allocation Index (PRAI) results.

The functions in this module render calculated results; they do not infer
causal effects or generate policy conclusions. All plots may be saved through
an explicit output path to support reproducible research workflows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


SCORE_COLUMN = "resource_allocation_score"
DIMENSION_COLUMNS: tuple[str, ...] = (
    "financial",
    "human",
    "material",
    "demand_responsiveness",
)
DIMENSION_LABELS: tuple[str, ...] = (
    "Financial\nResources",
    "Human\nResources",
    "Material\nResources",
    "Demand\nResponsiveness",
)


def _validate_score_results(results: pd.DataFrame) -> None:
    """Validate that a result table contains the fields needed for score plots."""
    required = {"city", "year", SCORE_COLUMN}
    missing = sorted(required - set(results.columns))
    if missing:
        raise ValueError(f"Results DataFrame is missing required columns: {missing}")
    if results[SCORE_COLUMN].isna().any():
        raise ValueError("Resource allocation scores must not contain missing values.")


def _save_figure(fig: plt.Figure, output_path: str | Path | None) -> None:
    """Save a figure when an explicit output path is supplied."""
    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")


def plot_resource_allocation_ranking(
    results: pd.DataFrame,
    year: int | None = None,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot a descending city ranking of PRAI scores for one year.

    Parameters
    ----------
    results:
        PRAI score DataFrame containing ``city``, ``year``, and
        ``resource_allocation_score``.
    year:
        Year to plot. It is required when ``results`` contains multiple years.
    ax:
        Existing matplotlib axes. A new figure and axes are created when not
        supplied.
    output_path:
        Optional output file path. Figures are saved at 300 dpi when supplied.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the ranking chart.
    """
    _validate_score_results(results)
    available_years = results["year"].unique()
    if year is None and len(available_years) != 1:
        raise ValueError("Specify year when ranking results contain multiple years.")

    plot_year = available_years[0] if year is None else year
    ranked = results.loc[results["year"] == plot_year, ["city", SCORE_COLUMN]].copy()
    if ranked.empty:
        raise ValueError(f"No PRAI results are available for year {plot_year}.")
    ranked = ranked.sort_values(SCORE_COLUMN, ascending=True)

    if ax is None:
        fig, ax = plt.subplots(figsize=(9, max(4, 0.45 * len(ranked))))
    else:
        fig = ax.figure

    bars = ax.barh(ranked["city"], ranked[SCORE_COLUMN], color="#3B6EA5")
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Resource Allocation Score (0–100)")
    ax.set_ylabel("City")
    ax.set_title(f"Preschool Resource Allocation Ranking, {plot_year}")
    ax.grid(axis="x", linestyle="--", linewidth=0.6, alpha=0.5)
    ax.set_axisbelow(True)
    _save_figure(fig, output_path)
    return ax


def plot_trend_analysis(
    results: pd.DataFrame,
    cities: Sequence[str] | None = None,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot city-level PRAI score trajectories across years.

    Parameters
    ----------
    results:
        PRAI score DataFrame containing ``city``, ``year``, and
        ``resource_allocation_score``.
    cities:
        Optional city names to include. When omitted, all cities are shown.
    ax:
        Existing matplotlib axes. A new figure and axes are created when not
        supplied.
    output_path:
        Optional output file path. Figures are saved at 300 dpi when supplied.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the trend chart.
    """
    _validate_score_results(results)
    plot_data = results.copy()
    if cities is not None:
        plot_data = plot_data.loc[plot_data["city"].isin(cities)].copy()
        missing_cities = sorted(set(cities) - set(plot_data["city"]))
        if missing_cities:
            raise ValueError(f"No PRAI results are available for cities: {missing_cities}")

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure

    for city, city_data in plot_data.groupby("city", sort=True):
        city_data = city_data.sort_values("year")
        ax.plot(
            city_data["year"],
            city_data[SCORE_COLUMN],
            marker="o",
            linewidth=1.8,
            markersize=4,
            label=city,
        )

    ax.set_ylim(0, 100)
    ax.set_xlabel("Year")
    ax.set_ylabel("Resource Allocation Score (0–100)")
    ax.set_title("Preschool Resource Allocation Score Trends")
    ax.grid(linestyle="--", linewidth=0.6, alpha=0.5)
    ax.legend(title="City", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    fig.tight_layout()
    _save_figure(fig, output_path)
    return ax


def calculate_dimension_scores(normalised_indicators: pd.DataFrame) -> pd.DataFrame:
    """Aggregate normalised PRAI indicators into four 0–100 dimension scores.

    This helper implements the documented MVP rule of equal indicator weights
    within each dimension. Its input must be the output of
    ``models.allocation.normalize_indicators``; it intentionally does not
    re-normalise raw data.

    Parameters
    ----------
    normalised_indicators:
        Normalised indicator DataFrame with identifier fields and the eleven
        PRAI indicator columns.

    Returns
    -------
    pandas.DataFrame
        City-year table with Financial, Human, Material, and Demand
        Responsiveness scores on a 0–100 scale.
    """
    from models.allocation import DIMENSION_INDICATORS

    required = {"city", "year", *DIMENSION_COLUMNS}
    # ``required`` is expanded below because input columns use the individual
    # indicator names rather than the output dimension labels.
    required_indicators = {
        indicator for indicators in DIMENSION_INDICATORS.values() for indicator in indicators
    }
    missing = sorted(({"city", "year"} | required_indicators) - set(normalised_indicators.columns))
    if missing:
        raise ValueError(f"Normalised indicators are missing required columns: {missing}")

    scores = normalised_indicators.loc[:, ["city", "year"]].copy()
    for dimension, indicators in DIMENSION_INDICATORS.items():
        scores[dimension] = normalised_indicators.loc[:, list(indicators)].mean(axis=1) * 100
    return scores


def plot_dimension_radar(
    dimension_scores: pd.DataFrame,
    year: int | None = None,
    cities: Sequence[str] | None = None,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot four-dimensional PRAI profiles for selected cities in one year.

    Parameters
    ----------
    dimension_scores:
        DataFrame containing ``city``, ``year``, and the four columns
        ``financial``, ``human``, ``material``, and ``demand_responsiveness``.
        Values must be on a 0–100 scale.
    year:
        Year to plot. Required when more than one year is present.
    cities:
        Optional city names to include. When omitted, all cities in the chosen
        year are plotted.
    ax:
        Existing polar matplotlib axes. A new polar axes is created when not
        supplied.
    output_path:
        Optional output file path. Figures are saved at 300 dpi when supplied.

    Returns
    -------
    matplotlib.axes.Axes
        The polar axes containing the radar chart.
    """
    required = {"city", "year", *DIMENSION_COLUMNS}
    missing = sorted(required - set(dimension_scores.columns))
    if missing:
        raise ValueError(f"Dimension score DataFrame is missing required columns: {missing}")

    available_years = dimension_scores["year"].unique()
    if year is None and len(available_years) != 1:
        raise ValueError("Specify year when dimension scores contain multiple years.")
    plot_year = available_years[0] if year is None else year
    plot_data = dimension_scores.loc[dimension_scores["year"] == plot_year].copy()

    if cities is not None:
        plot_data = plot_data.loc[plot_data["city"].isin(cities)].copy()
        missing_cities = sorted(set(cities) - set(plot_data["city"]))
        if missing_cities:
            raise ValueError(f"No dimension scores are available for cities: {missing_cities}")
    if plot_data.empty:
        raise ValueError(f"No dimension scores are available for year {plot_year}.")

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"projection": "polar"})
    else:
        fig = ax.figure
        if ax.name != "polar":
            raise ValueError("Radar charts require polar matplotlib axes.")

    angles = np.linspace(0, 2 * np.pi, len(DIMENSION_COLUMNS), endpoint=False).tolist()
    closed_angles = angles + angles[:1]
    for _, row in plot_data.sort_values("city").iterrows():
        values = row.loc[list(DIMENSION_COLUMNS)].astype(float).tolist()
        closed_values = values + values[:1]
        ax.plot(closed_angles, closed_values, linewidth=1.8, label=row["city"])
        ax.fill(closed_angles, closed_values, alpha=0.08)

    ax.set_xticks(angles)
    ax.set_xticklabels(DIMENSION_LABELS)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"])
    ax.set_title(f"PRAI Dimension Profiles, {plot_year}", pad=28)
    ax.legend(title="City", bbox_to_anchor=(1.2, 1.1), loc="upper left", frameon=False)
    _save_figure(fig, output_path)
    return ax


def plot_score_heatmap(
    results: pd.DataFrame,
    cities: Iterable[str] | None = None,
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot a city-by-year heatmap of PRAI scores without seaborn.

    Parameters
    ----------
    results:
        PRAI score DataFrame containing ``city``, ``year``, and
        ``resource_allocation_score``.
    cities:
        Optional city names to include. When omitted, all cities are shown.
    ax:
        Existing matplotlib axes. A new figure and axes are created when not
        supplied.
    output_path:
        Optional output file path. Figures are saved at 300 dpi when supplied.

    Returns
    -------
    matplotlib.axes.Axes
        The axes containing the heatmap.
    """
    _validate_score_results(results)
    plot_data = results.copy()
    if cities is not None:
        city_list = list(cities)
        plot_data = plot_data.loc[plot_data["city"].isin(city_list)].copy()
        missing_cities = sorted(set(city_list) - set(plot_data["city"]))
        if missing_cities:
            raise ValueError(f"No PRAI results are available for cities: {missing_cities}")

    matrix = plot_data.pivot(index="city", columns="year", values=SCORE_COLUMN).sort_index()
    if matrix.empty:
        raise ValueError("No PRAI results are available for the requested heatmap.")

    if ax is None:
        fig, ax = plt.subplots(figsize=(9, max(4, 0.45 * len(matrix))))
    else:
        fig = ax.figure

    image = ax.imshow(matrix.to_numpy(), aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
    ax.set_xticks(np.arange(len(matrix.columns)), labels=matrix.columns)
    ax.set_yticks(np.arange(len(matrix.index)), labels=matrix.index)
    ax.set_xlabel("Year")
    ax.set_ylabel("City")
    ax.set_title("Preschool Resource Allocation Scores by City and Year")

    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            value = matrix.iat[row_index, column_index]
            if pd.notna(value):
                text_colour = "white" if value < 45 else "black"
                ax.text(column_index, row_index, f"{value:.1f}", ha="center", va="center", color=text_colour, fontsize=8)

    colourbar = fig.colorbar(image, ax=ax, pad=0.02)
    colourbar.set_label("Resource Allocation Score (0–100)")
    _save_figure(fig, output_path)
    return ax
