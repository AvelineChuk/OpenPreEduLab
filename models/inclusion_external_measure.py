"""External-measure relationship readiness audits for inclusive education.

The module links complete, non-identifying institutional item responses to one
declared independent institutional measure. Descriptive correlations and
uncertainty intervals support future validation planning but do not establish
convergent, discriminant, criterion-related, predictive, or causal validity.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd
from scipy.stats import norm, pearsonr, spearmanr

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS
from models.inclusion_reliability import (
    RELIABILITY_COLUMNS,
    validate_reliability_audit_data,
)


EXTERNAL_METADATA_COLUMNS: Final[tuple[str, ...]] = (
    "external_measure_name",
    "external_measure_source",
    "expected_relationship_type",
    "external_measure_value",
)
EXTERNAL_MEASURE_COLUMNS: Final[tuple[str, ...]] = (
    RELIABILITY_COLUMNS + EXTERNAL_METADATA_COLUMNS
)
EXPECTED_RELATIONSHIP_TYPES: Final[tuple[str, ...]] = (
    "convergent_candidate",
    "discriminant_candidate",
    "criterion_related_candidate",
    "exploratory_related_measure",
)
MINIMUM_COMPLETE_RECORDS: Final[int] = 5


def create_external_measure_template() -> pd.DataFrame:
    """Return a blank schema for one declared external institutional measure."""
    return pd.DataFrame(
        [{column: "" for column in EXTERNAL_MEASURE_COLUMNS}],
        columns=EXTERNAL_MEASURE_COLUMNS,
    )


def load_external_measure_csv(
    source: object,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Load and validate a UTF-8 external-measure audit CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"External-measure CSV could not be read: {error}") from error
    return validate_external_measure_data(data, source_min, source_max)


def validate_external_measure_data(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Validate complete instrument responses and external-measure metadata."""
    missing = sorted(set(EXTERNAL_METADATA_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"External-measure data are missing required columns: {missing}")
    validated = validate_reliability_audit_data(data, source_min, source_max)
    for column in (
        "external_measure_name",
        "external_measure_source",
        "expected_relationship_type",
    ):
        values = data[column].fillna("").astype(str).str.strip()
        if values.eq("").any():
            raise ValueError(f"External-measure field '{column}' must not be blank.")
        validated[column] = values.to_numpy()
    invalid_types = sorted(
        set(validated["expected_relationship_type"]) - set(EXPECTED_RELATIONSHIP_TYPES)
    )
    if invalid_types:
        raise ValueError(f"Unknown expected relationship types: {invalid_types}")
    external_values = pd.to_numeric(data["external_measure_value"], errors="coerce")
    if external_values.isna().any() or not np.isfinite(
        external_values.to_numpy(dtype=float)
    ).all():
        raise ValueError("external_measure_value must contain complete finite numeric values.")
    validated["external_measure_value"] = external_values.to_numpy(dtype=float)
    return validated.loc[:, list(EXTERNAL_MEASURE_COLUMNS)]


def _select_external_measure_sample(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Select one version-round and enforce one consistent external measure."""
    validated = validate_external_measure_data(data, source_min, source_max)
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
            f"External-measure audit requires at least {MINIMUM_COMPLETE_RECORDS} complete "
            "records as a prototype computation condition."
        )
    for column in (
        "external_measure_name",
        "external_measure_source",
        "expected_relationship_type",
    ):
        if selected[column].nunique() != 1:
            raise ValueError(
                f"The selected version and round must declare exactly one consistent '{column}'."
            )
    return selected


def _fisher_interval(correlation: float, sample_size: int) -> tuple[float, float]:
    """Return an approximate two-sided 95% Fisher-z interval for Pearson r."""
    if sample_size <= 3 or not np.isfinite(correlation) or abs(correlation) >= 1:
        if np.isfinite(correlation) and abs(correlation) == 1:
            return correlation, correlation
        return np.nan, np.nan
    transformed = np.arctanh(correlation)
    margin = float(norm.ppf(0.975) / np.sqrt(sample_size - 3))
    return float(np.tanh(transformed - margin)), float(np.tanh(transformed + margin))


def audit_external_measure_relationships(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Describe five-dimension relationships with one external measure.

    Dimension scores use the current equal-item prototype mean after linear
    conversion of item responses to 0-100. Pearson and Spearman correlations
    are descriptive. The approximate Pearson interval uses Fisher's z
    transformation and is not an automatic validity decision.
    """
    selected = _select_external_measure_sample(
        data,
        instrument_version,
        administration_round,
        source_min,
        source_max,
    )
    external = selected["external_measure_value"].to_numpy(dtype=float)
    external_variance = float(np.var(external, ddof=1))
    standardised_items = (
        100
        * (selected.loc[:, [item for items in DIMENSION_ITEMS.values() for item in items]] - source_min)
        / (source_max - source_min)
    )
    metadata = selected.iloc[0]
    coverage = pd.DataFrame(
        [
            {
                "instrument_version": str(instrument_version).strip(),
                "administration_round": int(administration_round),
                "complete_record_count": len(selected),
                "external_measure_name": metadata["external_measure_name"],
                "external_measure_source": metadata["external_measure_source"],
                "expected_relationship_type": metadata["expected_relationship_type"],
                "external_measure_mean": round(float(external.mean()), 6),
                "external_measure_standard_deviation": round(
                    float(external.std(ddof=1)), 6
                ),
                "external_measure_variance_positive": bool(external_variance > 0),
            }
        ]
    )

    relationship_rows = []
    for score_column, items in DIMENSION_ITEMS.items():
        dimension_scores = standardised_items.loc[:, list(items)].mean(axis=1).to_numpy()
        dimension_variance = float(np.var(dimension_scores, ddof=1))
        correlation_defined = bool(external_variance > 0 and dimension_variance > 0)
        if correlation_defined:
            pearson = float(pearsonr(dimension_scores, external).statistic)
            spearman = float(spearmanr(dimension_scores, external).statistic)
            lower, upper = _fisher_interval(pearson, len(selected))
        else:
            pearson = spearman = lower = upper = np.nan
        relationship_rows.append(
            {
                "score_column": score_column,
                "dimension": DIMENSION_LABELS[score_column],
                "complete_record_count": len(selected),
                "dimension_mean": round(float(dimension_scores.mean()), 6),
                "dimension_standard_deviation": round(
                    float(dimension_scores.std(ddof=1)), 6
                ),
                "pearson_correlation": round(pearson, 6) if np.isfinite(pearson) else np.nan,
                "pearson_fisher_95_ci_lower": (
                    round(lower, 6) if np.isfinite(lower) else np.nan
                ),
                "pearson_fisher_95_ci_upper": (
                    round(upper, 6) if np.isfinite(upper) else np.nan
                ),
                "spearman_correlation": (
                    round(spearman, 6) if np.isfinite(spearman) else np.nan
                ),
                "correlation_defined": correlation_defined,
            }
        )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Is the declared external measure theoretically independent from the "
                    "inclusive education items and appropriate for the proposed relationship?"
                ),
                "required_future_evidence": "Measure provenance, construct definition, and method review",
            },
            {
                "research_question_candidate": (
                    "Are the observed dimension relationships stable under a preregistered "
                    "design, adequate sample, and alternative scoring assumptions?"
                ),
                "required_future_evidence": "Independent sample, uncertainty and sensitivity analysis",
            },
            {
                "research_question_candidate": (
                    "Could common method, administration timing, institutional context, or "
                    "selection processes explain the observed associations?"
                ),
                "required_future_evidence": "Design audit and appropriately timed independent measures",
            },
        ]
    )
    interpretation = (
        "Relationship-readiness evidence only. Correlations and approximate Fisher-z "
        "intervals do not establish convergent, discriminant, criterion-related, "
        "predictive, or causal validity. The declared expected relationship is research "
        "metadata, not an automatic hypothesis test. No pass/fail threshold, ranking, "
        "item decision, or substantive institution conclusion is produced."
    )
    return {
        "external_measure_coverage_summary": coverage,
        "dimension_relationship_summary": pd.DataFrame(relationship_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
