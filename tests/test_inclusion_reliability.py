"""Tests for preliminary inclusive reliability audits."""

from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_reliability import (
    calculate_internal_consistency,
    calculate_repeated_administration_stability,
    create_reliability_audit_template,
    load_reliability_audit_csv,
    validate_reliability_audit_data,
)


def _reliability_data(unit_count: int = 6, rounds: tuple[int, ...] = (1, 2)) -> pd.DataFrame:
    rows = []
    for administration_round in rounds:
        for unit_index in range(unit_count):
            row = {
                "pseudonymous_unit_id": f"unit_{unit_index + 1}",
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": administration_round,
            }
            for item_index, item in enumerate(ITEM_COLUMNS):
                base = 20 + unit_index * 8 + item_index * 0.5
                row[item] = min(100.0, base + (administration_round - 1) * 2)
            rows.append(row)
    return pd.DataFrame(rows)


def test_reliability_template_contains_complete_item_schema() -> None:
    template = create_reliability_audit_template()
    assert len(template) == 1
    assert set(ITEM_COLUMNS).issubset(template.columns)
    assert "pseudonymous_unit_id" in template.columns


def test_reliability_validation_and_utf8_csv_roundtrip() -> None:
    data = _reliability_data()
    validated = validate_reliability_audit_data(data)
    assert len(validated) == 12
    payload = BytesIO(data.to_csv(index=False).encode("utf-8-sig"))
    loaded = load_reliability_audit_csv(payload)
    assert len(loaded) == len(data)


def test_reliability_validation_rejects_missing_and_duplicate_records() -> None:
    data = _reliability_data()
    data.loc[0, "policy_clarity"] = np.nan
    with pytest.raises(ValueError, match="complete numeric values"):
        validate_reliability_audit_data(data)

    data = _reliability_data()
    duplicate = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="may appear only once"):
        validate_reliability_audit_data(duplicate)


def test_internal_consistency_returns_dimension_and_item_diagnostics() -> None:
    audit = calculate_internal_consistency(_reliability_data(rounds=(1,)))
    dimensions = audit["dimension_summary"]
    items = audit["item_summary"]
    assert len(dimensions) == 5
    assert len(items) == len(ITEM_COLUMNS)
    assert dimensions["response_count"].eq(6).all()
    assert dimensions["alpha_defined"].all()
    assert "automatic" in audit["interpretation"]
    assert "item_decision" not in items.columns


def test_internal_consistency_handles_zero_total_variance_transparently() -> None:
    data = _reliability_data(rounds=(1,))
    data[list(ITEM_COLUMNS)] = 50.0
    audit = calculate_internal_consistency(data)
    assert audit["dimension_summary"]["cronbach_alpha"].isna().all()
    assert not audit["dimension_summary"]["alpha_defined"].any()


def test_internal_consistency_requires_minimum_group_size() -> None:
    with pytest.raises(ValueError, match="at least three complete responses"):
        calculate_internal_consistency(_reliability_data(unit_count=2, rounds=(1,)))


def test_repeated_administration_reports_stability_and_matching_coverage() -> None:
    data = _reliability_data()
    extra = data.iloc[[0]].copy()
    extra["pseudonymous_unit_id"] = "round_one_only"
    extra["administration_round"] = 1
    data = pd.concat([data, extra], ignore_index=True)
    audit = calculate_repeated_administration_stability(data, "inclusive_items_v0.1", 1, 2)
    stability = audit["dimension_stability_summary"]
    coverage = audit["matching_coverage_summary"].iloc[0]
    assert len(stability) == 5
    assert stability["matched_unit_count"].eq(6).all()
    assert stability["mean_change"].eq(2.0).all()
    assert stability["pearson_correlation"].eq(1.0).all()
    assert stability["icc_3_1_consistency"].notna().all()
    assert coverage["first_round_only_count"] == 1
    assert coverage["second_round_only_count"] == 0
    assert "cross-version comparison" in audit["interpretation"]


def test_repeated_administration_rejects_invalid_round_design() -> None:
    data = _reliability_data()
    with pytest.raises(ValueError, match="must differ"):
        calculate_repeated_administration_stability(data, "inclusive_items_v0.1", 1, 1)
    with pytest.raises(ValueError, match="must exist"):
        calculate_repeated_administration_stability(data, "inclusive_items_v0.1", 1, 3)
    with pytest.raises(ValueError, match="at least three matched units"):
        calculate_repeated_administration_stability(
            _reliability_data(unit_count=2), "inclusive_items_v0.1", 1, 2
        )


def test_reliability_outputs_exclude_unit_ids() -> None:
    internal = calculate_internal_consistency(_reliability_data(rounds=(1,)))
    repeated = calculate_repeated_administration_stability(
        _reliability_data(), "inclusive_items_v0.1", 1, 2
    )
    for frame in (
        internal["dimension_summary"],
        internal["item_summary"],
        repeated["dimension_stability_summary"],
        repeated["matching_coverage_summary"],
    ):
        assert "pseudonymous_unit_id" not in frame.columns
