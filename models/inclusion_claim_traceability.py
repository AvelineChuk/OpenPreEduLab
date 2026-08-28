"""Claim-evidence traceability readiness audits for inclusive research.

The workflow links planned claim records to documented evidence references. It
does not inspect result values, verify truth, or authorise causal conclusions.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


TRACEABILITY_COLUMNS: Final[tuple[str, ...]] = (
    "claim_record_id",
    "reporting_plan_id",
    "execution_record_id",
    "specification_id",
    "instrument_version",
    "claim_label",
    "claim_scope",
    "evidence_output_reference",
    "evidence_type",
    "population_scope",
    "time_scope",
    "uncertainty_reference",
    "limitation_reference",
    "alternative_explanation_record",
    "support_gap_interpretation_status",
    "source_provenance_status",
    "ai_origin_status",
    "human_review_status",
    "public_disclosure_status",
    "researcher_notes",
)
CLAIM_SCOPES: Final[tuple[str, ...]] = (
    "descriptive_statement",
    "association_candidate",
    "mechanism_hypothesis",
    "research_question_candidate",
    "causal_claim_withheld",
)
EVIDENCE_TYPES: Final[tuple[str, ...]] = (
    "descriptive_summary",
    "uncertainty_summary",
    "sensitivity_output",
    "qualitative_context",
    "literature_context",
    "no_empirical_evidence",
)
SUPPORT_GAP_STATUSES: Final[tuple[str, ...]] = (
    "diagnostic_indicator_only",
    "descriptive_difference_only",
    "not_applicable",
    "not_defined",
)
PROVENANCE_STATUSES: Final[tuple[str, ...]] = (
    "documented",
    "pending_review",
    "not_documented",
)
AI_ORIGIN_STATUSES: Final[tuple[str, ...]] = (
    "human_authored",
    "ai_assisted_pending_review",
    "ai_assisted_human_reviewed",
)
HUMAN_REVIEW_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "review_pending",
    "reviewed_no_truth_endorsement",
)
DISCLOSURE_STATUSES: Final[tuple[str, ...]] = (
    "not_for_public_disclosure",
    "aggregate_release_pending_review",
    "aggregate_release_reviewed",
)


def create_claim_traceability_template() -> pd.DataFrame:
    """Return a blank non-identifying claim-traceability schema."""
    return pd.DataFrame(
        [{column: "" for column in TRACEABILITY_COLUMNS}],
        columns=TRACEABILITY_COLUMNS,
    )


def load_claim_traceability_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 claim-traceability CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Claim-traceability CSV could not be read: {error}") from error
    return validate_claim_traceability(data)


def validate_claim_traceability(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, non-identifying claim-evidence declarations."""
    missing = sorted(set(TRACEABILITY_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Claim traceability record is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Claim traceability record must contain at least one record.")
    validated = data.loc[:, list(TRACEABILITY_COLUMNS)].copy()
    required = [
        column for column in TRACEABILITY_COLUMNS if column != "researcher_notes"
    ]
    for column in required:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Claim-traceability field '{column}' must not be blank.")
    validated["researcher_notes"] = (
        validated["researcher_notes"].fillna("").astype(str).str.strip()
    )
    if validated["claim_record_id"].duplicated().any():
        raise ValueError("claim_record_id values must be unique.")
    allowed = {
        "claim_scope": CLAIM_SCOPES,
        "evidence_type": EVIDENCE_TYPES,
        "support_gap_interpretation_status": SUPPORT_GAP_STATUSES,
        "source_provenance_status": PROVENANCE_STATUSES,
        "ai_origin_status": AI_ORIGIN_STATUSES,
        "human_review_status": HUMAN_REVIEW_STATUSES,
        "public_disclosure_status": DISCLOSURE_STATUSES,
    }
    for column, options in allowed.items():
        invalid = sorted(set(validated[column]) - set(options))
        if invalid:
            raise ValueError(f"Unknown {column} values: {invalid}")
    return validated


def audit_claim_traceability(
    data: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Summarise traceability records and unresolved evidence-link prompts."""
    selected = validate_claim_traceability(data)
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
        "evidence_output_reference": "Evidence output reference is unresolved.",
        "population_scope": "Population scope is unresolved.",
        "time_scope": "Time scope is unresolved.",
        "uncertainty_reference": "Uncertainty reference is unresolved.",
        "limitation_reference": "Limitation reference is unresolved.",
        "alternative_explanation_record": "Alternative-explanation record is unresolved.",
    }
    summaries: list[dict[str, object]] = []
    prompts: list[dict[str, str]] = []
    for row in selected.to_dict(orient="records"):
        current = [
            message
            for field, message in prompt_fields.items()
            if str(row[field]).lower() in unresolved
        ]
        if row["evidence_type"] == "no_empirical_evidence":
            current.append(
                "No empirical evidence is linked; the record cannot support an empirical finding."
            )
        if row["support_gap_interpretation_status"] == "not_defined":
            current.append(
                "Support Gap interpretation must remain descriptive or diagnostic."
            )
        if row["source_provenance_status"] != "documented":
            current.append("Evidence-source provenance is not fully documented.")
        if row["ai_origin_status"] == "ai_assisted_pending_review":
            current.append("AI-assisted claim record remains pending human review.")
        if row["human_review_status"] != "reviewed_no_truth_endorsement":
            current.append("Human claim-boundary review remains incomplete.")
        if row["public_disclosure_status"] == "aggregate_release_pending_review":
            current.append("Aggregate public disclosure remains pending review.")
        summaries.append(
            {
                "claim_record_id": row["claim_record_id"],
                "reporting_plan_id": row["reporting_plan_id"],
                "execution_record_id": row["execution_record_id"],
                "specification_id": row["specification_id"],
                "instrument_version": row["instrument_version"],
                "claim_scope": row["claim_scope"],
                "evidence_type": row["evidence_type"],
                "support_gap_interpretation_status": row[
                    "support_gap_interpretation_status"
                ],
                "source_provenance_status": row["source_provenance_status"],
                "ai_origin_status": row["ai_origin_status"],
                "human_review_status": row["human_review_status"],
                "public_disclosure_status": row["public_disclosure_status"],
                "evidence_reference_documented": str(
                    row["evidence_output_reference"]
                ).lower()
                not in unresolved,
                "uncertainty_reference_documented": str(
                    row["uncertainty_reference"]
                ).lower()
                not in unresolved,
                "limitation_reference_documented": str(
                    row["limitation_reference"]
                ).lower()
                not in unresolved,
                "documentation_prompt_count": len(current),
            }
        )
        prompts.extend(
            {
                "claim_record_id": row["claim_record_id"],
                "prompt_type": "claim_traceability_prompt",
                "prompt": prompt,
            }
            for prompt in current
        )
    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Which documented output, population, time window, and uncertainty "
                    "record support each planned research statement?"
                ),
                "required_future_evidence": (
                    "Versioned claim inventory linked to reviewed aggregate outputs"
                ),
            },
            {
                "research_question_candidate": (
                    "Are alternative explanations and limitations traceable alongside "
                    "the evidence rather than added after interpretation?"
                ),
                "required_future_evidence": (
                    "Reviewed limitation and alternative-explanation register"
                ),
            },
            {
                "research_question_candidate": (
                    "Do AI-assisted and public-facing statements retain evidence, "
                    "privacy, Support Gap, and causal-language boundaries?"
                ),
                "required_future_evidence": (
                    "Human claim review and aggregate disclosure audit"
                ),
            },
        ]
    )
    interpretation = (
        "Claim-evidence traceability readiness evidence only. A documented link does "
        "not verify the evidence, truth, completeness, validity, practical importance, "
        "policy effect, or causality of a statement. The workflow reads no result "
        "values, reproduces no free-text claim in outputs, and produces no estimate, "
        "p-value, significance label, ranking, approval, or publication decision."
    )
    return {
        "claim_traceability_summary": pd.DataFrame(summaries),
        "claim_traceability_prompts": pd.DataFrame(prompts),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
