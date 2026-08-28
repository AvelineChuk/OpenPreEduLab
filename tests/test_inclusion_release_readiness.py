"""Tests for inclusive release-package readiness audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_release_readiness import (
    RELEASE_COLUMNS,
    audit_release_readiness,
    create_release_readiness_template,
    load_release_readiness_csv,
    validate_release_readiness,
)


def _release_data() -> pd.DataFrame:
    values = {column: "documented" for column in RELEASE_COLUMNS}
    values.update(
        {
            "release_record_id": "release-001",
            "claim_inventory_version": "not_recorded",
            "reporting_plan_id": "report-001",
            "execution_record_id": "run-001",
            "instrument_version": "v1",
            "package_version": "not_defined",
            "release_scope": "aggregate_research_outputs_only",
            "file_manifest_reference": "not_recorded",
            "checksum_manifest_reference": "not_recorded",
            "documentation_index_reference": "not_recorded",
            "license_status": "not_documented",
            "citation_metadata_status": "not_documented",
            "privacy_review_status": "pending",
            "accessibility_review_status": "not_started",
            "claim_traceability_review_status": "pending",
            "ai_disclosure_status": "not_documented",
            "limitations_included": "not_documented",
            "synthetic_data_label_status": "not_documented",
            "release_channel": "not_defined",
            "embargo_status": "not_assessed",
            "independent_review_status": "not_started",
            "release_status": "draft",
            "researcher_notes": "Restricted path must not be exported.",
        }
    )
    return pd.DataFrame([values])


def test_template_loader_and_unresolved_prompts() -> None:
    """The template is stable and release gaps remain visible."""
    assert tuple(create_release_readiness_template().columns) == RELEASE_COLUMNS
    loaded = load_release_readiness_csv(StringIO(_release_data().to_csv(index=False)))
    audit = audit_release_readiness(loaded, "v1")
    summary = audit["release_readiness_summary"].iloc[0]
    assert summary["documentation_prompt_count"] >= 15
    assert not summary["file_manifest_documented"]
    assert not summary["checksum_manifest_documented"]
    assert not summary["synthetic_label_documented"]


def test_validation_rejects_schema_duplicates_and_release_approval() -> None:
    """Invalid or automatic release statuses should fail closed."""
    with pytest.raises(ValueError, match="missing required columns"):
        validate_release_readiness(
            _release_data().drop(columns="checksum_manifest_reference")
        )
    with pytest.raises(ValueError, match="must be unique"):
        validate_release_readiness(
            pd.concat([_release_data(), _release_data()], ignore_index=True)
        )
    invalid = _release_data()
    invalid.loc[0, "release_status"] = "automatically_published"
    with pytest.raises(ValueError, match="Unknown release_status values"):
        validate_release_readiness(invalid)


def test_review_and_synthetic_label_prompts_remain_visible() -> None:
    """Privacy, accessibility, review, and synthetic labels are never inferred."""
    audit = audit_release_readiness(_release_data(), "v1")
    prompts = audit["release_readiness_prompts"]["prompt"].tolist()
    assert any("Privacy review" in prompt for prompt in prompts)
    assert any("Accessibility review" in prompt for prompt in prompts)
    assert any("Independent release review" in prompt for prompt in prompts)
    assert any("Synthetic-data label" in prompt for prompt in prompts)


def test_outputs_exclude_paths_notes_results_and_release_decisions() -> None:
    """Audit outputs must not expose paths, notes, results, or approvals."""
    audit = audit_release_readiness(_release_data(), "v1")
    prohibited = {
        "file_manifest_reference",
        "checksum_manifest_reference",
        "documentation_index_reference",
        "researcher_notes",
        "coefficient",
        "effect_estimate",
        "p_value",
        "significance",
        "release_approved",
        "pass",
        "fail",
    }
    for key in (
        "release_readiness_summary",
        "release_readiness_prompts",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
    assert "does not approve or publish" in str(audit["interpretation"])
