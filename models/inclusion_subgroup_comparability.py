"""Subgroup measurement-comparability readiness audits.

The module compares complete, non-identifying institutional response patterns
within one instrument version and administration round. Its descriptive
outputs identify questions for a future governed DIF or measurement-invariance
study; they do not establish invariance, bias, fairness, or group differences.
"""

from __future__ import annotations

from itertools import combinations
from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import (
    RELIABILITY_COLUMNS,
    validate_reliability_audit_data,
)


COMPARISON_GROUP_COLUMN: Final[str] = "comparison_group"
SUBGROUP_COMPARABILITY_COLUMNS: Final[tuple[str, ...]] = (
    RELIABILITY_COLUMNS + (COMPARISON_GROUP_COLUMN,)
)
MINIMUM_GROUP_SIZE: Final[int] = 5


def create_subgroup_comparability_template() -> pd.DataFrame:
    """Return a blank complete-response schema with an institutional group field."""
    return pd.DataFrame(
        [{column: "" for column in SUBGROUP_COMPARABILITY_COLUMNS}],
        columns=SUBGROUP_COMPARABILITY_COLUMNS,
    )


def load_subgroup_comparability_csv(
    source: object,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Load and validate a UTF-8 subgroup-comparability CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Subgroup-comparability CSV could not be read: {error}") from error
    return validate_subgroup_comparability_data(data, source_min, source_max)


def validate_subgroup_comparability_data(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Validate complete institutional records and non-blank group labels."""
    if COMPARISON_GROUP_COLUMN not in data.columns:
        raise ValueError(
            f"Subgroup-comparability data are missing required column: "
            f"'{COMPARISON_GROUP_COLUMN}'."
        )
    validated = validate_reliability_audit_data(data, source_min, source_max)
    groups = data[COMPARISON_GROUP_COLUMN].fillna("").astype(str).str.strip()
    if groups.eq("").any():
        raise ValueError("comparison_group must not contain missing or blank values.")
    validated[COMPARISON_GROUP_COLUMN] = groups.to_numpy()
    return validated.loc[:, list(SUBGROUP_COMPARABILITY_COLUMNS)]


def _select_subgroup_sample(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Select one version-round sample and enforce prototype group coverage."""
    validated = validate_subgroup_comparability_data(data, source_min, source_max)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    try:
        round_number = int(administration_round)
    except (TypeError, ValueError) as error:
        raise ValueError("administration_round must be a positive integer.") from error
    if round_number < 1 or round_number != administration_round:
        raise ValueError("administration_round must be a positive integer.")
    selected = validated[
        validated["instrument_version"].eq(version)
        & validated["administration_round"].eq(round_number)
    ].copy()
    if selected.empty:
        raise ValueError("The selected instrument version and administration round do not exist.")
    group_counts = selected[COMPARISON_GROUP_COLUMN].value_counts()
    if len(group_counts) < 2:
        raise ValueError("Subgroup-comparability audit requires at least two comparison groups.")
    undersized = group_counts[group_counts < MINIMUM_GROUP_SIZE].index.tolist()
    if undersized:
        raise ValueError(
            f"Every comparison group requires at least {MINIMUM_GROUP_SIZE} complete records "
            f"as a prototype privacy and computation condition; undersized groups: {undersized}"
        )
    return selected


def _item_dimensions() -> dict[str, str]:
    """Return the registered conceptual dimension label for each current item."""
    return {
        item: DIMENSION_LABELS[score_column]
        for score_column, items in DIMENSION_ITEMS.items()
        for item in items
    }


def audit_subgroup_comparability(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Describe response-pattern comparability across institutional groups.

    The audit reports group coverage, item distributions, pairwise descriptive
    standardised mean differences, and differences between item-correlation
    matrices. It performs no significance test, DIF model, CFA, thresholding,
    ranking, or automatic item decision.
    """
    selected = _select_subgroup_sample(
        data,
        instrument_version,
        administration_round,
        source_min,
        source_max,
    )
    groups = sorted(selected[COMPARISON_GROUP_COLUMN].unique())
    dimensions = _item_dimensions()
    coverage = pd.DataFrame(
        [
            {
                "instrument_version": str(instrument_version).strip(),
                "administration_round": int(administration_round),
                "comparison_group": group,
                "complete_record_count": int(
                    selected[COMPARISON_GROUP_COLUMN].eq(group).sum()
                ),
                "item_count": len(ITEM_COLUMNS),
            }
            for group in groups
        ]
    )

    distribution_rows: list[dict[str, float | int | str]] = []
    for group in groups:
        group_data = selected[selected[COMPARISON_GROUP_COLUMN].eq(group)]
        for item in ITEM_COLUMNS:
            values = group_data[item].to_numpy(dtype=float)
            distribution_rows.append(
                {
                    "comparison_group": group,
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
    distributions = pd.DataFrame(distribution_rows)

    difference_rows: list[dict[str, float | int | str | bool]] = []
    correlation_rows: list[dict[str, float | int | str]] = []
    for first_group, second_group in combinations(groups, 2):
        first = selected[selected[COMPARISON_GROUP_COLUMN].eq(first_group)]
        second = selected[selected[COMPARISON_GROUP_COLUMN].eq(second_group)]
        for item in ITEM_COLUMNS:
            first_values = first[item].to_numpy(dtype=float)
            second_values = second[item].to_numpy(dtype=float)
            first_variance = float(first_values.var(ddof=1))
            second_variance = float(second_values.var(ddof=1))
            pooled_variance = (
                (len(first_values) - 1) * first_variance
                + (len(second_values) - 1) * second_variance
            ) / (len(first_values) + len(second_values) - 2)
            raw_difference = float(first_values.mean() - second_values.mean())
            standardised_difference = (
                raw_difference / np.sqrt(pooled_variance)
                if pooled_variance > 0 and np.isfinite(pooled_variance)
                else np.nan
            )
            difference_rows.append(
                {
                    "first_group": first_group,
                    "second_group": second_group,
                    "item": item,
                    "conceptual_dimension": dimensions[item],
                    "first_group_count": len(first_values),
                    "second_group_count": len(second_values),
                    "raw_mean_difference_first_minus_second": round(raw_difference, 6),
                    "standardised_mean_difference": (
                        round(float(standardised_difference), 6)
                        if np.isfinite(standardised_difference)
                        else np.nan
                    ),
                    "standardised_difference_defined": bool(
                        np.isfinite(standardised_difference)
                    ),
                }
            )

        first_variances = first.loc[:, list(ITEM_COLUMNS)].var(axis=0, ddof=1)
        second_variances = second.loc[:, list(ITEM_COLUMNS)].var(axis=0, ddof=1)
        zero_variance_count = int((first_variances.le(0) | second_variances.le(0)).sum())
        if zero_variance_count:
            rms_difference = np.nan
            maximum_difference = np.nan
            pair_count = 0
        else:
            first_correlation = first.loc[:, list(ITEM_COLUMNS)].corr().to_numpy(dtype=float)
            second_correlation = second.loc[:, list(ITEM_COLUMNS)].corr().to_numpy(dtype=float)
            upper = np.triu_indices(len(ITEM_COLUMNS), k=1)
            correlation_differences = first_correlation[upper] - second_correlation[upper]
            finite = correlation_differences[np.isfinite(correlation_differences)]
            pair_count = len(finite)
            rms_difference = float(np.sqrt(np.mean(finite**2))) if pair_count else np.nan
            maximum_difference = float(np.max(np.abs(finite))) if pair_count else np.nan
        correlation_rows.append(
            {
                "first_group": first_group,
                "second_group": second_group,
                "first_group_count": len(first),
                "second_group_count": len(second),
                "finite_item_pair_count": pair_count,
                "zero_variance_item_count": zero_variance_count,
                "root_mean_square_correlation_difference": (
                    round(rms_difference, 6) if np.isfinite(rms_difference) else np.nan
                ),
                "maximum_absolute_correlation_difference": (
                    round(maximum_difference, 6)
                    if np.isfinite(maximum_difference)
                    else np.nan
                ),
            }
        )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Do item response relationships remain comparable across the declared "
                    "institutional groups under a separately specified measurement model?"
                ),
                "required_future_method": "Governed multi-group CFA or another justified invariance design",
            },
            {
                "research_question_candidate": (
                    "Could observed item-level distribution differences reflect context, "
                    "sampling, administration, response style, or differential item functioning?"
                ),
                "required_future_method": "Governed DIF analysis with theory and adequate samples",
            },
            {
                "research_question_candidate": (
                    "Are comparison-group definitions substantively meaningful, ethically "
                    "justified, and sufficiently represented for future validation?"
                ),
                "required_future_method": "Sampling, governance, and qualitative review",
            },
        ]
    )
    interpretation = (
        "Readiness evidence only. Group coverage, descriptive item distributions, "
        "standardised mean differences, and correlation-structure differences do not "
        "establish measurement invariance, DIF, bias, fairness, or substantive group "
        "differences. No automatic threshold, ranking, item decision, or group judgement "
        "is produced. Future conclusions require a governed measurement model, adequate "
        "samples, theory, uncertainty analysis, and ethical review."
    )
    return {
        "group_coverage_summary": coverage,
        "group_item_distribution_summary": distributions,
        "pairwise_item_difference_summary": pd.DataFrame(difference_rows),
        "correlation_structure_difference_summary": pd.DataFrame(correlation_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
