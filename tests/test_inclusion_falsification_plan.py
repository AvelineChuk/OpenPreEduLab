"""Tests for falsification-plan readiness audits."""
from io import StringIO
import pandas as pd
import pytest
from models.inclusion_falsification_plan import *

def _data():
    return pd.DataFrame([{"falsification_plan_id":"f1","design_id":"d1","instrument_version":"v1","pretrend_diagnostic":"not_assessed","placebo_event_time_plan":"not_defined","negative_control_outcome":"not_defined","negative_control_exposure":"not_defined","alternative_comparison_plan":"documented alternative group","alternative_time_window_plan":"not_defined","alternative_model_specification":"not_defined","unobserved_confounding_sensitivity":"not_assessed","missing_data_sensitivity":"not_assessed","multiple_testing_strategy":"not_defined","decision_rule":"not_defined","preregistration_status":"draft","researcher_notes":""}])

def test_template_loader_and_prompts():
    assert tuple(create_falsification_plan_template().columns) == PLAN_COLUMNS
    audit=audit_falsification_plan(load_falsification_plan_csv(StringIO(_data().to_csv(index=False))),"v1")
    assert audit["falsification_plan_summary"].iloc[0]["documentation_prompt_count"] == 10
    assert len(audit["falsification_plan_prompts"]) == 10

def test_validation_rejects_schema_duplicate_and_status():
    with pytest.raises(ValueError,match="missing required columns"): validate_falsification_plan(_data().drop(columns="decision_rule"))
    with pytest.raises(ValueError,match="must be unique"): validate_falsification_plan(pd.concat([_data(),_data()],ignore_index=True))
    bad=_data();bad.loc[0,"preregistration_status"]="approved"
    with pytest.raises(ValueError,match="Unknown preregistration statuses"): validate_falsification_plan(bad)

def test_outputs_exclude_notes_results_and_causal_decisions():
    audit=audit_falsification_plan(_data(),"v1")
    prohibited={"researcher_notes","p_value","effect_estimate","placebo_result","causal_conclusion","pass","fail"}
    for key in ("falsification_plan_summary","falsification_plan_prompts","research_question_candidates"):
        assert prohibited.isdisjoint(audit[key].columns)
