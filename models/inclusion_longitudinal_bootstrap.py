"""Paired Bootstrap uncertainty audits for longitudinal inclusive summaries.

Matched institutional records are resampled as intact pairs across adjacent
rounds of one instrument version. The audit describes uncertainty in mean
changes for five dimensions and three Support Gaps; it is not a causal,
policy-effect, growth, trend-classification, or measurement-invariance model.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import validate_reliability_audit_data
from models.support_gap import calculate_support_gaps


MINIMUM_MATCHED_RECORDS: Final[int] = 5
MINIMUM_RESAMPLES: Final[int] = 100
MAXIMUM_RESAMPLES: Final[int] = 10_000
GAP_COLUMNS: Final[tuple[str, ...]] = (
    "gap_resource_practice",
    "gap_practice_participation",
    "overall_support_conversion_gap",
)


def _validate_settings(
    n_resamples: int,
    confidence_level: float,
    random_seed: int,
) -> tuple[int, float, int]:
    """Validate bounded, reproducible paired-Bootstrap settings."""
    if (
        not isinstance(n_resamples, (int, np.integer))
        or isinstance(n_resamples, bool)
        or not MINIMUM_RESAMPLES <= n_resamples <= MAXIMUM_RESAMPLES
    ):
        raise ValueError(
            f"n_resamples must be an integer between {MINIMUM_RESAMPLES} and "
            f"{MAXIMUM_RESAMPLES}."
        )
    if (
        not isinstance(confidence_level, (int, float, np.integer, np.floating))
        or isinstance(confidence_level, bool)
        or not np.isfinite(confidence_level)
        or not 0.80 <= float(confidence_level) <= 0.99
    ):
        raise ValueError("confidence_level must be finite and between 0.80 and 0.99.")
    if (
        not isinstance(random_seed, (int, np.integer))
        or isinstance(random_seed, bool)
        or random_seed < 0
    ):
        raise ValueError("random_seed must be a non-negative integer.")
    return int(n_resamples), float(confidence_level), int(random_seed)


def _score_selected_records(
    data: pd.DataFrame,
    instrument_version: str,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Validate one multi-round version and calculate internal record scores."""
    validated = validate_reliability_audit_data(data, source_min, source_max)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    selected = validated[validated["instrument_version"].eq(version)].copy()
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    if selected["administration_round"].nunique() < 2:
        raise ValueError("Paired longitudinal Bootstrap requires at least two rounds.")

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


def audit_paired_longitudinal_bootstrap(
    data: pd.DataFrame,
    instrument_version: str,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    random_seed: int = 42,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Audit uncertainty in adjacent-round matched mean changes.

    Each adjacent observed-round comparison resamples matched institutions with
    replacement while keeping their two observations paired. At least five
    matched institutions are required for every adjacent comparison. Percentile
    intervals are descriptive prototype summaries and no automatic inference,
    significance, direction, improvement, or policy-effect label is produced.
    """
    n_resamples, confidence_level, random_seed = _validate_settings(
        n_resamples, confidence_level, random_seed
    )
    scored = _score_selected_records(
        data, instrument_version, source_min, source_max
    )
    rounds = sorted(scored["administration_round"].unique())
    statistics = list(DIMENSION_ITEMS) + list(GAP_COLUMNS)
    labels = {
        **{column: DIMENSION_LABELS[column] for column in DIMENSION_ITEMS},
        "gap_resource_practice": "Resource to Practice Gap",
        "gap_practice_participation": "Practice to Participation Gap",
        "overall_support_conversion_gap": "Overall Support Conversion Gap",
    }
    types = {
        **{column: "dimension_mean_change" for column in DIMENSION_ITEMS},
        **{column: "support_gap_mean_change" for column in GAP_COLUMNS},
    }

    run_rows: list[dict[str, object]] = []
    interval_rows: list[dict[str, object]] = []
    rng = np.random.default_rng(random_seed)
    alpha = 1 - confidence_level
    for first_round, second_round in zip(rounds[:-1], rounds[1:], strict=True):
        first = scored[scored["administration_round"].eq(first_round)].set_index(
            "pseudonymous_unit_id"
        )
        second = scored[scored["administration_round"].eq(second_round)].set_index(
            "pseudonymous_unit_id"
        )
        matched_ids = sorted(set(first.index) & set(second.index))
        if len(matched_ids) < MINIMUM_MATCHED_RECORDS:
            raise ValueError(
                f"Adjacent rounds {first_round} and {second_round} require at least "
                f"{MINIMUM_MATCHED_RECORDS} matched units for paired Bootstrap; found "
                f"{len(matched_ids)}."
            )
        changes = (
            second.loc[matched_ids, statistics].to_numpy(dtype=float)
            - first.loc[matched_ids, statistics].to_numpy(dtype=float)
        )
        point_estimates = changes.mean(axis=0)
        indices = rng.integers(
            0, len(matched_ids), size=(n_resamples, len(matched_ids))
        )
        bootstrap_means = changes[indices].mean(axis=1)
        bootstrap_average = bootstrap_means.mean(axis=0)
        bootstrap_standard_error = bootstrap_means.std(axis=0, ddof=1)
        lower = np.quantile(bootstrap_means, alpha / 2, axis=0)
        upper = np.quantile(bootstrap_means, 1 - alpha / 2, axis=0)

        run_rows.append(
            {
                "instrument_version": str(instrument_version).strip(),
                "first_round": int(first_round),
                "second_round": int(second_round),
                "matched_unit_count": len(matched_ids),
                "resampling_unit": "matched_institutional_pair",
                "sampling_method": "paired_nonparametric_bootstrap_with_replacement",
                "n_resamples": n_resamples,
                "confidence_level": confidence_level,
                "interval_method": "percentile",
                "random_seed": random_seed,
                "change_definition": "second_round_minus_first_round",
                "missing_rounds_imputed": False,
                "cross_version_records_combined": False,
            }
        )
        for index, statistic in enumerate(statistics):
            interval_rows.append(
                {
                    "first_round": int(first_round),
                    "second_round": int(second_round),
                    "statistic_type": types[statistic],
                    "statistic": statistic,
                    "label": labels[statistic],
                    "matched_unit_count": len(matched_ids),
                    "point_mean_change_second_minus_first": round(
                        float(point_estimates[index]), 6
                    ),
                    "bootstrap_mean_change": round(
                        float(bootstrap_average[index]), 6
                    ),
                    "bootstrap_bias": round(
                        float(bootstrap_average[index] - point_estimates[index]), 6
                    ),
                    "bootstrap_standard_error": round(
                        float(bootstrap_standard_error[index]), 6
                    ),
                    "percentile_interval_lower": round(float(lower[index]), 6),
                    "percentile_interval_upper": round(float(upper[index]), 6),
                    "confidence_level": confidence_level,
                }
            )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "How uncertain are adjacent-round mean changes under paired "
                    "institutional resampling?"
                ),
                "required_future_evidence": (
                    "Governed sampling design and longitudinal comparability evidence"
                ),
            },
            {
                "research_question_candidate": (
                    "Would uncertainty summaries change under cluster-aware, block, "
                    "multilevel, or missing-data methods?"
                ),
                "required_future_evidence": (
                    "Preregistered dependence and missing-data sensitivity analysis"
                ),
            },
            {
                "research_question_candidate": (
                    "Do descriptive change patterns replicate across additional rounds "
                    "and independent institutional samples?"
                ),
                "required_future_evidence": (
                    "Additional governed rounds and independent replication samples"
                ),
            },
        ]
    )
    interpretation = (
        "Paired longitudinal Bootstrap evidence only. Intervals describe resampling "
        "uncertainty for matched institutional mean changes under the current sample, "
        "equal-item scoring, and adjacent-round definitions. They do not establish "
        "longitudinal measurement comparability, population representativeness, statistical "
        "significance, improvement, deterioration, policy effects, or causality. Missing "
        "rounds are not imputed, versions are not combined, and no unit trajectories, "
        "automatic direction labels, thresholds, rankings, or decisions are produced."
    )
    return {
        "paired_bootstrap_run_summary": pd.DataFrame(run_rows),
        "paired_bootstrap_interval_summary": pd.DataFrame(interval_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
