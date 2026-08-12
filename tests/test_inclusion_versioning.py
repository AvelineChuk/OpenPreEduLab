"""Tests for inclusive instrument versioning and comparability audits."""

from io import BytesIO

import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_versioning import (
    audit_instrument_version_comparability,
    create_instrument_version_registry_template,
    load_instrument_version_registry_csv,
    validate_instrument_version_registry,
)


def _version_snapshot(version: str, effective_date: str) -> pd.DataFrame:
    snapshot = create_instrument_version_registry_template()
    snapshot["instrument_version"] = version
    snapshot["release_status"] = "draft"
    snapshot["effective_date"] = effective_date
    snapshot["item_wording"] = snapshot["item_id"].str.replace("_", " ")
    snapshot["change_type"] = "baseline" if version == "v0.1" else "retain"
    snapshot["predecessor_item_id"] = "" if version == "v0.1" else snapshot["item_id"]
    snapshot["comparability_assessment"] = "direct_comparison_not_established"
    snapshot["comparability_note"] = "Structural registry only; empirical linking not completed."
    snapshot["governance_status"] = "draft"
    return snapshot


def _two_version_registry() -> pd.DataFrame:
    return pd.concat(
        [_version_snapshot("v0.1", "2026-08-01"), _version_snapshot("v0.2", "2026-08-12")],
        ignore_index=True,
    )


def test_version_registry_template_has_current_equal_weight_structure() -> None:
    template = create_instrument_version_registry_template()
    assert len(template) == len(ITEM_COLUMNS)
    assert template["item_id"].is_unique
    sums = template.groupby("score_column")["item_weight"].sum()
    assert all(abs(value - 1.0) < 1e-6 for value in sums)


def test_version_registry_validates_complete_snapshots_and_utf8_csv() -> None:
    registry = _two_version_registry()
    validated = validate_instrument_version_registry(registry)
    assert validated["instrument_version"].nunique() == 2
    payload = BytesIO(registry.to_csv(index=False).encode("utf-8-sig"))
    loaded = load_instrument_version_registry_csv(payload)
    assert len(loaded) == len(registry)


def test_version_registry_rejects_incomplete_dimension_and_bad_weights() -> None:
    registry = _two_version_registry()
    first_policy_index = registry[
        registry["instrument_version"].eq("v0.2")
        & registry["score_column"].eq("policy_support_score")
    ].index[0]
    with pytest.raises(ValueError, match="sum to 1"):
        validate_instrument_version_registry(registry.drop(index=first_policy_index))

    registry = _two_version_registry()
    registry.loc[registry.index[0], "item_weight"] = 0
    with pytest.raises(ValueError, match="must be positive"):
        validate_instrument_version_registry(registry)


def test_version_registry_rejects_invalid_predecessor_and_metadata() -> None:
    registry = _two_version_registry()
    target_index = registry[registry["instrument_version"].eq("v0.2")].index[0]
    registry.loc[target_index, "predecessor_item_id"] = ""
    with pytest.raises(ValueError, match="requires predecessor_item_id"):
        validate_instrument_version_registry(registry)

    registry = _two_version_registry()
    registry.loc[target_index, "release_status"] = "released"
    with pytest.raises(ValueError, match="one release status"):
        validate_instrument_version_registry(registry)


def test_aligned_structure_does_not_authorize_direct_comparison() -> None:
    audit = audit_instrument_version_comparability(_two_version_registry(), "v0.1", "v0.2")
    assert audit["structural_change_detected"] is False
    assert audit["direct_score_comparison_authorized"] is False
    assert "empirical score comparability has not been established" in audit["interpretation"]
    assert audit["transition_summary"].loc[0, "shared_item_count"] == len(ITEM_COLUMNS)


def test_audit_detects_wording_weight_and_item_set_changes() -> None:
    registry = _two_version_registry()
    target_mask = registry["instrument_version"].eq("v0.2")
    target_indices = registry[target_mask & registry["score_column"].eq("policy_support_score")].index
    registry.loc[target_indices[0], "item_wording"] = "Revised wording"
    registry.loc[target_indices[0], "item_weight"] += 0.01
    registry.loc[target_indices[1], "item_weight"] -= 0.01
    audit = audit_instrument_version_comparability(registry, "v0.1", "v0.2")
    assert audit["structural_change_detected"] is True
    assert audit["item_change_summary"]["wording_changed"].any()
    assert audit["item_change_summary"]["weight_changed"].any()
    assert audit["direct_score_comparison_authorized"] is False


def test_audit_detects_removed_and_new_item_ids() -> None:
    source = _version_snapshot("v0.1", "2026-08-01")
    target = _version_snapshot("v0.2", "2026-08-12")
    old_index = target[target["score_column"].eq("policy_support_score")].index[0]
    new_row = target.loc[[old_index]].copy()
    target = target.drop(index=old_index)
    new_row["item_id"] = "policy_clarity_revised"
    new_row["predecessor_item_id"] = "policy_clarity"
    new_row["change_type"] = "revise"
    target = pd.concat([target, new_row], ignore_index=True)
    audit = audit_instrument_version_comparability(
        pd.concat([source, target], ignore_index=True), "v0.1", "v0.2"
    )
    assert audit["added_items"].loc[0, "item_id"] == "policy_clarity_revised"
    assert audit["removed_items"].loc[0, "item_id"] == "policy_clarity"
    assert audit["structural_change_detected"] is True


def test_audit_requires_two_declared_versions() -> None:
    registry = _two_version_registry()
    with pytest.raises(ValueError, match="must exist"):
        audit_instrument_version_comparability(registry, "v0.1", "v9.9")
    with pytest.raises(ValueError, match="must differ"):
        audit_instrument_version_comparability(registry, "v0.1", "v0.1")
