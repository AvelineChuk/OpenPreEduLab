"""Data Envelopment Analysis utilities for preschool education efficiency.

The default model is an input-oriented variable-returns-to-scale (VRS/BCC)
DEA. It compares city-year decision-making units within the same year and
estimates the proportional input contraction possible while holding selected
outputs constant. DEA scores are relative to the observed comparison set.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
from scipy.optimize import linprog


def prepare_efficiency_data(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare a minimal DEA-ready table from the PRAI sample-data schema.

    The helper provides an illustrative specification for the synthetic data:
    total public expenditure, FTE teachers, and indoor area are inputs; total
    enrolment, age-specific enrolment coverage, and qualified-teacher rate are
    outputs. Researchers must justify and validate any specification used with
    real data before drawing substantive conclusions.

    Parameters
    ----------
    data:
        Raw city-year data following ``docs/Data_Dictionary.md``.

    Returns
    -------
    pandas.DataFrame
        A city-year DataFrame with named DEA input and output columns.
    """
    required = {
        "city",
        "year",
        "government_expenditure_per_child_yuan",
        "enrolled_children",
        "fte_teacher_count",
        "usable_indoor_area_sqm",
        "resident_preschool_age_population",
        "resident_target_age_children_enrolled",
        "qualified_teacher_rate_pct",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Cannot prepare DEA data; missing columns: {missing}")

    prepared = data.loc[:, ["city", "year"]].copy()
    prepared["total_government_expenditure_yuan"] = (
        data["government_expenditure_per_child_yuan"] * data["enrolled_children"]
    )
    prepared["fte_teacher_count"] = data["fte_teacher_count"]
    prepared["usable_indoor_area_sqm"] = data["usable_indoor_area_sqm"]
    prepared["enrolled_children"] = data["enrolled_children"]
    prepared["age_specific_enrolment_coverage_pct"] = (
        100
        * data["resident_target_age_children_enrolled"]
        / data["resident_preschool_age_population"]
    )
    prepared["qualified_teacher_rate_pct"] = data["qualified_teacher_rate_pct"]
    return prepared


def _validate_dea_data(
    data: pd.DataFrame,
    input_columns: Sequence[str],
    output_columns: Sequence[str],
) -> None:
    """Validate DEA data and column selections before optimisation."""
    if len(data) < 2:
        raise ValueError("DEA requires at least two decision-making units.")
    if not input_columns or not output_columns:
        raise ValueError("DEA requires at least one input and one output column.")

    required = set(input_columns) | set(output_columns)
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"DEA data are missing selected columns: {missing}")
    overlap = sorted(set(input_columns) & set(output_columns))
    if overlap:
        raise ValueError(f"A variable cannot be both a DEA input and output: {overlap}")

    values = data.loc[:, list(required)].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise ValueError("DEA input and output values must be finite numeric values.")
    if (values <= 0).any().any():
        raise ValueError("DEA input and output values must be strictly positive.")


def calculate_dea_efficiency(
    data: pd.DataFrame,
    input_columns: Sequence[str],
    output_columns: Sequence[str],
    returns_to_scale: str = "vrs",
) -> pd.DataFrame:
    """Calculate input-oriented DEA efficiency for one cross-sectional sample.

    Each row is a decision-making unit (DMU), typically a city in one year.
    Under the default VRS/BCC formulation, the score is the smallest
    proportion of the DMU's observed inputs required to reproduce its outputs
    relative to the observed production frontier. A score of one denotes
    relative technical efficiency; a score below one denotes relative
    inefficiency in the selected sample and model specification.

    Parameters
    ----------
    data:
        One cross-sectional DataFrame. It should contain a ``city`` column and
        may contain a common ``year`` column.
    input_columns:
        Positive input-variable names.
    output_columns:
        Positive output-variable names.
    returns_to_scale:
        ``"vrs"`` for the BCC model or ``"crs"`` for the CCR model.

    Returns
    -------
    pandas.DataFrame
        ``city``, optional ``year``, and ``efficiency_score`` columns.
    """
    if "city" not in data.columns:
        raise ValueError("DEA data must contain a city column identifying each DMU.")
    if data["city"].duplicated().any():
        raise ValueError("A cross-sectional DEA sample must contain one row per city.")
    if returns_to_scale not in {"vrs", "crs"}:
        raise ValueError("returns_to_scale must be either 'vrs' or 'crs'.")
    _validate_dea_data(data, input_columns, output_columns)

    inputs = data.loc[:, list(input_columns)].to_numpy(dtype=float)
    outputs = data.loc[:, list(output_columns)].to_numpy(dtype=float)
    n_dmus, n_inputs = inputs.shape
    n_outputs = outputs.shape[1]
    scores: list[float] = []

    for dmu_index in range(n_dmus):
        # Decision variables are lambda_1, ..., lambda_n, theta. The objective
        # minimises theta in the input-oriented DEA envelopment formulation.
        objective = np.zeros(n_dmus + 1)
        objective[-1] = 1.0

        input_constraints = np.hstack(
            [inputs.T, -inputs[dmu_index, :].reshape(n_inputs, 1)]
        )
        output_constraints = np.hstack(
            [-outputs.T, np.zeros((n_outputs, 1))]
        )
        a_ub = np.vstack([input_constraints, output_constraints])
        b_ub = np.concatenate([np.zeros(n_inputs), -outputs[dmu_index, :]])

        a_eq = None
        b_eq = None
        if returns_to_scale == "vrs":
            # Convexity constraint for the BCC/VRS frontier.
            a_eq = np.concatenate([np.ones(n_dmus), [0.0]]).reshape(1, -1)
            b_eq = np.array([1.0])

        result = linprog(
            c=objective,
            A_ub=a_ub,
            b_ub=b_ub,
            A_eq=a_eq,
            b_eq=b_eq,
            bounds=[(0, None)] * (n_dmus + 1),
            method="highs",
        )
        if not result.success:
            raise RuntimeError(
                f"DEA optimisation failed for city '{data.iloc[dmu_index]['city']}': {result.message}"
            )
        scores.append(float(np.clip(result.x[-1], 0, 1)))

    identifier_columns = ["city"] + (["year"] if "year" in data.columns else [])
    result_frame = data.loc[:, identifier_columns].copy()
    result_frame["efficiency_score"] = np.round(scores, 6)
    return result_frame


def evaluate_panel_efficiency(
    panel_data: pd.DataFrame,
    input_columns: Sequence[str],
    output_columns: Sequence[str],
    returns_to_scale: str = "vrs",
) -> pd.DataFrame:
    """Evaluate DEA efficiency separately for each year of a panel dataset.

    Year-specific frontiers avoid treating temporal shifts in prices, policy,
    population, or technology as if they were cross-sectional city differences.
    Scores are relative to the DMUs observed in the same year and are not
    automatically comparable across separately estimated years.

    Parameters
    ----------
    panel_data:
        DataFrame with city, year, selected inputs, and selected outputs.
    input_columns:
        Positive input-variable names.
    output_columns:
        Positive output-variable names.
    returns_to_scale:
        ``"vrs"`` for BCC or ``"crs"`` for CCR.

    Returns
    -------
    pandas.DataFrame
        One efficiency score for every city-year observation.
    """
    if "year" not in panel_data.columns:
        raise ValueError("Panel DEA evaluation requires a year column.")
    if panel_data.duplicated(subset=["city", "year"]).any():
        raise ValueError("Panel data must contain one row per city-year observation.")

    year_results = []
    for _, year_data in panel_data.groupby("year", sort=True):
        year_results.append(
            calculate_dea_efficiency(
                year_data,
                input_columns=input_columns,
                output_columns=output_columns,
                returns_to_scale=returns_to_scale,
            )
        )
    return pd.concat(year_results, ignore_index=True)
