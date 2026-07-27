"""Software validation tests for the PRAI allocation module."""

import pandas as pd
import pytest

from models.allocation import calculate_prai_score, evaluate_level, load_data, normalize_indicators, prepare_indicators


def test_allocation_normal_case(sample_dataset_path):
    """Synthetic city-year data produce one bounded PRAI score per observation."""
    data = load_data(sample_dataset_path)
    scores = calculate_prai_score(data)
    assert len(scores) == len(data)
    assert scores["resource_allocation_score"].between(0, 100).all()
    assert not scores.duplicated(["city", "year"]).any()


def test_allocation_boundary_case_constant_indicator(sample_dataset_path):
    """A constant positive indicator receives the documented neutral score."""
    indicators = prepare_indicators(load_data(sample_dataset_path))
    indicators["qualified_teacher_rate_pct"] = 80.0
    normalised = normalize_indicators(indicators)
    assert (normalised["qualified_teacher_rate_pct"] == 0.5).all()
    assert evaluate_level(80) == "High Allocation"
    assert evaluate_level(60) == "Medium Allocation"
    assert evaluate_level(59.99) == "Low Allocation"


def test_allocation_missing_value_case(sample_dataset_path, tmp_path):
    """Missing required CSV fields are rejected during data loading."""
    data = pd.read_csv(sample_dataset_path).drop(columns=["fte_teacher_count"])
    invalid_path = tmp_path / "missing_allocation_field.csv"
    data.to_csv(invalid_path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_data(invalid_path)


def test_allocation_invalid_input_case(sample_dataset_path, tmp_path):
    """Duplicate city-year observations are rejected during data loading."""
    data = pd.read_csv(sample_dataset_path)
    duplicated = pd.concat([data, data.iloc[[0]]], ignore_index=True)
    invalid_path = tmp_path / "duplicate_city_year.csv"
    duplicated.to_csv(invalid_path, index=False)
    with pytest.raises(ValueError, match="duplicate city-year"):
        load_data(invalid_path)
