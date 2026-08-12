"""Longitudinal attrition and panel-composition readiness audits.

The audit compares retained, first-round-only, and second-round-only
institutional groups across adjacent rounds of one instrument version. It
describes possible selection questions without establishing attrition
mechanisms, missingness assumptions, bias, causality, or corrective weights.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import validate_reliability_audit_data
from models.support_gap import calculate_support_gaps


MINIMUM_DISCLOSABLE_GROUP_SIZE: Final[int] = 3
GAP_COLUMNS: Final[tuple[str, ...]] = (
    "gap_resource_practice",
    "gap_practice_participation",
    "overall_support_conversion_gap",
)


def _select_version(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Select one complete instrument version containing at least two rounds."""
    validated = validate_reliability_audit_data(data, source_min, source_max)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    selected = validated[validated["instrument_version"].eq(version)].copy()
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    if selected["administration_round"].nunique() < 2:
        raise ValueError("Attrition audit requires at least two administration rounds.")
    return selected


def _score_records(selected: pd.DataFrame, source_min: float, source_max: float) -> pd.DataFrame:
    """Calculate internal equal-item scores and gaps without exposing them."""
    items = 100 * (selected.loc[:, list(ITEM_COLUMNS)] - source_min) / (source_max - source_min)
    scores = pd.DataFrame(
        {
            column: items.loc[:, list(dimension_items)].mean(axis=1)
            for column, dimension_items in DIMENSION_ITEMS.items()
        },
        index=selected.index,
    )
    gaps = calculate_support_gaps(scores)
    result = selected.loc[:, ["pseudonymous_unit_id", "administration_round"]].copy()
    for column in DIMENSION_ITEMS:
        result[column] = scores[column]
    for column in GAP_COLUMNS:
        result[column] = gaps[column]
    return result


def _standardised_difference(first: np.ndarray, second: np.ndarray) -> float:
    """Return a pooled-standard-deviation mean difference or NaN."""
    pooled = (
        (len(first) - 1) * float(first.var(ddof=1))
        + (len(second) - 1) * float(second.var(ddof=1))
    ) / (len(first) + len(second) - 2)
    if pooled <= 0 or not np.isfinite(pooled):
        return np.nan
    return float((first.mean() - second.mean()) / np.sqrt(pooled))


def audit_longitudinal_attrition(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Describe retained, exiting, and entering panel composition.

    Comparisons are suppressed unless both groups contain at least three units.
    No missingness mechanism, attrition weight, imputation, causal explanation,
    or automatic bias conclusion is produced.
    """
    selected = _select_version(data, instrument_version, source_min, source_max)
    scored = _score_records(selected, source_min, source_max)
    rounds = sorted(scored["administration_round"].unique())
    statistics = list(DIMENSION_ITEMS) + list(GAP_COLUMNS)
    labels = {
        **{column: DIMENSION_LABELS[column] for column in DIMENSION_ITEMS},
        "gap_resource_practice": "Resource to Practice Gap",
        "gap_practice_participation": "Practice to Participation Gap",
        "overall_support_conversion_gap": "Overall Support Conversion Gap",
    }
    types = {
        **{column: "dimension_score" for column in DIMENSION_ITEMS},
        **{column: "support_gap" for column in GAP_COLUMNS},
    }
    coverage_rows = []
    comparison_rows = []
    for first_round, second_round in zip(rounds[:-1], rounds[1:], strict=True):
        first = scored[scored["administration_round"].eq(first_round)].set_index(
            "pseudonymous_unit_id"
        )
        second = scored[scored["administration_round"].eq(second_round)].set_index(
            "pseudonymous_unit_id"
        )
        first_ids, second_ids = set(first.index), set(second.index)
        retained = sorted(first_ids & second_ids)
        exited = sorted(first_ids - second_ids)
        entered = sorted(second_ids - first_ids)
        coverage_rows.append(
            {
                "first_round": int(first_round),
                "second_round": int(second_round),
                "first_round_unit_count": len(first_ids),
                "second_round_unit_count": len(second_ids),
                "retained_unit_count": len(retained),
                "first_round_only_unit_count": len(exited),
                "second_round_only_unit_count": len(entered),
                "retention_proportion": round(len(retained) / len(first_ids), 6),
                "entry_proportion_of_second_round": round(len(entered) / len(second_ids), 6),
            }
        )
        comparisons = (
            ("first_round_retained_vs_exited", first, retained, exited),
            ("second_round_retained_vs_entered", second, retained, entered),
        )
        for comparison, frame, reference_ids, comparison_ids in comparisons:
            disclosed = (
                len(reference_ids) >= MINIMUM_DISCLOSABLE_GROUP_SIZE
                and len(comparison_ids) >= MINIMUM_DISCLOSABLE_GROUP_SIZE
            )
            for statistic in statistics:
                row: dict[str, object] = {
                    "first_round": int(first_round),
                    "second_round": int(second_round),
                    "comparison": comparison,
                    "statistic_type": types[statistic],
                    "statistic": statistic,
                    "label": labels[statistic],
                    "reference_group_count": len(reference_ids),
                    "comparison_group_count": len(comparison_ids),
                    "comparison_disclosed": disclosed,
                }
                if disclosed:
                    reference = frame.loc[reference_ids, statistic].to_numpy(dtype=float)
                    comparison_values = frame.loc[comparison_ids, statistic].to_numpy(dtype=float)
                    difference = float(reference.mean() - comparison_values.mean())
                    standardised = _standardised_difference(reference, comparison_values)
                    row.update(
                        {
                            "reference_group_mean": round(float(reference.mean()), 6),
                            "comparison_group_mean": round(float(comparison_values.mean()), 6),
                            "raw_mean_difference_reference_minus_comparison": round(difference, 6),
                            "standardised_mean_difference": (
                                round(standardised, 6) if np.isfinite(standardised) else np.nan
                            ),
                            "standardised_difference_defined": bool(np.isfinite(standardised)),
                            "suppression_reason": "",
                        }
                    )
                else:
                    row.update(
                        {
                            "reference_group_mean": np.nan,
                            "comparison_group_mean": np.nan,
                            "raw_mean_difference_reference_minus_comparison": np.nan,
                            "standardised_mean_difference": np.nan,
                            "standardised_difference_defined": False,
                            "suppression_reason": (
                                "At least three units are required in both groups for this "
                                "prototype descriptive comparison."
                            ),
                        }
                    )
                comparison_rows.append(row)

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Do institutions retained in the next round differ descriptively from "
                    "institutions observed only in the earlier round?"
                ),
                "required_future_evidence": "Fieldwork exit reasons and governed attrition analysis",
            },
            {
                "research_question_candidate": (
                    "Do newly entering institutions change the composition and interpretation "
                    "of later-round dimension or Support Gap summaries?"
                ),
                "required_future_evidence": "Recruitment records and composition sensitivity analysis",
            },
            {
                "research_question_candidate": (
                    "Which missing-data assumptions and longitudinal estimators are justified "
                    "by the study design and observed follow-up process?"
                ),
                "required_future_evidence": "Preregistered missingness model and sensitivity analysis",
            },
        ]
    )
    interpretation = (
        "Attrition-readiness evidence only. Retention, exit, entry, and descriptive score "
        "differences do not establish why records are missing, whether attrition is random, "
        "whether estimates are biased, or how weights or imputations should be constructed. "
        "Small-group statistics are suppressed. No causal, quality, improvement, correction, "
        "or automatic attrition judgement is produced."
    )
    return {
        "attrition_coverage_summary": pd.DataFrame(coverage_rows),
        "panel_composition_comparison_summary": pd.DataFrame(comparison_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
