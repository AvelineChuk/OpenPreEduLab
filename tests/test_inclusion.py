"""Software validation for the inclusive education research model."""

import numpy as np
import pandas as pd
import pytest

from models.inclusion import (
    ITEM_COLUMNS,
    SCORE_COLUMNS,
    calculate_inclusion_dimension_scores,
    cluster_institutions,
    correlation_matrix,
    descriptive_statistics,
    generate_research_insights,
    load_inclusion_data,
    simulate_inclusion_scenarios,
    standardize_inclusion_data,
    validate_inclusion_data,
)
from models.support_gap import calculate_support_gaps
from llm.inclusion_prompts import create_inclusion_interpretation_request


def test_inclusion_five_dimension_scores(sample_inclusive_dataset_path) -> None:
    """Every synthetic institution receives five bounded dimension scores."""
    data = load_inclusion_data(sample_inclusive_dataset_path)
    scores = calculate_inclusion_dimension_scores(data)
    assert len(scores) == len(data) == 12
    assert set(SCORE_COLUMNS).issubset(scores.columns)
    assert scores[list(SCORE_COLUMNS)].apply(lambda column: column.between(0, 100)).all().all()


def test_inclusion_declared_zero_one_scale_is_converted(sample_inclusive_dataset_path) -> None:
    """A researcher-declared 0–1 scale is converted linearly to 0–100."""
    data = pd.read_csv(sample_inclusive_dataset_path)
    data[list(ITEM_COLUMNS)] = data[list(ITEM_COLUMNS)] / 100
    converted = standardize_inclusion_data(data, source_min=0, source_max=1)
    assert converted.loc[0, "policy_clarity"] == 84
    assert converted[list(ITEM_COLUMNS)].max().max() <= 100


def test_inclusion_missing_column_is_rejected(sample_inclusive_dataset_path) -> None:
    """Required item omissions cannot silently change a dimension definition."""
    data = pd.read_csv(sample_inclusive_dataset_path).drop(columns=["belonging"])
    with pytest.raises(ValueError, match="missing required columns"):
        validate_inclusion_data(data)


def test_inclusion_missing_value_is_rejected(sample_inclusive_dataset_path) -> None:
    """Missing scoring values are reported rather than automatically imputed."""
    data = pd.read_csv(sample_inclusive_dataset_path)
    data.loc[0, "peer_interaction"] = np.nan
    with pytest.raises(ValueError, match="missing or invalid"):
        validate_inclusion_data(data)


def test_inclusion_out_of_range_value_is_rejected(sample_inclusive_dataset_path) -> None:
    """Values outside the declared instrument range fail validation."""
    data = pd.read_csv(sample_inclusive_dataset_path)
    data.loc[0, "teacher_support"] = 101
    with pytest.raises(ValueError, match="declared source range"):
        validate_inclusion_data(data)


def test_inclusion_boundary_values_are_valid(sample_inclusive_dataset_path) -> None:
    """The closed 0–100 scale accepts both endpoints."""
    data = pd.read_csv(sample_inclusive_dataset_path)
    data.loc[0, "teacher_support"] = 0
    data.loc[1, "teacher_support"] = 100
    validated = validate_inclusion_data(data)
    assert validated.loc[0, "teacher_support"] == 0
    assert validated.loc[1, "teacher_support"] == 100


def test_inclusion_descriptive_correlation_and_clusters(sample_inclusive_dataset_path) -> None:
    """Researcher-mode descriptive analyses return reproducible output."""
    data = load_inclusion_data(sample_inclusive_dataset_path)
    scores = calculate_inclusion_dimension_scores(data)
    descriptive = descriptive_statistics(scores, SCORE_COLUMNS)
    correlation = correlation_matrix(scores, SCORE_COLUMNS)
    clusters = cluster_institutions(scores, n_clusters=3)
    assert len(descriptive) == 5
    assert correlation.shape == (5, 5)
    assert clusters["exploratory_cluster"].between(1, 3).all()


def test_inclusion_insights_and_scenarios_are_bounded(sample_inclusive_dataset_path) -> None:
    """Insights remain question-generating and scenarios retain explicit labels."""
    data = load_inclusion_data(sample_inclusive_dataset_path)
    scores = calculate_inclusion_dimension_scores(data)
    gaps = calculate_support_gaps(scores)
    insights = generate_research_insights(scores, gaps)
    scenarios = simulate_inclusion_scenarios(data, change_points=10)
    assert "descriptive sample patterns" in insights["insight"]
    assert len(insights["research_question_candidates"]) == 3
    assert set(scenarios["scenario"]) == {
        "Baseline",
        "Increase Teacher Support",
        "Increase Training Support",
        "Increase Financial Support",
        "Improve Curriculum Adaptation",
    }
    assert scenarios[list(SCORE_COLUMNS)].apply(lambda column: column.between(0, 100)).all().all()


def test_inclusion_llm_request_preserves_non_diagnostic_boundary() -> None:
    """The inclusion prompt prohibits diagnosis, labelling, and causal claims."""
    request = create_inclusion_interpretation_request(
        {"dimension_means": {"resource_support_score": 80}, "support_gap": 22},
        "Synthetic demonstration data.",
    )
    assert "Do not diagnose" in request.system_prompt
    assert "not a causal estimator" in request.system_prompt
    assert "Research Question Candidates" in request.system_prompt
