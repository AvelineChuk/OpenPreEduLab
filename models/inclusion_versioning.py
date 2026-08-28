"""Instrument-version registry and structural comparability audit utilities.

The registry records complete active-item snapshots for declared versions of
the aggregate Inclusive Education research instrument. Structural audits flag
changes between versions but never establish empirical score comparability or
create a cross-version conversion.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS


VERSION_COLUMNS: Final[tuple[str, ...]] = (
    "instrument_version",
    "release_status",
    "effective_date",
    "item_id",
    "predecessor_item_id",
    "score_column",
    "dimension",
    "item_wording",
    "response_min",
    "response_max",
    "item_weight",
    "change_type",
    "comparability_assessment",
    "comparability_note",
    "governance_status",
)

RELEASE_STATUSES: Final[tuple[str, ...]] = ("draft", "released", "retired")
CHANGE_TYPES: Final[tuple[str, ...]] = (
    "baseline",
    "retain",
    "revise",
    "move",
    "split",
    "add",
)
COMPARABILITY_ASSESSMENTS: Final[tuple[str, ...]] = (
    "direct_comparison_not_established",
    "potentially_comparable_pending_review",
    "empirical_linking_required",
)
GOVERNANCE_STATUSES: Final[tuple[str, ...]] = (
    "draft",
    "review_pending",
    "documented_research_version",
)


def create_instrument_version_registry_template() -> pd.DataFrame:
    """Return a blank metadata template for the current 28-item structure.

    Item weights reproduce the current equal-item prototype assumption within
    each dimension. Version, wording, governance, and comparability fields are
    deliberately blank and must be completed by the research team.
    """
    rows = []
    for score_column, items in DIMENSION_ITEMS.items():
        weight = round(1.0 / len(items), 10)
        for item in items:
            rows.append(
                {
                    "instrument_version": "",
                    "release_status": "",
                    "effective_date": "",
                    "item_id": item,
                    "predecessor_item_id": "",
                    "score_column": score_column,
                    "dimension": DIMENSION_LABELS[score_column],
                    "item_wording": "",
                    "response_min": 0.0,
                    "response_max": 100.0,
                    "item_weight": weight,
                    "change_type": "",
                    "comparability_assessment": "",
                    "comparability_note": "",
                    "governance_status": "",
                }
            )
    return pd.DataFrame(rows, columns=VERSION_COLUMNS)


def load_instrument_version_registry_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 instrument-version registry CSV."""
    try:
        registry = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Instrument-version registry CSV could not be read: {error}") from error
    return validate_instrument_version_registry(registry)


def validate_instrument_version_registry(registry: pd.DataFrame) -> pd.DataFrame:
    """Validate complete active-item snapshots for one or more versions."""
    missing = sorted(set(VERSION_COLUMNS) - set(registry.columns))
    if missing:
        raise ValueError(f"Instrument-version registry is missing required columns: {missing}")
    if registry.empty:
        raise ValueError("Instrument-version registry must contain at least one version snapshot.")
    validated = registry.loc[:, list(VERSION_COLUMNS)].copy()

    required_text = (
        "instrument_version",
        "release_status",
        "item_id",
        "score_column",
        "dimension",
        "item_wording",
        "change_type",
        "comparability_assessment",
        "comparability_note",
        "governance_status",
    )
    for column in required_text:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Instrument-version field '{column}' must not be blank.")
    validated["predecessor_item_id"] = (
        validated["predecessor_item_id"].fillna("").astype(str).str.strip()
    )

    invalid_release = sorted(set(validated["release_status"]) - set(RELEASE_STATUSES))
    if invalid_release:
        raise ValueError(f"Unknown release statuses: {invalid_release}")
    invalid_changes = sorted(set(validated["change_type"]) - set(CHANGE_TYPES))
    if invalid_changes:
        raise ValueError(f"Unknown change types: {invalid_changes}")
    invalid_comparability = sorted(
        set(validated["comparability_assessment"]) - set(COMPARABILITY_ASSESSMENTS)
    )
    if invalid_comparability:
        raise ValueError(f"Unknown comparability assessments: {invalid_comparability}")
    invalid_governance = sorted(
        set(validated["governance_status"]) - set(GOVERNANCE_STATUSES)
    )
    if invalid_governance:
        raise ValueError(f"Unknown governance statuses: {invalid_governance}")

    for column in ("response_min", "response_max", "item_weight"):
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
        if not np.isfinite(validated[column].to_numpy(dtype=float)).all():
            raise ValueError(f"{column} must contain finite numeric values.")
    if validated["response_min"].ge(validated["response_max"]).any():
        raise ValueError("Every response_min must be smaller than response_max.")
    if validated["item_weight"].le(0).any():
        raise ValueError("Every item_weight must be positive.")

    validated["effective_date"] = pd.to_datetime(
        validated["effective_date"], errors="coerce"
    )
    if validated["effective_date"].isna().any():
        raise ValueError("effective_date must use valid dates.")
    validated["effective_date"] = validated["effective_date"].dt.strftime("%Y-%m-%d")

    if validated.duplicated(["instrument_version", "item_id"]).any():
        raise ValueError("item_id values must be unique within each instrument version.")
    valid_scores = set(DIMENSION_ITEMS)
    invalid_scores = sorted(set(validated["score_column"]) - valid_scores)
    if invalid_scores:
        raise ValueError(f"Unknown score columns: {invalid_scores}")
    for row in validated.itertuples(index=False):
        if DIMENSION_LABELS[row.score_column] != row.dimension:
            raise ValueError(
                f"Score column and dimension do not match for item_id '{row.item_id}'."
            )
        needs_predecessor = row.change_type in {"retain", "revise", "move", "split"}
        if needs_predecessor and not row.predecessor_item_id:
            raise ValueError(f"change_type={row.change_type} requires predecessor_item_id.")
        if row.change_type in {"baseline", "add"} and row.predecessor_item_id:
            raise ValueError(
                f"change_type={row.change_type} must not declare predecessor_item_id."
            )

    version_metadata = validated.groupby("instrument_version").agg(
        release_status_count=("release_status", "nunique"),
        effective_date_count=("effective_date", "nunique"),
        governance_status_count=("governance_status", "nunique"),
    )
    if not version_metadata.eq(1).all().all():
        raise ValueError(
            "Each instrument version must use one release status, effective date, and governance status."
        )

    required_dimensions = set(DIMENSION_ITEMS)
    for version, version_rows in validated.groupby("instrument_version", sort=False):
        if set(version_rows["score_column"]) != required_dimensions:
            raise ValueError(
                f"Instrument version '{version}' must contain active items in all five dimensions."
            )
    weight_sums = validated.groupby(["instrument_version", "score_column"])[
        "item_weight"
    ].sum()
    if not np.isclose(weight_sums.to_numpy(dtype=float), 1.0, atol=1e-6).all():
        raise ValueError("Item weights must sum to 1 within every version and dimension.")
    return validated


def audit_instrument_version_comparability(
    registry: pd.DataFrame,
    source_version: str,
    target_version: str,
) -> dict[str, pd.DataFrame | str | bool]:
    """Audit structural changes without authorizing score comparison.

    The result never estimates a conversion and never claims empirical
    equivalence. Identical structure is reported only as structural alignment.
    """
    validated = validate_instrument_version_registry(registry)
    source_version = str(source_version).strip()
    target_version = str(target_version).strip()
    versions = set(validated["instrument_version"])
    if source_version not in versions or target_version not in versions:
        raise ValueError("Both source_version and target_version must exist in the registry.")
    if source_version == target_version:
        raise ValueError("Source and target versions must differ.")

    source = validated[validated["instrument_version"].eq(source_version)].set_index("item_id")
    target = validated[validated["instrument_version"].eq(target_version)].set_index("item_id")
    source_ids = set(source.index)
    target_ids = set(target.index)
    shared_ids = sorted(source_ids & target_ids)
    added_ids = sorted(target_ids - source_ids)
    removed_ids = sorted(source_ids - target_ids)

    change_rows = []
    for item_id in shared_ids:
        before = source.loc[item_id]
        after = target.loc[item_id]
        change_rows.append(
            {
                "item_id": item_id,
                "dimension_changed": before["score_column"] != after["score_column"],
                "wording_changed": before["item_wording"] != after["item_wording"],
                "response_scale_changed": (
                    before["response_min"] != after["response_min"]
                    or before["response_max"] != after["response_max"]
                ),
                "weight_changed": not np.isclose(
                    float(before["item_weight"]), float(after["item_weight"]), atol=1e-9
                ),
            }
        )
    item_changes = pd.DataFrame(
        change_rows,
        columns=(
            "item_id",
            "dimension_changed",
            "wording_changed",
            "response_scale_changed",
            "weight_changed",
        ),
    )

    dimension_rows = []
    for score_column in DIMENSION_ITEMS:
        source_dimension = source[source["score_column"].eq(score_column)]
        target_dimension = target[target["score_column"].eq(score_column)]
        source_dimension_ids = set(source_dimension.index)
        target_dimension_ids = set(target_dimension.index)
        dimension_rows.append(
            {
                "score_column": score_column,
                "dimension": DIMENSION_LABELS[score_column],
                "source_item_count": len(source_dimension_ids),
                "target_item_count": len(target_dimension_ids),
                "shared_item_count": len(source_dimension_ids & target_dimension_ids),
                "added_item_count": len(target_dimension_ids - source_dimension_ids),
                "removed_item_count": len(source_dimension_ids - target_dimension_ids),
            }
        )
    dimension_summary = pd.DataFrame(dimension_rows)

    structural_change = bool(
        added_ids
        or removed_ids
        or (
            not item_changes.empty
            and item_changes[
                [
                    "dimension_changed",
                    "wording_changed",
                    "response_scale_changed",
                    "weight_changed",
                ]
            ].any().any()
        )
    )
    transition_summary = pd.DataFrame(
        [
            {
                "source_version": source_version,
                "target_version": target_version,
                "source_item_count": len(source_ids),
                "target_item_count": len(target_ids),
                "shared_item_count": len(shared_ids),
                "added_item_count": len(added_ids),
                "removed_item_count": len(removed_ids),
                "structural_change_detected": structural_change,
                "direct_score_comparison_authorized": False,
            }
        ]
    )
    if structural_change:
        interpretation = (
            "Structural change detected. Direct score comparison or conversion is not "
            "authorized without a separately justified linking or recalibration study."
        )
    else:
        interpretation = (
            "The registered item structure is aligned, but empirical score comparability "
            "has not been established. Direct comparison still requires documented review."
        )
    return {
        "transition_summary": transition_summary,
        "dimension_summary": dimension_summary,
        "item_change_summary": item_changes,
        "added_items": pd.DataFrame({"item_id": added_ids}),
        "removed_items": pd.DataFrame({"item_id": removed_ids}),
        "structural_change_detected": structural_change,
        "direct_score_comparison_authorized": False,
        "interpretation": interpretation,
    }
