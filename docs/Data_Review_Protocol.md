# Data Review Protocol for the Provincial Pilot

## Purpose

This protocol governs independent review of provincial pilot records held in `datasets/staging/`. It supports data-quality assurance for software and research workflow development. It does not establish empirical or policy validity.

## Review Principle

Raw official files are immutable evidence. A reviewer must compare each staging record with the retained raw source, document the result in `datasets/metadata/staging_review_tracker.csv`, and must not silently alter, interpolate, smooth, or remove reported values.

An independent reviewer should not be the original transcriber. If this is not feasible, the review must use a separately documented pass and state the limitation in the tracker.

## Required Checks

For every staging dataset, the reviewer must check:

1. **Provenance** — the source identifier, official publisher, table title, reference year, and raw-file checksum match the manifest.
2. **Transcription** — each entered value matches the source table. Numeric units and any conversions are checked explicitly.
3. **Definitions** — the field meaning matches the staging column. Similar terms such as enrolment, children in kindergartens, teaching staff, and full-time teachers must not be treated as interchangeable without a source-supported mapping.
4. **Coverage** — no unreported year has been filled and no geographic aggregation has been manufactured.
5. **Integrity** — duplicate region-year records, missing values, non-positive counts, and implausible changes are recorded as findings.
6. **Anomaly handling** — extreme or discontinuous values are cross-checked against the raw table and flagged. They are never automatically excluded.

## Review Outcomes

Use one of the following decisions in the tracker:

- `approved_for_processed`: all required checks pass and the record has a documented model-variable mapping.
- `approved_context_only`: source-faithful contextual record; not eligible for a model input.
- `return_for_correction`: transcription, provenance, or unit issue requires correction.
- `hold_for_definition_review`: values are source-faithful, but the variable definition or comparability is unresolved.
- `not_reviewed`: review has not started.

Only a record marked `approved_for_processed` may be copied to `datasets/processed/`. Approval applies to the reviewed dataset and fields, not to a broad claim that a province has complete PRAI coverage.

## Evidence Record

The reviewer records their name or anonymized reviewer ID, date, method, reviewed fields, decision, and issue notes. If a correction is made, the raw file remains unchanged and the correction rationale must be committed with the updated staging record.

## Current Scope Limitation

The current pilot contains incomplete regional and temporal coverage. It also lacks a validated, comparable series for preschool-specific public expenditure and preschool-age population. Existing records must therefore not be promoted as a complete provincial PRAI panel.
