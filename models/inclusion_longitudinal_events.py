"""Time-alignment audits for longitudinal policy and context events.

Declared events are aligned with documented collection windows. Temporal
ordering and overlap are descriptive metadata; they do not establish exposure,
mechanisms, policy effects, counterfactuals, or causality.
"""

from __future__ import annotations

from typing import Final

import pandas as pd

from models.inclusion_longitudinal_metadata import validate_longitudinal_metadata


EVENT_COLUMNS: Final[tuple[str, ...]] = (
    "event_id",
    "instrument_version",
    "event_type",
    "event_start_date",
    "event_end_date",
    "event_scope",
    "evidence_source",
    "evidence_status",
    "event_description",
)
EVENT_TYPES: Final[tuple[str, ...]] = (
    "policy_change",
    "resource_change",
    "training_activity",
    "curriculum_change",
    "administrative_change",
    "calendar_disruption",
    "public_health_event",
    "other_context_event",
)
EVIDENCE_STATUSES: Final[tuple[str, ...]] = (
    "documented_primary_source",
    "documented_secondary_source",
    "researcher_record",
    "verification_pending",
)


def create_longitudinal_event_template() -> pd.DataFrame:
    """Return a blank non-identifying event-registry schema."""
    return pd.DataFrame([{column: "" for column in EVENT_COLUMNS}], columns=EVENT_COLUMNS)


def load_longitudinal_event_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 longitudinal event CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(f"Longitudinal event CSV could not be read: {error}") from error
    return validate_longitudinal_events(data)


def validate_longitudinal_events(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, versioned, non-identifying event records."""
    missing = sorted(set(EVENT_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Longitudinal events are missing required columns: {missing}")
    if data.empty:
        raise ValueError("Longitudinal events must contain at least one event record.")
    validated = data.loc[:, list(EVENT_COLUMNS)].copy()
    for column in (
        "event_id",
        "instrument_version",
        "event_type",
        "event_scope",
        "evidence_source",
        "evidence_status",
        "event_description",
    ):
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Longitudinal event field '{column}' must not be blank.")
    if validated["event_id"].duplicated().any():
        raise ValueError("event_id values must be unique.")
    invalid_types = sorted(set(validated["event_type"]) - set(EVENT_TYPES))
    if invalid_types:
        raise ValueError(f"Unknown event types: {invalid_types}")
    invalid_statuses = sorted(set(validated["evidence_status"]) - set(EVIDENCE_STATUSES))
    if invalid_statuses:
        raise ValueError(f"Unknown event evidence statuses: {invalid_statuses}")
    for column in ("event_start_date", "event_end_date"):
        parsed = pd.to_datetime(validated[column], format="%Y-%m-%d", errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"{column} must use complete ISO dates in YYYY-MM-DD format.")
        validated[column] = parsed
    if (validated["event_end_date"] < validated["event_start_date"]).any():
        raise ValueError("event_end_date must not be earlier than event_start_date.")
    return validated


def audit_longitudinal_event_alignment(
    metadata: pd.DataFrame,
    events: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Align declared events with round windows for one instrument version."""
    rounds = validate_longitudinal_metadata(metadata)
    registered_events = validate_longitudinal_events(events)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    rounds = rounds[rounds["instrument_version"].eq(version)].sort_values(
        "administration_round"
    )
    registered_events = registered_events[
        registered_events["instrument_version"].eq(version)
    ].sort_values("event_start_date")
    if len(rounds) < 2:
        raise ValueError("Event-alignment audit requires at least two metadata rounds.")
    if registered_events.empty:
        raise ValueError("The selected instrument version has no registered events.")

    event_rows = []
    for event in registered_events.itertuples(index=False):
        overlapping_rounds = rounds[
            (rounds["collection_start_date"] <= event.event_end_date)
            & (rounds["collection_end_date"] >= event.event_start_date)
        ]["administration_round"].astype(int).tolist()
        prior_rounds = rounds[rounds["collection_end_date"] < event.event_start_date]
        later_rounds = rounds[rounds["collection_start_date"] > event.event_end_date]
        event_rows.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "event_start_date": event.event_start_date.date().isoformat(),
                "event_end_date": event.event_end_date.date().isoformat(),
                "event_duration_days_inclusive": int(
                    (event.event_end_date - event.event_start_date).days + 1
                ),
                "event_scope": event.event_scope,
                "evidence_source": event.evidence_source,
                "evidence_status": event.evidence_status,
                "overlapping_round_count": len(overlapping_rounds),
                "overlapping_rounds": ",".join(map(str, overlapping_rounds)),
                "latest_round_before_event": (
                    int(prior_rounds.iloc[-1]["administration_round"])
                    if not prior_rounds.empty
                    else pd.NA
                ),
                "earliest_round_after_event": (
                    int(later_rounds.iloc[0]["administration_round"])
                    if not later_rounds.empty
                    else pd.NA
                ),
                "event_description_present": bool(event.event_description),
            }
        )

    pair_rows = []
    round_records = list(rounds.itertuples(index=False))
    for first, second in zip(round_records[:-1], round_records[1:], strict=True):
        interval_events = registered_events[
            (registered_events["event_start_date"] > first.collection_end_date)
            & (registered_events["event_end_date"] < second.collection_start_date)
        ]
        overlap_first = registered_events[
            (registered_events["event_start_date"] <= first.collection_end_date)
            & (registered_events["event_end_date"] >= first.collection_start_date)
        ]
        overlap_second = registered_events[
            (registered_events["event_start_date"] <= second.collection_end_date)
            & (registered_events["event_end_date"] >= second.collection_start_date)
        ]
        pair_rows.append(
            {
                "first_round": int(first.administration_round),
                "second_round": int(second.administration_round),
                "events_strictly_between_windows": len(interval_events),
                "events_overlapping_first_window": len(overlap_first),
                "events_overlapping_second_window": len(overlap_second),
                "distinct_event_types_between_windows": interval_events["event_type"].nunique(),
                "verification_pending_events_between_windows": interval_events[
                    "evidence_status"
                ].eq("verification_pending").sum(),
            }
        )

    questions = pd.DataFrame(
        [
            {"research_question_candidate": "Which documented events overlap collection windows or occur between adjacent rounds?", "required_future_evidence": "Verified event chronology and scope"},
            {"research_question_candidate": "How should event timing and institutional exposure be defined before any policy or context analysis?", "required_future_evidence": "Preregistered exposure definition and identification strategy"},
            {"research_question_candidate": "Could multiple concurrent events, fieldwork changes, or selection processes complicate interpretation of observed changes?", "required_future_evidence": "Integrated metadata, attrition, and design review"},
        ]
    )
    interpretation = (
        "Event time-alignment evidence only. Chronology, overlap, and source status do not "
        "establish institutional exposure, mechanisms, attribution, policy effects, confounding "
        "control, counterfactual outcomes, or causality. Event descriptions are not reproduced. "
        "No automatic effect label, exclusion, adjustment, ranking, or causal conclusion is produced."
    )
    return {
        "event_alignment_summary": pd.DataFrame(event_rows),
        "adjacent_round_event_context_summary": pd.DataFrame(pair_rows),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
