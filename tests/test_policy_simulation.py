"""Software validation tests for the policy simulation module."""

import pytest

from models.allocation import load_data
from models.policy_simulation import simulate_policy_scenarios, simulate_population_change


def test_policy_simulation_normal_case(sample_dataset_path):
    """Joint simulation produces all baseline and A-D scenario output fields."""
    raw = load_data(sample_dataset_path)
    result = simulate_policy_scenarios(raw, 0.10, -0.08, 0.08, 80000, -0.12)
    expected_scenarios = {"Baseline", "Increase Subsidy", "Declining Population", "Teacher Cost Increase", "Fiscal Constraint"}
    expected_columns = {"fiscal_requirement_yuan", "fiscal_sustainability_ratio", "resource_allocation_score", "teacher_demand", "education_coverage_pct"}
    assert len(result) == len(raw) * len(expected_scenarios)
    assert set(result["scenario"]) == expected_scenarios
    assert expected_columns.issubset(result.columns)
    assert result["resource_allocation_score"].between(0, 100).all()


def test_policy_simulation_boundary_case_zero_population_change(sample_dataset_path):
    """A zero population change retains baseline resource-allocation scores."""
    raw = load_data(sample_dataset_path)
    result = simulate_population_change(raw, population_change_rate=0.0)
    baseline = result.loc[result["scenario"] == "Baseline", ["city", "year", "resource_allocation_score"]]
    scenario = result.loc[result["scenario"] == "Declining Population", ["city", "year", "resource_allocation_score"]]
    merged = baseline.merge(scenario, on=["city", "year"], suffixes=("_base", "_scenario"))
    assert (merged["resource_allocation_score_base"] == merged["resource_allocation_score_scenario"]).all()


def test_policy_simulation_missing_value_case(sample_dataset_path):
    """Missing policy-simulation baseline fields are rejected."""
    raw = load_data(sample_dataset_path).drop(columns=["resident_target_age_children_enrolled"])
    with pytest.raises(ValueError, match="missing required columns"):
        simulate_population_change(raw, population_change_rate=-0.05)


def test_policy_simulation_invalid_input_case(sample_dataset_path):
    """A population change at or below -100 percent is invalid."""
    raw = load_data(sample_dataset_path)
    with pytest.raises(ValueError, match="greater than -1"):
        simulate_population_change(raw, population_change_rate=-1.0)
