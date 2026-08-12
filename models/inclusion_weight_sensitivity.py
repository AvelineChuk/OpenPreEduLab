"""Alternative item-weight sensitivity audits for inclusive education.

Researcher-declared, complete weighting schemes are compared with the current
equal-item prototype baseline. The workflow describes score and Support Gap
sensitivity; it does not learn, optimise, recommend, or validate weights and
does not change the platform's default scoring model.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import validate_reliability_audit_data
from models.support_gap import calculate_support_gaps


WEIGHT_SCHEME_COLUMNS: Final[tuple[str, ...]] = (
    "scheme_name",
    "scheme_rationale",
    "evidence_status",
    "score_column",
    "dimension",
    "item",
    "item_weight",
)
EVIDENCE_STATUSES: Final[tuple[str, ...]] = (
    "theory_candidate",
    "expert_proposed",
    "empirical_candidate",
    "exploratory_sensitivity",
)


def create_weight_scheme_template() -> pd.DataFrame:
    """Return a complete blank-metadata equal-weight scheme template."""
    rows = []
    for score_column, items in DIMENSION_ITEMS.items():
        for item in items:
            rows.append(
                {
                    "scheme_name": "",
                    "scheme_rationale": "",
                    "evidence_status": "",
                    "score_column": score_column,
                    "dimension": DIMENSION_LABELS[score_column],
                    "item": item,
                    "item_weight": round(1 / len(items), 10),
                }
            )
    return pd.DataFrame(rows, columns=WEIGHT_SCHEME_COLUMNS)


def load_weight_scheme_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 alternative weighting-scheme CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Weight-scheme CSV could not be read: {error}") from error
    return validate_weight_schemes(data)


def validate_weight_schemes(schemes: pd.DataFrame) -> pd.DataFrame:
    """Validate complete positive item weights for one or more named schemes."""
    missing = sorted(set(WEIGHT_SCHEME_COLUMNS) - set(schemes.columns))
    if missing:
        raise ValueError(f"Weight-scheme data are missing required columns: {missing}")
    if schemes.empty:
        raise ValueError("Weight-scheme data must contain at least one complete scheme.")
    validated = schemes.loc[:, list(WEIGHT_SCHEME_COLUMNS)].copy()
    for column in (
        "scheme_name",
        "scheme_rationale",
        "evidence_status",
        "score_column",
        "dimension",
        "item",
    ):
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Weight-scheme field '{column}' must not be blank.")
    invalid_statuses = sorted(set(validated["evidence_status"]) - set(EVIDENCE_STATUSES))
    if invalid_statuses:
        raise ValueError(f"Unknown weight evidence statuses: {invalid_statuses}")
    validated["item_weight"] = pd.to_numeric(validated["item_weight"], errors="coerce")
    weights = validated["item_weight"].to_numpy(dtype=float)
    if not np.isfinite(weights).all() or (weights <= 0).any():
        raise ValueError("Every item_weight must be a finite positive numeric value.")
    if validated.duplicated(["scheme_name", "item"]).any():
        raise ValueError("Every item may appear only once within a weighting scheme.")

    expected_items = set(ITEM_COLUMNS)
    for scheme_name, scheme in validated.groupby("scheme_name", sort=False):
        if set(scheme["item"]) != expected_items:
            missing_items = sorted(expected_items - set(scheme["item"]))
            extra_items = sorted(set(scheme["item"]) - expected_items)
            raise ValueError(
                f"Weighting scheme '{scheme_name}' must contain exactly the current 28 items; "
                f"missing: {missing_items}; unknown: {extra_items}"
            )
        for metadata_column in ("scheme_rationale", "evidence_status"):
            if scheme[metadata_column].nunique() != 1:
                raise ValueError(
                    f"Weighting scheme '{scheme_name}' must use one consistent "
                    f"'{metadata_column}'."
                )
        for row in scheme.itertuples(index=False):
            expected_score = next(
                score_column
                for score_column, items in DIMENSION_ITEMS.items()
                if row.item in items
            )
            if row.score_column != expected_score:
                raise ValueError(f"Item '{row.item}' is mapped to the wrong score_column.")
            if row.dimension != DIMENSION_LABELS[expected_score]:
                raise ValueError(f"Item '{row.item}' has an inconsistent dimension label.")
    weight_sums = validated.groupby(["scheme_name", "score_column"])["item_weight"].sum()
    if not np.isclose(weight_sums.to_numpy(dtype=float), 1.0, atol=1e-6).all():
        raise ValueError("Item weights must sum to 1 within every scheme and dimension.")
    return validated


def _select_response_sample(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Select one complete version-round response sample."""
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
    return selected


def _scores_from_weights(items: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Calculate five dimension scores for a complete item-weight mapping."""
    scores = pd.DataFrame(index=items.index)
    for score_column, dimension_items in DIMENSION_ITEMS.items():
        dimension_weights = np.array([weights[item] for item in dimension_items])
        scores[score_column] = items.loc[:, list(dimension_items)].to_numpy().dot(
            dimension_weights
        )
    return scores


def audit_weight_sensitivity(
    response_data: pd.DataFrame,
    weight_schemes: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Compare declared weighting schemes with the equal-item baseline.

    Outputs aggregate institution-level changes without returning unit IDs.
    Weight schemes remain researcher declarations and are never optimised,
    ranked, selected, or applied to the platform's default scores.
    """
    selected = _select_response_sample(
        response_data,
        instrument_version,
        administration_round,
        source_min,
        source_max,
    )
    schemes = validate_weight_schemes(weight_schemes)
    items = (
        100
        * (selected.loc[:, list(ITEM_COLUMNS)] - source_min)
        / (source_max - source_min)
    )
    equal_weights = {
        item: 1 / len(dimension_items)
        for dimension_items in DIMENSION_ITEMS.values()
        for item in dimension_items
    }
    baseline_scores = _scores_from_weights(items, equal_weights)
    baseline_gaps = calculate_support_gaps(baseline_scores)

    scheme_rows = []
    dimension_rows = []
    gap_rows = []
    for scheme_name, scheme in schemes.groupby("scheme_name", sort=False):
        weights = dict(zip(scheme["item"], scheme["item_weight"], strict=True))
        alternative_scores = _scores_from_weights(items, weights)
        alternative_gaps = calculate_support_gaps(alternative_scores)
        metadata = scheme.iloc[0]
        scheme_rows.append(
            {
                "scheme_name": scheme_name,
                "scheme_rationale": metadata["scheme_rationale"],
                "evidence_status": metadata["evidence_status"],
                "instrument_version": str(instrument_version).strip(),
                "administration_round": int(administration_round),
                "complete_record_count": len(selected),
                "default_scoring_changed": False,
            }
        )
        for score_column in DIMENSION_ITEMS:
            change = alternative_scores[score_column] - baseline_scores[score_column]
            dimension_rows.append(
                {
                    "scheme_name": scheme_name,
                    "score_column": score_column,
                    "dimension": DIMENSION_LABELS[score_column],
                    "complete_record_count": len(selected),
                    "equal_weight_mean": round(float(baseline_scores[score_column].mean()), 6),
                    "alternative_weight_mean": round(
                        float(alternative_scores[score_column].mean()), 6
                    ),
                    "mean_score_change": round(float(change.mean()), 6),
                    "mean_absolute_institution_change": round(float(change.abs().mean()), 6),
                    "maximum_absolute_institution_change": round(float(change.abs().max()), 6),
                }
            )
        for gap_column in (
            "gap_resource_practice",
            "gap_practice_participation",
            "overall_support_conversion_gap",
        ):
            change = alternative_gaps[gap_column] - baseline_gaps[gap_column]
            gap_rows.append(
                {
                    "scheme_name": scheme_name,
                    "gap_indicator": gap_column,
                    "complete_record_count": len(selected),
                    "equal_weight_mean": round(float(baseline_gaps[gap_column].mean()), 6),
                    "alternative_weight_mean": round(
                        float(alternative_gaps[gap_column].mean()), 6
                    ),
                    "mean_gap_change": round(float(change.mean()), 6),
                    "mean_absolute_institution_change": round(float(change.abs().mean()), 6),
                    "maximum_absolute_institution_change": round(float(change.abs().max()), 6),
                }
            )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Are substantive interpretations stable across theoretically justified "
                    "item-weight schemes?"
                ),
                "required_future_evidence": "Theory, expert review, and independent sensitivity analysis",
            },
            {
                "research_question_candidate": (
                    "Which item-weight assumptions account for observed changes in dimension "
                    "or Support Gap summaries?"
                ),
                "required_future_evidence": "Transparent scheme rationale and item-level review",
            },
            {
                "research_question_candidate": (
                    "Would alternative scoring conclusions replicate in an independent, "
                    "governed empirical sample?"
                ),
                "required_future_evidence": "Independent validation sample and preregistered scoring plan",
            },
        ]
    )
    interpretation = (
        "Sensitivity evidence only. Alternative weights are researcher-declared assumptions, "
        "not learned or validated parameters. Score and Support Gap changes do not identify "
        "a best scheme, justify item importance, establish validity, or estimate causal "
        "effects. The platform default remains equal-item weighting and no automatic "
        "threshold, ranking, or scheme recommendation is produced."
    )
    return {
        "weight_scheme_summary": pd.DataFrame(scheme_rows),
        "dimension_sensitivity_summary": pd.DataFrame(dimension_rows),
        "support_gap_sensitivity_summary": pd.DataFrame(gap_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
