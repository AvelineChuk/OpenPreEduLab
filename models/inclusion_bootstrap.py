"""Bootstrap sampling-uncertainty audits for inclusive education summaries.

Complete institutional records are resampled with replacement to describe the
sampling variability of five equal-item dimension means and three descriptive
Support Gap means. Intervals are prototype uncertainty summaries, not validity,
population-representativeness, causal, or policy-effect intervals.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import validate_reliability_audit_data
from models.support_gap import calculate_support_gaps


MINIMUM_COMPLETE_RECORDS: Final[int] = 5
MINIMUM_RESAMPLES: Final[int] = 100
MAXIMUM_RESAMPLES: Final[int] = 10_000
GAP_COLUMNS: Final[tuple[str, ...]] = (
    "gap_resource_practice",
    "gap_practice_participation",
    "overall_support_conversion_gap",
)


def _select_bootstrap_sample(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Validate and select one complete version-round institutional sample."""
    validated = validate_reliability_audit_data(data, source_min, source_max)
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
    if len(selected) < MINIMUM_COMPLETE_RECORDS:
        raise ValueError(
            f"Bootstrap audit requires at least {MINIMUM_COMPLETE_RECORDS} complete records "
            "as a prototype computation condition."
        )
    return selected


def _validate_bootstrap_settings(
    n_resamples: int,
    confidence_level: float,
    random_seed: int,
) -> tuple[int, float, int]:
    """Validate reproducible prototype bootstrap settings."""
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


def _dimension_scores(items: pd.DataFrame) -> pd.DataFrame:
    """Calculate current equal-item dimension scores from standardised items."""
    return pd.DataFrame(
        {
            score_column: items.loc[:, list(dimension_items)].mean(axis=1)
            for score_column, dimension_items in DIMENSION_ITEMS.items()
        },
        index=items.index,
    )


def audit_bootstrap_uncertainty(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    random_seed: int = 42,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Bootstrap dimension and Support Gap means for one version-round sample.

    Institutional rows are sampled with replacement using a local reproducible
    random generator. Percentile bounds and bootstrap standard errors describe
    the submitted sample and assumptions. No stability threshold or population
    inference decision is generated.
    """
    n_resamples, confidence_level, random_seed = _validate_bootstrap_settings(
        n_resamples,
        confidence_level,
        random_seed,
    )
    selected = _select_bootstrap_sample(
        data,
        instrument_version,
        administration_round,
        source_min,
        source_max,
    )
    standardised_items = (
        100
        * (selected.loc[:, list(ITEM_COLUMNS)] - source_min)
        / (source_max - source_min)
    )
    scores = _dimension_scores(standardised_items)
    gaps = calculate_support_gaps(scores)
    statistic_frame = pd.concat([scores, gaps.loc[:, list(GAP_COLUMNS)]], axis=1)
    statistic_columns = list(DIMENSION_ITEMS) + list(GAP_COLUMNS)
    values = statistic_frame.loc[:, statistic_columns].to_numpy(dtype=float)
    point_estimates = values.mean(axis=0)

    rng = np.random.default_rng(random_seed)
    indices = rng.integers(0, len(values), size=(n_resamples, len(values)))
    bootstrap_means = values[indices].mean(axis=1)
    alpha = 1 - confidence_level
    lower = np.quantile(bootstrap_means, alpha / 2, axis=0)
    upper = np.quantile(bootstrap_means, 1 - alpha / 2, axis=0)
    bootstrap_average = bootstrap_means.mean(axis=0)
    bootstrap_standard_error = bootstrap_means.std(axis=0, ddof=1)

    labels = {
        **{score_column: DIMENSION_LABELS[score_column] for score_column in DIMENSION_ITEMS},
        "gap_resource_practice": "Resource to Practice Gap",
        "gap_practice_participation": "Practice to Participation Gap",
        "overall_support_conversion_gap": "Overall Support Conversion Gap",
    }
    types = {
        **{score_column: "dimension_mean" for score_column in DIMENSION_ITEMS},
        **{gap_column: "support_gap_mean" for gap_column in GAP_COLUMNS},
    }
    rows = []
    for index, statistic in enumerate(statistic_columns):
        rows.append(
            {
                "statistic_type": types[statistic],
                "statistic": statistic,
                "label": labels[statistic],
                "complete_record_count": len(selected),
                "point_estimate": round(float(point_estimates[index]), 6),
                "bootstrap_mean": round(float(bootstrap_average[index]), 6),
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
    run_summary = pd.DataFrame(
        [
            {
                "instrument_version": str(instrument_version).strip(),
                "administration_round": int(administration_round),
                "complete_record_count": len(selected),
                "resampling_unit": "institutional_record",
                "sampling_method": "nonparametric_bootstrap_with_replacement",
                "n_resamples": n_resamples,
                "confidence_level": confidence_level,
                "interval_method": "percentile",
                "random_seed": random_seed,
                "default_equal_item_scoring": True,
            }
        ]
    )
    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "How sensitive are the five dimension and Support Gap means to "
                    "institutional sampling variation in a governed target population?"
                ),
                "required_future_evidence": "Probability or justified sampling design and population definition",
            },
            {
                "research_question_candidate": (
                    "Would uncertainty conclusions change under alternative weights, "
                    "cluster-aware resampling, or missing-data assumptions?"
                ),
                "required_future_evidence": "Preregistered sensitivity and dependence-aware analysis",
            },
            {
                "research_question_candidate": (
                    "Do interval widths and bias estimates replicate in an independent "
                    "institutional sample?"
                ),
                "required_future_evidence": "Independent governed validation sample",
            },
        ]
    )
    interpretation = (
        "Prototype sampling-uncertainty evidence only. Percentile intervals and bootstrap "
        "standard errors describe resampling of the submitted institutional records under "
        "equal-item scoring. They do not establish representativeness, validity, causal "
        "effects, policy effects, population parameters, or model correctness. No automatic "
        "stable/unstable label, threshold, ranking, or decision is produced."
    )
    return {
        "bootstrap_run_summary": run_summary,
        "bootstrap_interval_summary": pd.DataFrame(rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
