"""Tests for longitudinal event time-alignment audits."""

from io import StringIO

import pandas as pd
import pytest

from models.inclusion_longitudinal_events import (
    EVENT_COLUMNS,
    audit_longitudinal_event_alignment,
    create_longitudinal_event_template,
    load_longitudinal_event_csv,
    validate_longitudinal_events,
)


def _metadata() -> pd.DataFrame:
    return pd.DataFrame([
        {"instrument_version":"v1","administration_round":1,"collection_start_date":"2026-01-05","collection_end_date":"2026-01-15","administration_mode":"web","recruitment_scope":"scope_a","sampling_frame_reference":"frame_a","round_purpose":"baseline","fieldwork_event_status":"none_reported","fieldwork_event_notes":""},
        {"instrument_version":"v1","administration_round":2,"collection_start_date":"2026-04-05","collection_end_date":"2026-04-15","administration_mode":"web","recruitment_scope":"scope_a","sampling_frame_reference":"frame_a","round_purpose":"follow_up","fieldwork_event_status":"none_reported","fieldwork_event_notes":""},
    ])


def _events() -> pd.DataFrame:
    return pd.DataFrame([
        {"event_id":"event_1","instrument_version":"v1","event_type":"training_activity","event_start_date":"2026-02-01","event_end_date":"2026-02-03","event_scope":"participating_sites","evidence_source":"training_log","evidence_status":"researcher_record","event_description":"Aggregate training schedule."},
        {"event_id":"event_2","instrument_version":"v1","event_type":"calendar_disruption","event_start_date":"2026-04-10","event_end_date":"2026-04-12","event_scope":"study_region","evidence_source":"official_calendar","evidence_status":"documented_primary_source","event_description":"Calendar interruption."},
    ])


def test_template_loader_and_event_alignment() -> None:
    assert tuple(create_longitudinal_event_template().columns) == EVENT_COLUMNS
    loaded = load_longitudinal_event_csv(StringIO(_events().to_csv(index=False)))
    audit = audit_longitudinal_event_alignment(_metadata(), loaded, "v1")
    events = audit["event_alignment_summary"]
    pairs = audit["adjacent_round_event_context_summary"]
    assert len(events) == 2
    assert events.loc[events["event_id"].eq("event_2"), "overlapping_rounds"].iloc[0] == "2"
    assert pairs.iloc[0]["events_strictly_between_windows"] == 1
    assert pairs.iloc[0]["events_overlapping_second_window"] == 1
    assert "event_description" not in events.columns


def test_event_validation_rejects_schema_duplicates_dates_and_categories() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        validate_longitudinal_events(_events().drop(columns="event_scope"))
    duplicated = pd.concat([_events(), _events().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="must be unique"):
        validate_longitudinal_events(duplicated)
    reversed_dates = _events()
    reversed_dates.loc[0, "event_end_date"] = "2026-01-01"
    with pytest.raises(ValueError, match="must not be earlier"):
        validate_longitudinal_events(reversed_dates)
    invalid = _events()
    invalid.loc[0, "event_type"] = "policy_effect"
    with pytest.raises(ValueError, match="Unknown event types"):
        validate_longitudinal_events(invalid)


def test_event_alignment_requires_version_rounds_and_events() -> None:
    with pytest.raises(ValueError, match="at least two metadata rounds"):
        audit_longitudinal_event_alignment(_metadata().iloc[[0]], _events(), "v1")
    other = _events().copy()
    other["instrument_version"] = "v2"
    with pytest.raises(ValueError, match="no registered events"):
        audit_longitudinal_event_alignment(_metadata(), other, "v1")


def test_event_outputs_exclude_descriptions_ids_scores_and_effects() -> None:
    audit = audit_longitudinal_event_alignment(_metadata(), _events(), "v1")
    prohibited = {"event_description","pseudonymous_unit_id","institution_id","effect_estimate","policy_effect","causal_status","pass","fail"}
    for key in ("event_alignment_summary","adjacent_round_event_context_summary","research_question_candidates"):
        assert prohibited.isdisjoint(audit[key].columns)
