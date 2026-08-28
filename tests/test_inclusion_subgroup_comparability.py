"""Tests for subgroup measurement-comparability readiness audits."""

from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_subgroup_comparability import (
    audit_subgroup_comparability,
    create_subgroup_comparability_template,
    load_subgroup_comparability_csv,
    validate_subgroup_comparability_data,
)


def _subgroup_data(group_size: int = 8) -> pd.DataFrame:
    rng = np.random.default_rng(20260812)
    rows = []
    for group_index, group in enumerate(("community", "public")):
        for unit_index in range(group_size):
            row = {
                "pseudonymous_unit_id": f"{group}_{unit_index + 1}",
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": 1,
                "comparison_group": group,
            }
            shared = rng.normal(0, 6)
            for item_index, item in enumerate(ITEM_COLUMNS):
                value = 45 + group_index * 4 + shared + item_index * 0.25 + rng.normal(0, 5)
                row[item] = float(np.clip(value, 0, 100))
            rows.append(row)
    return pd.DataFrame(rows)


def test_subgroup_template_and_utf8_bom_roundtrip() -> None:
    template = create_subgroup_comparability_template()
    assert "comparison_group" in template.columns
    assert set(ITEM_COLUMNS).issubset(template.columns)
    payload = BytesIO(_subgroup_data().to_csv(index=False).encode("utf-8-sig"))
    loaded = load_subgroup_comparability_csv(payload)
    assert len(loaded) == 16


def test_subgroup_validation_rejects_missing_group_and_invalid_item_values() -> None:
    data = _subgroup_data()
    data.loc[0, "comparison_group"] = ""
    with pytest.raises(ValueError, match="comparison_group"):
        validate_subgroup_comparability_data(data)
    data = _subgroup_data()
    data.loc[0, ITEM_COLUMNS[0]] = np.nan
    with pytest.raises(ValueError, match="complete numeric values"):
        validate_subgroup_comparability_data(data)
    data = _subgroup_data()
    data.loc[0, ITEM_COLUMNS[0]] = 101
    with pytest.raises(ValueError, match="declared source range"):
        validate_subgroup_comparability_data(data)


def test_subgroup_audit_reports_coverage_distributions_differences_and_questions() -> None:
    audit = audit_subgroup_comparability(_subgroup_data(), "inclusive_items_v0.1", 1)
    coverage = audit["group_coverage_summary"]
    distributions = audit["group_item_distribution_summary"]
    differences = audit["pairwise_item_difference_summary"]
    correlations = audit["correlation_structure_difference_summary"]
    assert len(coverage) == 2
    assert coverage["complete_record_count"].eq(8).all()
    assert len(distributions) == 2 * len(ITEM_COLUMNS)
    assert len(differences) == len(ITEM_COLUMNS)
    assert differences["standardised_difference_defined"].all()
    assert len(correlations) == 1
    assert correlations.iloc[0]["finite_item_pair_count"] == (
        len(ITEM_COLUMNS) * (len(ITEM_COLUMNS) - 1) // 2
    )
    assert len(audit["research_question_candidates"]) == 3
    assert "do not establish measurement invariance" in audit["interpretation"]


def test_subgroup_audit_selects_one_version_and_round() -> None:
    first = _subgroup_data()
    second = _subgroup_data()
    second["instrument_version"] = "inclusive_items_v0.2"
    second["administration_round"] = 2
    data = pd.concat([first, second], ignore_index=True)
    audit = audit_subgroup_comparability(data, "inclusive_items_v0.2", 2)
    assert audit["group_coverage_summary"]["instrument_version"].eq(
        "inclusive_items_v0.2"
    ).all()
    with pytest.raises(ValueError, match="do not exist"):
        audit_subgroup_comparability(data, "inclusive_items_v0.1", 2)


def test_subgroup_audit_requires_two_groups_and_minimum_group_coverage() -> None:
    one_group = _subgroup_data().query("comparison_group == 'public'")
    with pytest.raises(ValueError, match="at least two comparison groups"):
        audit_subgroup_comparability(one_group, "inclusive_items_v0.1", 1)
    small_group = pd.concat(
        [
            _subgroup_data(group_size=5).query("comparison_group == 'public'"),
            _subgroup_data(group_size=4).query("comparison_group == 'community'"),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="at least 5 complete records"):
        audit_subgroup_comparability(small_group, "inclusive_items_v0.1", 1)


def test_subgroup_audit_marks_undefined_standardised_difference_without_decision() -> None:
    data = _subgroup_data()
    data[ITEM_COLUMNS[0]] = 50.0
    audit = audit_subgroup_comparability(data, "inclusive_items_v0.1", 1)
    item_row = audit["pairwise_item_difference_summary"].query(
        "item == @ITEM_COLUMNS[0]"
    ).iloc[0]
    correlation_row = audit["correlation_structure_difference_summary"].iloc[0]
    assert np.isnan(item_row["standardised_mean_difference"])
    assert not item_row["standardised_difference_defined"]
    assert correlation_row["zero_variance_item_count"] == 1
    assert np.isnan(correlation_row["root_mean_square_correlation_difference"])


def test_subgroup_outputs_exclude_ids_and_decision_or_ranking_fields() -> None:
    audit = audit_subgroup_comparability(_subgroup_data(), "inclusive_items_v0.1", 1)
    prohibited = {
        "pseudonymous_unit_id",
        "pass",
        "fail",
        "item_decision",
        "remove_item",
        "group_rank",
        "fairness_conclusion",
        "invariance_status",
    }
    for key in (
        "group_coverage_summary",
        "group_item_distribution_summary",
        "pairwise_item_difference_summary",
        "correlation_structure_difference_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
