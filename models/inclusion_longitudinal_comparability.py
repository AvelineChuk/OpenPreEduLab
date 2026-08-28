"""Longitudinal measurement-comparability readiness audits.

Complete institutional response patterns are compared across administration
rounds within one instrument version. Descriptive item distributions,
standardised mean differences, and correlation-structure differences identify
questions for a future governed longitudinal measurement-invariance study; they
do not establish invariance, non-invariance, validity, bias, or causal change.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import validate_reliability_audit_data


MINIMUM_ROUND_SIZE: Final[int] = 5


def _item_dimensions() -> dict[str, str]:
    """Return the registered conceptual dimension label for each item."""
    return {
        item: DIMENSION_LABELS[score_column]
        for score_column, items in DIMENSION_ITEMS.items()
        for item in items
    }


def _select_version(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Validate and select one version with at least two adequately sized rounds."""
    validated = validate_reliability_audit_data(data, source_min, source_max)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    selected = validated[validated["instrument_version"].eq(version)].copy()
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    counts = selected["administration_round"].value_counts().sort_index()
    if len(counts) < 2:
        raise ValueError("Longitudinal comparability readiness audit requires at least two rounds.")
    undersized = counts[counts < MINIMUM_ROUND_SIZE].index.tolist()
    if undersized:
        raise ValueError(
            f"Every round requires at least {MINIMUM_ROUND_SIZE} complete records as a "
            f"prototype privacy and computation condition; undersized rounds: {undersized}"
        )
    return selected


def _standardised_difference(first: np.ndarray, second: np.ndarray) -> float:
    """Return the pooled-standard-deviation difference or NaN when undefined."""
    pooled_variance = (
        (len(first) - 1) * float(first.var(ddof=1))
        + (len(second) - 1) * float(second.var(ddof=1))
    ) / (len(first) + len(second) - 2)
    if pooled_variance <= 0 or not np.isfinite(pooled_variance):
        return np.nan
    return float((first.mean() - second.mean()) / np.sqrt(pooled_variance))


def audit_longitudinal_comparability(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Describe item-response comparability questions across observed rounds.

    Only adjacent observed rounds are compared. All complete records in each
    round contribute to distribution and correlation summaries; changing panel
    composition is not corrected and must be reviewed with the attrition audit.
    No significance test, CFA, invariance decision, threshold, or item action is
    produced.
    """
    selected = _select_version(data, instrument_version, source_min, source_max)
    rounds = sorted(selected["administration_round"].unique())
    dimensions = _item_dimensions()

    coverage_rows = []
    distribution_rows = []
    for round_number in rounds:
        round_data = selected[selected["administration_round"].eq(round_number)]
        coverage_rows.append(
            {
                "instrument_version": str(instrument_version).strip(),
                "administration_round": int(round_number),
                "complete_record_count": len(round_data),
                "unique_unit_count": round_data["pseudonymous_unit_id"].nunique(),
                "item_count": len(ITEM_COLUMNS),
            }
        )
        for item in ITEM_COLUMNS:
            values = round_data[item].to_numpy(dtype=float)
            distribution_rows.append(
                {
                    "administration_round": int(round_number),
                    "item": item,
                    "conceptual_dimension": dimensions[item],
                    "record_count": len(values),
                    "mean": round(float(values.mean()), 6),
                    "standard_deviation": round(float(values.std(ddof=1)), 6),
                    "source_minimum_proportion": round(
                        float(np.isclose(values, source_min).mean()), 6
                    ),
                    "source_maximum_proportion": round(
                        float(np.isclose(values, source_max).mean()), 6
                    ),
                }
            )

    difference_rows = []
    correlation_rows = []
    for first_round, second_round in zip(rounds[:-1], rounds[1:], strict=True):
        first = selected[selected["administration_round"].eq(first_round)]
        second = selected[selected["administration_round"].eq(second_round)]
        first_ids = set(first["pseudonymous_unit_id"])
        second_ids = set(second["pseudonymous_unit_id"])
        matched_count = len(first_ids & second_ids)
        for item in ITEM_COLUMNS:
            first_values = first[item].to_numpy(dtype=float)
            second_values = second[item].to_numpy(dtype=float)
            raw_difference = float(first_values.mean() - second_values.mean())
            standardised = _standardised_difference(first_values, second_values)
            difference_rows.append(
                {
                    "first_round": int(first_round),
                    "second_round": int(second_round),
                    "item": item,
                    "conceptual_dimension": dimensions[item],
                    "first_round_count": len(first_values),
                    "second_round_count": len(second_values),
                    "matched_unit_count": matched_count,
                    "raw_mean_difference_first_minus_second": round(raw_difference, 6),
                    "standardised_mean_difference": (
                        round(standardised, 6) if np.isfinite(standardised) else np.nan
                    ),
                    "standardised_difference_defined": bool(np.isfinite(standardised)),
                    "composition_adjusted": False,
                }
            )

        first_variances = first.loc[:, list(ITEM_COLUMNS)].var(axis=0, ddof=1)
        second_variances = second.loc[:, list(ITEM_COLUMNS)].var(axis=0, ddof=1)
        zero_variance_count = int((first_variances.le(0) | second_variances.le(0)).sum())
        if zero_variance_count:
            finite_pair_count = 0
            rms_difference = np.nan
            maximum_difference = np.nan
        else:
            first_correlation = first.loc[:, list(ITEM_COLUMNS)].corr().to_numpy(dtype=float)
            second_correlation = second.loc[:, list(ITEM_COLUMNS)].corr().to_numpy(dtype=float)
            upper = np.triu_indices(len(ITEM_COLUMNS), k=1)
            differences = first_correlation[upper] - second_correlation[upper]
            finite = differences[np.isfinite(differences)]
            finite_pair_count = len(finite)
            rms_difference = float(np.sqrt(np.mean(finite**2))) if len(finite) else np.nan
            maximum_difference = float(np.max(np.abs(finite))) if len(finite) else np.nan
        correlation_rows.append(
            {
                "first_round": int(first_round),
                "second_round": int(second_round),
                "first_round_count": len(first),
                "second_round_count": len(second),
                "matched_unit_count": matched_count,
                "finite_item_pair_count": finite_pair_count,
                "zero_variance_item_count": zero_variance_count,
                "root_mean_square_correlation_difference": (
                    round(rms_difference, 6) if np.isfinite(rms_difference) else np.nan
                ),
                "maximum_absolute_correlation_difference": (
                    round(maximum_difference, 6)
                    if np.isfinite(maximum_difference)
                    else np.nan
                ),
                "composition_adjusted": False,
            }
        )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Do the proposed item relationships and score meanings remain comparable "
                    "across rounds under an explicitly specified longitudinal measurement model?"
                ),
                "required_future_method": (
                    "Governed longitudinal CFA or another justified invariance design"
                ),
            },
            {
                "research_question_candidate": (
                    "Could item distribution or correlation changes reflect panel composition, "
                    "administration, timing, context, response style, or measurement change?"
                ),
                "required_future_method": (
                    "Integrated attrition, metadata, qualitative, and measurement review"
                ),
            },
            {
                "research_question_candidate": (
                    "Are sample sizes, response properties, round intervals, and estimator "
                    "assumptions adequate for a future longitudinal invariance study?"
                ),
                "required_future_method": (
                    "Preregistered model, estimator, identification, and sample-size rationale"
                ),
            },
        ]
    )
    interpretation = (
        "Longitudinal measurement-comparability readiness evidence only. Round coverage, "
        "item distributions, standardised mean differences, and correlation-structure "
        "differences do not establish configural, metric, scalar, strict, or other forms of "
        "measurement invariance. They also do not establish bias, validity, substantive "
        "change, improvement, deterioration, policy effects, or causality. Comparisons use "
        "all complete records and are not adjusted for changing panel composition. No "
        "automatic threshold, significance test, item decision, ranking, or judgement is produced."
    )
    return {
        "round_coverage_summary": pd.DataFrame(coverage_rows),
        "round_item_distribution_summary": pd.DataFrame(distribution_rows),
        "adjacent_round_item_difference_summary": pd.DataFrame(difference_rows),
        "adjacent_round_correlation_difference_summary": pd.DataFrame(correlation_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
