"""Analysis reproducibility readiness audits for inclusive policy research.

This workflow records artefacts needed to reproduce a future analysis. It does
not execute code, verify results, approve a specification, or authorise causal
language.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


REPRODUCIBILITY_COLUMNS: Final[tuple[str, ...]] = (
    "execution_record_id",
    "specification_id",
    "instrument_version",
    "data_snapshot_id",
    "data_snapshot_date",
    "data_checksum",
    "code_repository_reference",
    "code_commit",
    "environment_lock_reference",
    "software_environment",
    "random_seed_policy",
    "specification_lock_status",
    "deviation_log_reference",
    "execution_status",
    "quality_control_status",
    "output_storage_boundary",
    "output_disclosure_boundary",
    "review_status",
    "researcher_notes",
)
SPECIFICATION_LOCK_STATUSES: Final[tuple[str, ...]] = (
    "not_locked",
    "draft_lock",
    "locked_before_execution",
    "amended_with_deviation_log",
)
EXECUTION_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "dry_run_only",
    "execution_pending_review",
    "completed_not_interpreted",
)
QUALITY_CONTROL_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "planned",
    "documented_pending_review",
    "reviewed_no_method_approval",
)
REVIEW_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "draft",
    "review_pending",
    "reviewed_no_result_endorsement",
)


def create_analysis_reproducibility_template() -> pd.DataFrame:
    """Return a blank non-identifying analysis-reproducibility schema."""
    return pd.DataFrame(
        [{column: "" for column in REPRODUCIBILITY_COLUMNS}],
        columns=REPRODUCIBILITY_COLUMNS,
    )


def load_analysis_reproducibility_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 analysis-reproducibility CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Analysis-reproducibility CSV could not be read: {error}"
        ) from error
    return validate_analysis_reproducibility(data)


def validate_analysis_reproducibility(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, non-identifying reproducibility declarations."""
    missing = sorted(set(REPRODUCIBILITY_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(
            f"Analysis reproducibility record is missing required columns: {missing}"
        )
    if data.empty:
        raise ValueError(
            "Analysis reproducibility record must contain at least one record."
        )
    validated = data.loc[:, list(REPRODUCIBILITY_COLUMNS)].copy()
    required = [
        column for column in REPRODUCIBILITY_COLUMNS if column != "researcher_notes"
    ]
    for column in required:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(
                f"Analysis-reproducibility field '{column}' must not be blank."
            )
    validated["researcher_notes"] = (
        validated["researcher_notes"].fillna("").astype(str).str.strip()
    )
    if validated["execution_record_id"].duplicated().any():
        raise ValueError("execution_record_id values must be unique.")
    allowed = {
        "specification_lock_status": SPECIFICATION_LOCK_STATUSES,
        "execution_status": EXECUTION_STATUSES,
        "quality_control_status": QUALITY_CONTROL_STATUSES,
        "review_status": REVIEW_STATUSES,
    }
    for column, options in allowed.items():
        invalid = sorted(set(validated[column]) - set(options))
        if invalid:
            raise ValueError(f"Unknown {column} values: {invalid}")
    return validated


def audit_analysis_reproducibility(
    data: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Summarise reproducibility records and unresolved documentation prompts."""
    selected = validate_analysis_reproducibility(data)
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
        "data_snapshot_id": "Immutable data snapshot identifier is unresolved.",
        "data_snapshot_date": "Data snapshot date is unresolved.",
        "data_checksum": "Data checksum is unresolved.",
        "code_repository_reference": "Code repository reference is unresolved.",
        "code_commit": "Exact code commit is unresolved.",
        "environment_lock_reference": "Environment lock reference is unresolved.",
        "software_environment": "Software environment is unresolved.",
        "random_seed_policy": "Random-seed policy is unresolved.",
        "output_storage_boundary": "Output storage boundary is unresolved.",
        "output_disclosure_boundary": "Output disclosure boundary is unresolved.",
    }
    summaries: list[dict[str, object]] = []
    prompts: list[dict[str, str]] = []
    for row in selected.to_dict(orient="records"):
        current = [
            message
            for field, message in prompt_fields.items()
            if str(row[field]).lower() in unresolved
        ]
        if row["specification_lock_status"] in {"not_locked", "draft_lock"}:
            current.append(
                "Specification is not documented as locked before execution."
            )
        if (
            row["specification_lock_status"] == "amended_with_deviation_log"
            and str(row["deviation_log_reference"]).lower() in unresolved
        ):
            current.append(
                "Amended specification requires a traceable deviation log reference."
            )
        if row["quality_control_status"] in {"not_started", "planned"}:
            current.append(
                "Quality-control checks are not documented as completed and reviewed."
            )
        if row["review_status"] in {"not_started", "draft", "review_pending"}:
            current.append("Reproducibility record review remains incomplete.")
        summaries.append(
            {
                "execution_record_id": row["execution_record_id"],
                "specification_id": row["specification_id"],
                "instrument_version": row["instrument_version"],
                "specification_lock_status": row["specification_lock_status"],
                "execution_status": row["execution_status"],
                "quality_control_status": row["quality_control_status"],
                "review_status": row["review_status"],
                "data_snapshot_documented": str(row["data_snapshot_id"]).lower()
                not in unresolved,
                "data_checksum_documented": str(row["data_checksum"]).lower()
                not in unresolved,
                "code_commit_documented": str(row["code_commit"]).lower()
                not in unresolved,
                "environment_lock_documented": str(
                    row["environment_lock_reference"]
                ).lower()
                not in unresolved,
                "seed_policy_documented": str(row["random_seed_policy"]).lower()
                not in unresolved,
                "disclosure_boundary_documented": str(
                    row["output_disclosure_boundary"]
                ).lower()
                not in unresolved,
                "documentation_prompt_count": len(current),
            }
        )
        prompts.extend(
            {
                "execution_record_id": row["execution_record_id"],
                "prompt_type": "analysis_reproducibility_prompt",
                "prompt": prompt,
            }
            for prompt in current
        )
    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Can the analysis be reconstructed from a fixed data snapshot, "
                    "exact code commit, and locked environment?"
                ),
                "required_future_evidence": (
                    "Checksummed data snapshot, versioned code, and environment lock"
                ),
            },
            {
                "research_question_candidate": (
                    "Were deviations from the preregistered specification recorded "
                    "before results were interpreted?"
                ),
                "required_future_evidence": (
                    "Timestamped specification lock and deviation log"
                ),
            },
            {
                "research_question_candidate": (
                    "Which aggregate outputs may be stored and disclosed without "
                    "exposing institution-level records?"
                ),
                "required_future_evidence": (
                    "Governed storage, disclosure, and independent review record"
                ),
            },
        ]
    )
    interpretation = (
        "Analysis-reproducibility readiness evidence only. A complete record does not "
        "verify the data, code, estimator, results, identification strategy, policy "
        "effects, or causality. The workflow executes no code, opens no repository or "
        "data snapshot, and produces no coefficient, effect estimate, p-value, "
        "significance label, approval, ranking, or decision."
    )
    return {
        "analysis_reproducibility_summary": pd.DataFrame(summaries),
        "analysis_reproducibility_prompts": pd.DataFrame(prompts),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
