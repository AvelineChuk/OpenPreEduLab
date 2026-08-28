"""Tests for inclusive results-reporting and claim-boundary audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_results_reporting import (
    REPORTING_COLUMNS,
    audit_results_reporting,
    create_results_reporting_template,
    load_results_reporting_csv,
    validate_results_reporting,
)


def _reporting_data() -> pd.DataFrame:
    values = {column: "documented" for column in REPORTING_COLUMNS}
    values.update(
        {
            "reporting_plan_id": "report-001",
            "execution_record_id": "run-001",
            "specification_id": "spec-001",
            "instrument_version": "v1",
            "primary_analysis_label": "not_defined",
            "secondary_analysis_policy": "report all labelled analyses",
            "outcome_reporting_scope": "not_recorded",
            "null_uncertain_result_policy": "report without directional spin",
            "uncertainty_reporting_policy": "not_defined",
            "multiple_testing_reporting": "not_defined",
            "specification_deviation_disclosure": "not_recorded",
            "subgroup_reporting_policy": "not_assessed",
            "small_cell_suppression": "not_defined",
            "institution_identifier_policy": "aggregate outputs only",
            "visualization_scale_disclosure": "not_defined",
            "support_gap_language": "not_defined",
            "causal_language_status": "pending_independent_design_review",
            "ai_assistance_status": "planned_bounded_assistance",
            "ai_verification_plan": "not_defined",
            "data_limitations_statement": "not_recorded",
            "conflict_of_interest_statement": "not_recorded",
            "review_status": "review_pending",
            "researcher_notes": "Do not export this note.",
        }
    )
    return pd.DataFrame([values])


def test_template_loader_and_unresolved_prompts() -> None:
    """The template is stable and reporting gaps remain visible."""
    assert tuple(create_results_reporting_template().columns) == REPORTING_COLUMNS
    loaded = load_results_reporting_csv(
        StringIO(_reporting_data().to_csv(index=False))
    )
    audit = audit_results_reporting(loaded, "v1")
    summary = audit["results_reporting_summary"].iloc[0]
    assert summary["documentation_prompt_count"] >= 12
    assert not summary["primary_analysis_documented"]
    assert not summary["uncertainty_reporting_documented"]
    assert not summary["privacy_suppression_documented"]


def test_validation_rejects_schema_duplicates_and_unknown_statuses() -> None:
    """Invalid or causal-claim-like declarations should fail closed."""
    with pytest.raises(ValueError, match="missing required columns"):
        validate_results_reporting(
            _reporting_data().drop(columns="outcome_reporting_scope")
        )
    with pytest.raises(ValueError, match="must be unique"):
        validate_results_reporting(
            pd.concat([_reporting_data(), _reporting_data()], ignore_index=True)
        )
    invalid = _reporting_data()
    invalid.loc[0, "causal_language_status"] = "causal_effect_confirmed"
    with pytest.raises(ValueError, match="Unknown causal_language_status values"):
        validate_results_reporting(invalid)


def test_ai_and_support_gap_boundaries_remain_explicit() -> None:
    """AI and Support Gap gaps must produce documentation prompts."""
    audit = audit_results_reporting(_reporting_data(), "v1")
    prompts = audit["results_reporting_prompts"]["prompt"].tolist()
    assert any("Support Gap" in prompt for prompt in prompts)
    assert any("AI assistance" in prompt for prompt in prompts)
    assert any("Causal language remains withheld" in prompt for prompt in prompts)


def test_outputs_exclude_notes_and_result_values() -> None:
    """The audit must not expose notes or create result fields."""
    audit = audit_results_reporting(_reporting_data(), "v1")
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
        "results_reporting_summary",
        "results_reporting_prompts",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
    assert "receives no result values" in str(audit["interpretation"])
