"""Tests for inclusive analysis-reproducibility readiness audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_analysis_reproducibility import (
    REPRODUCIBILITY_COLUMNS,
    audit_analysis_reproducibility,
    create_analysis_reproducibility_template,
    load_analysis_reproducibility_csv,
    validate_analysis_reproducibility,
)


def _reproducibility_data() -> pd.DataFrame:
    values = {column: "documented" for column in REPRODUCIBILITY_COLUMNS}
    values.update(
        {
            "execution_record_id": "run-001",
            "specification_id": "spec-001",
            "instrument_version": "v1",
            "data_snapshot_id": "not_recorded",
            "data_snapshot_date": "not_recorded",
            "data_checksum": "not_recorded",
            "code_repository_reference": "repository record",
            "code_commit": "not_recorded",
            "environment_lock_reference": "not_recorded",
            "software_environment": "Python environment pending",
            "random_seed_policy": "not_defined",
            "specification_lock_status": "draft_lock",
            "deviation_log_reference": "not_applicable",
            "execution_status": "not_started",
            "quality_control_status": "planned",
            "output_storage_boundary": "session-only aggregate outputs",
            "output_disclosure_boundary": "aggregate outputs only",
            "review_status": "review_pending",
            "researcher_notes": "Do not export this note.",
        }
    )
    return pd.DataFrame([values])


def test_template_loader_and_unresolved_prompts() -> None:
    """The schema is stable and unresolved fields remain visible."""
    assert tuple(create_analysis_reproducibility_template().columns) == (
        REPRODUCIBILITY_COLUMNS
    )
    loaded = load_analysis_reproducibility_csv(
        StringIO(_reproducibility_data().to_csv(index=False))
    )
    audit = audit_analysis_reproducibility(loaded, "v1")
    summary = audit["analysis_reproducibility_summary"].iloc[0]
    assert summary["documentation_prompt_count"] >= 8
    assert not summary["data_snapshot_documented"]
    assert not summary["code_commit_documented"]
    assert summary["disclosure_boundary_documented"]


def test_validation_rejects_schema_duplicates_and_unknown_statuses() -> None:
    """Invalid or ambiguous declarations should fail closed."""
    with pytest.raises(ValueError, match="missing required columns"):
        validate_analysis_reproducibility(
            _reproducibility_data().drop(columns="data_checksum")
        )
    with pytest.raises(ValueError, match="must be unique"):
        validate_analysis_reproducibility(
            pd.concat(
                [_reproducibility_data(), _reproducibility_data()],
                ignore_index=True,
            )
        )
    invalid = _reproducibility_data()
    invalid.loc[0, "execution_status"] = "causal_effect_confirmed"
    with pytest.raises(ValueError, match="Unknown execution_status values"):
        validate_analysis_reproducibility(invalid)


def test_amended_specification_requires_deviation_log_prompt() -> None:
    """An amended specification must retain a visible deviation-log gap."""
    data = _reproducibility_data()
    data.loc[0, "specification_lock_status"] = "amended_with_deviation_log"
    data.loc[0, "deviation_log_reference"] = "not_recorded"
    audit = audit_analysis_reproducibility(data, "v1")
    prompts = audit["analysis_reproducibility_prompts"]["prompt"].tolist()
    assert any("deviation log" in prompt for prompt in prompts)


def test_outputs_exclude_notes_results_and_causal_decisions() -> None:
    """The audit must remain documentation-only and aggregate-safe."""
    audit = audit_analysis_reproducibility(_reproducibility_data(), "v1")
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
        "analysis_reproducibility_summary",
        "analysis_reproducibility_prompts",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
    assert "executes no code" in str(audit["interpretation"])
