"""Causal-identification design readiness audits for inclusive policy research.

The audit records proposed design assumptions but never authorises causal
language, fits an effect model, or concludes that identification is valid.
"""
from __future__ import annotations
from typing import Final
import pandas as pd

DESIGN_COLUMNS: Final[tuple[str, ...]] = (
    "design_id", "instrument_version", "event_id", "design_type",
    "treatment_definition", "comparison_definition", "time_zero_definition",
    "pre_period_definition", "post_period_definition", "identification_assumption",
    "confounding_strategy", "anticipation_assessment", "interference_assessment",
    "pretrend_or_baseline_evidence", "negative_control_plan",
    "sensitivity_analysis_plan", "causal_claim_status", "researcher_notes",
)
DESIGN_TYPES: Final[tuple[str, ...]] = (
    "descriptive_only", "interrupted_time_series_candidate",
    "difference_in_differences_candidate", "matched_comparison_candidate",
    "natural_experiment_candidate", "randomized_design_candidate",
)
CAUSAL_STATUSES: Final[tuple[str, ...]] = (
    "not_permitted", "design_under_review", "independent_review_required",
)

def create_identification_design_template() -> pd.DataFrame:
    """Return a blank identification-design schema."""
    return pd.DataFrame([{c: "" for c in DESIGN_COLUMNS}], columns=DESIGN_COLUMNS)

def load_identification_design_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 identification-design CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Identification-design CSV could not be read: {error}") from error
    return validate_identification_design(data)

def validate_identification_design(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete non-identifying design declarations."""
    missing = sorted(set(DESIGN_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Identification design is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Identification design must contain at least one record.")
    out = data.loc[:, list(DESIGN_COLUMNS)].copy()
    for c in [x for x in DESIGN_COLUMNS if x != "researcher_notes"]:
        out[c] = out[c].fillna("").astype(str).str.strip()
        if out[c].eq("").any():
            raise ValueError(f"Identification-design field '{c}' must not be blank.")
    out["researcher_notes"] = out["researcher_notes"].fillna("").astype(str).str.strip()
    if out["design_id"].duplicated().any():
        raise ValueError("design_id values must be unique.")
    invalid = sorted(set(out["design_type"]) - set(DESIGN_TYPES))
    if invalid:
        raise ValueError(f"Unknown design types: {invalid}")
    invalid = sorted(set(out["causal_claim_status"]) - set(CAUSAL_STATUSES))
    if invalid:
        raise ValueError(f"Unknown causal claim statuses: {invalid}")
    return out

def audit_identification_design(data: pd.DataFrame, instrument_version: str) -> dict[str, pd.DataFrame | str]:
    """Summarise design declarations and unresolved identification prompts."""
    validated = validate_identification_design(data)
    selected = validated[validated["instrument_version"].eq(str(instrument_version).strip())]
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    undefined = {"none", "not_assessed", "not_defined", "unknown"}
    rows, prompts = [], []
    prompt_fields = {
        "comparison_definition": "Comparison definition is unresolved.",
        "identification_assumption": "Identification assumption is unresolved.",
        "confounding_strategy": "Confounding strategy is unresolved.",
        "anticipation_assessment": "Anticipation has not been assessed.",
        "interference_assessment": "Interference has not been assessed.",
        "pretrend_or_baseline_evidence": "Pretrend or baseline evidence is unresolved.",
        "sensitivity_analysis_plan": "Sensitivity analysis is unresolved.",
    }
    for row in selected.to_dict(orient="records"):
        current = [message for field, message in prompt_fields.items() if row[field].lower() in undefined]
        if row["design_type"] == "descriptive_only":
            current.append("Descriptive-only design does not support causal effect claims.")
        rows.append({"design_id": row["design_id"], "event_id": row["event_id"], "design_type": row["design_type"], "causal_claim_status": row["causal_claim_status"], "treatment_defined": row["treatment_definition"].lower() not in undefined, "comparison_defined": row["comparison_definition"].lower() not in undefined, "time_zero_defined": row["time_zero_definition"].lower() not in undefined, "sensitivity_plan_defined": row["sensitivity_analysis_plan"].lower() not in undefined, "documentation_prompt_count": len(current)})
        prompts.extend({"design_id": row["design_id"], "prompt_type": "identification_design_prompt", "prompt": p} for p in current)
    questions = pd.DataFrame([
        {"research_question_candidate": "What explicit assumptions identify the proposed policy or context effect?", "required_future_evidence": "Preregistered identification argument and design evidence"},
        {"research_question_candidate": "Are comparison units, timing, anticipation, interference, and confounding strategies defensible?", "required_future_evidence": "Design diagnostics and independent methodological review"},
        {"research_question_candidate": "Which falsification, negative-control, and sensitivity analyses are required?", "required_future_evidence": "Preregistered robustness and falsification plan"},
    ])
    interpretation = ("Identification-design readiness evidence only. Completed fields do not establish identification, exchangeability, parallel trends, valid controls, absence of interference, policy effects, or causality. No effect model, approval, causal claim, ranking, or decision is produced.")
    return {"identification_design_summary": pd.DataFrame(rows), "identification_design_prompts": pd.DataFrame(prompts), "research_question_candidates": questions, "interpretation": interpretation}
