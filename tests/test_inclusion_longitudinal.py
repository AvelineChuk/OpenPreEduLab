"""Tests for inclusive longitudinal panel readiness audits."""

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_longitudinal import audit_longitudinal_panel_readiness


def _longitudinal_data(
    unit_count: int = 6,
    rounds: tuple[int, ...] = (1, 2, 3),
) -> pd.DataFrame:
    rows = []
    for round_number in rounds:
        for unit_index in range(unit_count):
            row = {
                "pseudonymous_unit_id": f"unit_{unit_index + 1}",
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": round_number,
            }
            for item_index, item in enumerate(ITEM_COLUMNS):
                row[item] = float(
                    20 + unit_index * 6 + item_index * 0.5 + (round_number - 1) * 2
                )
            rows.append(row)
    return pd.DataFrame(rows)


def test_longitudinal_audit_reports_panel_round_matching_and_change_summaries() -> None:
    audit = audit_longitudinal_panel_readiness(
        _longitudinal_data(), "inclusive_items_v0.1"
    )
    panel = audit["longitudinal_panel_summary"].iloc[0]
    coverage = audit["round_coverage_summary"]
    round_statistics = audit["round_statistic_summary"]
    matching = audit["adjacent_round_matching_summary"]
    changes = audit["adjacent_round_change_summary"]
    assert panel["round_count"] == 3
    assert panel["complete_panel_unit_count"] == 6
    assert panel["complete_panel_coverage_proportion"] == 1
    assert len(coverage) == 3
    assert len(round_statistics) == 3 * 8
    assert len(matching) == 2
    assert matching["matched_unit_count"].eq(6).all()
    assert len(changes) == 2 * 8
    dimension_changes = changes.query("statistic_type == 'dimension_score'")
    assert dimension_changes["mean_change_second_minus_first"].eq(2).all()
    assert len(audit["research_question_candidates"]) == 3
    assert "Time order does not establish causality" in audit["interpretation"]


def test_longitudinal_audit_reports_unbalanced_panel_without_imputation() -> None:
    data = _longitudinal_data()
    data = data[
        ~(
            data["pseudonymous_unit_id"].eq("unit_6")
            & data["administration_round"].eq(2)
        )
    ]
    audit = audit_longitudinal_panel_readiness(data, "inclusive_items_v0.1")
    panel = audit["longitudinal_panel_summary"].iloc[0]
    matching = audit["adjacent_round_matching_summary"]
    assert panel["all_observed_unit_count"] == 6
    assert panel["complete_panel_unit_count"] == 5
    assert not panel["missing_rounds_imputed"]
    assert matching["matched_unit_count"].eq(5).all()
    assert matching["first_round_only_count"].iloc[0] == 1
    assert matching["second_round_only_count"].iloc[1] == 1


def test_longitudinal_audit_selects_one_version_only() -> None:
    first = _longitudinal_data()
    second = _longitudinal_data()
    second["instrument_version"] = "inclusive_items_v0.2"
    second[list(ITEM_COLUMNS)] += 10
    mixed = pd.concat([first, second], ignore_index=True)
    audit = audit_longitudinal_panel_readiness(mixed, "inclusive_items_v0.2")
    panel = audit["longitudinal_panel_summary"].iloc[0]
    assert panel["instrument_version"] == "inclusive_items_v0.2"
    assert not panel["cross_version_records_combined"]
    with pytest.raises(ValueError, match="does not exist"):
        audit_longitudinal_panel_readiness(mixed, "unknown_version")


def test_longitudinal_audit_requires_two_rounds_and_minimum_round_size() -> None:
    with pytest.raises(ValueError, match="at least two rounds"):
        audit_longitudinal_panel_readiness(
            _longitudinal_data(rounds=(1,)), "inclusive_items_v0.1"
        )
    data = pd.concat(
        [
            _longitudinal_data(unit_count=3, rounds=(1,)),
            _longitudinal_data(unit_count=2, rounds=(2,)),
        ],
        ignore_index=True,
    )
    with pytest.raises(ValueError, match="undersized rounds"):
        audit_longitudinal_panel_readiness(data, "inclusive_items_v0.1")


def test_longitudinal_audit_requires_adjacent_matched_units() -> None:
    first = _longitudinal_data(unit_count=3, rounds=(1,))
    second = _longitudinal_data(unit_count=3, rounds=(2,))
    second["pseudonymous_unit_id"] = ["unit_1", "new_1", "new_2"]
    data = pd.concat([first, second], ignore_index=True)
    with pytest.raises(ValueError, match="at least 3 matched units"):
        audit_longitudinal_panel_readiness(data, "inclusive_items_v0.1")


def test_longitudinal_audit_supports_nonconsecutive_round_labels() -> None:
    audit = audit_longitudinal_panel_readiness(
        _longitudinal_data(rounds=(1, 3, 6)), "inclusive_items_v0.1"
    )
    matching = audit["adjacent_round_matching_summary"]
    assert list(zip(matching["first_round"], matching["second_round"], strict=True)) == [
        (1, 3),
        (3, 6),
    ]


def test_longitudinal_audit_supports_non_100_source_scale() -> None:
    data = _longitudinal_data()
    data[list(ITEM_COLUMNS)] = data[list(ITEM_COLUMNS)] / 100
    audit = audit_longitudinal_panel_readiness(
        data, "inclusive_items_v0.1", source_min=0, source_max=1
    )
    dimension_rows = audit["round_statistic_summary"].query(
        "statistic_type == 'dimension_score'"
    )
    assert dimension_rows["mean"].between(0, 100).all()


def test_longitudinal_outputs_exclude_ids_and_automatic_change_judgements() -> None:
    audit = audit_longitudinal_panel_readiness(
        _longitudinal_data(), "inclusive_items_v0.1"
    )
    prohibited = {
        "pseudonymous_unit_id",
        "improvement_status",
        "deterioration_status",
        "trajectory_class",
        "institution_rank",
        "policy_effect",
        "causal_effect",
        "pass",
        "fail",
    }
    for key in (
        "longitudinal_panel_summary",
        "round_coverage_summary",
        "round_statistic_summary",
        "adjacent_round_matching_summary",
        "adjacent_round_change_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
