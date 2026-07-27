"""Scenario-based policy simulation prototype for preschool education research.

The module applies explicit counterfactual changes to a baseline city-year
dataset. It is not a forecasting or causal-inference model: every output is
conditional on the supplied transition rules and fiscal assumptions.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd

from models.allocation import calculate_weights, normalize_indicators, prepare_indicators


def _validate_baseline(data: pd.DataFrame) -> pd.DataFrame:
    """Validate the fields required by the prototype transition mechanisms."""
    required = {
        "city", "year", "government_expenditure_per_child_yuan", "fte_teacher_count",
        "enrolled_children", "licensed_preschool_places", "resident_preschool_age_population",
        "resident_target_age_children_enrolled",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Baseline data are missing required columns: {missing}")
    baseline = data.copy()
    numeric = list(required - {"city", "year"})
    baseline[numeric] = baseline[numeric].apply(pd.to_numeric, errors="coerce")
    if baseline[numeric].isna().any().any() or (baseline[numeric] <= 0).any().any():
        raise ValueError("Required baseline numeric values must be finite and greater than zero.")
    if baseline.duplicated(["city", "year"]).any():
        raise ValueError("Baseline data must contain one observation per city-year.")
    return baseline


def _base_requirement(data: pd.DataFrame) -> pd.Series:
    """Calculate baseline service requirement from expenditure intensity and enrolment."""
    return data["government_expenditure_per_child_yuan"] * data["enrolled_children"]


def _score_scenarios(scenarios: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Calculate comparable PRAI scores by jointly normalising all scenarios."""
    labelled = []
    for label, frame in scenarios.items():
        copy = frame.copy()
        copy["scenario"] = label
        labelled.append(copy)
    combined = pd.concat(labelled, ignore_index=True)
    indicators = prepare_indicators(combined)
    normalised = normalize_indicators(indicators)
    weights = calculate_weights(normalised, method="equal")
    combined["resource_allocation_score"] = (
        normalised[weights.index].mul(weights, axis="columns").sum(axis=1) * 100
    ).round(2)
    return combined


def _build_comparison(
    baseline: pd.DataFrame,
    scenarios: dict[str, pd.DataFrame],
    requirements: dict[str, pd.Series],
    capacities: dict[str, pd.Series],
    teacher_demands: dict[str, pd.Series],
) -> pd.DataFrame:
    """Attach common output indicators to jointly scored scenario datasets."""
    all_frames = {"Baseline": baseline, **scenarios}
    base_requirement = _base_requirement(baseline)
    requirements = {"Baseline": base_requirement, **requirements}
    base_capacity = capacities.pop("Baseline", base_requirement * 1.10)
    capacities = {"Baseline": base_capacity, **capacities}
    base_teacher_demand = baseline["fte_teacher_count"]
    teacher_demands = {"Baseline": base_teacher_demand, **teacher_demands}

    scored = _score_scenarios(all_frames)
    result_frames = []
    for label, frame in all_frames.items():
        subset = scored.loc[scored["scenario"] == label, ["city", "year", "scenario", "resource_allocation_score"]].copy()
        subset["fiscal_requirement_yuan"] = requirements[label].to_numpy(dtype=float)
        subset["fiscal_capacity_yuan"] = capacities[label].to_numpy(dtype=float)
        subset["fiscal_sustainability_ratio"] = (
            subset["fiscal_capacity_yuan"] / subset["fiscal_requirement_yuan"]
        ).round(4)
        scenario_teacher_demand = teacher_demands.get(label, frame["fte_teacher_count"])
        subset["teacher_demand"] = scenario_teacher_demand.to_numpy(dtype=float)
        subset["education_coverage_pct"] = (
            100 * frame["resident_target_age_children_enrolled"] / frame["resident_preschool_age_population"]
        ).round(2).to_numpy()
        result_frames.append(subset)
    return pd.concat(result_frames, ignore_index=True)


def _subsidy_case(baseline: pd.DataFrame, subsidy_increase_rate: float) -> tuple[pd.DataFrame, pd.Series]:
    """Create a higher-per-child-subsidy counterfactual."""
    if subsidy_increase_rate < 0:
        raise ValueError("subsidy_increase_rate must be non-negative.")
    scenario = baseline.copy()
    scenario["government_expenditure_per_child_yuan"] *= 1 + subsidy_increase_rate
    return scenario, _base_requirement(scenario)


def _population_case(
    baseline: pd.DataFrame, population_change_rate: float, teacher_child_ratio: float | None
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Create a population-change counterfactual with proportional enrolment demand."""
    if population_change_rate <= -1:
        raise ValueError("population_change_rate must be greater than -1.")
    scenario = baseline.copy()
    factor = 1 + population_change_rate
    coverage = baseline["resident_target_age_children_enrolled"] / baseline["resident_preschool_age_population"]
    scenario["resident_preschool_age_population"] *= factor
    scenario["resident_target_age_children_enrolled"] = scenario["resident_preschool_age_population"] * coverage
    scenario["enrolled_children"] *= factor
    ratio = (
        pd.Series(teacher_child_ratio, index=baseline.index)
        if teacher_child_ratio is not None
        else baseline["fte_teacher_count"] / baseline["enrolled_children"]
    )
    if (ratio <= 0).any():
        raise ValueError("teacher_child_ratio must be greater than zero.")
    return scenario, _base_requirement(scenario), scenario["enrolled_children"] * ratio


def _teacher_cost_case(
    baseline: pd.DataFrame, teacher_cost_increase_rate: float, baseline_teacher_cost_yuan: float
) -> tuple[pd.DataFrame, pd.Series]:
    """Create a teacher-wage-cost counterfactual without changing service volume."""
    if teacher_cost_increase_rate < 0 or baseline_teacher_cost_yuan <= 0:
        raise ValueError("Teacher-cost parameters must be non-negative increase and positive base cost.")
    scenario = baseline.copy()
    added_cost = baseline["fte_teacher_count"] * baseline_teacher_cost_yuan * teacher_cost_increase_rate
    return scenario, _base_requirement(scenario) + added_cost


def _fiscal_constraint_case(baseline: pd.DataFrame, fiscal_growth_rate: float, capacity_multiplier: float) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Create a fiscal-capacity constraint and scale per-child support if needed."""
    if fiscal_growth_rate <= -1 or capacity_multiplier <= 0:
        raise ValueError("Fiscal growth must be greater than -1 and capacity multiplier must be positive.")
    requirement = _base_requirement(baseline)
    capacity = requirement * capacity_multiplier * (1 + fiscal_growth_rate)
    scenario = baseline.copy()
    support_factor = np.minimum(1.0, capacity / requirement)
    scenario["government_expenditure_per_child_yuan"] *= support_factor
    # Requirement remains the cost of maintaining baseline service; lower
    # spending in the scenario represents a potential resource constraint.
    return scenario, requirement, capacity


def simulate_subsidy_policy(baseline_data: pd.DataFrame, subsidy_increase_rate: float, fiscal_capacity_multiplier: float = 1.10) -> pd.DataFrame:
    """Compare baseline conditions with an increased-subsidy scenario.

    ``subsidy_increase_rate`` changes per-child government expenditure; fiscal
    capacity is held at baseline requirement times ``fiscal_capacity_multiplier``.
    """
    baseline = _validate_baseline(baseline_data)
    scenario, requirement = _subsidy_case(baseline, subsidy_increase_rate)
    capacity = _base_requirement(baseline) * fiscal_capacity_multiplier
    return _build_comparison(baseline, {"Increase Subsidy": scenario}, {"Increase Subsidy": requirement}, {"Baseline": capacity, "Increase Subsidy": capacity}, {})


def simulate_population_change(baseline_data: pd.DataFrame, population_change_rate: float, teacher_child_ratio: float | None = None, fiscal_capacity_multiplier: float = 1.10) -> pd.DataFrame:
    """Compare baseline conditions with a population-change scenario.

    A negative ``population_change_rate`` represents declining preschool-age
    population. Enrolment demand changes proportionally while existing staff
    and facilities remain fixed; teacher demand uses the supplied or baseline
    FTE-teacher-per-child ratio.
    """
    baseline = _validate_baseline(baseline_data)
    scenario, requirement, teacher_demand = _population_case(baseline, population_change_rate, teacher_child_ratio)
    capacity = _base_requirement(baseline) * fiscal_capacity_multiplier
    return _build_comparison(baseline, {"Declining Population": scenario}, {"Declining Population": requirement}, {"Baseline": capacity, "Declining Population": capacity}, {"Declining Population": teacher_demand})


def simulate_teacher_cost_change(baseline_data: pd.DataFrame, teacher_cost_increase_rate: float, baseline_teacher_cost_yuan: float, fiscal_capacity_multiplier: float = 1.10) -> pd.DataFrame:
    """Compare baseline conditions with a higher-teacher-cost scenario."""
    baseline = _validate_baseline(baseline_data)
    scenario, requirement = _teacher_cost_case(baseline, teacher_cost_increase_rate, baseline_teacher_cost_yuan)
    capacity = _base_requirement(baseline) * fiscal_capacity_multiplier
    return _build_comparison(baseline, {"Teacher Cost Increase": scenario}, {"Teacher Cost Increase": requirement}, {"Teacher Cost Increase": capacity, "Baseline": capacity}, {})


def simulate_fiscal_constraint(baseline_data: pd.DataFrame, fiscal_growth_rate: float, fiscal_capacity_multiplier: float = 1.10) -> pd.DataFrame:
    """Compare baseline conditions with a constrained-fiscal-capacity scenario."""
    baseline = _validate_baseline(baseline_data)
    scenario, requirement, capacity = _fiscal_constraint_case(baseline, fiscal_growth_rate, fiscal_capacity_multiplier)
    baseline_capacity = _base_requirement(baseline) * fiscal_capacity_multiplier
    return _build_comparison(baseline, {"Fiscal Constraint": scenario}, {"Fiscal Constraint": requirement}, {"Baseline": baseline_capacity, "Fiscal Constraint": capacity}, {})


def simulate_policy_scenarios(baseline_data: pd.DataFrame, subsidy_increase_rate: float, population_change_rate: float, teacher_cost_increase_rate: float, baseline_teacher_cost_yuan: float, fiscal_growth_rate: float, fiscal_capacity_multiplier: float = 1.10, teacher_child_ratio: float | None = None) -> pd.DataFrame:
    """Run the four policy scenarios in one jointly normalised comparison set.

    Use this function, rather than concatenating individually simulated score
    tables, when comparing PRAI scores across Scenario A–D.
    """
    baseline = _validate_baseline(baseline_data)
    subsidy, subsidy_req = _subsidy_case(baseline, subsidy_increase_rate)
    population, population_req, population_teachers = _population_case(baseline, population_change_rate, teacher_child_ratio)
    teacher, teacher_req = _teacher_cost_case(baseline, teacher_cost_increase_rate, baseline_teacher_cost_yuan)
    constraint, constraint_req, constraint_capacity = _fiscal_constraint_case(baseline, fiscal_growth_rate, fiscal_capacity_multiplier)
    base_capacity = _base_requirement(baseline) * fiscal_capacity_multiplier
    scenarios = {"Increase Subsidy": subsidy, "Declining Population": population, "Teacher Cost Increase": teacher, "Fiscal Constraint": constraint}
    requirements = {"Increase Subsidy": subsidy_req, "Declining Population": population_req, "Teacher Cost Increase": teacher_req, "Fiscal Constraint": constraint_req}
    capacities = {"Baseline": base_capacity, "Increase Subsidy": base_capacity, "Declining Population": base_capacity, "Teacher Cost Increase": base_capacity, "Fiscal Constraint": constraint_capacity}
    demands = {"Declining Population": population_teachers}
    return _build_comparison(baseline, scenarios, requirements, capacities, demands)
