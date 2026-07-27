"""Software validation tests for the educational equity module."""

import pytest

from models.allocation import calculate_prai_score, load_data
from models.equity import calculate_cv, calculate_gini, calculate_theil, generate_equity_report


def test_equity_normal_case(sample_dataset_path):
    """PRAI results produce a complete province-decomposed equity report."""
    raw = load_data(sample_dataset_path)
    scores = calculate_prai_score(raw).merge(raw[["city", "year", "province"]], on=["city", "year"])
    report = generate_equity_report(scores, year=2025, group_column="province")
    assert len(report) == 5
    assert {"indicator", "value", "equity_level", "interpretation"}.issubset(report.columns)


def test_equity_boundary_case_equal_distribution():
    """An equal distribution has zero CV, Gini, and Theil values."""
    values = [5.0, 5.0, 5.0]
    assert calculate_cv(values) == 0.0
    assert calculate_gini(values) == 0.0
    assert calculate_theil(values) == 0.0


def test_equity_missing_value_case():
    """Missing values are rejected rather than silently omitted."""
    with pytest.raises(ValueError, match="finite numeric"):
        calculate_gini([1.0, None, 3.0])


def test_equity_invalid_input_case():
    """Negative allocation values are invalid for the implemented measures."""
    with pytest.raises(ValueError, match="non-negative"):
        calculate_theil([1.0, -1.0, 2.0])
