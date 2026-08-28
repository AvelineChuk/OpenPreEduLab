"""Results-reporting and claim-boundary audits for inclusive policy research.

The workflow records a reporting plan without receiving result values. It does
not verify findings, judge significance, or authorise causal language.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


REPORTING_COLUMNS: Final[tuple[str, ...]] = (
    "reporting_plan_id",
    "execution_record_id",
    "specification_id",
    "instrument_version",
    "primary_analysis_label",
    "secondary_analysis_policy",
    "outcome_reporting_scope",
    "null_uncertain_result_policy",
    "uncertainty_reporting_policy",
    "multiple_testing_reporting",
    "specification_deviation_disclosure",
    "subgroup_reporting_policy",
    "small_cell_suppression",
    "institution_identifier_policy",
    "visualization_scale_disclosure",
    "support_gap_language",
    "causal_language_status",
    "ai_assistance_status",
    "ai_verification_plan",
    "data_limitations_statement",
    "conflict_of_interest_statement",
    "review_status",
    "researcher_notes",
)

SUPPORT_GAP_LANGUAGE_OPTIONS: Final[tuple[str, ...]] = (
    "diagnostic_indicator_only",
    "descriptive_difference_only",
    "not_applicable",
    "not_defined",
)
CAUSAL_LANGUAGE_STATUSES: Final[tuple[str, ...]] = (
    "descriptive_only",
    "association_only",
    "causal_language_withheld",
    "pending_independent_design_review",
)
AI_ASSISTANCE_STATUSES: Final[tuple[str, ...]] = (
    "not_used",
    "planned_bounded_assistance",
    "draft_generated_pending_human_review",
    "human_review_documented",
)
REPORTING_REVIEW_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "draft",
    "review_pending",
    "reviewed_no_result_endorsement",
)


def create_results_reporting_template() -> pd.DataFrame:
    """Return a blank non-identifying results-reporting plan schema."""
    return pd.DataFrame(
        [{column: "" for column in REPORTING_COLUMNS}],
        columns=REPORTING_COLUMNS,
    )


def load_results_reporting_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 results-reporting plan CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Results-reporting CSV could not be read: {error}") from error
    return validate_results_reporting(data)


def validate_results_reporting(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, non-identifying reporting-plan declarations."""
    missing = sorted(set(REPORTING_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Results reporting plan is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Results reporting plan must contain at least one record.")
    validated = data.loc[:, list(REPORTING_COLUMNS)].copy()
    required = [column for column in REPORTING_COLUMNS if column != "researcher_notes"]
    for column in required:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Results-reporting field '{column}' must not be blank.")
    validated["researcher_notes"] = (
        validated["researcher_notes"].fillna("").astype(str).str.strip()
    )
    if validated["reporting_plan_id"].duplicated().any():
        raise ValueError("reporting_plan_id values must be unique.")
    allowed = {
        "support_gap_language": SUPPORT_GAP_LANGUAGE_OPTIONS,
        "causal_language_status": CAUSAL_LANGUAGE_STATUSES,
        "ai_assistance_status": AI_ASSISTANCE_STATUSES,
        "review_status": REPORTING_REVIEW_STATUSES,
    }
    for column, options in allowed.items():
        invalid = sorted(set(validated[column]) - set(options))
        if invalid:
            raise ValueError(f"Unknown {column} values: {invalid}")
    return validated


def audit_results_reporting(
    data: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Summarise reporting plans and unresolved claim-boundary prompts."""
    selected = validate_results_reporting(data)
    selected = selected[
        selected["instrument_version"].eq(str(instrument_version).strip())
    ]
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")

    unresolved = {
        "none",
        "not_assessed",
        "not_defined",
        "not_recorded",
        "unknown",
        "pending",
    }
    prompt_fields = {
        "primary_analysis_label": "Primary analysis label is unresolved.",
        "secondary_analysis_policy": "Secondary and exploratory analysis policy is unresolved.",
        "outcome_reporting_scope": "Outcome reporting scope is unresolved.",
        "null_uncertain_result_policy": "Null and uncertain result reporting policy is unresolved.",
        "uncertainty_reporting_policy": "Uncertainty reporting policy is unresolved.",
        "multiple_testing_reporting": "Multiple-testing reporting is unresolved.",
        "specification_deviation_disclosure": "Specification-deviation disclosure is unresolved.",
        "subgroup_reporting_policy": "Subgroup reporting policy is unresolved.",
        "small_cell_suppression": "Small-cell suppression rule is unresolved.",
        "institution_identifier_policy": "Institution identifier policy is unresolved.",
        "visualization_scale_disclosure": "Visualization scale disclosure is unresolved.",
        "ai_verification_plan": "Human verification plan for AI assistance is unresolved.",
        "data_limitations_statement": "Data limitations statement is unresolved.",
        "conflict_of_interest_statement": "Conflict-of-interest statement is unresolved.",
    }
    summaries: list[dict[str, object]] = []
    prompts: list[dict[str, str]] = []
    for row in selected.to_dict(orient="records"):
        current = [
            message
            for field, message in prompt_fields.items()
            if str(row[field]).lower() in unresolved
        ]
        if row["support_gap_language"] == "not_defined":
            current.append(
                "Support Gap language must remain descriptive or diagnostic, not causal."
            )
        if row["causal_language_status"] == "pending_independent_design_review":
            current.append(
                "Causal language remains withheld pending independent design review."
            )
        if row["ai_assistance_status"] in {
            "planned_bounded_assistance",
            "draft_generated_pending_human_review",
        } and str(row["ai_verification_plan"]).lower() in unresolved:
            current.append(
                "Planned AI assistance requires an explicit human verification record."
            )
        if row["review_status"] in {"not_started", "draft", "review_pending"}:
            current.append("Reporting-plan review remains incomplete.")
        summaries.append(
            {
                "reporting_plan_id": row["reporting_plan_id"],
                "execution_record_id": row["execution_record_id"],
                "specification_id": row["specification_id"],
                "instrument_version": row["instrument_version"],
                "support_gap_language": row["support_gap_language"],
                "causal_language_status": row["causal_language_status"],
                "ai_assistance_status": row["ai_assistance_status"],
                "review_status": row["review_status"],
                "primary_analysis_documented": str(
                    row["primary_analysis_label"]
                ).lower()
                not in unresolved,
                "uncertainty_reporting_documented": str(
                    row["uncertainty_reporting_policy"]
                ).lower()
                not in unresolved,
                "privacy_suppression_documented": str(
                    row["small_cell_suppression"]
                ).lower()
                not in unresolved,
                "limitations_documented": str(
                    row["data_limitations_statement"]
                ).lower()
                not in unresolved,
                "documentation_prompt_count": len(current),
            }
        )
        prompts.extend(
            {
                "reporting_plan_id": row["reporting_plan_id"],
                "prompt_type": "results_reporting_prompt",
                "prompt": prompt,
            }
            for prompt in current
        )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Will primary, secondary, null, and uncertain results be reported "
                    "without selective omission?"
                ),
                "required_future_evidence": (
                    "Preregistered reporting scope and complete result inventory"
                ),
            },
            {
                "research_question_candidate": (
                    "How will uncertainty, multiplicity, deviations, and visualization "
                    "scales be disclosed?"
                ),
                "required_future_evidence": (
                    "Reviewed tables, figures, uncertainty notes, and deviation record"
                ),
            },
            {
                "research_question_candidate": (
                    "Do privacy, Support Gap, causal-language, and AI-review boundaries "
                    "remain visible in every public output?"
                ),
                "required_future_evidence": (
                    "Disclosure review, suppression audit, and human sign-off"
                ),
            },
        ]
    )
    interpretation = (
        "Results-reporting and claim-boundary readiness evidence only. A complete plan "
        "does not verify a result, prevent selective reporting, establish statistical "
        "or practical significance, validate Support Gap, endorse AI text, identify a "
        "policy effect, or establish causality. The workflow receives no result values "
        "and produces no estimate, p-value, significance label, ranking, approval, or "
        "decision."
    )
    return {
        "results_reporting_summary": pd.DataFrame(summaries),
        "results_reporting_prompts": pd.DataFrame(prompts),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
