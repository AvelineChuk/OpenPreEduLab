"""Feasibility-pilot and data-quality audits for the inclusion instrument.

This module examines administration completeness, missingness, endpoint
concentration, item variation, duration, and reported implementation burden.
It does not estimate reliability or validity, score incomplete records, assess
children, rank institutions, or automatically remove items.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS


FEASIBILITY_METADATA_COLUMNS: Final[tuple[str, ...]] = (
    "administration_id",
    "instrument_version",
    "administration_mode",
    "administration_status",
    "duration_minutes",
    "burden_rating",
)
FEASIBILITY_COLUMNS: Final[tuple[str, ...]] = FEASIBILITY_METADATA_COLUMNS + ITEM_COLUMNS
ADMINISTRATION_STATUSES: Final[tuple[str, ...]] = ("complete", "partial", "abandoned")
BURDEN_SCALE: Final[tuple[int, ...]] = (1, 2, 3, 4, 5)


def create_feasibility_pilot_template() -> pd.DataFrame:
    """Return a blank one-row schema for non-identifying pilot administrations."""
    row = {column: "" for column in FEASIBILITY_COLUMNS}
    return pd.DataFrame([row], columns=FEASIBILITY_COLUMNS)


def load_feasibility_pilot_csv(
    source: object,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Load and validate a UTF-8 feasibility-pilot CSV without imputation."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Feasibility-pilot CSV could not be read: {error}") from error
    return validate_feasibility_pilot_data(data, source_min, source_max)


def validate_feasibility_pilot_data(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Validate pilot records while preserving legitimate item missingness.

    Item responses may be missing because missingness is an audit target. All
    observed item values must be finite and within the declared source range.
    """
    if not np.isfinite([source_min, source_max]).all() or source_min >= source_max:
        raise ValueError("source_min and source_max must be finite with source_min < source_max.")
    missing_columns = sorted(set(FEASIBILITY_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Feasibility-pilot data are missing required columns: {missing_columns}")
    if data.empty:
        raise ValueError("Feasibility-pilot data must contain at least one administration.")
    validated = data.loc[:, list(FEASIBILITY_COLUMNS)].copy()

    for column in ("administration_id", "instrument_version", "administration_mode", "administration_status"):
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Feasibility-pilot field '{column}' must not be blank.")
    if validated["administration_id"].duplicated().any():
        raise ValueError("administration_id values must be unique.")
    invalid_statuses = sorted(
        set(validated["administration_status"]) - set(ADMINISTRATION_STATUSES)
    )
    if invalid_statuses:
        raise ValueError(f"Unknown administration statuses: {invalid_statuses}")

    for column in ("duration_minutes", "burden_rating"):
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
        if validated[column].isna().any() or not np.isfinite(
            validated[column].to_numpy(dtype=float)
        ).all():
            raise ValueError(f"{column} must contain complete finite numeric values.")
    if validated["duration_minutes"].le(0).any():
        raise ValueError("duration_minutes must be positive.")
    if not validated["burden_rating"].isin(BURDEN_SCALE).all():
        raise ValueError("burden_rating must use integer categories 1, 2, 3, 4, or 5.")
    validated["burden_rating"] = validated["burden_rating"].astype(int)

    original_items = validated.loc[:, list(ITEM_COLUMNS)].copy()
    converted_items = original_items.apply(pd.to_numeric, errors="coerce")
    supplied_mask = original_items.notna() & original_items.astype(str).apply(
        lambda column: column.str.strip().ne("")
    )
    invalid_numeric = supplied_mask & converted_items.isna()
    if invalid_numeric.any().any():
        invalid_columns = invalid_numeric.columns[invalid_numeric.any()].tolist()
        raise ValueError(
            f"Observed item responses contain non-numeric values: {invalid_columns}"
        )
    validated[list(ITEM_COLUMNS)] = converted_items
    item_values = validated.loc[:, list(ITEM_COLUMNS)].to_numpy(dtype=float)
    observed_values = item_values[~np.isnan(item_values)]
    if observed_values.size == 0:
        raise ValueError("Feasibility-pilot data must contain at least one observed item response.")
    if not np.isfinite(observed_values).all():
        raise ValueError("Observed item responses must be finite numeric values.")
    if (observed_values < source_min).any() or (observed_values > source_max).any():
        raise ValueError(
            f"Observed item responses must lie within the declared source range "
            f"[{source_min}, {source_max}]."
        )

    missing_counts = validated.loc[:, list(ITEM_COLUMNS)].isna().sum(axis=1)
    expected_status = np.where(
        missing_counts.eq(0),
        "complete",
        np.where(missing_counts.lt(len(ITEM_COLUMNS)), "partial", "abandoned"),
    )
    mismatch = validated["administration_status"].to_numpy() != expected_status
    if mismatch.any():
        raise ValueError(
            "administration_status must match observed item completion: complete, partial, or abandoned."
        )
    return validated


def audit_feasibility_pilot(
    data: pd.DataFrame,
    source_min: float = 0.0,
    source_max: float = 100.0,
    endpoint_flag_threshold: float = 0.15,
    missing_flag_threshold: float = 0.10,
) -> dict[str, pd.DataFrame | str]:
    """Calculate descriptive feasibility and data-quality summaries.

    Thresholds are explicit prototype audit parameters. Flags identify follow-
    up questions only; they are not psychometric criteria or deletion rules.
    """
    if not 0 <= endpoint_flag_threshold <= 1:
        raise ValueError("endpoint_flag_threshold must lie between 0 and 1.")
    if not 0 <= missing_flag_threshold <= 1:
        raise ValueError("missing_flag_threshold must lie between 0 and 1.")
    validated = validate_feasibility_pilot_data(data, source_min, source_max)
    items = validated.loc[:, list(ITEM_COLUMNS)]
    record_count = len(validated)
    item_missing_counts = items.isna().sum()
    observed_counts = items.notna().sum()
    floor_counts = items.eq(source_min).sum()
    ceiling_counts = items.eq(source_max).sum()
    means = items.mean(skipna=True)
    standard_deviations = items.std(skipna=True, ddof=1)
    unique_counts = items.nunique(dropna=True)

    item_rows = []
    item_to_dimension = {
        item: (score_column, DIMENSION_LABELS[score_column])
        for score_column, dimension_items in DIMENSION_ITEMS.items()
        for item in dimension_items
    }
    for item in ITEM_COLUMNS:
        score_column, dimension = item_to_dimension[item]
        observed_count = int(observed_counts[item])
        missing_rate = float(item_missing_counts[item] / record_count)
        floor_rate = float(floor_counts[item] / observed_count) if observed_count else np.nan
        ceiling_rate = float(ceiling_counts[item] / observed_count) if observed_count else np.nan
        item_rows.append(
            {
                "score_column": score_column,
                "dimension": dimension,
                "item": item,
                "administration_count": record_count,
                "observed_count": observed_count,
                "missing_count": int(item_missing_counts[item]),
                "missing_rate": round(missing_rate, 4),
                "floor_rate": round(floor_rate, 4) if np.isfinite(floor_rate) else np.nan,
                "ceiling_rate": round(ceiling_rate, 4) if np.isfinite(ceiling_rate) else np.nan,
                "mean_observed_response": round(float(means[item]), 4) if observed_count else np.nan,
                "standard_deviation": (
                    round(float(standard_deviations[item]), 4)
                    if np.isfinite(standard_deviations[item])
                    else np.nan
                ),
                "unique_observed_values": int(unique_counts[item]),
                "missingness_follow_up_flag": missing_rate >= missing_flag_threshold,
                "floor_follow_up_flag": (
                    bool(floor_rate >= endpoint_flag_threshold) if np.isfinite(floor_rate) else False
                ),
                "ceiling_follow_up_flag": (
                    bool(ceiling_rate >= endpoint_flag_threshold) if np.isfinite(ceiling_rate) else False
                ),
                "no_variation_follow_up_flag": int(unique_counts[item]) <= 1 and observed_count > 0,
            }
        )
    item_summary = pd.DataFrame(item_rows)

    answered_counts = items.notna().sum(axis=1)
    record_summary = pd.DataFrame(
        [
            {
                "instrument_version": version,
                "administration_count": len(group),
                "complete_count": int(group["administration_status"].eq("complete").sum()),
                "partial_count": int(group["administration_status"].eq("partial").sum()),
                "abandoned_count": int(group["administration_status"].eq("abandoned").sum()),
                "complete_rate": round(float(group["administration_status"].eq("complete").mean()), 4),
                "median_duration_minutes": round(float(group["duration_minutes"].median()), 4),
                "mean_duration_minutes": round(float(group["duration_minutes"].mean()), 4),
                "median_burden_rating": round(float(group["burden_rating"].median()), 4),
                "mean_burden_rating": round(float(group["burden_rating"].mean()), 4),
                "mean_items_answered": round(float(answered_counts.loc[group.index].mean()), 4),
            }
            for version, group in validated.groupby("instrument_version", sort=False)
        ]
    )
    missing_count_distribution = (
        pd.DataFrame({"missing_item_count": items.isna().sum(axis=1)})
        .value_counts(sort=False)
        .rename("administration_count")
        .reset_index()
        .sort_values("missing_item_count")
        .reset_index(drop=True)
    )
    mode_summary = (
        validated.groupby(["instrument_version", "administration_mode"], sort=False)
        .agg(
            administration_count=("administration_id", "count"),
            complete_rate=("administration_status", lambda values: float(values.eq("complete").mean())),
            median_duration_minutes=("duration_minutes", "median"),
            mean_burden_rating=("burden_rating", "mean"),
        )
        .reset_index()
        .round(4)
    )
    interpretation = (
        "Feasibility and data-quality flags identify collection and measurement questions for "
        "follow-up. They do not establish reliability or validity and do not justify automatic "
        "item removal, score correction, child assessment, or institution ranking."
    )
    return {
        "administration_summary": record_summary,
        "item_quality_summary": item_summary,
        "missing_count_distribution": missing_count_distribution,
        "administration_mode_summary": mode_summary,
        "interpretation": interpretation,
    }
