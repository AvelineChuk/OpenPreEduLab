"""Tests for identification-design readiness audits."""
from io import StringIO
import pandas as pd
import pytest
from models.inclusion_identification_design import *

def _data():
    return pd.DataFrame([{"design_id":"d1","instrument_version":"v1","event_id":"e1","design_type":"difference_in_differences_candidate","treatment_definition":"documented institutional exposure","comparison_definition":"not_defined","time_zero_definition":"event start","pre_period_definition":"rounds before event","post_period_definition":"rounds after event","identification_assumption":"not_assessed","confounding_strategy":"not_assessed","anticipation_assessment":"unknown","interference_assessment":"unknown","pretrend_or_baseline_evidence":"not_assessed","negative_control_plan":"not_defined","sensitivity_analysis_plan":"not_defined","causal_claim_status":"not_permitted","researcher_notes":""}])

def test_template_loader_and_prompts():
    assert tuple(create_identification_design_template().columns) == DESIGN_COLUMNS
    audit=audit_identification_design(load_identification_design_csv(StringIO(_data().to_csv(index=False))),"v1")
    assert audit["identification_design_summary"].iloc[0]["documentation_prompt_count"] == 7
    assert len(audit["identification_design_prompts"]) == 7

def test_validation_rejects_schema_duplicate_and_choices():
    with pytest.raises(ValueError,match="missing required columns"): validate_identification_design(_data().drop(columns="event_id"))
    with pytest.raises(ValueError,match="must be unique"): validate_identification_design(pd.concat([_data(),_data()],ignore_index=True))
    bad=_data();bad.loc[0,"design_type"]="causal"
    with pytest.raises(ValueError,match="Unknown design types"): validate_identification_design(bad)

def test_outputs_exclude_notes_effects_and_approval():
    audit=audit_identification_design(_data(),"v1")
    prohibited={"researcher_notes","effect_estimate","policy_effect","approval_status","causal_conclusion","pass","fail"}
    for key in ("identification_design_summary","identification_design_prompts","research_question_candidates"):
        assert prohibited.isdisjoint(audit[key].columns)
