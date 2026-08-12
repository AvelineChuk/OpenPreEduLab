"""Longitudinal panel readiness audits for inclusive education research.

Complete pseudonymous institutional records are summarised across multiple
administration rounds within one instrument version. The audit describes round
coverage, adjacent-round matching, and score changes; it is not a growth,
causal, policy-effect, or longitudinal measurement-invariance model.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import validate_reliability_audit_data
from models.support_gap import calculate_support_gaps


MINIMUM_ROUND_RECORDS: Final[int] = 3
MINIMUM_MATCHED_RECORDS: Final[int] = 3
GAP_COLUMNS: Final[tuple[str, ...]] = (
    "gap_resource_practice",
    "gap_practice_participation",
    "overall_support_conversion_gap",
)


def _select_longitudinal_version(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Validate records and select one version with at least two viable rounds."""
    validated = validate_reliability_audit_data(data, source_min, source_max)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    selected = validated[validated["instrument_version"].eq(version)].copy()
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    rounds = sorted(selected["administration_round"].unique())
    if len(rounds) < 2:
        raise ValueError("Longitudinal readiness audit requires at least two rounds.")
    counts = selected["administration_round"].value_counts()
    undersized = sorted(counts[counts < MINIMUM_ROUND_RECORDS].index.tolist())
    if undersized:
        raise ValueError(
            f"Every round requires at least {MINIMUM_ROUND_RECORDS} complete records as "
            f"a prototype computation condition; undersized rounds: {undersized}"
        )
    return selected


def _score_records(
    selected: pd.DataFrame,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Return record-level equal-item dimensions and gaps for internal matching."""
    standardised = (
        100
        * (selected.loc[:, list(ITEM_COLUMNS)] - source_min)
        / (source_max - source_min)
    )
    scores = pd.DataFrame(
        {
            score_column: standardised.loc[:, list(items)].mean(axis=1)
            for score_column, items in DIMENSION_ITEMS.items()
        },
        index=selected.index,
    )
    gaps = calculate_support_gaps(scores)
    result = selected.loc[
        :, ["pseudonymous_unit_id", "administration_round"]
    ].copy()
    for column in DIMENSION_ITEMS:
        result[column] = scores[column]
    for column in GAP_COLUMNS:
        result[column] = gaps[column]
    return result


def audit_longitudinal_panel_readiness(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Describe multi-round coverage and adjacent matched changes.

    Rounds are ordered by their positive integer administration_round values.
    Missing rounds are not imputed, and only adjacent observed rounds are
    paired. Each adjacent pair requires at least three matched units. Outputs
    are aggregate and exclude pseudonymous IDs.
    """
    selected = _select_longitudinal_version(
        data,
        instrument_version,
        source_min,
        source_max,
    )
    scored = _score_records(selected, source_min, source_max)
    rounds = sorted(scored["administration_round"].unique())
    statistic_columns = list(DIMENSION_ITEMS) + list(GAP_COLUMNS)
    labels = {
        **{column: DIMENSION_LABELS[column] for column in DIMENSION_ITEMS},
        "gap_resource_practice": "Resource to Practice Gap",
        "gap_practice_participation": "Practice to Participation Gap",
        "overall_support_conversion_gap": "Overall Support Conversion Gap",
    }
    statistic_types = {
        **{column: "dimension_score" for column in DIMENSION_ITEMS},
        **{column: "support_gap" for column in GAP_COLUMNS},
    }

    round_coverage_rows = []
    round_statistic_rows = []
    round_id_sets: dict[int, set[str]] = {}
    for round_number in rounds:
        round_data = scored[scored["administration_round"].eq(round_number)]
        ids = set(round_data["pseudonymous_unit_id"])
        round_id_sets[int(round_number)] = ids
        round_coverage_rows.append(
            {
                "instrument_version": str(instrument_version).strip(),
                "administration_round": int(round_number),
                "complete_record_count": len(round_data),
                "unique_unit_count": len(ids),
                "statistic_count": len(statistic_columns),
            }
        )
        for statistic in statistic_columns:
            values = round_data[statistic].to_numpy(dtype=float)
            round_statistic_rows.append(
                {
                    "administration_round": int(round_number),
                    "statistic_type": statistic_types[statistic],
                    "statistic": statistic,
                    "label": labels[statistic],
                    "complete_record_count": len(values),
                    "mean": round(float(values.mean()), 6),
                    "standard_deviation": round(float(values.std(ddof=1)), 6),
                    "minimum": round(float(values.min()), 6),
                    "maximum": round(float(values.max()), 6),
                }
            )

    adjacent_coverage_rows = []
    adjacent_change_rows = []
    for first_round, second_round in zip(rounds[:-1], rounds[1:], strict=True):
        first_ids = round_id_sets[int(first_round)]
        second_ids = round_id_sets[int(second_round)]
        matched_ids = sorted(first_ids & second_ids)
        if len(matched_ids) < MINIMUM_MATCHED_RECORDS:
            raise ValueError(
                f"Adjacent rounds {first_round} and {second_round} require at least "
                f"{MINIMUM_MATCHED_RECORDS} matched units; found {len(matched_ids)}."
            )
        first = (
            scored[scored["administration_round"].eq(first_round)]
            .set_index("pseudonymous_unit_id")
            .loc[matched_ids]
        )
        second = (
            scored[scored["administration_round"].eq(second_round)]
            .set_index("pseudonymous_unit_id")
            .loc[matched_ids]
        )
        adjacent_coverage_rows.append(
            {
                "first_round": int(first_round),
                "second_round": int(second_round),
                "first_round_unit_count": len(first_ids),
                "second_round_unit_count": len(second_ids),
                "matched_unit_count": len(matched_ids),
                "first_round_retention_proportion": round(
                    len(matched_ids) / len(first_ids), 6
                ),
                "second_round_matched_proportion": round(
                    len(matched_ids) / len(second_ids), 6
                ),
                "first_round_only_count": len(first_ids - set(matched_ids)),
                "second_round_only_count": len(second_ids - set(matched_ids)),
            }
        )
        for statistic in statistic_columns:
            first_values = first[statistic].to_numpy(dtype=float)
            second_values = second[statistic].to_numpy(dtype=float)
            changes = second_values - first_values
            adjacent_change_rows.append(
                {
                    "first_round": int(first_round),
                    "second_round": int(second_round),
                    "statistic_type": statistic_types[statistic],
                    "statistic": statistic,
                    "label": labels[statistic],
                    "matched_unit_count": len(matched_ids),
                    "first_round_matched_mean": round(float(first_values.mean()), 6),
                    "second_round_matched_mean": round(float(second_values.mean()), 6),
                    "mean_change_second_minus_first": round(float(changes.mean()), 6),
                    "mean_absolute_change": round(float(np.abs(changes).mean()), 6),
                    "standard_deviation_of_change": round(
                        float(changes.std(ddof=1)), 6
                    ),
                    "minimum_change": round(float(changes.min()), 6),
                    "maximum_change": round(float(changes.max()), 6),
                }
            )

    complete_panel_ids = set.intersection(*(round_id_sets[round_number] for round_number in rounds))
    all_observed_ids = set.union(*(round_id_sets[round_number] for round_number in rounds))
    panel_summary = pd.DataFrame(
        [
            {
                "instrument_version": str(instrument_version).strip(),
                "round_count": len(rounds),
                "first_round": int(rounds[0]),
                "last_round": int(rounds[-1]),
                "all_observed_unit_count": len(all_observed_ids),
                "complete_panel_unit_count": len(complete_panel_ids),
                "complete_panel_coverage_proportion": round(
                    len(complete_panel_ids) / len(all_observed_ids), 6
                ),
                "missing_rounds_imputed": False,
                "cross_version_records_combined": False,
            }
        ]
    )
    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Which sampling, administration, institutional, or measurement factors "
                    "may explain changes in coverage and matched score summaries over rounds?"
                ),
                "required_future_evidence": "Attrition analysis, fieldwork records, and measurement review",
            },
            {
                "research_question_candidate": (
                    "Are five-dimension and Support Gap changes comparable after establishing "
                    "longitudinal measurement invariance?"
                ),
                "required_future_evidence": "Governed longitudinal invariance study",
            },
            {
                "research_question_candidate": (
                    "Do observed changes persist under time-aware, multilevel, and uncertainty "
                    "models appropriate to the institutional sampling design?"
                ),
                "required_future_evidence": "Preregistered longitudinal model and adequate panel",
            },
        ]
    )
    interpretation = (
        "Longitudinal readiness evidence only. Round coverage, matching, means, and matched "
        "changes are descriptive summaries under the current equal-item scoring assumptions. "
        "Time order does not establish causality, policy effects, improvement, deterioration, "
        "or valid longitudinal comparability. Missing rounds are not imputed, versions are "
        "not combined, and no automatic trajectory, institution, or quality judgement is produced."
    )
    return {
        "longitudinal_panel_summary": panel_summary,
        "round_coverage_summary": pd.DataFrame(round_coverage_rows),
        "round_statistic_summary": pd.DataFrame(round_statistic_rows),
        "adjacent_round_matching_summary": pd.DataFrame(adjacent_coverage_rows),
        "adjacent_round_change_summary": pd.DataFrame(adjacent_change_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
