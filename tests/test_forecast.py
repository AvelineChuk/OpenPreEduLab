"""Software validation tests for the forecast module."""

import pytest

from models.allocation import load_data
from models.forecast import forecast_fiscal_requirement, forecast_population, forecast_teacher_demand


def test_forecast_normal_case(sample_dataset_path):
    """Population, teacher, and fiscal projections are produced for future years."""
    raw = load_data(sample_dataset_path)
    population = forecast_population(raw, [2026, 2027])
    teachers = forecast_teacher_demand(population, 0.065)
    fiscal = forecast_fiscal_requirement(population, 20000)
    assert len(population) == 20
    assert population["future_child_population"].ge(0).all()
    assert teachers["future_teacher_demand"].ge(0).all()
    assert fiscal["future_fiscal_need"].ge(0).all()


def test_forecast_boundary_case_one_future_year(sample_dataset_path):
    """One future year is a valid minimum forecast horizon."""
    raw = load_data(sample_dataset_path)
    forecast = forecast_population(raw, [2026])
    assert len(forecast) == raw["city"].nunique()
    assert (forecast["year"] == 2026).all()


def test_forecast_missing_value_case(sample_dataset_path):
    """A missing population field is rejected before model fitting."""
    raw = load_data(sample_dataset_path).drop(columns=["resident_preschool_age_population"])
    with pytest.raises(ValueError, match="missing required columns"):
        forecast_population(raw, [2026])


def test_forecast_invalid_input_case(sample_dataset_path):
    """Historical or current years cannot be passed as forecast years."""
    raw = load_data(sample_dataset_path)
    with pytest.raises(ValueError, match="must be later"):
        forecast_population(raw, [2025])
