"""Tests for longitudinal timing and fieldwork-metadata audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_longitudinal_metadata import (
    LONGITUDINAL_METADATA_COLUMNS,
    audit_longitudinal_metadata,
    create_longitudinal_metadata_template,
    load_longitudinal_metadata_csv,
    validate_longitudinal_metadata,
)


def _metadata() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": 1,
                "collection_start_date": "2026-01-05",
                "collection_end_date": "2026-01-16",
                "administration_mode": "secure_web_form",
                "recruitment_scope": "participating_preschools_wave_1",
                "sampling_frame_reference": "frame_2025_12",
                "round_purpose": "baseline_description",
                "fieldwork_event_status": "none_reported",
                "fieldwork_event_notes": "",
            },
            {
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": 3,
                "collection_start_date": "2026-04-06",
                "collection_end_date": "2026-04-17",
                "administration_mode": "secure_web_form",
                "recruitment_scope": "participating_preschools_wave_1",
                "sampling_frame_reference": "frame_2025_12",
                "round_purpose": "follow_up_description",
                "fieldwork_event_status": "event_recorded",
                "fieldwork_event_notes": "Calendar interruption documented in field log.",
            },
            {
                "instrument_version": "inclusive_items_v0.1",
                "administration_round": 6,
                "collection_start_date": "2026-08-03",
                "collection_end_date": "2026-08-21",
                "administration_mode": "assisted_secure_form",
                "recruitment_scope": "participating_preschools_wave_2",
                "sampling_frame_reference": "frame_2026_07",
                "round_purpose": "follow_up_description",
                "fieldwork_event_status": "unknown",
                "fieldwork_event_notes": "",
            },
        ]
    )


def test_template_and_csv_loader_use_expected_schema() -> None:
    assert tuple(create_longitudinal_metadata_template().columns) == LONGITUDINAL_METADATA_COLUMNS
    loaded = load_longitudinal_metadata_csv(StringIO(_metadata().to_csv(index=False)))
    assert len(loaded) == 3


def test_metadata_audit_reports_rounds_intervals_and_changes() -> None:
    audit = audit_longitudinal_metadata(_metadata(), "inclusive_items_v0.1")
    overview = audit["longitudinal_metadata_overview"].iloc[0]
    rounds = audit["round_metadata_summary"]
    adjacent = audit["adjacent_round_metadata_comparison"]
    assert overview["round_count"] == 3
    assert not overview["equal_midpoint_intervals"]
    assert overview["administration_mode_change_observed"]
    assert overview["sampling_frame_change_observed"]
    assert list(zip(adjacent["first_round"], adjacent["second_round"], strict=True)) == [
        (1, 3),
        (3, 6),
    ]
    assert len(rounds) == 3
    assert "fieldwork_event_notes" not in rounds.columns
    assert rounds["fieldwork_event_notes_present"].sum() == 1
    assert len(audit["research_question_candidates"]) == 3


def test_metadata_validation_rejects_missing_columns_duplicates_and_bad_dates() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_longitudinal_metadata(_metadata().drop(columns="round_purpose"))
    duplicated = pd.concat([_metadata(), _metadata().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="must be unique"):
        validate_longitudinal_metadata(duplicated)
    bad_date = _metadata()
    bad_date.loc[0, "collection_start_date"] = "05/01/2026"
    with pytest.raises(ValueError, match="ISO dates"):
        validate_longitudinal_metadata(bad_date)
    reversed_date = _metadata()
    reversed_date.loc[0, "collection_end_date"] = "2026-01-01"
    with pytest.raises(ValueError, match="must not be earlier"):
        validate_longitudinal_metadata(reversed_date)


def test_metadata_validation_requires_event_notes_and_known_status() -> None:
    missing_notes = _metadata()
    missing_notes.loc[1, "fieldwork_event_notes"] = ""
    with pytest.raises(ValueError, match="must be supplied"):
        validate_longitudinal_metadata(missing_notes)
    unknown_status = _metadata()
    unknown_status.loc[0, "fieldwork_event_status"] = "probably_none"
    with pytest.raises(ValueError, match="Unknown fieldwork event statuses"):
        validate_longitudinal_metadata(unknown_status)


def test_metadata_audit_selects_one_version_and_requires_two_rounds() -> None:
    second = _metadata().copy()
    second["instrument_version"] = "inclusive_items_v0.2"
    mixed = pd.concat([_metadata(), second], ignore_index=True)
    assert len(audit_longitudinal_metadata(mixed, "inclusive_items_v0.2")["round_metadata_summary"]) == 3
    with pytest.raises(ValueError, match="does not exist"):
        audit_longitudinal_metadata(mixed, "unknown")
    with pytest.raises(ValueError, match="at least two rounds"):
        audit_longitudinal_metadata(_metadata().iloc[[0]], "inclusive_items_v0.1")


def test_metadata_outputs_exclude_notes_ids_scores_and_judgements() -> None:
    audit = audit_longitudinal_metadata(_metadata(), "inclusive_items_v0.1")
    prohibited = {
        "fieldwork_event_notes",
        "pseudonymous_unit_id",
        "institution_id",
        "quality_status",
        "bias_status",
        "policy_effect",
        "institution_rank",
        "pass",
        "fail",
    }
    for key in (
        "longitudinal_metadata_overview",
        "round_metadata_summary",
        "adjacent_round_metadata_comparison",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
