"""Cognitive-interview and item-revision audit utilities.

The workflow records human-generated evidence about how inclusion items are
understood and a separate, versioned research-team decision log. It does not
simulate participants, infer item validity, or make automatic revision choices.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS


INTERVIEW_COLUMNS: Final[tuple[str, ...]] = (
    "interview_id",
    "participant_role",
    "interview_round",
    "instrument_version",
    "score_column",
    "dimension",
    "item",
    "issue_type",
    "issue_observed",
    "evidence_note",
    "suggested_revision",
    "minority_or_distinct_view",
    "safeguarding_flag",
    "accessibility_flag",
)

ISSUE_TYPES: Final[tuple[str, ...]] = (
    "no_issue",
    "comprehension",
    "retrieval",
    "judgment",
    "response_mapping",
    "terminology",
    "cultural_context",
    "accessibility",
    "safeguarding",
)

YES_NO: Final[tuple[str, ...]] = ("yes", "no")

REVISION_COLUMNS: Final[tuple[str, ...]] = (
    "decision_id",
    "source_instrument_version",
    "target_instrument_version",
    "decision_round",
    "score_column",
    "dimension",
    "item",
    "decision",
    "target_score_column",
    "target_dimension",
    "revised_item_wording",
    "decision_rationale",
    "minority_view_record",
    "safeguarding_review",
    "equity_accessibility_review",
    "responsible_researcher_id",
    "decision_date",
)

REVISION_DECISIONS: Final[tuple[str, ...]] = (
    "retain",
    "revise",
    "move",
    "split",
    "remove",
)

REVIEW_STATUSES: Final[tuple[str, ...]] = ("completed", "pending", "not_required")


def _item_mapping() -> dict[str, tuple[str, str]]:
    return {
        item: (score_column, DIMENSION_LABELS[score_column])
        for score_column, items in DIMENSION_ITEMS.items()
        for item in items
    }


def create_cognitive_interview_template() -> pd.DataFrame:
    """Return one blank cognitive-interview row per current item."""
    rows = []
    for item, (score_column, dimension) in _item_mapping().items():
        rows.append(
            {
                "interview_id": "",
                "participant_role": "",
                "interview_round": "",
                "instrument_version": "",
                "score_column": score_column,
                "dimension": dimension,
                "item": item,
                "issue_type": "",
                "issue_observed": "",
                "evidence_note": "",
                "suggested_revision": "",
                "minority_or_distinct_view": "",
                "safeguarding_flag": "",
                "accessibility_flag": "",
            }
        )
    return pd.DataFrame(rows, columns=INTERVIEW_COLUMNS)


def load_cognitive_interview_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 cognitive-interview record CSV."""
    try:
        records = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Cognitive-interview CSV could not be read: {error}") from error
    return validate_cognitive_interview_records(records)


def validate_cognitive_interview_records(records: pd.DataFrame) -> pd.DataFrame:
    """Validate human-entered interview observations without requiring all items."""
    missing = sorted(set(INTERVIEW_COLUMNS) - set(records.columns))
    if missing:
        raise ValueError(f"Cognitive-interview data are missing required columns: {missing}")
    if records.empty:
        raise ValueError("Cognitive-interview data must contain at least one observation.")
    validated = records.loc[:, list(INTERVIEW_COLUMNS)].copy()
    required_text = (
        "interview_id",
        "participant_role",
        "instrument_version",
        "score_column",
        "dimension",
        "item",
        "issue_type",
        "issue_observed",
        "minority_or_distinct_view",
        "safeguarding_flag",
        "accessibility_flag",
    )
    for column in required_text:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Cognitive-interview field '{column}' must not be blank.")
    for column in ("evidence_note", "suggested_revision"):
        validated[column] = validated[column].fillna("").astype(str).str.strip()

    validated["interview_round"] = pd.to_numeric(
        validated["interview_round"], errors="coerce"
    )
    rounds = validated["interview_round"].to_numpy(dtype=float)
    if not np.isfinite(rounds).all() or not validated["interview_round"].ge(1).all():
        raise ValueError("interview_round must contain positive integers.")
    if not validated["interview_round"].mod(1).eq(0).all():
        raise ValueError("interview_round must contain positive integers.")
    validated["interview_round"] = validated["interview_round"].astype(int)

    invalid_issues = sorted(set(validated["issue_type"]) - set(ISSUE_TYPES))
    if invalid_issues:
        raise ValueError(f"Unknown cognitive-interview issue types: {invalid_issues}")
    for column in (
        "issue_observed",
        "minority_or_distinct_view",
        "safeguarding_flag",
        "accessibility_flag",
    ):
        invalid = sorted(set(validated[column]) - set(YES_NO))
        if invalid:
            raise ValueError(f"{column} must use yes or no; invalid values: {invalid}")

    mapping = _item_mapping()
    unexpected = sorted(set(validated["item"]) - set(ITEM_COLUMNS))
    if unexpected:
        raise ValueError(f"Unknown inclusion items in cognitive-interview data: {unexpected}")
    for row in validated.itertuples(index=False):
        expected_score, expected_dimension = mapping[row.item]
        if row.score_column != expected_score or row.dimension != expected_dimension:
            raise ValueError(f"Item-to-dimension mapping is invalid for '{row.item}'.")
        if row.issue_observed == "no" and row.issue_type != "no_issue":
            raise ValueError("issue_observed=no requires issue_type=no_issue.")
        if row.issue_observed == "yes" and row.issue_type == "no_issue":
            raise ValueError("issue_observed=yes requires a substantive issue_type.")
        if row.issue_observed == "yes" and not row.evidence_note:
            raise ValueError("Observed issues require a non-identifying evidence_note.")

    if validated.duplicated(["interview_id", "interview_round", "item", "issue_type"]).any():
        raise ValueError("Duplicate interview-round, item, and issue_type observations are not allowed.")
    consistency = validated.groupby(["interview_id", "interview_round"]).agg(
        participant_roles=("participant_role", "nunique"),
        instrument_versions=("instrument_version", "nunique"),
    )
    if not consistency["participant_roles"].eq(1).all():
        raise ValueError("Each interview_id and round must use one participant_role.")
    if not consistency["instrument_versions"].eq(1).all():
        raise ValueError("Each interview_id and round must use one instrument_version.")
    return validated


def summarize_cognitive_interviews(records: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Summarize issue counts without exposing interview IDs or free text."""
    validated = validate_cognitive_interview_records(records)
    observed = validated[validated["issue_observed"].eq("yes")]
    issue_summary = (
        observed.groupby(["score_column", "dimension", "item", "issue_type"], sort=False)
        .agg(
            observation_count=("issue_type", "size"),
            interview_count=("interview_id", "nunique"),
            safeguarding_flag_count=("safeguarding_flag", lambda values: int(values.eq("yes").sum())),
            accessibility_flag_count=("accessibility_flag", lambda values: int(values.eq("yes").sum())),
        )
        .reset_index()
    )
    coverage_summary = (
        validated.groupby(["instrument_version", "interview_round", "participant_role"], sort=False)
        .agg(
            interview_count=("interview_id", "nunique"),
            item_count=("item", "nunique"),
            observation_count=("item", "size"),
        )
        .reset_index()
    )
    return {"issue_summary": issue_summary, "coverage_summary": coverage_summary}


def create_item_revision_log_template() -> pd.DataFrame:
    """Return a blank versioned research-team decision row per current item."""
    rows = []
    for item, (score_column, dimension) in _item_mapping().items():
        rows.append(
            {
                "decision_id": "",
                "source_instrument_version": "",
                "target_instrument_version": "",
                "decision_round": "",
                "score_column": score_column,
                "dimension": dimension,
                "item": item,
                "decision": "",
                "target_score_column": "",
                "target_dimension": "",
                "revised_item_wording": "",
                "decision_rationale": "",
                "minority_view_record": "",
                "safeguarding_review": "",
                "equity_accessibility_review": "",
                "responsible_researcher_id": "",
                "decision_date": "",
            }
        )
    return pd.DataFrame(rows, columns=REVISION_COLUMNS)


def load_item_revision_log_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 item-revision audit CSV."""
    try:
        records = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Item-revision CSV could not be read: {error}") from error
    return validate_item_revision_log(records)


def validate_item_revision_log(records: pd.DataFrame) -> pd.DataFrame:
    """Validate explicit human decisions without generating or changing them."""
    missing = sorted(set(REVISION_COLUMNS) - set(records.columns))
    if missing:
        raise ValueError(f"Item-revision data are missing required columns: {missing}")
    if records.empty:
        raise ValueError("Item-revision data must contain at least one decision.")
    validated = records.loc[:, list(REVISION_COLUMNS)].copy()
    optional_text = {"decision_round", "target_score_column", "target_dimension", "revised_item_wording"}
    text_columns = [column for column in REVISION_COLUMNS if column not in optional_text]
    for column in text_columns:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Item-revision field '{column}' must not be blank.")
    for column in ("target_score_column", "target_dimension", "revised_item_wording"):
        validated[column] = validated[column].fillna("").astype(str).str.strip()
    validated["decision_round"] = pd.to_numeric(validated["decision_round"], errors="coerce")
    rounds = validated["decision_round"].to_numpy(dtype=float)
    if not np.isfinite(rounds).all() or not validated["decision_round"].ge(1).all() or not validated["decision_round"].mod(1).eq(0).all():
        raise ValueError("decision_round must contain positive integers.")
    validated["decision_round"] = validated["decision_round"].astype(int)

    invalid_decisions = sorted(set(validated["decision"]) - set(REVISION_DECISIONS))
    if invalid_decisions:
        raise ValueError(f"Unknown item-revision decisions: {invalid_decisions}")
    for column in ("safeguarding_review", "equity_accessibility_review"):
        invalid = sorted(set(validated[column]) - set(REVIEW_STATUSES))
        if invalid:
            raise ValueError(f"Unknown {column} statuses: {invalid}")
    if validated["decision_id"].duplicated().any():
        raise ValueError("decision_id values must be unique.")
    if validated.duplicated(["source_instrument_version", "target_instrument_version", "item"]).any():
        raise ValueError("Each item may appear only once in a declared version transition.")
    if validated["source_instrument_version"].eq(validated["target_instrument_version"]).any():
        raise ValueError("Source and target instrument versions must differ.")

    mapping = _item_mapping()
    unexpected = sorted(set(validated["item"]) - set(ITEM_COLUMNS))
    if unexpected:
        raise ValueError(f"Unknown inclusion items in revision data: {unexpected}")
    for row in validated.itertuples(index=False):
        expected_score, expected_dimension = mapping[row.item]
        if row.score_column != expected_score or row.dimension != expected_dimension:
            raise ValueError(f"Item-to-dimension mapping is invalid for '{row.item}'.")
        if row.decision in {"revise", "split"} and not row.revised_item_wording:
            raise ValueError("revise and split decisions require revised_item_wording.")
        if row.decision == "move":
            if not row.target_score_column or not row.target_dimension:
                raise ValueError("move decisions require a target score column and dimension.")
            if row.target_score_column not in DIMENSION_ITEMS:
                raise ValueError("move decisions require a valid target score column.")
            if DIMENSION_LABELS[row.target_score_column] != row.target_dimension:
                raise ValueError("Move target score column and dimension do not match.")
            if row.target_score_column == row.score_column:
                raise ValueError("move decisions must identify a different target dimension.")
        elif row.target_score_column or row.target_dimension:
            raise ValueError("Target dimension fields are only permitted for move decisions.")
    validated["decision_date"] = pd.to_datetime(validated["decision_date"], errors="coerce")
    if validated["decision_date"].isna().any():
        raise ValueError("decision_date must use valid dates.")
    validated["decision_date"] = validated["decision_date"].dt.strftime("%Y-%m-%d")
    return validated


def summarize_item_revision_log(records: pd.DataFrame) -> pd.DataFrame:
    """Return a version-level count of explicit human decisions."""
    validated = validate_item_revision_log(records)
    return (
        validated.groupby(
            ["source_instrument_version", "target_instrument_version", "decision_round", "decision"],
            sort=False,
        )
        .agg(item_count=("item", "count"))
        .reset_index()
    )
