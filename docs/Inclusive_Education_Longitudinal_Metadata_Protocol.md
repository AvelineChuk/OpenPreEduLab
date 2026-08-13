# Inclusive Education Longitudinal Timing and Fieldwork Metadata Protocol

## 1. Purpose

Longitudinal score summaries cannot be interpreted responsibly from round
numbers alone. Researchers need to know when collection occurred, how long each
window lasted, whether intervals were comparable, how administration and
recruitment were organised, which sampling frame was used, and whether relevant
fieldwork events were documented.

This protocol structures those research records. It is a metadata-readiness
audit, not an evaluation of study quality or an explanation of score change.

## 2. Required round-level fields

One record is supplied per instrument version and administration round:

- `instrument_version`;
- `administration_round`;
- `collection_start_date` and `collection_end_date` in ISO `YYYY-MM-DD` format;
- `administration_mode`;
- `recruitment_scope`;
- `sampling_frame_reference`;
- `round_purpose`;
- `fieldwork_event_status`; and
- `fieldwork_event_notes`.

Allowed event statuses are `none_reported`, `event_recorded`, and `unknown`.
Notes are required when an event is recorded. Notes should be concise,
non-identifying references to governed fieldwork documentation. They must not
contain child, family, teacher, researcher, or institution identities.

## 3. Validation

The platform checks required columns, non-blank research metadata, positive
integer round labels, unique version-round records, valid ISO dates, collection
end dates that are not earlier than start dates, recognised event statuses, and
the conditional event-note requirement.

Validation confirms that the submitted file follows the declared schema. It
does not certify that the metadata are accurate, complete in a substantive
sense, independently verified, or sufficient for a longitudinal model.

## 4. Timing summaries

For every round, the audit reports the collection window and inclusive window
length. For adjacent observed rounds it calculates:

- days between collection-window midpoints;
- days from the earlier window end to the later window start; and
- whether the collection windows overlap.

Rounds are ordered by their positive integer labels. A sequence such as 1, 3,
and 6 is treated as the observed adjacent pairs 1→3 and 3→6. Round labels are
not assumed to represent equal time units.

## 5. Design-change prompts

Adjacent-round outputs state whether the submitted text differs for:

- administration mode;
- recruitment scope;
- sampling-frame reference; and
- round purpose.

The audit also records whether either round has a documented or unknown
fieldwork-event status. These Boolean indicators are prompts for researcher
review. A change is not automatically a problem, bias, design failure, or reason
to exclude data. Conversely, unchanged text does not prove equivalent
implementation.

## 6. Interpretation boundaries

The audit does not establish:

- longitudinal measurement invariance or score comparability;
- data quality, validity, reliability, or representativeness;
- why dimension or Support Gap values changed;
- whether attrition is ignorable;
- improvement, deterioration, institutional quality, or effectiveness; or
- policy effects, mechanisms, counterfactual outcomes, or causality.

There are no automated adequacy thresholds, red/green ratings, rankings,
exclusions, weights, imputations, or corrections.

## 7. Privacy and governance

Uploaded metadata are processed in the current Streamlit session and are not
intentionally persisted. Human-entered fieldwork notes are validated but are not
reproduced in platform summaries or downloads; only note presence is reported.
Researchers remain responsible for data minimisation, access control, lawful
processing, retention, documentation governance, and independent verification.

## 8. Relationship to other audits

This workflow should be interpreted alongside:

- longitudinal panel readiness, which describes round coverage and matched
  changes;
- longitudinal attrition and panel composition, which describes retained,
  exited, and entered groups; and
- paired longitudinal Bootstrap uncertainty, which describes resampling
  uncertainty in matched mean changes.

Metadata do not repair limitations identified by those audits. They make the
study context more explicit so researchers can decide what further evidence and
methods are justified.

## 9. Future validation

Future governed work may link versioned protocol records, dated policy and
context events, interval-specific exposure definitions, fieldwork deviation
logs, ethics amendments, and independently reviewed sampling-frame histories.
Time-aware or multilevel models require preregistered definitions, adequate
samples, diagnostics, and appropriate uncertainty methods.

Completion means timing and implementation metadata were audited reproducibly.
It does not mean the study design, scores, longitudinal interpretations, or
causal claims have been validated.
