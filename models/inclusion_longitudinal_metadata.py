"""Longitudinal timing and fieldwork-metadata readiness audits.

The module validates one non-identifying metadata record per instrument version
and administration round. It describes collection windows, observed intervals,
administration changes, sampling-frame changes, and whether fieldwork events
were documented. It does not evaluate study quality or explain score changes.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd


LONGITUDINAL_METADATA_COLUMNS: Final[tuple[str, ...]] = (
    "instrument_version",
    "administration_round",
    "collection_start_date",
    "collection_end_date",
    "administration_mode",
    "recruitment_scope",
    "sampling_frame_reference",
    "round_purpose",
    "fieldwork_event_status",
    "fieldwork_event_notes",
)
FIELDWORK_EVENT_STATUSES: Final[tuple[str, ...]] = (
    "none_reported",
    "event_recorded",
    "unknown",
)


def create_longitudinal_metadata_template() -> pd.DataFrame:
    """Return a blank one-row schema for round-level research metadata."""
    return pd.DataFrame(
        [{column: "" for column in LONGITUDINAL_METADATA_COLUMNS}],
        columns=LONGITUDINAL_METADATA_COLUMNS,
    )


def load_longitudinal_metadata_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 longitudinal metadata CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Longitudinal metadata CSV could not be read: {error}") from error
    return validate_longitudinal_metadata(data)


def validate_longitudinal_metadata(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, unique, non-identifying round metadata records."""
    missing = sorted(set(LONGITUDINAL_METADATA_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Longitudinal metadata are missing required columns: {missing}")
    if data.empty:
        raise ValueError("Longitudinal metadata must contain at least one round record.")
    validated = data.loc[:, list(LONGITUDINAL_METADATA_COLUMNS)].copy()

    required_text = (
        "instrument_version",
        "administration_mode",
        "recruitment_scope",
        "sampling_frame_reference",
        "round_purpose",
        "fieldwork_event_status",
    )
    for column in required_text:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Longitudinal metadata field '{column}' must not be blank.")

    rounds = pd.to_numeric(validated["administration_round"], errors="coerce")
    if rounds.isna().any() or not np.isfinite(rounds.to_numpy(dtype=float)).all():
        raise ValueError("administration_round must contain positive integers.")
    if rounds.le(0).any() or not rounds.eq(np.floor(rounds)).all():
        raise ValueError("administration_round must contain positive integers.")
    validated["administration_round"] = rounds.astype(int)
    if validated.duplicated(["instrument_version", "administration_round"]).any():
        raise ValueError("Each instrument version and administration round must be unique.")

    for column in ("collection_start_date", "collection_end_date"):
        parsed = pd.to_datetime(validated[column], format="%Y-%m-%d", errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"{column} must use complete ISO dates in YYYY-MM-DD format.")
        validated[column] = parsed
    if (validated["collection_end_date"] < validated["collection_start_date"]).any():
        raise ValueError("collection_end_date must not be earlier than collection_start_date.")

    invalid_statuses = sorted(
        set(validated["fieldwork_event_status"]) - set(FIELDWORK_EVENT_STATUSES)
    )
    if invalid_statuses:
        raise ValueError(f"Unknown fieldwork event statuses: {invalid_statuses}")
    notes = validated["fieldwork_event_notes"].fillna("").astype(str).str.strip()
    recorded_without_notes = validated["fieldwork_event_status"].eq("event_recorded") & notes.eq("")
    if recorded_without_notes.any():
        raise ValueError(
            "fieldwork_event_notes must be supplied when fieldwork_event_status is event_recorded."
        )
    validated["fieldwork_event_notes"] = notes
    return validated


def audit_longitudinal_metadata(
    data: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Describe round timing and adjacent-round metadata changes for one version.

    Human-entered fieldwork notes are validated but are not reproduced in the
    outputs. Boolean change indicators are documentation prompts, not quality,
    bias, validity, or causal judgements.
    """
    validated = validate_longitudinal_metadata(data)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    selected = validated[validated["instrument_version"].eq(version)].copy()
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")
    if len(selected) < 2:
        raise ValueError("Longitudinal metadata audit requires at least two rounds.")
    selected = selected.sort_values("administration_round").reset_index(drop=True)
    selected["collection_window_days_inclusive"] = (
        selected["collection_end_date"] - selected["collection_start_date"]
    ).dt.days + 1
    selected["collection_midpoint"] = selected["collection_start_date"] + (
        selected["collection_end_date"] - selected["collection_start_date"]
    ) / 2

    round_rows = []
    for row in selected.itertuples(index=False):
        round_rows.append(
            {
                "instrument_version": row.instrument_version,
                "administration_round": int(row.administration_round),
                "collection_start_date": row.collection_start_date.date().isoformat(),
                "collection_end_date": row.collection_end_date.date().isoformat(),
                "collection_window_days_inclusive": int(row.collection_window_days_inclusive),
                "administration_mode": row.administration_mode,
                "recruitment_scope": row.recruitment_scope,
                "sampling_frame_reference": row.sampling_frame_reference,
                "round_purpose": row.round_purpose,
                "fieldwork_event_status": row.fieldwork_event_status,
                "fieldwork_event_notes_present": bool(row.fieldwork_event_notes),
            }
        )

    adjacent_rows = []
    for index in range(len(selected) - 1):
        first = selected.iloc[index]
        second = selected.iloc[index + 1]
        midpoint_days = int(
            round((second["collection_midpoint"] - first["collection_midpoint"]).total_seconds() / 86400)
        )
        days_after_prior_end = int(
            (second["collection_start_date"] - first["collection_end_date"]).days
        )
        adjacent_rows.append(
            {
                "first_round": int(first["administration_round"]),
                "second_round": int(second["administration_round"]),
                "days_between_collection_midpoints": midpoint_days,
                "days_from_first_end_to_second_start": days_after_prior_end,
                "collection_windows_overlap": days_after_prior_end < 0,
                "administration_mode_changed": first["administration_mode"]
                != second["administration_mode"],
                "recruitment_scope_changed": first["recruitment_scope"]
                != second["recruitment_scope"],
                "sampling_frame_reference_changed": first["sampling_frame_reference"]
                != second["sampling_frame_reference"],
                "round_purpose_changed": first["round_purpose"] != second["round_purpose"],
                "fieldwork_event_recorded_in_either_round": (
                    first["fieldwork_event_status"] == "event_recorded"
                    or second["fieldwork_event_status"] == "event_recorded"
                ),
                "fieldwork_event_unknown_in_either_round": (
                    first["fieldwork_event_status"] == "unknown"
                    or second["fieldwork_event_status"] == "unknown"
                ),
            }
        )

    interval_values = [row["days_between_collection_midpoints"] for row in adjacent_rows]
    overview = pd.DataFrame(
        [
            {
                "instrument_version": version,
                "round_count": len(selected),
                "first_round": int(selected.iloc[0]["administration_round"]),
                "last_round": int(selected.iloc[-1]["administration_round"]),
                "first_collection_start_date": selected.iloc[0]["collection_start_date"].date().isoformat(),
                "last_collection_end_date": selected.iloc[-1]["collection_end_date"].date().isoformat(),
                "minimum_midpoint_interval_days": min(interval_values),
                "maximum_midpoint_interval_days": max(interval_values),
                "equal_midpoint_intervals": len(set(interval_values)) == 1,
                "administration_mode_change_observed": any(
                    row["administration_mode_changed"] for row in adjacent_rows
                ),
                "recruitment_scope_change_observed": any(
                    row["recruitment_scope_changed"] for row in adjacent_rows
                ),
                "sampling_frame_change_observed": any(
                    row["sampling_frame_reference_changed"] for row in adjacent_rows
                ),
                "fieldwork_event_recorded": selected["fieldwork_event_status"]
                .eq("event_recorded")
                .any(),
                "fieldwork_event_status_unknown": selected["fieldwork_event_status"]
                .eq("unknown")
                .any(),
            }
        ]
    )
    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "Could unequal collection intervals or overlapping fieldwork windows "
                    "affect how adjacent-round descriptive changes should be interpreted?"
                ),
                "required_future_evidence": "Preregistered time scale and date-aware longitudinal model",
            },
            {
                "research_question_candidate": (
                    "Could changes in administration mode, recruitment scope, or sampling "
                    "frame contribute to observed round differences?"
                ),
                "required_future_evidence": "Fieldwork documentation and design sensitivity analysis",
            },
            {
                "research_question_candidate": (
                    "Which documented fieldwork events require qualitative investigation "
                    "before interpreting score or Support Gap changes?"
                ),
                "required_future_evidence": "Governed event records and researcher review",
            },
        ]
    )
    interpretation = (
        "Longitudinal timing and fieldwork-metadata evidence only. Dates, intervals, mode "
        "changes, recruitment changes, sampling-frame changes, and event-status records are "
        "documentation prompts. They do not establish data quality, bias, validity, reasons "
        "for score changes, improvement, deterioration, policy effects, or causality. No "
        "automatic adequacy threshold, ranking, exclusion, correction, or judgement is produced."
    )
    return {
        "longitudinal_metadata_overview": overview,
        "round_metadata_summary": pd.DataFrame(round_rows),
        "adjacent_round_metadata_comparison": pd.DataFrame(adjacent_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
