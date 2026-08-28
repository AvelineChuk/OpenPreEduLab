"""Inclusive education research utilities for institution-level prototype data.

The module operationalises the conceptual pathway Policy -> Resources ->
Practices -> Child Participation -> Equity. Scores are transparent equal-item
means on a 0–100 scale. They are research-prototype summaries, not diagnostic
assessments of children, teachers, or institutions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from models.equity import calculate_cv, calculate_gini, calculate_theil


IDENTIFIER_COLUMNS: tuple[str, ...] = ("institution_id", "institution_type", "region")

DIMENSION_ITEMS: Mapping[str, tuple[str, ...]] = {
    "policy_support_score": (
        "policy_clarity",
        "implementation_requirements",
        "professional_support",
        "resource_guarantee",
        "evaluation_mechanism",
    ),
    "resource_support_score": (
        "teacher_support",
        "special_education_support",
        "financial_support",
        "material_support",
        "environmental_support",
        "training_support",
        "family_community_support",
    ),
    "inclusive_practice_score": (
        "curriculum_adaptation",
        "instructional_support",
        "individualized_support",
        "behavior_support",
        "peer_support",
        "family_collaboration",
        "teacher_reflection",
    ),
    "child_participation_score": (
        "play_participation",
        "group_activity_participation",
        "peer_interaction",
        "communication",
        "autonomy",
        "belonging",
    ),
    "equity_score": (
        "support_equity",
        "participation_equity",
        "resource_equity",
    ),
}

DIMENSION_LABELS: Mapping[str, str] = {
    "policy_support_score": "Policy Support",
    "resource_support_score": "Resource Support",
    "inclusive_practice_score": "Inclusive Practices",
    "child_participation_score": "Child Participation",
    "equity_score": "Equity",
}

ITEM_COLUMNS: tuple[str, ...] = tuple(
    item for dimension_items in DIMENSION_ITEMS.values() for item in dimension_items
)
REQUIRED_COLUMNS: tuple[str, ...] = IDENTIFIER_COLUMNS + ITEM_COLUMNS
SCORE_COLUMNS: tuple[str, ...] = tuple(DIMENSION_ITEMS)


def inspect_inclusion_data(data: pd.DataFrame) -> pd.DataFrame:
    """Return a variable-level inspection table without altering input values."""
    return pd.DataFrame(
        {
            "variable": data.columns,
            "data_type": [str(data[column].dtype) for column in data.columns],
            "missing_values": [int(data[column].isna().sum()) for column in data.columns],
            "unique_values": [int(data[column].nunique(dropna=True)) for column in data.columns],
        }
    )


def validate_inclusion_data(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Validate identifiers and required inclusion items on a declared scale.

    Missing or non-numeric scoring values are rejected rather than imputed.
    ``source_min`` and ``source_max`` must describe the source instrument's
    legitimate closed interval and are recorded by the caller in research
    output when conversion is used.
    """
    if not np.isfinite([source_min, source_max]).all() or source_min >= source_max:
        raise ValueError("source_min and source_max must be finite with source_min < source_max.")

    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Inclusive education data are missing required columns: {missing_columns}")

    validated = data.copy()
    for column in IDENTIFIER_COLUMNS:
        if validated[column].isna().any() or validated[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Identifier field '{column}' must not contain missing or blank values.")
        validated[column] = validated[column].astype(str).str.strip()
    if validated["institution_id"].duplicated().any():
        raise ValueError("Inclusive education data contain duplicate institution_id values.")

    validated[list(ITEM_COLUMNS)] = validated[list(ITEM_COLUMNS)].apply(
        pd.to_numeric, errors="coerce"
    )
    if validated[list(ITEM_COLUMNS)].isna().any().any():
        invalid = validated[list(ITEM_COLUMNS)].columns[
            validated[list(ITEM_COLUMNS)].isna().any()
        ].tolist()
        raise ValueError(f"Required inclusion items contain missing or invalid values: {invalid}")
    values = validated.loc[:, list(ITEM_COLUMNS)].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Required inclusion items must contain finite numeric values.")
    if (values < source_min).any() or (values > source_max).any():
        raise ValueError(
            f"Required inclusion items must lie within the declared source range "
            f"[{source_min}, {source_max}]."
        )
    return validated


def standardize_inclusion_data(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Linearly convert a declared source scale to the common 0–100 scale."""
    validated = validate_inclusion_data(data, source_min=source_min, source_max=source_max)
    standardised = validated.copy()
    standardised[list(ITEM_COLUMNS)] = (
        100
        * (validated[list(ITEM_COLUMNS)] - float(source_min))
        / (float(source_max) - float(source_min))
    ).round(4)
    return standardised


def load_inclusion_data(
    file_path: str | Path,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Load a CSV and return validated inclusion items on a 0–100 scale."""
    return standardize_inclusion_data(
        pd.read_csv(file_path), source_min=source_min, source_max=source_max
    )


def calculate_inclusion_dimension_scores(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Calculate five transparent equal-item dimension scores.

    Equal item weighting is a prototype assumption. The resulting scores are
    descriptive research summaries and require future content, construct, and
    sensitivity validation before substantive use.
    """
    standardised = standardize_inclusion_data(
        data, source_min=source_min, source_max=source_max
    )
    scores = standardised.loc[:, list(IDENTIFIER_COLUMNS)].copy()
    for score_column, items in DIMENSION_ITEMS.items():
        scores[score_column] = standardised.loc[:, list(items)].mean(axis=1).round(2)
    return scores


def descriptive_statistics(data: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Return reproducible descriptive statistics for selected numeric variables."""
    selected = list(dict.fromkeys(columns))
    if not selected:
        raise ValueError("Select at least one variable for descriptive statistics.")
    missing = sorted(set(selected) - set(data.columns))
    if missing:
        raise ValueError(f"Selected variables are missing from the data: {missing}")
    values = data[selected].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise ValueError("Selected variables must contain complete finite numeric values.")
    result = values.describe().transpose().reset_index(names="variable")
    return result.round(4)


def calculate_dimension_sensitivity(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Run transparent leave-one-item-out sensitivity for each dimension.

    For every dimension, one item is removed at a time and the equal-item
    mean is recalculated. The output compares sample means and the largest
    institution-level absolute change with the default score. This is a
    diagnostic robustness check, not evidence that any item is more valid or
    causally important.
    """
    standardised = standardize_inclusion_data(data, source_min, source_max)
    rows: list[dict[str, float | str]] = []
    for score_column, items in DIMENSION_ITEMS.items():
        if len(items) < 2:
            raise ValueError(f"Sensitivity analysis requires at least two items in {score_column}.")
        baseline = standardised.loc[:, list(items)].mean(axis=1)
        for excluded_item in items:
            retained = [item for item in items if item != excluded_item]
            leave_one_out = standardised.loc[:, retained].mean(axis=1)
            rows.append(
                {
                    "dimension": DIMENSION_LABELS[score_column],
                    "score_column": score_column,
                    "item_excluded": excluded_item,
                    "baseline_mean_score": round(float(baseline.mean()), 4),
                    "leave_one_out_mean_score": round(float(leave_one_out.mean()), 4),
                    "mean_score_delta": round(float((leave_one_out.mean() - baseline.mean())), 4),
                    "max_abs_institution_delta": round(float((leave_one_out - baseline).abs().max()), 4),
                }
            )
    return pd.DataFrame(rows)


def correlation_matrix(data: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Calculate a descriptive Pearson correlation matrix for selected variables."""
    selected = list(dict.fromkeys(columns))
    if len(selected) < 2:
        raise ValueError("Correlation analysis requires at least two variables.")
    values = data[selected].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise ValueError("Correlation variables must contain complete finite numeric values.")
    if len(values) < 3:
        raise ValueError("Correlation analysis requires at least three observations.")
    return values.corr(method="pearson").round(4)


def distributional_equity_report(scores: pd.DataFrame, value_column: str) -> pd.DataFrame:
    """Describe cross-institution inequality for one selected dimension score."""
    if value_column not in scores.columns:
        raise ValueError(f"Score column '{value_column}' is not available.")
    values = scores[value_column]
    return pd.DataFrame(
        [
            {"indicator": "Coefficient of Variation", "value": calculate_cv(values)},
            {"indicator": "Gini Coefficient", "value": calculate_gini(values)},
            {"indicator": "Theil Index", "value": calculate_theil(values)},
        ]
    ).round(6)


def cluster_institutions(
    scores: pd.DataFrame,
    score_columns: Sequence[str] = SCORE_COLUMNS,
    n_clusters: int = 3,
    random_state: int = 42,
) -> pd.DataFrame:
    """Run exploratory K-means clustering on selected dimension scores.

    Cluster numbers are neutral pattern identifiers, not quality labels or
    validated institution types. At least six institutions are required.
    """
    selected = list(dict.fromkeys(score_columns))
    if len(scores) < 6:
        raise ValueError("Exploratory cluster analysis requires at least six institutions.")
    if n_clusters < 2 or n_clusters >= len(scores):
        raise ValueError("n_clusters must be at least 2 and smaller than the institution count.")
    missing = sorted(set(selected) - set(scores.columns))
    if missing:
        raise ValueError(f"Cluster score columns are missing: {missing}")
    values = scores[selected].apply(pd.to_numeric, errors="coerce")
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise ValueError("Cluster inputs must contain complete finite numeric values.")
    labels = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=20).fit_predict(
        StandardScaler().fit_transform(values)
    )
    result = scores.loc[:, list(IDENTIFIER_COLUMNS)].copy()
    result["exploratory_cluster"] = labels + 1
    return result


def generate_research_insights(
    dimension_scores: pd.DataFrame,
    support_gaps: pd.DataFrame,
) -> dict[str, object]:
    """Generate deterministic, evidence-bounded insights and question candidates."""
    from models.support_gap import identify_major_support_gap

    score_means = dimension_scores.loc[:, list(SCORE_COLUMNS)].mean()
    gap_means = support_gaps[
        ["gap_resource_practice", "gap_practice_participation", "overall_support_conversion_gap"]
    ].mean()
    strongest = str(score_means.idxmax())
    weakest = str(score_means.idxmin())
    major_gap = identify_major_support_gap(gap_means)
    insight = (
        f"{DIMENSION_LABELS[strongest]} is the highest aggregate dimension "
        f"({score_means[strongest]:.1f}), while {DIMENSION_LABELS[weakest]} is the "
        f"lowest ({score_means[weakest]:.1f}). These are descriptive sample patterns."
    )
    questions = [
        str(major_gap["research_question"]),
        (
            f"Which institutional and policy conditions may be associated with the "
            f"comparatively lower {DIMENSION_LABELS[weakest].lower()} score?"
        ),
        (
            "How stable are the five dimension scores and support-gap patterns under "
            "alternative item weights and independently validated measures?"
        ),
    ]
    return {
        "insight": insight,
        "major_gap": major_gap,
        "research_question_candidates": questions,
        "score_means": score_means.round(4).to_dict(),
        "gap_means": gap_means.round(4).to_dict(),
    }


def simulate_inclusion_scenarios(
    data: pd.DataFrame,
    change_points: float = 10.0,
) -> pd.DataFrame:
    """Compare four exploratory support scenarios on the 0–100 item scale.

    Each scenario adds ``change_points`` to one named item and clips the value
    at 100. All other items remain fixed. Outputs are arithmetic scenario
    comparisons, not forecasts or causal predictions.
    """
    if not np.isfinite(change_points) or change_points < 0:
        raise ValueError("change_points must be a finite non-negative value.")
    baseline = standardize_inclusion_data(data)
    scenarios = {
        "Baseline": None,
        "Increase Teacher Support": "teacher_support",
        "Increase Training Support": "training_support",
        "Increase Financial Support": "financial_support",
        "Improve Curriculum Adaptation": "curriculum_adaptation",
    }
    rows: list[dict[str, float | str]] = []
    from models.support_gap import calculate_support_gaps

    for scenario, changed_item in scenarios.items():
        scenario_data = baseline.copy()
        if changed_item is not None:
            scenario_data[changed_item] = (scenario_data[changed_item] + change_points).clip(upper=100)
        scores = calculate_inclusion_dimension_scores(scenario_data)
        gaps = calculate_support_gaps(scores)
        row: dict[str, float | str] = {"scenario": scenario}
        row.update(scores[list(SCORE_COLUMNS)].mean().round(4).to_dict())
        row.update(
            gaps[
                ["gap_resource_practice", "gap_practice_participation", "overall_support_conversion_gap"]
            ].mean().round(4).to_dict()
        )
        rows.append(row)
    return pd.DataFrame(rows)
