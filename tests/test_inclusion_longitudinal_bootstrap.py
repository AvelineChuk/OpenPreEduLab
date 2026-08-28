"""Tests for paired longitudinal Bootstrap uncertainty audits."""

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_longitudinal_bootstrap import (
    audit_paired_longitudinal_bootstrap,
)


def _panel_data(unit_count: int = 8, rounds: tuple[int, ...] = (1, 2)) -> pd.DataFrame:
    rng = np.random.default_rng(20260813)
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
                    np.clip(
                        35
                        + unit_index * 4
                        + item_index * 0.25
                        + (round_number - 1) * (2 + item_index % 3)
                        + rng.normal(0, 1.5),
                        0,
                        100,
                    )
                )
            rows.append(row)
    return pd.DataFrame(rows)


def test_paired_bootstrap_reports_run_and_eight_interval_rows() -> None:
    audit = audit_paired_longitudinal_bootstrap(
        _panel_data(), "inclusive_items_v0.1", n_resamples=400
    )
    run = audit["paired_bootstrap_run_summary"].iloc[0]
    intervals = audit["paired_bootstrap_interval_summary"]
    assert run["matched_unit_count"] == 8
    assert run["resampling_unit"] == "matched_institutional_pair"
    assert len(intervals) == 8
    assert set(intervals["statistic_type"]) == {
        "dimension_mean_change",
        "support_gap_mean_change",
    }
    assert (
        intervals["percentile_interval_lower"]
        <= intervals["point_mean_change_second_minus_first"]
    ).all()
    assert (
        intervals["point_mean_change_second_minus_first"]
        <= intervals["percentile_interval_upper"]
    ).all()
    assert intervals["bootstrap_standard_error"].ge(0).all()
    assert "do not establish" in audit["interpretation"]


def test_paired_bootstrap_is_reproducible_for_same_seed() -> None:
    first = audit_paired_longitudinal_bootstrap(
        _panel_data(), "inclusive_items_v0.1", n_resamples=300, random_seed=7
    )
    second = audit_paired_longitudinal_bootstrap(
        _panel_data(), "inclusive_items_v0.1", n_resamples=300, random_seed=7
    )
    pd.testing.assert_frame_equal(
        first["paired_bootstrap_interval_summary"],
        second["paired_bootstrap_interval_summary"],
    )


def test_paired_bootstrap_handles_multiple_nonconsecutive_rounds() -> None:
    audit = audit_paired_longitudinal_bootstrap(
        _panel_data(rounds=(1, 3, 7)),
        "inclusive_items_v0.1",
        n_resamples=200,
    )
    run = audit["paired_bootstrap_run_summary"]
    assert list(zip(run["first_round"], run["second_round"], strict=True)) == [
        (1, 3),
        (3, 7),
    ]
    assert len(audit["paired_bootstrap_interval_summary"]) == 16


def test_paired_bootstrap_requires_five_matches_for_every_pair() -> None:
    data = _panel_data(unit_count=5)
    data = data[
        ~(
            data["administration_round"].eq(2)
            & data["pseudonymous_unit_id"].eq("unit_5")
        )
    ]
    with pytest.raises(ValueError, match="at least 5 matched units"):
        audit_paired_longitudinal_bootstrap(data, "inclusive_items_v0.1")


@pytest.mark.parametrize("n_resamples", [99, 10001, 100.5, True])
def test_paired_bootstrap_rejects_invalid_resample_count(n_resamples: object) -> None:
    with pytest.raises(ValueError, match="n_resamples"):
        audit_paired_longitudinal_bootstrap(
            _panel_data(),
            "inclusive_items_v0.1",
            n_resamples=n_resamples,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("confidence_level", [0.79, 1.0, np.nan, True])
def test_paired_bootstrap_rejects_invalid_interval_level(
    confidence_level: object,
) -> None:
    with pytest.raises(ValueError, match="confidence_level"):
        audit_paired_longitudinal_bootstrap(
            _panel_data(),
            "inclusive_items_v0.1",
            confidence_level=confidence_level,  # type: ignore[arg-type]
        )


def test_paired_bootstrap_supports_non_100_scale_and_version_selection() -> None:
    first = _panel_data()
    second = _panel_data()
    second["instrument_version"] = "inclusive_items_v0.2"
    mixed = pd.concat([first, second], ignore_index=True)
    mixed[list(ITEM_COLUMNS)] = mixed[list(ITEM_COLUMNS)] / 100
    audit = audit_paired_longitudinal_bootstrap(
        mixed,
        "inclusive_items_v0.2",
        n_resamples=200,
        source_min=0,
        source_max=1,
    )
    assert len(audit["paired_bootstrap_interval_summary"]) == 8
    with pytest.raises(ValueError, match="does not exist"):
        audit_paired_longitudinal_bootstrap(mixed, "unknown")


def test_paired_bootstrap_outputs_exclude_ids_draws_and_judgements() -> None:
    audit = audit_paired_longitudinal_bootstrap(
        _panel_data(), "inclusive_items_v0.1", n_resamples=200
    )
    prohibited = {
        "pseudonymous_unit_id",
        "bootstrap_draw",
        "resampled_unit_id",
        "significance_status",
        "improvement_status",
        "deterioration_status",
        "policy_effect",
        "institution_rank",
        "pass",
        "fail",
    }
    for key in (
        "paired_bootstrap_run_summary",
        "paired_bootstrap_interval_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
