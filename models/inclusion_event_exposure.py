"""Readiness audit for policy/context event exposure definitions.

The audit checks whether an event registry distinguishes documented chronology
from institution-level exposure. It does not infer exposure or estimate effects.
"""
from __future__ import annotations

from typing import Final
import pandas as pd

EXPOSURE_COLUMNS: Final[tuple[str, ...]] = (
    "event_id", "instrument_version", "exposure_definition",
    "exposure_scope", "exposure_status", "exposure_start_date",
    "exposure_end_date", "intensity_definition", "lag_definition",
    "comparator_definition", "evidence_reference", "researcher_notes",
)
EXPOSURE_STATUSES: Final[tuple[str, ...]] = (
    "not_assessed", "documented_exposure", "documented_non_exposure",
    "mixed_or_unknown",
)

def create_event_exposure_template() -> pd.DataFrame:
    """Return a blank non-identifying event-exposure schema."""
    return pd.DataFrame([{c: "" for c in EXPOSURE_COLUMNS}], columns=EXPOSURE_COLUMNS)

def load_event_exposure_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 exposure-definition CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Event-exposure CSV could not be read: {error}") from error
    return validate_event_exposure(data)

def validate_event_exposure(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete event-level exposure definitions."""
    missing = sorted(set(EXPOSURE_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Event-exposure data are missing required columns: {missing}")
    if data.empty:
        raise ValueError("Event-exposure data must contain at least one record.")
    out = data.loc[:, list(EXPOSURE_COLUMNS)].copy()
    required = [c for c in EXPOSURE_COLUMNS if c != "researcher_notes"]
    for c in required:
        out[c] = out[c].fillna("").astype(str).str.strip()
        if out[c].eq("").any():
            raise ValueError(f"Event-exposure field '{c}' must not be blank.")
    out["researcher_notes"] = out["researcher_notes"].fillna("").astype(str).str.strip()
    if out["event_id"].duplicated().any():
        raise ValueError("event_id values must be unique.")
    invalid = sorted(set(out["exposure_status"]) - set(EXPOSURE_STATUSES))
    if invalid:
        raise ValueError(f"Unknown exposure statuses: {invalid}")
    for c in ("exposure_start_date", "exposure_end_date"):
        parsed = pd.to_datetime(out[c], format="%Y-%m-%d", errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"{c} must use complete ISO dates in YYYY-MM-DD format.")
        out[c] = parsed
    if (out["exposure_end_date"] < out["exposure_start_date"]).any():
        raise ValueError("exposure_end_date must not be earlier than exposure_start_date.")
    return out

def audit_event_exposure_definitions(data: pd.DataFrame, instrument_version: str) -> dict[str, pd.DataFrame | str]:
    """Summarise exposure-definition completeness and unresolved prompts."""
    validated = validate_event_exposure(data)
    version = str(instrument_version).strip()
    selected = validated[validated["instrument_version"].eq(version)].copy()
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    rows, prompts = [], []
    for row in selected.to_dict(orient="records"):
        event_prompts = []
        if row["exposure_status"] in {"not_assessed", "mixed_or_unknown"}:
            event_prompts.append("Institution-level exposure is unresolved.")
        if row["intensity_definition"].lower() in {"none", "not_defined", "unknown"}:
            event_prompts.append("Exposure intensity is not defined.")
        if row["lag_definition"].lower() in {"none", "not_defined", "unknown"}:
            event_prompts.append("Exposure lag is not defined.")
        if row["comparator_definition"].lower() in {"none", "not_defined", "unknown"}:
            event_prompts.append("Comparator definition is not documented.")
        rows.append({"event_id": row["event_id"], "instrument_version": row["instrument_version"], "exposure_scope": row["exposure_scope"], "exposure_status": row["exposure_status"], "exposure_start_date": row["exposure_start_date"].date().isoformat(), "exposure_end_date": row["exposure_end_date"].date().isoformat(), "intensity_defined": row["intensity_definition"].lower() not in {"none", "not_defined", "unknown"}, "lag_defined": row["lag_definition"].lower() not in {"none", "not_defined", "unknown"}, "comparator_defined": row["comparator_definition"].lower() not in {"none", "not_defined", "unknown"}, "documentation_prompt_count": len(event_prompts)})
        prompts.extend({"event_id": row["event_id"], "prompt_type": "exposure_definition_prompt", "prompt": p} for p in event_prompts)
    questions = pd.DataFrame([
        {"research_question_candidate": "Which institutions were actually exposed to the registered event, and how was exposure verified?", "required_future_evidence": "Institution-level exposure records and source verification"},
        {"research_question_candidate": "What intensity, duration, and lag definitions are justified before any outcome comparison?", "required_future_evidence": "Preregistered exposure and lag specification"},
        {"research_question_candidate": "What is the defensible non-exposed or alternative-exposure comparator?", "required_future_evidence": "Sampling and comparison-design rationale"},
    ])
    interpretation = ("Exposure-definition readiness evidence only. Event registration is not institution-level exposure. "
                      "The audit does not infer treatment, dose, lag, comparator validity, policy effects, or causality. "
                      "Prompts are not approval decisions, exclusions, rankings, or effect estimates.")
    return {"event_exposure_summary": pd.DataFrame(rows), "exposure_definition_prompts": pd.DataFrame(prompts), "research_question_candidates": questions, "interpretation": interpretation}
