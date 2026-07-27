"""Transparent MVP forecasts for preschool education resource planning.

Population forecasts use separate city-level linear time-trend regressions.
Teacher and fiscal projections translate forecast child population into
resource requirements under explicit, user-supplied planning assumptions.
These functions create scenario-dependent projections, not factual forecasts
or policy-effect estimates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


FORECAST_POPULATION_COLUMN = "future_child_population"


def _validate_forecast_years(forecast_years: Sequence[int]) -> list[int]:
    """Validate and return unique, ordered future forecast years."""
    years = sorted({int(year) for year in forecast_years})
    if not years:
        raise ValueError("forecast_years must contain at least one future year.")
    return years


def forecast_population(
    historical_data: pd.DataFrame,
    forecast_years: Sequence[int],
    population_column: str = "resident_preschool_age_population",
) -> pd.DataFrame:
    """Forecast preschool-age child population by city with linear regression.

    A separate ordinary least-squares model is fit for every city:
    ``population = intercept + slope * year``. The function is intended for
    transparent MVP trend extrapolation when only short annual series are
    available. Negative extrapolations are truncated to zero because a child
    population cannot be negative.

    Parameters
    ----------
    historical_data:
        City-year panel containing ``city``, ``year``, and the selected
        population column.
    forecast_years:
        Years to forecast. Every supplied year must be later than the latest
        observed year for each city.
    population_column:
        Name of the observed preschool-age population field.

    Returns
    -------
    pandas.DataFrame
        ``city``, ``year``, and ``future_child_population`` for the requested
        years. The output contains projections only, not historical records.
    """
    required = {"city", "year", population_column}
    missing = sorted(required - set(historical_data.columns))
    if missing:
        raise ValueError(f"Historical data are missing required columns: {missing}")
    if historical_data.duplicated(["city", "year"]).any():
        raise ValueError("Historical data must contain one observation per city-year.")

    years = _validate_forecast_years(forecast_years)
    data = historical_data.loc[:, ["city", "year", population_column]].copy()
    data["year"] = pd.to_numeric(data["year"], errors="coerce")
    data[population_column] = pd.to_numeric(data[population_column], errors="coerce")
    if data.isna().any().any() or not np.isfinite(data[["year", population_column]].to_numpy()).all():
        raise ValueError("Historical year and population values must be finite numeric values.")
    if (data[population_column] < 0).any():
        raise ValueError("Historical population values must be non-negative.")

    forecast_rows: list[dict[str, float | int | str]] = []
    for city, city_data in data.groupby("city", sort=True):
        city_data = city_data.sort_values("year")
        if len(city_data) < 2:
            raise ValueError(f"At least two historical years are required for city '{city}'.")
        last_observed_year = int(city_data["year"].max())
        invalid_years = [year for year in years if year <= last_observed_year]
        if invalid_years:
            raise ValueError(
                f"Forecast years must be later than {last_observed_year} for city '{city}': {invalid_years}"
            )

        model = LinearRegression()
        model.fit(city_data[["year"]], city_data[population_column])
        predictions = model.predict(pd.DataFrame({"year": years}, dtype=float))
        for year, prediction in zip(years, predictions, strict=True):
            forecast_rows.append(
                {
                    "city": city,
                    "year": year,
                    FORECAST_POPULATION_COLUMN: round(max(0.0, float(prediction)), 2),
                }
            )

    return pd.DataFrame(forecast_rows)


def _resolve_planning_assumption(
    forecast_data: pd.DataFrame,
    assumption: float | str,
    assumption_name: str,
) -> pd.Series:
    """Resolve a positive scalar or column-based planning assumption."""
    if isinstance(assumption, str):
        if assumption not in forecast_data.columns:
            raise ValueError(f"Assumption column '{assumption}' is not present in forecast data.")
        values = pd.to_numeric(forecast_data[assumption], errors="coerce")
    else:
        values = pd.Series(float(assumption), index=forecast_data.index)
    if values.isna().any() or not np.isfinite(values.to_numpy()).all() or (values <= 0).any():
        raise ValueError(f"{assumption_name} must contain finite values greater than zero.")
    return values


def forecast_teacher_demand(
    population_forecast: pd.DataFrame,
    teacher_child_ratio: float | str,
) -> pd.DataFrame:
    """Translate forecast child population into projected FTE teacher demand.

    ``teacher_child_ratio`` is defined as the planned number of FTE teachers
    per child (for example, 0.065 means 6.5 FTE teachers per 100 children).
    It may be a positive scalar applied to all city-years or the name of a
    positive column in ``population_forecast`` for city-specific assumptions.

    Parameters
    ----------
    population_forecast:
        Output from :func:`forecast_population` containing city, year, and
        ``future_child_population``.
    teacher_child_ratio:
        FTE teachers per child, as a scalar or column name.

    Returns
    -------
    pandas.DataFrame
        City-year projections with child population and ``future_teacher_demand``.
    """
    required = {"city", "year", FORECAST_POPULATION_COLUMN}
    missing = sorted(required - set(population_forecast.columns))
    if missing:
        raise ValueError(f"Population forecast is missing required columns: {missing}")
    population = pd.to_numeric(population_forecast[FORECAST_POPULATION_COLUMN], errors="coerce")
    if population.isna().any() or (population < 0).any():
        raise ValueError("Forecast child population must be finite and non-negative.")

    ratio = _resolve_planning_assumption(
        population_forecast, teacher_child_ratio, "teacher_child_ratio"
    )
    result = population_forecast.loc[:, ["city", "year", FORECAST_POPULATION_COLUMN]].copy()
    result["future_teacher_demand"] = (population * ratio).round(2)
    return result


def forecast_fiscal_requirement(
    population_forecast: pd.DataFrame,
    cost_per_child: float | str,
) -> pd.DataFrame:
    """Translate forecast child population into a fiscal-resource requirement.

    ``cost_per_child`` is an explicit planning assumption in currency per child
    per year. It may be a positive scalar or the name of a positive column in
    ``population_forecast`` for city-specific assumptions. Users should state
    the price year and whether the cost represents public expenditure, total
    operating cost, or another clearly defined fiscal scope.

    Parameters
    ----------
    population_forecast:
        Output from :func:`forecast_population` containing city, year, and
        ``future_child_population``.
    cost_per_child:
        Annual cost per child as a scalar or column name.

    Returns
    -------
    pandas.DataFrame
        City-year projections with child population and ``future_fiscal_need``.
    """
    required = {"city", "year", FORECAST_POPULATION_COLUMN}
    missing = sorted(required - set(population_forecast.columns))
    if missing:
        raise ValueError(f"Population forecast is missing required columns: {missing}")
    population = pd.to_numeric(population_forecast[FORECAST_POPULATION_COLUMN], errors="coerce")
    if population.isna().any() or (population < 0).any():
        raise ValueError("Forecast child population must be finite and non-negative.")

    cost = _resolve_planning_assumption(population_forecast, cost_per_child, "cost_per_child")
    result = population_forecast.loc[:, ["city", "year", FORECAST_POPULATION_COLUMN]].copy()
    result["future_fiscal_need"] = (population * cost).round(2)
    return result
