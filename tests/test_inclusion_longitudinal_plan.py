"""Tests for longitudinal analysis-plan readiness audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_longitudinal_plan import (
    LONGITUDINAL_PLAN_COLUMNS,
    audit_longitudinal_plan,
    create_longitudinal_plan_template,
    load_longitudinal_plan_csv,
    validate_longitudinal_plan,
)


def _plan() -> pd.DataFrame:
    return pd.DataFrame(
        [{
            "analysis_plan_id": "plan_001",
            "instrument_version": "inclusive_items_v0.1",
            "unit_of_analysis": "institutional_panel_unit",
            "target_population_scope": "participating_preschools_in_study_frame",
            "round_comparison": "round_1_vs_round_2",
            "change_definition": "later_minus_earlier",
            "estimand_scope": "descriptive_matched_mean_change",
            "missing_data_strategy": "complete_case_with_attrition_sensitivity",
            "weighting_strategy": "none_declared",
            "uncertainty_method": "paired_nonparametric_bootstrap",
            "dependence_structure": "institution_paired_across_rounds",
            "measurement_comparability_basis": "comparability_readiness_audit_pending_invariance",
            "attrition_evidence_reference": "attrition_audit_v0.1",
            "metadata_evidence_reference": "metadata_audit_v0.1",
            "causal_language_allowed": "no",
            "preregistration_status": "draft",
            "researcher_notes": "",
        }]
    )


def test_template_loader_and_audit_summary() -> None:
    assert tuple(create_longitudinal_plan_template().columns) == LONGITUDINAL_PLAN_COLUMNS
    loaded = load_longitudinal_plan_csv(StringIO(_plan().to_csv(index=False)))
    audit = audit_longitudinal_plan(loaded)
    summary = audit["longitudinal_plan_summary"].iloc[0]
    assert summary["change_definition"] == "later_minus_earlier"
    assert summary["documentation_prompt_count"] == 0
    assert audit["method_documentation_prompts"].empty
    assert len(audit["research_question_candidates"]) == 3


def test_plan_generates_bounded_documentation_prompts() -> None:
    data = _plan()
    data.loc[0, "change_definition"] = "not_yet_defined"
    data.loc[0, "missing_data_strategy"] = "not_assessed"
    data.loc[0, "uncertainty_method"] = "none"
    data.loc[0, "causal_language_allowed"] = "yes"
    audit = audit_longitudinal_plan(data)
    prompts = audit["method_documentation_prompts"]
    assert len(prompts) == 4
    assert prompts["prompt_type"].eq("method_documentation_prompt").all()


def test_validation_rejects_missing_columns_duplicates_and_invalid_choices() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_longitudinal_plan(_plan().drop(columns="estimand_scope"))
    duplicated = pd.concat([_plan(), _plan()], ignore_index=True)
    with pytest.raises(ValueError, match="must be unique"):
        validate_longitudinal_plan(duplicated)
    invalid = _plan()
    invalid.loc[0, "causal_language_allowed"] = "maybe"
    with pytest.raises(ValueError, match="causal_language_allowed"):
        validate_longitudinal_plan(invalid)
    invalid_status = _plan()
    invalid_status.loc[0, "preregistration_status"] = "approved"
    with pytest.raises(ValueError, match="preregistration statuses"):
        validate_longitudinal_plan(invalid_status)


def test_validation_rejects_blank_required_text_and_unknown_change_definition() -> None:
    blank = _plan()
    blank.loc[0, "target_population_scope"] = ""
    with pytest.raises(ValueError, match="target_population_scope"):
        validate_longitudinal_plan(blank)
    invalid_change = _plan()
    invalid_change.loc[0, "change_definition"] = "trend"
    with pytest.raises(ValueError, match="change definitions"):
        validate_longitudinal_plan(invalid_change)


def test_plan_outputs_exclude_notes_ids_scores_and_judgements() -> None:
    audit = audit_longitudinal_plan(_plan())
    prohibited = {
        "researcher_notes",
        "pseudonymous_unit_id",
        "institution_id",
        "effect_estimate",
        "policy_effect",
        "causal_conclusion",
        "approval_status",
        "pass",
        "fail",
    }
    for key in (
        "longitudinal_plan_summary",
        "method_documentation_prompts",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
