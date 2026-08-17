"""Tests for inclusive claim-evidence traceability readiness audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_claim_traceability import (
    TRACEABILITY_COLUMNS,
    audit_claim_traceability,
    create_claim_traceability_template,
    load_claim_traceability_csv,
    validate_claim_traceability,
)


def _traceability_data() -> pd.DataFrame:
    values = {column: "documented" for column in TRACEABILITY_COLUMNS}
    values.update(
        {
            "claim_record_id": "claim-001",
            "reporting_plan_id": "report-001",
            "execution_record_id": "run-001",
            "specification_id": "spec-001",
            "instrument_version": "v1",
            "claim_label": "Researcher-controlled short label",
            "claim_scope": "mechanism_hypothesis",
            "evidence_output_reference": "not_recorded",
            "evidence_type": "no_empirical_evidence",
            "population_scope": "not_defined",
            "time_scope": "not_defined",
            "uncertainty_reference": "not_recorded",
            "limitation_reference": "not_recorded",
            "alternative_explanation_record": "not_recorded",
            "support_gap_interpretation_status": "not_defined",
            "source_provenance_status": "pending_review",
            "ai_origin_status": "ai_assisted_pending_review",
            "human_review_status": "review_pending",
            "public_disclosure_status": "aggregate_release_pending_review",
            "researcher_notes": "Do not export this note.",
        }
    )
    return pd.DataFrame([values])


def test_template_loader_and_unresolved_prompts() -> None:
    """The template is stable and unsupported links remain visible."""
    assert tuple(create_claim_traceability_template().columns) == TRACEABILITY_COLUMNS
    loaded = load_claim_traceability_csv(
        StringIO(_traceability_data().to_csv(index=False))
    )
    audit = audit_claim_traceability(loaded, "v1")
    summary = audit["claim_traceability_summary"].iloc[0]
    assert summary["documentation_prompt_count"] >= 11
    assert not summary["evidence_reference_documented"]
    assert not summary["uncertainty_reference_documented"]
    assert not summary["limitation_reference_documented"]


def test_validation_rejects_schema_duplicates_and_unknown_statuses() -> None:
    """Invalid or truth-claim-like statuses should fail closed."""
    with pytest.raises(ValueError, match="missing required columns"):
        validate_claim_traceability(
            _traceability_data().drop(columns="uncertainty_reference")
        )
    with pytest.raises(ValueError, match="must be unique"):
        validate_claim_traceability(
            pd.concat([_traceability_data(), _traceability_data()], ignore_index=True)
        )
    invalid = _traceability_data()
    invalid.loc[0, "human_review_status"] = "claim_verified_true"
    with pytest.raises(ValueError, match="Unknown human_review_status values"):
        validate_claim_traceability(invalid)


def test_boundary_prompts_cover_evidence_ai_and_disclosure() -> None:
    """Unsupported evidence, AI, Support Gap, and release gaps remain visible."""
    audit = audit_claim_traceability(_traceability_data(), "v1")
    prompts = audit["claim_traceability_prompts"]["prompt"].tolist()
    assert any("No empirical evidence" in prompt for prompt in prompts)
    assert any("Support Gap" in prompt for prompt in prompts)
    assert any("AI-assisted" in prompt for prompt in prompts)
    assert any("public disclosure" in prompt for prompt in prompts)


def test_outputs_exclude_claim_text_notes_and_result_values() -> None:
    """Public audit outputs must not reproduce claim text or numerical results."""
    audit = audit_claim_traceability(_traceability_data(), "v1")
    prohibited = {
        "claim_label",
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
        "claim_traceability_summary",
        "claim_traceability_prompts",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
    assert "reproduces no free-text claim" in str(audit["interpretation"])
