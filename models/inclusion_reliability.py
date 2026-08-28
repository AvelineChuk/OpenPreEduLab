"""Preliminary reliability audits for the inclusive education instrument.

The module calculates internal-consistency and repeated-administration
stability summaries from complete, non-identifying institutional research
records. Reliability evidence does not establish validity, unidimensionality,
fairness, measurement invariance, or cross-version comparability.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS


RELIABILITY_METADATA_COLUMNS: Final[tuple[str, ...]] = (
    "pseudonymous_unit_id",
    "instrument_version",
    "administration_round",
)
RELIABILITY_COLUMNS: Final[tuple[str, ...]] = RELIABILITY_METADATA_COLUMNS + ITEM_COLUMNS


def create_reliability_audit_template() -> pd.DataFrame:
    """Return a blank complete-response schema for reliability studies."""
    return pd.DataFrame(
        [{column: "" for column in RELIABILITY_COLUMNS}],
        columns=RELIABILITY_COLUMNS,
    )


def load_reliability_audit_csv(
    source: object,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Load and validate a UTF-8 reliability-study CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Reliability-study CSV could not be read: {error}") from error
    return validate_reliability_audit_data(data, source_min, source_max)


def validate_reliability_audit_data(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Validate complete item responses without imputation or clipping."""
    if not np.isfinite([source_min, source_max]).all() or source_min >= source_max:
        raise ValueError("source_min and source_max must be finite with source_min < source_max.")
    missing_columns = sorted(set(RELIABILITY_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Reliability-study data are missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Reliability-study data must contain at least one response.")
    validated = data.loc[:, list(RELIABILITY_COLUMNS)].copy()
    for column in ("pseudonymous_unit_id", "instrument_version"):
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Reliability-study field '{column}' must not be blank.")
    validated["administration_round"] = pd.to_numeric(
        validated["administration_round"], errors="coerce"
    )
    rounds = validated["administration_round"].to_numpy(dtype=float)
    if (
        not np.isfinite(rounds).all()
        or not validated["administration_round"].ge(1).all()
        or not validated["administration_round"].mod(1).eq(0).all()
    ):
        raise ValueError("administration_round must contain positive integers.")
    validated["administration_round"] = validated["administration_round"].astype(int)
    if validated.duplicated(
        ["pseudonymous_unit_id", "instrument_version", "administration_round"]
    ).any():
        raise ValueError("Each unit, version, and administration round may appear only once.")

    original_items = validated.loc[:, list(ITEM_COLUMNS)].copy()
    converted_items = original_items.apply(pd.to_numeric, errors="coerce")
    if converted_items.isna().any().any():
        invalid_columns = converted_items.columns[converted_items.isna().any()].tolist()
        raise ValueError(
            "Reliability-study item responses must be complete numeric values; "
            f"invalid or missing columns: {invalid_columns}"
        )
    values = converted_items.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Reliability-study item responses must be finite numeric values.")
    if (values < source_min).any() or (values > source_max).any():
        raise ValueError(
            f"Reliability-study item responses must lie within the declared source range "
            f"[{source_min}, {source_max}]."
        )
    validated[list(ITEM_COLUMNS)] = converted_items
    return validated


def _cronbach_alpha(values: pd.DataFrame) -> float:
    """Return sample Cronbach alpha or NaN when total variance is zero."""
    item_count = values.shape[1]
    total_variance = float(values.sum(axis=1).var(ddof=1))
    if item_count < 2 or not np.isfinite(total_variance) or total_variance <= 0:
        return float("nan")
    item_variance_sum = float(values.var(axis=0, ddof=1).sum())
    return float(item_count / (item_count - 1) * (1 - item_variance_sum / total_variance))


def calculate_internal_consistency(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Calculate alpha and item diagnostics by version, round, and dimension.

    At least three complete responses are required per version and round. No
    coefficient threshold is applied and no item decision is generated.
    """
    validated = validate_reliability_audit_data(data, source_min, source_max)
    dimension_rows = []
    item_rows = []
    for (version, administration_round), group in validated.groupby(
        ["instrument_version", "administration_round"], sort=False
    ):
        if len(group) < 3:
            raise ValueError(
                "Internal-consistency audit requires at least three complete responses "
                f"for version '{version}', round {administration_round}."
            )
        for score_column, items in DIMENSION_ITEMS.items():
            values = group.loc[:, list(items)]
            alpha = _cronbach_alpha(values)
            dimension_rows.append(
                {
                    "instrument_version": version,
                    "administration_round": int(administration_round),
                    "score_column": score_column,
                    "dimension": DIMENSION_LABELS[score_column],
                    "response_count": len(group),
                    "item_count": len(items),
                    "cronbach_alpha": round(alpha, 4) if np.isfinite(alpha) else np.nan,
                    "alpha_defined": bool(np.isfinite(alpha)),
                }
            )
            for item in items:
                remaining = [candidate for candidate in items if candidate != item]
                corrected_total = values.loc[:, remaining].sum(axis=1)
                item_values = values[item]
                if item_values.nunique() <= 1 or corrected_total.nunique() <= 1:
                    corrected_correlation = np.nan
                else:
                    corrected_correlation = float(item_values.corr(corrected_total))
                alpha_without_item = _cronbach_alpha(values.loc[:, remaining])
                item_rows.append(
                    {
                        "instrument_version": version,
                        "administration_round": int(administration_round),
                        "score_column": score_column,
                        "dimension": DIMENSION_LABELS[score_column],
                        "item": item,
                        "response_count": len(group),
                        "corrected_item_total_correlation": (
                            round(corrected_correlation, 4)
                            if np.isfinite(corrected_correlation)
                            else np.nan
                        ),
                        "alpha_if_item_removed": (
                            round(alpha_without_item, 4)
                            if np.isfinite(alpha_without_item)
                            else np.nan
                        ),
                        "item_variance": round(float(item_values.var(ddof=1)), 4),
                    }
                )
    interpretation = (
        "Internal-consistency coefficients describe covariance in the submitted sample. "
        "They do not prove unidimensionality or validity and do not create automatic "
        "retain or remove decisions."
    )
    return {
        "dimension_summary": pd.DataFrame(dimension_rows),
        "item_summary": pd.DataFrame(item_rows),
        "interpretation": interpretation,
    }


def _icc_3_1(first: np.ndarray, second: np.ndarray) -> float:
    """Return two-way mixed, single-measure consistency ICC(3,1)."""
    matrix = np.column_stack([first, second]).astype(float)
    subject_count, measurement_count = matrix.shape
    grand_mean = float(matrix.mean())
    subject_means = matrix.mean(axis=1)
    measurement_means = matrix.mean(axis=0)
    ss_subject = measurement_count * float(((subject_means - grand_mean) ** 2).sum())
    ss_measurement = subject_count * float(((measurement_means - grand_mean) ** 2).sum())
    ss_total = float(((matrix - grand_mean) ** 2).sum())
    ss_error = ss_total - ss_subject - ss_measurement
    ms_subject = ss_subject / (subject_count - 1)
    ms_error = ss_error / ((subject_count - 1) * (measurement_count - 1))
    denominator = ms_subject + (measurement_count - 1) * ms_error
    if denominator <= 0 or not np.isfinite(denominator):
        return float("nan")
    return float((ms_subject - ms_error) / denominator)


def calculate_repeated_administration_stability(
    data: pd.DataFrame,
    instrument_version: str,
    first_round: int,
    second_round: int,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Compare two rounds for matched units within one instrument version.

    At least three matched units are required. Pearson correlation and ICC(3,1)
    are descriptive stability coefficients, not evidence of temporal validity or
    absence of real change.
    """
    validated = validate_reliability_audit_data(data, source_min, source_max)
    instrument_version = str(instrument_version).strip()
    if not instrument_version:
        raise ValueError("instrument_version must not be blank.")
    if first_round == second_round:
        raise ValueError("first_round and second_round must differ.")
    version_data = validated[validated["instrument_version"].eq(instrument_version)]
    available_rounds = set(version_data["administration_round"])
    if first_round not in available_rounds or second_round not in available_rounds:
        raise ValueError("Both requested administration rounds must exist for the selected version.")

    first = version_data[version_data["administration_round"].eq(first_round)].set_index(
        "pseudonymous_unit_id"
    )
    second = version_data[version_data["administration_round"].eq(second_round)].set_index(
        "pseudonymous_unit_id"
    )
    first_ids = set(first.index)
    second_ids = set(second.index)
    matched_ids = sorted(first_ids & second_ids)
    if len(matched_ids) < 3:
        raise ValueError("Repeated-administration audit requires at least three matched units.")
    first = first.loc[matched_ids]
    second = second.loc[matched_ids]

    rows = []
    for score_column, items in DIMENSION_ITEMS.items():
        first_scores = first.loc[:, list(items)].mean(axis=1).to_numpy(dtype=float)
        second_scores = second.loc[:, list(items)].mean(axis=1).to_numpy(dtype=float)
        differences = second_scores - first_scores
        if np.unique(first_scores).size <= 1 or np.unique(second_scores).size <= 1:
            pearson = np.nan
        else:
            pearson = float(np.corrcoef(first_scores, second_scores)[0, 1])
        icc = _icc_3_1(first_scores, second_scores)
        rows.append(
            {
                "instrument_version": instrument_version,
                "first_round": int(first_round),
                "second_round": int(second_round),
                "score_column": score_column,
                "dimension": DIMENSION_LABELS[score_column],
                "matched_unit_count": len(matched_ids),
                "first_round_mean": round(float(first_scores.mean()), 4),
                "second_round_mean": round(float(second_scores.mean()), 4),
                "mean_change": round(float(differences.mean()), 4),
                "mean_absolute_change": round(float(np.abs(differences).mean()), 4),
                "pearson_correlation": round(pearson, 4) if np.isfinite(pearson) else np.nan,
                "icc_3_1_consistency": round(icc, 4) if np.isfinite(icc) else np.nan,
            }
        )
    coverage = pd.DataFrame(
        [
            {
                "instrument_version": instrument_version,
                "first_round": int(first_round),
                "second_round": int(second_round),
                "first_round_unit_count": len(first_ids),
                "second_round_unit_count": len(second_ids),
                "matched_unit_count": len(matched_ids),
                "first_round_only_count": len(first_ids - set(matched_ids)),
                "second_round_only_count": len(second_ids - set(matched_ids)),
            }
        ]
    )
    interpretation = (
        "Repeated-administration coefficients describe stability for matched units in the "
        "submitted design. They do not prove validity, rule out real change, or authorize "
        "cross-version comparison."
    )
    return {
        "dimension_stability_summary": pd.DataFrame(rows),
        "matching_coverage_summary": coverage,
        "interpretation": interpretation,
    }
