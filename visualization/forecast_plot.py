"""Visualisation utilities for historical preschool trends and projections."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_population_forecast(
    historical_data: pd.DataFrame,
    population_forecast: pd.DataFrame,
    city: str,
    historical_population_column: str = "resident_preschool_age_population",
    ax: plt.Axes | None = None,
    output_path: str | Path | None = None,
) -> plt.Axes:
    """Plot observed child population and projected population for one city.

    Historical observations and model projections are deliberately displayed
    with different line styles. The function does not calculate forecasts; it
    only visualises values already supplied by the caller.

    Parameters
    ----------
    historical_data:
        Historical city-year data containing the selected population column.
    population_forecast:
        Output from ``models.forecast.forecast_population``.
    city:
        City to display.
    historical_population_column:
        Column containing observed preschool-age population.
    ax:
        Existing matplotlib axes. A new figure and axes are created when not
        supplied.
    output_path:
        Optional output path; supplied figures are saved at 300 dpi.

    Returns
    -------
    matplotlib.axes.Axes
        Axes containing the historical and forecast population series.
    """
    historical_required = {"city", "year", historical_population_column}
    forecast_required = {"city", "year", "future_child_population"}
    missing_historical = sorted(historical_required - set(historical_data.columns))
    missing_forecast = sorted(forecast_required - set(population_forecast.columns))
    if missing_historical:
        raise ValueError(f"Historical data are missing required columns: {missing_historical}")
    if missing_forecast:
        raise ValueError(f"Forecast data are missing required columns: {missing_forecast}")

    observed = historical_data.loc[historical_data["city"] == city].sort_values("year")
    projected = population_forecast.loc[population_forecast["city"] == city].sort_values("year")
    if observed.empty:
        raise ValueError(f"No historical population data are available for city '{city}'.")
    if projected.empty:
        raise ValueError(f"No population forecast is available for city '{city}'.")

    if ax is None:
        fig, ax = plt.subplots(figsize=(9, 5))
    else:
        fig = ax.figure

    ax.plot(
        observed["year"],
        observed[historical_population_column],
        color="#2B6CB0",
        marker="o",
        linewidth=2,
        label="Historical observation",
    )
    ax.plot(
        projected["year"],
        projected["future_child_population"],
        color="#C05621",
        marker="o",
        linestyle="--",
        linewidth=2,
        label="Model projection",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Preschool-age child population")
    ax.set_title(f"Historical Trend and Population Projection: {city}")
    ax.grid(linestyle="--", linewidth=0.6, alpha=0.5)
    ax.legend(frameon=False)
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
    return ax
