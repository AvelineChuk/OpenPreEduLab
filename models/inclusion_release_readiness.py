"""Release-package readiness audits for inclusive education research.

The workflow records release-preparation evidence. It does not publish files,
approve a release, inspect restricted artefacts, or verify research findings.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


RELEASE_COLUMNS: Final[tuple[str, ...]] = (
    "release_record_id",
    "claim_inventory_version",
    "reporting_plan_id",
    "execution_record_id",
    "instrument_version",
    "package_version",
    "release_scope",
    "file_manifest_reference",
    "checksum_manifest_reference",
    "documentation_index_reference",
    "license_status",
    "citation_metadata_status",
    "privacy_review_status",
    "accessibility_review_status",
    "claim_traceability_review_status",
    "ai_disclosure_status",
    "limitations_included",
    "synthetic_data_label_status",
    "release_channel",
    "embargo_status",
    "independent_review_status",
    "release_status",
    "researcher_notes",
)
RELEASE_SCOPES: Final[tuple[str, ...]] = (
    "aggregate_research_outputs_only",
    "documentation_only",
    "internal_review_only",
)
REVIEW_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "pending",
    "documented_pending_independent_review",
    "reviewed_no_release_approval",
)
BINARY_DOCUMENTATION_STATUSES: Final[tuple[str, ...]] = (
    "not_documented",
    "documented_pending_review",
    "reviewed_no_quality_endorsement",
    "not_applicable",
)
RELEASE_STATUSES: Final[tuple[str, ...]] = (
    "draft",
    "review_pending",
    "release_candidate_not_approved",
    "archived_internal",
)


def create_release_readiness_template() -> pd.DataFrame:
    """Return a blank non-identifying release-readiness schema."""
    return pd.DataFrame(
        [{column: "" for column in RELEASE_COLUMNS}],
        columns=RELEASE_COLUMNS,
    )


def load_release_readiness_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 release-readiness CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Release-readiness CSV could not be read: {error}") from error
    return validate_release_readiness(data)


def validate_release_readiness(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, non-identifying release-package declarations."""
    missing = sorted(set(RELEASE_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Release readiness record is missing required columns: {missing}")
    if data.empty:
        raise ValueError("Release readiness record must contain at least one record.")
    validated = data.loc[:, list(RELEASE_COLUMNS)].copy()
    required = [column for column in RELEASE_COLUMNS if column != "researcher_notes"]
    for column in required:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Release-readiness field '{column}' must not be blank.")
    validated["researcher_notes"] = (
        validated["researcher_notes"].fillna("").astype(str).str.strip()
    )
    if validated["release_record_id"].duplicated().any():
        raise ValueError("release_record_id values must be unique.")
    allowed = {
        "release_scope": RELEASE_SCOPES,
        "privacy_review_status": REVIEW_STATUSES,
        "accessibility_review_status": REVIEW_STATUSES,
        "claim_traceability_review_status": REVIEW_STATUSES,
        "independent_review_status": REVIEW_STATUSES,
        "license_status": BINARY_DOCUMENTATION_STATUSES,
        "citation_metadata_status": BINARY_DOCUMENTATION_STATUSES,
        "ai_disclosure_status": BINARY_DOCUMENTATION_STATUSES,
        "limitations_included": BINARY_DOCUMENTATION_STATUSES,
        "synthetic_data_label_status": BINARY_DOCUMENTATION_STATUSES,
        "release_status": RELEASE_STATUSES,
    }
    for column, options in allowed.items():
        invalid = sorted(set(validated[column]) - set(options))
        if invalid:
            raise ValueError(f"Unknown {column} values: {invalid}")
    return validated


def audit_release_readiness(
    data: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Summarise release records and unresolved documentation prompts."""
    selected = validate_release_readiness(data)
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
    reference_prompts = {
        "claim_inventory_version": "Claim inventory version is unresolved.",
        "package_version": "Release package version is unresolved.",
        "file_manifest_reference": "File manifest reference is unresolved.",
        "checksum_manifest_reference": "Checksum manifest reference is unresolved.",
        "documentation_index_reference": "Documentation index reference is unresolved.",
        "release_channel": "Intended release channel is unresolved.",
        "embargo_status": "Embargo or timing status is unresolved.",
    }
    summaries: list[dict[str, object]] = []
    prompts: list[dict[str, str]] = []
    for row in selected.to_dict(orient="records"):
        current = [
            message
            for field, message in reference_prompts.items()
            if str(row[field]).lower() in unresolved
        ]
        for field, label in (
            ("license_status", "License"),
            ("citation_metadata_status", "Citation metadata"),
            ("ai_disclosure_status", "AI disclosure"),
            ("limitations_included", "Limitations statement"),
            ("synthetic_data_label_status", "Synthetic-data label"),
        ):
            if row[field] == "not_documented":
                current.append(f"{label} is not documented.")
        for field, label in (
            ("privacy_review_status", "Privacy review"),
            ("accessibility_review_status", "Accessibility review"),
            ("claim_traceability_review_status", "Claim-traceability review"),
            ("independent_review_status", "Independent release review"),
        ):
            if row[field] != "reviewed_no_release_approval":
                current.append(f"{label} remains incomplete.")
        summaries.append(
            {
                "release_record_id": row["release_record_id"],
                "instrument_version": row["instrument_version"],
                "package_version": row["package_version"],
                "release_scope": row["release_scope"],
                "privacy_review_status": row["privacy_review_status"],
                "accessibility_review_status": row["accessibility_review_status"],
                "claim_traceability_review_status": row[
                    "claim_traceability_review_status"
                ],
                "independent_review_status": row["independent_review_status"],
                "release_status": row["release_status"],
                "file_manifest_documented": str(
                    row["file_manifest_reference"]
                ).lower()
                not in unresolved,
                "checksum_manifest_documented": str(
                    row["checksum_manifest_reference"]
                ).lower()
                not in unresolved,
                "documentation_index_documented": str(
                    row["documentation_index_reference"]
                ).lower()
                not in unresolved,
                "synthetic_label_documented": row[
                    "synthetic_data_label_status"
                ]
                != "not_documented",
                "documentation_prompt_count": len(current),
            }
        )
        prompts.extend(
            {
                "release_record_id": row["release_record_id"],
                "prompt_type": "release_readiness_prompt",
                "prompt": prompt,
            }
            for prompt in current
        )
    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Can every proposed public artefact be located, checksummed, "
                    "licensed, cited, and connected to the documentation index?"
                ),
                "required_future_evidence": (
                    "Versioned file, checksum, license, citation, and document manifests"
                ),
            },
            {
                "research_question_candidate": (
                    "Have privacy, accessibility, claim traceability, limitations, "
                    "synthetic-data labels, and AI disclosures been reviewed?"
                ),
                "required_future_evidence": (
                    "Independent pre-release review records"
                ),
            },
            {
                "research_question_candidate": (
                    "Does the release candidate exclude restricted, identifying, "
                    "unreviewed, and institution-level materials?"
                ),
                "required_future_evidence": (
                    "Governed aggregate release inventory and disclosure audit"
                ),
            },
        ]
    )
    interpretation = (
        "Release-package readiness evidence only. A complete record does not inspect "
        "files, verify checksums, licenses, accessibility, privacy, findings, or claim "
        "validity and does not approve or publish a release. The workflow exposes no "
        "file paths, result values, credentials, or restricted notes and produces no "
        "estimate, significance label, policy effect, causal conclusion, or decision."
    )
    return {
        "release_readiness_summary": pd.DataFrame(summaries),
        "release_readiness_prompts": pd.DataFrame(prompts),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
