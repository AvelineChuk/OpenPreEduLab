"""Readiness audits for preregistered longitudinal analysis plans.

The audit checks whether a researcher has documented the comparison, estimand,
missing-data, weighting, uncertainty, and dependence decisions needed before a
longitudinal model is run. It does not select methods, run a model, or validate
causal assumptions.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


LONGITUDINAL_PLAN_COLUMNS: Final[tuple[str, ...]] = (
    "analysis_plan_id",
    "instrument_version",
    "unit_of_analysis",
    "target_population_scope",
    "round_comparison",
    "change_definition",
    "estimand_scope",
    "missing_data_strategy",
    "weighting_strategy",
    "uncertainty_method",
    "dependence_structure",
    "measurement_comparability_basis",
    "attrition_evidence_reference",
    "metadata_evidence_reference",
    "causal_language_allowed",
    "preregistration_status",
    "researcher_notes",
)
REQUIRED_TEXT_COLUMNS: Final[tuple[str, ...]] = tuple(
    column for column in LONGITUDINAL_PLAN_COLUMNS if column != "researcher_notes"
)
ALLOWED_YES_NO: Final[tuple[str, ...]] = ("yes", "no", "not_applicable")
ALLOWED_PREREGISTRATION: Final[tuple[str, ...]] = (
    "not_started",
    "draft",
    "review_pending",
    "registered",
)
ALLOWED_CHANGE_DEFINITIONS: Final[tuple[str, ...]] = (
    "later_minus_earlier",
    "earlier_minus_later",
    "round_specific_contrast",
    "not_yet_defined",
)


def create_longitudinal_plan_template() -> pd.DataFrame:
    """Return a blank longitudinal analysis-plan schema."""
    return pd.DataFrame(
        [{column: "" for column in LONGITUDINAL_PLAN_COLUMNS}],
        columns=LONGITUDINAL_PLAN_COLUMNS,
    )


def load_longitudinal_plan_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 longitudinal plan CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Longitudinal plan CSV could not be read: {error}") from error
    return validate_longitudinal_plan(data)


def validate_longitudinal_plan(data: pd.DataFrame) -> pd.DataFrame:
    """Validate one or more complete, non-identifying analysis-plan records."""
    missing = sorted(set(LONGITUDINAL_PLAN_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Longitudinal plan is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Longitudinal plan must contain at least one record.")
    validated = data.loc[:, list(LONGITUDINAL_PLAN_COLUMNS)].copy()
    for column in REQUIRED_TEXT_COLUMNS:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Longitudinal plan field '{column}' must not be blank.")
    validated["researcher_notes"] = validated["researcher_notes"].fillna("").astype(str).str.strip()
    if validated["analysis_plan_id"].duplicated().any():
        raise ValueError("analysis_plan_id values must be unique.")
    for column in ("causal_language_allowed",):
        invalid = sorted(set(validated[column]) - set(ALLOWED_YES_NO))
        if invalid:
            raise ValueError(f"Unknown values in {column}: {invalid}")
    invalid_status = sorted(set(validated["preregistration_status"]) - set(ALLOWED_PREREGISTRATION))
    if invalid_status:
        raise ValueError(f"Unknown preregistration statuses: {invalid_status}")
    invalid_changes = sorted(set(validated["change_definition"]) - set(ALLOWED_CHANGE_DEFINITIONS))
    if invalid_changes:
        raise ValueError(f"Unknown change definitions: {invalid_changes}")
    return validated


def audit_longitudinal_plan(data: pd.DataFrame) -> dict[str, pd.DataFrame | str]:
    """Summarise declared longitudinal plans and identify documentation prompts."""
    validated = validate_longitudinal_plan(data)
    overview_rows = []
    risk_rows = []
    for row in validated.to_dict(orient="records"):
        plan_id = row["analysis_plan_id"]
        prompts: list[str] = []
        if row["change_definition"] == "not_yet_defined":
            prompts.append("Change direction is not yet defined.")
        if row["measurement_comparability_basis"].lower() in {"", "none", "not_assessed"}:
            prompts.append("Longitudinal measurement-comparability basis is not documented.")
        if row["missing_data_strategy"].lower() in {"none", "not_assessed", "not_yet_defined"}:
            prompts.append("Missing-data strategy is not documented.")
        if row["uncertainty_method"].lower() in {"none", "not_assessed", "not_yet_defined"}:
            prompts.append("Uncertainty method is not documented.")
        if row["causal_language_allowed"] == "yes":
            prompts.append("Causal language is enabled and requires an explicit identification design.")
        overview_rows.append(
            {
                "analysis_plan_id": plan_id,
                "instrument_version": row["instrument_version"],
                "unit_of_analysis": row["unit_of_analysis"],
                "round_comparison": row["round_comparison"],
                "change_definition": row["change_definition"],
                "estimand_scope": row["estimand_scope"],
                "missing_data_strategy": row["missing_data_strategy"],
                "weighting_strategy": row["weighting_strategy"],
                "uncertainty_method": row["uncertainty_method"],
                "dependence_structure": row["dependence_structure"],
                "measurement_comparability_basis": row["measurement_comparability_basis"],
                "causal_language_allowed": row["causal_language_allowed"],
                "preregistration_status": row["preregistration_status"],
                "documentation_prompt_count": len(prompts),
            }
        )
        for prompt in prompts:
            risk_rows.append(
                {
                    "analysis_plan_id": plan_id,
                    "prompt_type": "method_documentation_prompt",
                    "prompt": prompt,
                }
            )
    questions = pd.DataFrame(
        [
            {"research_question_candidate": "What is the target estimand and population for the planned longitudinal comparison?", "required_future_evidence": "Preregistered estimand, unit, and population definition"},
            {"research_question_candidate": "Which missing-data, attrition, weighting, and dependence assumptions are justified by the design?", "required_future_evidence": "Design records, diagnostics, and sensitivity analysis"},
            {"research_question_candidate": "What evidence supports interpreting the planned score contrast across rounds?", "required_future_evidence": "Longitudinal comparability and measurement review"},
        ]
    )
    interpretation = (
        "Analysis-plan readiness evidence only. The audit checks documentation, not method quality, "
        "identification, validity, power, or causal assumptions. Prompts are not error scores, "
        "approval decisions, or reasons to exclude data. No model is fitted and no longitudinal "
        "effect, improvement, deterioration, policy effect, or causal conclusion is produced."
    )
    return {
        "longitudinal_plan_summary": pd.DataFrame(overview_rows),
        "method_documentation_prompts": pd.DataFrame(risk_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
