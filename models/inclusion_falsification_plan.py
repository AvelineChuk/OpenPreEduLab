"""Readiness audits for falsification and sensitivity-analysis plans.

The workflow documents planned diagnostics before results are interpreted. It
does not run tests or treat a favourable diagnostic as proof of causality.
"""
from __future__ import annotations
from typing import Final
import pandas as pd

PLAN_COLUMNS: Final[tuple[str, ...]] = (
    "falsification_plan_id", "design_id", "instrument_version",
    "pretrend_diagnostic", "placebo_event_time_plan", "negative_control_outcome",
    "negative_control_exposure", "alternative_comparison_plan",
    "alternative_time_window_plan", "alternative_model_specification",
    "unobserved_confounding_sensitivity", "missing_data_sensitivity",
    "multiple_testing_strategy", "decision_rule", "preregistration_status",
    "researcher_notes",
)
PREREGISTRATION_STATUSES: Final[tuple[str, ...]] = (
    "not_started", "draft", "review_pending", "registered",
)

def create_falsification_plan_template() -> pd.DataFrame:
    """Return a blank falsification-plan schema."""
    return pd.DataFrame([{c: "" for c in PLAN_COLUMNS}], columns=PLAN_COLUMNS)

def load_falsification_plan_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 falsification-plan CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Falsification-plan CSV could not be read: {error}") from error
    return validate_falsification_plan(data)

def validate_falsification_plan(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete non-identifying falsification-plan records."""
    missing = sorted(set(PLAN_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Falsification plan is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Falsification plan must contain at least one record.")
    out = data.loc[:, list(PLAN_COLUMNS)].copy()
    for c in [x for x in PLAN_COLUMNS if x != "researcher_notes"]:
        out[c] = out[c].fillna("").astype(str).str.strip()
        if out[c].eq("").any():
            raise ValueError(f"Falsification-plan field '{c}' must not be blank.")
    out["researcher_notes"] = out["researcher_notes"].fillna("").astype(str).str.strip()
    if out["falsification_plan_id"].duplicated().any():
        raise ValueError("falsification_plan_id values must be unique.")
    invalid = sorted(set(out["preregistration_status"]) - set(PREREGISTRATION_STATUSES))
    if invalid:
        raise ValueError(f"Unknown preregistration statuses: {invalid}")
    return out

def audit_falsification_plan(data: pd.DataFrame, instrument_version: str) -> dict[str, pd.DataFrame | str]:
    """Summarise declared diagnostics and unresolved robustness prompts."""
    selected = validate_falsification_plan(data)
    selected = selected[selected["instrument_version"].eq(str(instrument_version).strip())]
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    undefined = {"none", "not_assessed", "not_defined", "unknown"}
    fields = {
        "pretrend_diagnostic": "Pretrend or baseline diagnostic is unresolved.",
        "placebo_event_time_plan": "Placebo event-time plan is unresolved.",
        "negative_control_outcome": "Negative-control outcome is unresolved.",
        "negative_control_exposure": "Negative-control exposure is unresolved.",
        "alternative_comparison_plan": "Alternative comparison plan is unresolved.",
        "alternative_time_window_plan": "Alternative time-window plan is unresolved.",
        "alternative_model_specification": "Alternative specification is unresolved.",
        "unobserved_confounding_sensitivity": "Unobserved-confounding sensitivity is unresolved.",
        "missing_data_sensitivity": "Missing-data sensitivity is unresolved.",
        "multiple_testing_strategy": "Multiple-testing strategy is unresolved.",
        "decision_rule": "Interpretation decision rule is unresolved.",
    }
    rows, prompts = [], []
    for row in selected.to_dict(orient="records"):
        current = [message for field, message in fields.items() if row[field].lower() in undefined]
        rows.append({"falsification_plan_id": row["falsification_plan_id"], "design_id": row["design_id"], "preregistration_status": row["preregistration_status"], "pretrend_plan_defined": row["pretrend_diagnostic"].lower() not in undefined, "placebo_timing_defined": row["placebo_event_time_plan"].lower() not in undefined, "negative_control_outcome_defined": row["negative_control_outcome"].lower() not in undefined, "negative_control_exposure_defined": row["negative_control_exposure"].lower() not in undefined, "sensitivity_plan_defined": row["unobserved_confounding_sensitivity"].lower() not in undefined, "documentation_prompt_count": len(current)})
        prompts.extend({"falsification_plan_id": row["falsification_plan_id"], "prompt_type": "falsification_plan_prompt", "prompt": p} for p in current)
    questions = pd.DataFrame([
        {"research_question_candidate": "Which observations would contradict the proposed identification story?", "required_future_evidence": "Preregistered falsification criteria"},
        {"research_question_candidate": "Do conclusions depend on comparison groups, event dates, windows, or model specifications?", "required_future_evidence": "Alternative-specification sensitivity analysis"},
        {"research_question_candidate": "How strong would unobserved confounding or missing-data departures need to be to change interpretation?", "required_future_evidence": "Quantitative bias and missing-data sensitivity analysis"},
    ])
    interpretation = ("Falsification-plan readiness evidence only. A documented or favourable placebo, pretrend, negative-control, or sensitivity result would not prove identification or causality. The audit runs no diagnostic, model, significance test, effect estimate, or automatic decision.")
    return {"falsification_plan_summary": pd.DataFrame(rows), "falsification_plan_prompts": pd.DataFrame(prompts), "research_question_candidates": questions, "interpretation": interpretation}
