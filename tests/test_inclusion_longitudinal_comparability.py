"""Tests for longitudinal measurement-comparability readiness audits."""

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_longitudinal_comparability import (
    audit_longitudinal_comparability,
)


def _comparability_data(rounds: tuple[int, ...] = (1, 2), count: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(20260814)
    rows = []
    for round_number in rounds:
        for unit_index in range(count):
            row = {
                "pseudonymous_unit_id": f"unit_{unit_index + 1}",
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": round_number,
            }
            shared = rng.normal(0, 2)
            for item_index, item in enumerate(ITEM_COLUMNS):
                row[item] = float(
                    np.clip(
                        35
                        + unit_index * 6
                        + item_index * 0.35
                        + (round_number - 1) * (item_index % 4)
                        + shared
                        + rng.normal(0, 1),
                        0,
                        100,
                    )
                )
            rows.append(row)
    return pd.DataFrame(rows)


def test_longitudinal_comparability_reports_expected_summaries() -> None:
    audit = audit_longitudinal_comparability(
        _comparability_data(), "inclusive_items_v0.1"
    )
    assert len(audit["round_coverage_summary"]) == 2
    assert len(audit["round_item_distribution_summary"]) == 2 * len(ITEM_COLUMNS)
    differences = audit["adjacent_round_item_difference_summary"]
    assert len(differences) == len(ITEM_COLUMNS)
    assert differences["standardised_difference_defined"].all()
    assert not differences["composition_adjusted"].any()
    correlations = audit["adjacent_round_correlation_difference_summary"]
    assert len(correlations) == 1
    assert correlations.iloc[0]["finite_item_pair_count"] > 0
    assert len(audit["research_question_candidates"]) == 3
    assert "do not establish configural" in audit["interpretation"]


def test_longitudinal_comparability_supports_nonconsecutive_rounds() -> None:
    audit = audit_longitudinal_comparability(
        _comparability_data(rounds=(1, 4, 9)), "inclusive_items_v0.1"
    )
    correlations = audit["adjacent_round_correlation_difference_summary"]
    assert list(zip(correlations["first_round"], correlations["second_round"], strict=True)) == [
        (1, 4),
        (4, 9),
    ]
    assert len(audit["adjacent_round_item_difference_summary"]) == 2 * len(ITEM_COLUMNS)


def test_longitudinal_comparability_requires_two_sized_rounds() -> None:
    with pytest.raises(ValueError, match="at least two rounds"):
        audit_longitudinal_comparability(
            _comparability_data(rounds=(1,)), "inclusive_items_v0.1"
        )
    data = _comparability_data(count=5)
    data = data[
        ~(
            data["administration_round"].eq(2)
            & data["pseudonymous_unit_id"].eq("unit_5")
        )
    ]
    with pytest.raises(ValueError, match="undersized rounds"):
        audit_longitudinal_comparability(data, "inclusive_items_v0.1")


def test_longitudinal_comparability_handles_zero_variance_items() -> None:
    data = _comparability_data()
    data.loc[data["administration_round"].eq(2), ITEM_COLUMNS[0]] = 50.0
    audit = audit_longitudinal_comparability(data, "inclusive_items_v0.1")
    correlation = audit["adjacent_round_correlation_difference_summary"].iloc[0]
    assert correlation["zero_variance_item_count"] == 1
    assert pd.isna(correlation["root_mean_square_correlation_difference"])


def test_longitudinal_comparability_selects_version_and_supports_non_100_scale() -> None:
    first = _comparability_data()
    second = _comparability_data()
    second["instrument_version"] = "inclusive_items_v0.2"
    mixed = pd.concat([first, second], ignore_index=True)
    mixed[list(ITEM_COLUMNS)] = mixed[list(ITEM_COLUMNS)] / 100
    audit = audit_longitudinal_comparability(
        mixed, "inclusive_items_v0.2", source_min=0, source_max=1
    )
    assert len(audit["round_coverage_summary"]) == 2
    with pytest.raises(ValueError, match="does not exist"):
        audit_longitudinal_comparability(mixed, "unknown", 0, 1)


def test_longitudinal_comparability_outputs_exclude_ids_and_decisions() -> None:
    audit = audit_longitudinal_comparability(
        _comparability_data(), "inclusive_items_v0.1"
    )
    prohibited = {
        "pseudonymous_unit_id",
        "invariance_status",
        "bias_status",
        "item_removal_decision",
        "significance_status",
        "institution_rank",
        "policy_effect",
        "pass",
        "fail",
    }
    for key in (
        "round_coverage_summary",
        "round_item_distribution_summary",
        "adjacent_round_item_difference_summary",
        "adjacent_round_correlation_difference_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
