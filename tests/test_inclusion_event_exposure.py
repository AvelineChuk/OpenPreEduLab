"""Tests for event-exposure definition readiness audits."""
from io import StringIO
import pandas as pd
import pytest
from models.inclusion_event_exposure import *

def _data():
    return pd.DataFrame([{"event_id":"e1","instrument_version":"v1","exposure_definition":"institutional participation","exposure_scope":"study_sites","exposure_status":"mixed_or_unknown","exposure_start_date":"2026-01-01","exposure_end_date":"2026-01-10","intensity_definition":"not_defined","lag_definition":"30 days","comparator_definition":"not_defined","evidence_reference":"source_a","researcher_notes":""}])

def test_template_loader_and_prompts():
    assert tuple(create_event_exposure_template().columns) == EXPOSURE_COLUMNS
    audit = audit_event_exposure_definitions(load_event_exposure_csv(StringIO(_data().to_csv(index=False))), "v1")
    assert audit["event_exposure_summary"].iloc[0]["comparator_defined"] == False
    assert len(audit["exposure_definition_prompts"]) == 3

def test_validation_rejects_missing_duplicate_bad_date_and_status():
    with pytest.raises(ValueError, match="missing required columns"): validate_event_exposure(_data().drop(columns="evidence_reference"))
    with pytest.raises(ValueError, match="must be unique"): validate_event_exposure(pd.concat([_data(), _data()], ignore_index=True))
    bad = _data(); bad.loc[0,"exposure_end_date"]="2025-01-01"
    with pytest.raises(ValueError, match="must not be earlier"): validate_event_exposure(bad)
    bad = _data(); bad.loc[0,"exposure_status"]="maybe"
    with pytest.raises(ValueError, match="Unknown exposure statuses"): validate_event_exposure(bad)

def test_outputs_exclude_notes_ids_and_effects():
    audit = audit_event_exposure_definitions(_data(), "v1")
    prohibited={"researcher_notes","pseudonymous_unit_id","effect_estimate","policy_effect","causal_status","pass","fail"}
    for key in ("event_exposure_summary","exposure_definition_prompts","research_question_candidates"):
        assert prohibited.isdisjoint(audit[key].columns)
