"""Software validation tests for the DEA efficiency module."""

import pytest

from models.allocation import load_data
from models.efficiency import calculate_dea_efficiency, evaluate_panel_efficiency, prepare_efficiency_data


INPUTS = ["total_government_expenditure_yuan", "fte_teacher_count", "usable_indoor_area_sqm"]
OUTPUTS = ["enrolled_children", "age_specific_enrolment_coverage_pct", "qualified_teacher_rate_pct"]


def test_efficiency_normal_case(sample_dataset_path):
    """The synthetic panel produces a bounded DEA score for every city-year."""
    prepared = prepare_efficiency_data(load_data(sample_dataset_path))
    result = evaluate_panel_efficiency(prepared, INPUTS, OUTPUTS)
    assert len(result) == len(prepared)
    assert result["efficiency_score"].between(0, 1).all()


def test_efficiency_boundary_case_two_dmus(sample_dataset_path):
    """The minimum supported two-DMU cross-section can be evaluated."""
    prepared = prepare_efficiency_data(load_data(sample_dataset_path))
    two_dmus = prepared.loc[prepared["year"] == 2025].iloc[:2]
    result = calculate_dea_efficiency(two_dmus, INPUTS, OUTPUTS)
    assert len(result) == 2
    assert result["efficiency_score"].between(0, 1).all()


def test_efficiency_missing_value_case(sample_dataset_path):
    """Missing raw fields are rejected before DEA preparation."""
    raw = load_data(sample_dataset_path).drop(columns=["usable_indoor_area_sqm"])
    with pytest.raises(ValueError, match="missing columns"):
        prepare_efficiency_data(raw)


def test_efficiency_invalid_input_case(sample_dataset_path):
    """A DEA variable cannot be selected as both input and output."""
    prepared = prepare_efficiency_data(load_data(sample_dataset_path))
    cross_section = prepared.loc[prepared["year"] == 2025]
    with pytest.raises(ValueError, match="both a DEA input and output"):
        calculate_dea_efficiency(cross_section, ["fte_teacher_count"], ["fte_teacher_count"])
