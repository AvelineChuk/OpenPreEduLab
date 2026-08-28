"""Tests for inclusive feasibility-pilot and data-quality audits."""

from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_feasibility import (
    audit_feasibility_pilot,
    create_feasibility_pilot_template,
    load_feasibility_pilot_csv,
    validate_feasibility_pilot_data,
)


def _pilot_data() -> pd.DataFrame:
    rows = []
    for index in range(5):
        row = {
            "administration_id": f"admin_{index + 1}",
            "instrument_version": "inclusive_items_v0.1",
            "administration_mode": "facilitated_csv",
            "administration_status": "complete",
            "duration_minutes": 12 + index,
            "burden_rating": 2 + (index % 2),
        }
        for item_index, item in enumerate(ITEM_COLUMNS):
            row[item] = float((20 + index * 10 + item_index) % 101)
        rows.append(row)
    data = pd.DataFrame(rows)
    data["policy_clarity"] = 0.0
    data["implementation_requirements"] = 100.0
    data["professional_support"] = 50.0
    data.loc[4, "resource_guarantee"] = np.nan
    data.loc[4, "administration_status"] = "partial"
    return data


def test_feasibility_template_contains_metadata_and_items() -> None:
    template = create_feasibility_pilot_template()
    assert len(template) == 1
    assert set(ITEM_COLUMNS).issubset(template.columns)
    assert "duration_minutes" in template.columns
    assert "burden_rating" in template.columns


def test_feasibility_validation_preserves_missingness_and_csv_bom() -> None:
    data = _pilot_data()
    validated = validate_feasibility_pilot_data(data)
    assert validated["resource_guarantee"].isna().sum() == 1
    payload = BytesIO(data.to_csv(index=False).encode("utf-8-sig"))
    loaded = load_feasibility_pilot_csv(payload)
    assert len(loaded) == 5


def test_feasibility_rejects_non_numeric_item_and_status_mismatch() -> None:
    data = _pilot_data()
    data["teacher_support"] = data["teacher_support"].astype(object)
    data.loc[0, "teacher_support"] = "not_numeric"
    with pytest.raises(ValueError, match="non-numeric"):
        validate_feasibility_pilot_data(data)

    data = _pilot_data()
    data.loc[4, "administration_status"] = "complete"
    with pytest.raises(ValueError, match="must match observed item completion"):
        validate_feasibility_pilot_data(data)


def test_feasibility_rejects_invalid_duration_burden_and_range() -> None:
    data = _pilot_data()
    data.loc[0, "duration_minutes"] = 0
    with pytest.raises(ValueError, match="must be positive"):
        validate_feasibility_pilot_data(data)

    data = _pilot_data()
    data.loc[0, "burden_rating"] = 6
    with pytest.raises(ValueError, match="integer categories"):
        validate_feasibility_pilot_data(data)

    data = _pilot_data()
    data.loc[0, "peer_support"] = 101
    with pytest.raises(ValueError, match="declared source range"):
        validate_feasibility_pilot_data(data)


def test_feasibility_audit_reports_follow_up_flags_without_deletion() -> None:
    audit = audit_feasibility_pilot(
        _pilot_data(), endpoint_flag_threshold=0.8, missing_flag_threshold=0.2
    )
    items = audit["item_quality_summary"].set_index("item")
    assert items.loc["policy_clarity", "floor_follow_up_flag"]
    assert items.loc["implementation_requirements", "ceiling_follow_up_flag"]
    assert items.loc["professional_support", "no_variation_follow_up_flag"]
    assert items.loc["resource_guarantee", "missingness_follow_up_flag"]
    assert "item_removal" not in items.columns
    assert "do not establish reliability or validity" in audit["interpretation"]


def test_feasibility_audit_summarizes_completion_duration_and_modes() -> None:
    audit = audit_feasibility_pilot(_pilot_data())
    summary = audit["administration_summary"].iloc[0]
    assert summary["administration_count"] == 5
    assert summary["complete_count"] == 4
    assert summary["partial_count"] == 1
    assert summary["complete_rate"] == 0.8
    assert audit["missing_count_distribution"]["administration_count"].sum() == 5
    assert len(audit["administration_mode_summary"]) == 1


def test_feasibility_audit_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError, match="endpoint_flag_threshold"):
        audit_feasibility_pilot(_pilot_data(), endpoint_flag_threshold=1.1)
    with pytest.raises(ValueError, match="missing_flag_threshold"):
        audit_feasibility_pilot(_pilot_data(), missing_flag_threshold=-0.1)


def test_feasibility_summaries_exclude_administration_ids() -> None:
    audit = audit_feasibility_pilot(_pilot_data())
    for key in (
        "administration_summary",
        "item_quality_summary",
        "missing_count_distribution",
        "administration_mode_summary",
    ):
        assert "administration_id" not in audit[key].columns
