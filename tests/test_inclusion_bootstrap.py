"""Tests for inclusive Bootstrap sampling-uncertainty audits."""

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_bootstrap import audit_bootstrap_uncertainty


def _bootstrap_data(record_count: int = 12) -> pd.DataFrame:
    rng = np.random.default_rng(20260812)
    rows = []
    for unit_index in range(record_count):
        row = {
            "pseudonymous_unit_id": f"unit_{unit_index + 1}",
            "instrument_version": "inclusive_items_v0.1",
            "administration_round": 1,
        }
        shared = rng.normal(0, 5)
        for item_index, item in enumerate(ITEM_COLUMNS):
            row[item] = float(
                np.clip(30 + unit_index * 3 + item_index * 0.4 + shared + rng.normal(0, 3), 0, 100)
            )
        rows.append(row)
    return pd.DataFrame(rows)


def test_bootstrap_audit_reports_run_and_eight_interval_rows() -> None:
    audit = audit_bootstrap_uncertainty(
        _bootstrap_data(), "inclusive_items_v0.1", 1, n_resamples=500
    )
    run = audit["bootstrap_run_summary"].iloc[0]
    intervals = audit["bootstrap_interval_summary"]
    assert run["n_resamples"] == 500
    assert run["sampling_method"] == "nonparametric_bootstrap_with_replacement"
    assert len(intervals) == 8
    assert set(intervals["statistic_type"]) == {"dimension_mean", "support_gap_mean"}
    assert (intervals["percentile_interval_lower"] <= intervals["point_estimate"]).all()
    assert (intervals["point_estimate"] <= intervals["percentile_interval_upper"]).all()
    assert intervals["bootstrap_standard_error"].ge(0).all()
    assert len(audit["research_question_candidates"]) == 3
    assert "do not establish representativeness" in audit["interpretation"]


def test_bootstrap_same_seed_is_reproducible() -> None:
    first = audit_bootstrap_uncertainty(
        _bootstrap_data(), "inclusive_items_v0.1", 1, n_resamples=300, random_seed=73
    )
    second = audit_bootstrap_uncertainty(
        _bootstrap_data(), "inclusive_items_v0.1", 1, n_resamples=300, random_seed=73
    )
    pd.testing.assert_frame_equal(
        first["bootstrap_interval_summary"], second["bootstrap_interval_summary"]
    )


def test_bootstrap_different_seeds_preserve_points_but_change_resampling_summary() -> None:
    first = audit_bootstrap_uncertainty(
        _bootstrap_data(), "inclusive_items_v0.1", 1, n_resamples=300, random_seed=1
    )["bootstrap_interval_summary"]
    second = audit_bootstrap_uncertainty(
        _bootstrap_data(), "inclusive_items_v0.1", 1, n_resamples=300, random_seed=2
    )["bootstrap_interval_summary"]
    assert first["point_estimate"].equals(second["point_estimate"])
    assert not first["bootstrap_mean"].equals(second["bootstrap_mean"])


@pytest.mark.parametrize("n_resamples", [99, 10001, 100.5, True])
def test_bootstrap_rejects_invalid_resample_count(n_resamples: object) -> None:
    with pytest.raises(ValueError, match="n_resamples"):
        audit_bootstrap_uncertainty(
            _bootstrap_data(),
            "inclusive_items_v0.1",
            1,
            n_resamples=n_resamples,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("confidence_level", [0.79, 1.0, np.nan, True])
def test_bootstrap_rejects_invalid_confidence_level(confidence_level: object) -> None:
    with pytest.raises(ValueError, match="confidence_level"):
        audit_bootstrap_uncertainty(
            _bootstrap_data(),
            "inclusive_items_v0.1",
            1,
            confidence_level=confidence_level,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("random_seed", [-1, 2.5, True])
def test_bootstrap_rejects_invalid_random_seed(random_seed: object) -> None:
    with pytest.raises(ValueError, match="random_seed"):
        audit_bootstrap_uncertainty(
            _bootstrap_data(),
            "inclusive_items_v0.1",
            1,
            random_seed=random_seed,  # type: ignore[arg-type]
        )


def test_bootstrap_requires_minimum_sample_and_existing_version_round() -> None:
    with pytest.raises(ValueError, match="at least 5 complete records"):
        audit_bootstrap_uncertainty(
            _bootstrap_data(record_count=4), "inclusive_items_v0.1", 1
        )
    with pytest.raises(ValueError, match="do not exist"):
        audit_bootstrap_uncertainty(_bootstrap_data(), "inclusive_items_v0.1", 2)


def test_bootstrap_supports_non_100_source_scale_and_negative_gaps() -> None:
    data = _bootstrap_data()
    data[list(ITEM_COLUMNS)] = data[list(ITEM_COLUMNS)] / 100
    audit = audit_bootstrap_uncertainty(
        data,
        "inclusive_items_v0.1",
        1,
        n_resamples=200,
        source_min=0,
        source_max=1,
    )
    intervals = audit["bootstrap_interval_summary"]
    dimension_rows = intervals.query("statistic_type == 'dimension_mean'")
    assert dimension_rows["point_estimate"].between(0, 100).all()
    assert set(intervals.query("statistic_type == 'support_gap_mean'")["statistic"]) == {
        "gap_resource_practice",
        "gap_practice_participation",
        "overall_support_conversion_gap",
    }


def test_bootstrap_outputs_exclude_ids_draws_and_automatic_decisions() -> None:
    audit = audit_bootstrap_uncertainty(
        _bootstrap_data(), "inclusive_items_v0.1", 1, n_resamples=200
    )
    prohibited = {
        "pseudonymous_unit_id",
        "bootstrap_draw",
        "resampled_unit_id",
        "stability_status",
        "pass",
        "fail",
        "institution_rank",
        "policy_effect",
    }
    for key in (
        "bootstrap_run_summary",
        "bootstrap_interval_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
