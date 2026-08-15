"""Tests for inclusive estimation-specification readiness audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_estimation_specification import (
    ESTIMATOR_FAMILIES,
    SPECIFICATION_COLUMNS,
    audit_estimation_specification,
    create_estimation_specification_template,
    load_estimation_specification_csv,
    validate_estimation_specification,
)


def _specification_data() -> pd.DataFrame:
    values = {column: "documented" for column in SPECIFICATION_COLUMNS}
    values.update(
        {
            "specification_id": "spec-001",
            "design_id": "design-001",
            "falsification_plan_id": "false-001",
            "instrument_version": "v1",
            "outcome_definition": "not_defined",
            "estimand_definition": "not_defined",
            "analysis_population": "participating institutions",
            "unit_of_analysis": "institution-round",
            "time_scale": "round",
            "estimator_family": "panel_model_candidate",
            "functional_form": "not_defined",
            "treatment_encoding": "not_defined",
            "comparison_contrast": "not_defined",
            "covariate_adjustment": "not_assessed",
            "fixed_effects_structure": "not_applicable",
            "dependence_adjustment": "not_defined",
            "standard_error_method": "not_defined",
            "clustering_level": "not_defined",
            "weighting_strategy": "not_assessed",
            "missing_data_method": "not_assessed",
            "event_time_window": "not_defined",
            "reference_period": "not_defined",
            "multiple_testing_implementation": "not_defined",
            "uncertainty_reporting": "not_defined",
            "software_environment": "not_defined",
            "output_disclosure_boundary": "aggregate outputs only",
            "specification_status": "draft",
            "researcher_notes": "Do not export this note.",
        }
    )
    return pd.DataFrame([values])


def test_template_loader_and_unresolved_prompts() -> None:
    """The template is stable and unresolved declarations remain visible."""
    assert tuple(create_estimation_specification_template().columns) == (
        SPECIFICATION_COLUMNS
    )
    loaded = load_estimation_specification_csv(
        StringIO(_specification_data().to_csv(index=False))
    )
    audit = audit_estimation_specification(loaded, "v1")

    summary = audit["estimation_specification_summary"].iloc[0]
    assert summary["documentation_prompt_count"] == 16
    assert len(audit["estimation_specification_prompts"]) == 16
    assert not summary["outcome_defined"]
    assert summary["disclosure_boundary_defined"]


def test_validation_rejects_schema_duplicate_estimator_and_status() -> None:
    """Invalid or ambiguous plan declarations should fail closed."""
    with pytest.raises(ValueError, match="missing required columns"):
        validate_estimation_specification(
            _specification_data().drop(columns="estimand_definition")
        )
    with pytest.raises(ValueError, match="must be unique"):
        validate_estimation_specification(
            pd.concat([_specification_data(), _specification_data()], ignore_index=True)
        )
    invalid_estimator = _specification_data()
    invalid_estimator.loc[0, "estimator_family"] = "automatic_best_model"
    with pytest.raises(ValueError, match="Unknown estimator families"):
        validate_estimation_specification(invalid_estimator)
    invalid_status = _specification_data()
    invalid_status.loc[0, "specification_status"] = "approved"
    with pytest.raises(ValueError, match="Unknown specification statuses"):
        validate_estimation_specification(invalid_status)
    assert "descriptive_only" in ESTIMATOR_FAMILIES


def test_outputs_exclude_notes_results_and_causal_decisions() -> None:
    """The audit must remain documentation-only and aggregate-safe."""
    audit = audit_estimation_specification(_specification_data(), "v1")
    prohibited = {
        "researcher_notes",
        "coefficient",
        "effect_estimate",
        "p_value",
        "significance",
        "causal_conclusion",
        "pass",
        "fail",
    }
    for key in (
        "estimation_specification_summary",
        "estimation_specification_prompts",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
    assert "fits no model" in str(audit["interpretation"])
