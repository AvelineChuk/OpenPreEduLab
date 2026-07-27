"""Equity evaluation utilities for preschool resource-allocation results.

The module measures the distribution of a non-negative resource indicator,
such as the Preschool Resource Allocation Index (PRAI), across comparable
localities in one reference year. It describes inequality in observed scores;
it does not establish causes, policy effects, or child-level opportunity.
"""

from __future__ import annotations

from typing import Hashable, Sequence

import numpy as np
import pandas as pd


DEFAULT_SCORE_COLUMN = "resource_allocation_score"


def _validate_values(values: Sequence[float] | pd.Series | np.ndarray) -> np.ndarray:
    """Convert a score sequence to a validated non-negative numeric array."""
    array = pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(dtype=float)
    if array.size < 2:
        raise ValueError("Equity evaluation requires at least two observations.")
    if not np.isfinite(array).all():
        raise ValueError("Equity evaluation values must be finite numeric values.")
    if (array < 0).any():
        raise ValueError("Equity evaluation values must be non-negative.")
    if np.isclose(array.mean(), 0):
        raise ValueError("Equity evaluation is undefined when the mean value is zero.")
    return array


def calculate_cv(values: Sequence[float] | pd.Series | np.ndarray) -> float:
    """Calculate the coefficient of variation (CV).

    CV is the sample standard deviation divided by the arithmetic mean. Lower
    values indicate less relative dispersion across localities. The statistic
    is scale-invariant but should be compared only across substantively
    comparable populations and reference periods.

    Parameters
    ----------
    values:
        At least two non-negative resource-allocation values.

    Returns
    -------
    float
        The coefficient of variation.
    """
    array = _validate_values(values)
    return float(np.std(array, ddof=1) / np.mean(array))


def calculate_gini(values: Sequence[float] | pd.Series | np.ndarray) -> float:
    """Calculate the Gini coefficient for non-negative allocation values.

    A value of zero denotes equality in the observed distribution. Larger
    values denote greater inequality, with the theoretical upper bound
    approaching one for non-negative values.

    Parameters
    ----------
    values:
        At least two non-negative resource-allocation values.

    Returns
    -------
    float
        Gini coefficient in the interval from zero to one.
    """
    array = np.sort(_validate_values(values))
    n_observations = array.size
    ranks = np.arange(1, n_observations + 1)
    gini = (2 * np.sum(ranks * array) / (n_observations * array.sum())) - (
        (n_observations + 1) / n_observations
    )
    return float(np.clip(gini, 0, 1))


def calculate_theil(
    values: Sequence[float] | pd.Series | np.ndarray,
    groups: Sequence[Hashable] | pd.Series | np.ndarray | None = None,
) -> float | dict[str, float]:
    """Calculate the Theil T index, optionally decomposed by group.

    Without groups, the function returns the total Theil T index. With a
    group label for each observation, it returns total inequality and its
    additive within-group and between-group components. The decomposition is
    appropriate only when group labels are substantively meaningful and all
    observations belong to one comparison year.

    Parameters
    ----------
    values:
        At least two non-negative resource-allocation values.
    groups:
        Optional group label for each value, such as province or a documented
        macro-region classification.

    Returns
    -------
    float or dict[str, float]
        Total Theil T index, or a dictionary containing ``total``, ``within``,
        and ``between`` components when groups are supplied.
    """
    array = _validate_values(values)
    mean_value = array.mean()
    ratios = array / mean_value
    # The continuous limit of x * log(x) is zero at x = 0.
    total_terms = np.zeros_like(ratios)
    positive_ratios = ratios > 0
    total_terms[positive_ratios] = (
        ratios[positive_ratios] * np.log(ratios[positive_ratios])
    )
    total = float(np.sum(total_terms) / array.size)

    if groups is None:
        return total

    group_series = pd.Series(groups).reset_index(drop=True)
    if len(group_series) != array.size:
        raise ValueError("groups must have the same length as values.")
    if group_series.isna().any():
        raise ValueError("groups must not contain missing values.")

    frame = pd.DataFrame({"value": array, "group": group_series})
    within = 0.0
    between = 0.0
    for _, group_data in frame.groupby("group", sort=False):
        group_values = group_data["value"].to_numpy(dtype=float)
        group_mean = group_values.mean()
        group_share = group_values.size / array.size
        income_share = group_values.sum() / array.sum()

        if np.isclose(group_mean, 0):
            # A zero-mean group has no within-group dispersion and contributes
            # zero to the Theil T between-group term by the limiting value.
            continue

        group_ratios = group_values / group_mean
        group_terms = np.zeros_like(group_ratios)
        positive_group_ratios = group_ratios > 0
        group_terms[positive_group_ratios] = (
            group_ratios[positive_group_ratios]
            * np.log(group_ratios[positive_group_ratios])
        )
        group_theil = np.sum(group_terms) / group_values.size
        within += income_share * group_theil
        between += income_share * np.log(group_mean / mean_value)

    return {
        "total": total,
        "within": float(within),
        "between": float(between),
    }


def classify_equity(value: float, indicator: str) -> str:
    """Assign a provisional descriptive equity level for one inequality index.

    Thresholds are stated in ``docs/Equity_Evaluation.md``. They are intended
    as transparent reporting conventions for the MVP, not as universal policy
    standards. Lower inequality values receive stronger equity labels.

    Parameters
    ----------
    value:
        Non-negative CV, Gini, or Theil value.
    indicator:
        One of ``"cv"``, ``"gini"``, or ``"theil"``.

    Returns
    -------
    str
        ``"Excellent Equity"``, ``"Moderate Equity"``, or ``"Low Equity"``.
    """
    thresholds = {
        "cv": (0.10, 0.30),
        "gini": (0.20, 0.40),
        "theil": (0.10, 0.20),
    }
    if indicator not in thresholds:
        raise ValueError("indicator must be one of: 'cv', 'gini', 'theil'.")
    if value < 0 or not np.isfinite(value):
        raise ValueError("Equity classification requires a finite non-negative value.")

    excellent_limit, moderate_limit = thresholds[indicator]
    if value <= excellent_limit:
        return "Excellent Equity"
    if value <= moderate_limit:
        return "Moderate Equity"
    return "Low Equity"


def _interpretation(indicator: str, value: float, level: str) -> str:
    """Generate a bounded descriptive interpretation for an equity statistic."""
    descriptions = {
        "cv": "Relative dispersion in observed resource-allocation scores is",
        "gini": "Observed resource-allocation inequality is",
        "theil": "Observed resource-allocation inequality is",
    }
    return f"{descriptions[indicator]} classified as {level.lower()} under the MVP reporting thresholds."


def generate_equity_report(
    results: pd.DataFrame,
    year: int | None = None,
    value_column: str = DEFAULT_SCORE_COLUMN,
    group_column: str | None = None,
) -> pd.DataFrame:
    """Generate a cross-sectional CV, Gini, and Theil equity report.

    A report is calculated for one year because equity measures compare the
    distribution across localities at a common time. If multiple years are
    present, the caller must select one explicitly. When ``group_column`` is
    supplied, Theil within-group and between-group components are appended to
    the report.

    Parameters
    ----------
    results:
        DataFrame containing at least ``city``, ``year``, and the selected
        non-negative value column. It may contain a group column after a
        documented merge with geographic metadata.
    year:
        Reference year for the cross-sectional report. Required for a
        multi-year DataFrame.
    value_column:
        Column whose distribution is evaluated. Defaults to PRAI score.
    group_column:
        Optional categorical grouping field for Theil decomposition.

    Returns
    -------
    pandas.DataFrame
        Equity report with ``indicator``, ``value``, ``equity_level``, and
        ``interpretation`` columns.
    """
    required = {"city", "year", value_column}
    if group_column is not None:
        required.add(group_column)
    missing_columns = sorted(required - set(results.columns))
    if missing_columns:
        raise ValueError(f"Results DataFrame is missing required columns: {missing_columns}")

    available_years = results["year"].dropna().unique()
    if year is None and len(available_years) != 1:
        raise ValueError("Specify year when generating a report from multiple years.")
    report_year = available_years[0] if year is None else year
    cross_section = results.loc[results["year"] == report_year].copy()
    if cross_section.empty:
        raise ValueError(f"No results are available for year {report_year}.")

    values = cross_section[value_column]
    cv_value = calculate_cv(values)
    gini_value = calculate_gini(values)
    theil_result = calculate_theil(values, cross_section[group_column] if group_column else None)
    theil_value = theil_result["total"] if isinstance(theil_result, dict) else theil_result

    report_items = [("Coefficient of Variation", "cv", cv_value), ("Gini Coefficient", "gini", gini_value), ("Theil Index", "theil", theil_value)]
    report_rows = []
    for label, key, value in report_items:
        level = classify_equity(value, key)
        report_rows.append(
            {
                "indicator": label,
                "value": round(value, 6),
                "equity_level": level,
                "interpretation": _interpretation(key, value, level),
            }
        )

    if isinstance(theil_result, dict):
        report_rows.extend(
            [
                {
                    "indicator": "Theil Within-Group Component",
                    "value": round(theil_result["within"], 6),
                    "equity_level": "Decomposition component",
                    "interpretation": "Share of Theil inequality attributable to variation within the supplied groups.",
                },
                {
                    "indicator": "Theil Between-Group Component",
                    "value": round(theil_result["between"], 6),
                    "equity_level": "Decomposition component",
                    "interpretation": "Share of Theil inequality attributable to differences between the supplied groups.",
                },
            ]
        )

    return pd.DataFrame(report_rows)
