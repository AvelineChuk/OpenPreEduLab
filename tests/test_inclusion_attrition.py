"""Tests for longitudinal attrition and panel-composition audits."""

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_attrition import audit_longitudinal_attrition


def _attrition_data() -> pd.DataFrame:
    rows = []
    round_units = {
        1: ["keep_1", "keep_2", "keep_3", "exit_1", "exit_2", "exit_3"],
        2: ["keep_1", "keep_2", "keep_3", "enter_1", "enter_2", "enter_3"],
    }
    for round_number, units in round_units.items():
        for unit_index, unit in enumerate(units):
            group_offset = 0
            if unit.startswith("exit"):
                group_offset = -8
            elif unit.startswith("enter"):
                group_offset = 10
            row = {
                "pseudonymous_unit_id": unit,
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": round_number,
            }
            for item_index, item in enumerate(ITEM_COLUMNS):
                row[item] = float(45 + unit_index * 2 + item_index * 0.3 + group_offset)
            rows.append(row)
    return pd.DataFrame(rows)


def test_attrition_audit_reports_coverage_and_two_comparison_blocks() -> None:
    audit = audit_longitudinal_attrition(_attrition_data(), "inclusive_items_v0.1")
    coverage = audit["attrition_coverage_summary"].iloc[0]
    comparisons = audit["panel_composition_comparison_summary"]
    assert coverage["retained_unit_count"] == 3
    assert coverage["first_round_only_unit_count"] == 3
    assert coverage["second_round_only_unit_count"] == 3
    assert coverage["retention_proportion"] == 0.5
    assert len(comparisons) == 2 * 8
    assert comparisons["comparison_disclosed"].all()
    assert comparisons["raw_mean_difference_reference_minus_comparison"].notna().all()
    assert len(audit["research_question_candidates"]) == 3
    assert "do not establish why records are missing" in audit["interpretation"]


def test_attrition_audit_suppresses_small_comparison_groups() -> None:
    data = _attrition_data()
    data = data[~data["pseudonymous_unit_id"].isin(["exit_2", "exit_3"])]
    audit = audit_longitudinal_attrition(data, "inclusive_items_v0.1")
    comparisons = audit["panel_composition_comparison_summary"]
    exit_rows = comparisons.query("comparison == 'first_round_retained_vs_exited'")
    entry_rows = comparisons.query("comparison == 'second_round_retained_vs_entered'")
    assert not exit_rows["comparison_disclosed"].any()
    assert exit_rows["reference_group_mean"].isna().all()
    assert exit_rows["suppression_reason"].str.contains("At least three").all()
    assert entry_rows["comparison_disclosed"].all()


def test_attrition_audit_handles_zero_variance_standardised_difference() -> None:
    data = _attrition_data()
    data[ITEM_COLUMNS[0]] = 50.0
    audit = audit_longitudinal_attrition(data, "inclusive_items_v0.1")
    policy_rows = audit["panel_composition_comparison_summary"].query(
        "statistic == 'policy_support_score'"
    )
    assert policy_rows["comparison_disclosed"].all()
    assert policy_rows["standardised_difference_defined"].all()


def test_attrition_audit_selects_one_version_and_requires_two_rounds() -> None:
    first = _attrition_data()
    second = _attrition_data()
    second["instrument_version"] = "inclusive_items_v0.2"
    mixed = pd.concat([first, second], ignore_index=True)
    audit = audit_longitudinal_attrition(mixed, "inclusive_items_v0.2")
    assert len(audit["attrition_coverage_summary"]) == 1
    with pytest.raises(ValueError, match="does not exist"):
        audit_longitudinal_attrition(mixed, "unknown")
    with pytest.raises(ValueError, match="at least two"):
        audit_longitudinal_attrition(
            first[first["administration_round"].eq(1)], "inclusive_items_v0.1"
        )


def test_attrition_audit_supports_multiple_and_nonconsecutive_rounds() -> None:
    data = _attrition_data()
    third = data[data["administration_round"].eq(2)].copy()
    third["administration_round"] = 5
    combined = pd.concat([data, third], ignore_index=True)
    audit = audit_longitudinal_attrition(combined, "inclusive_items_v0.1")
    coverage = audit["attrition_coverage_summary"]
    assert list(zip(coverage["first_round"], coverage["second_round"], strict=True)) == [
        (1, 2),
        (2, 5),
    ]


def test_attrition_audit_supports_non_100_source_scale() -> None:
    data = _attrition_data()
    data[list(ITEM_COLUMNS)] = data[list(ITEM_COLUMNS)] / 100
    audit = audit_longitudinal_attrition(
        data, "inclusive_items_v0.1", source_min=0, source_max=1
    )
    disclosed = audit["panel_composition_comparison_summary"].query(
        "comparison_disclosed"
    )
    dimension_rows = disclosed.query("statistic_type == 'dimension_score'")
    assert dimension_rows["reference_group_mean"].between(0, 100).all()


def test_attrition_outputs_exclude_ids_causes_weights_and_judgements() -> None:
    audit = audit_longitudinal_attrition(_attrition_data(), "inclusive_items_v0.1")
    prohibited = {
        "pseudonymous_unit_id",
        "attrition_cause",
        "missingness_mechanism",
        "attrition_weight",
        "imputed_value",
        "bias_status",
        "institution_rank",
        "quality_status",
        "pass",
        "fail",
    }
    for key in (
        "attrition_coverage_summary",
        "panel_composition_comparison_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
