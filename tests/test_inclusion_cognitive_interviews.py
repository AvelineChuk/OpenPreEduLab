"""Tests for cognitive-interview and item-revision audit utilities."""

from io import BytesIO

import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_cognitive_interviews import (
    create_cognitive_interview_template,
    create_item_revision_log_template,
    load_cognitive_interview_csv,
    load_item_revision_log_csv,
    summarize_cognitive_interviews,
    summarize_item_revision_log,
    validate_cognitive_interview_records,
    validate_item_revision_log,
)


def _interview_records() -> pd.DataFrame:
    template = create_cognitive_interview_template().iloc[:3].copy()
    template["interview_id"] = "interview_001"
    template["participant_role"] = "preschool_teacher"
    template["interview_round"] = 1
    template["instrument_version"] = "inclusive_items_v0.1"
    template["issue_type"] = ["comprehension", "no_issue", "accessibility"]
    template["issue_observed"] = ["yes", "no", "yes"]
    template["evidence_note"] = [
        "Participant requested a clearer institutional referent.",
        "",
        "Participant requested a plain-language alternative.",
    ]
    template["suggested_revision"] = ["Clarify institutional referent.", "", "Add plain language."]
    template["minority_or_distinct_view"] = ["no", "no", "yes"]
    template["safeguarding_flag"] = "no"
    template["accessibility_flag"] = ["no", "no", "yes"]
    return template


def _revision_records() -> pd.DataFrame:
    template = create_item_revision_log_template().iloc[:2].copy()
    template["decision_id"] = ["decision_001", "decision_002"]
    template["source_instrument_version"] = "inclusive_items_v0.1"
    template["target_instrument_version"] = "inclusive_items_v0.2"
    template["decision_round"] = 1
    template["decision"] = ["revise", "retain"]
    template["target_score_column"] = ""
    template["target_dimension"] = ""
    template["revised_item_wording"] = ["Revised policy clarity wording", ""]
    template["decision_rationale"] = ["Clarify institutional referent.", "No issue identified."]
    template["minority_view_record"] = ["One reviewer preferred retention.", "None recorded."]
    template["safeguarding_review"] = "completed"
    template["equity_accessibility_review"] = "completed"
    template["responsible_researcher_id"] = "researcher_001"
    template["decision_date"] = "2026-08-12"
    return template


def test_cognitive_interview_template_has_current_items() -> None:
    template = create_cognitive_interview_template()
    assert len(template) == len(ITEM_COLUMNS)
    assert template["item"].is_unique
    assert template["interview_id"].eq("").all()


def test_cognitive_interviews_allow_partial_item_coverage_and_safe_summary() -> None:
    records = validate_cognitive_interview_records(_interview_records())
    summaries = summarize_cognitive_interviews(records)
    assert len(records) == 3
    assert summaries["issue_summary"]["observation_count"].sum() == 2
    assert summaries["coverage_summary"].loc[0, "item_count"] == 3
    excluded = {"interview_id", "evidence_note", "suggested_revision"}
    assert excluded.isdisjoint(summaries["issue_summary"].columns)
    assert excluded.isdisjoint(summaries["coverage_summary"].columns)


def test_cognitive_interview_csv_supports_utf8_bom() -> None:
    payload = BytesIO(_interview_records().to_csv(index=False).encode("utf-8-sig"))
    loaded = load_cognitive_interview_csv(payload)
    assert len(loaded) == 3


def test_cognitive_interviews_reject_inconsistent_issue_logic() -> None:
    records = _interview_records()
    records.loc[0, "issue_observed"] = "no"
    with pytest.raises(ValueError, match="requires issue_type=no_issue"):
        validate_cognitive_interview_records(records)

    records = _interview_records()
    records.loc[0, "evidence_note"] = ""
    with pytest.raises(ValueError, match="require a non-identifying evidence_note"):
        validate_cognitive_interview_records(records)


def test_revision_template_has_current_items() -> None:
    template = create_item_revision_log_template()
    assert len(template) == len(ITEM_COLUMNS)
    assert template["item"].is_unique
    assert template["decision_id"].eq("").all()


def test_revision_log_validates_and_summarizes_human_decisions() -> None:
    records = validate_item_revision_log(_revision_records())
    summary = summarize_item_revision_log(records)
    assert len(records) == 2
    assert set(summary["decision"]) == {"revise", "retain"}
    assert summary["item_count"].sum() == 2


def test_revision_csv_supports_utf8_bom() -> None:
    payload = BytesIO(_revision_records().to_csv(index=False).encode("utf-8-sig"))
    loaded = load_item_revision_log_csv(payload)
    assert len(loaded) == 2


def test_revision_log_rejects_invalid_versions_and_missing_wording() -> None:
    records = _revision_records()
    records["target_instrument_version"] = records["source_instrument_version"]
    with pytest.raises(ValueError, match="must differ"):
        validate_item_revision_log(records)

    records = _revision_records()
    records.loc[0, "revised_item_wording"] = ""
    with pytest.raises(ValueError, match="require revised_item_wording"):
        validate_item_revision_log(records)


def test_revision_log_rejects_duplicate_decisions() -> None:
    records = _revision_records()
    records.loc[1, "decision_id"] = records.loc[0, "decision_id"]
    with pytest.raises(ValueError, match="must be unique"):
        validate_item_revision_log(records)


def test_cognitive_interviews_reject_invalid_minority_flag() -> None:
    records = _interview_records()
    records.loc[0, "minority_or_distinct_view"] = "unclear"
    with pytest.raises(ValueError, match="minority_or_distinct_view must use yes or no"):
        validate_cognitive_interview_records(records)


def test_move_decision_requires_a_different_valid_target_dimension() -> None:
    records = _revision_records().iloc[[0]].copy()
    records.loc[records.index[0], "decision"] = "move"
    records.loc[records.index[0], "revised_item_wording"] = ""
    with pytest.raises(ValueError, match="require a target"):
        validate_item_revision_log(records)

    records.loc[records.index[0], "target_score_column"] = "resource_support_score"
    records.loc[records.index[0], "target_dimension"] = "Resource Support"
    validated = validate_item_revision_log(records)
    assert validated.loc[validated.index[0], "target_dimension"] == "Resource Support"
