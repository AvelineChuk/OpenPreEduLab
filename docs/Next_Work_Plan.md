# Next Work Plan: Real-Data Pilot

## Immediate Objective

Advance the provincial pilot from source-faithful staging records to a small, independently reviewed, definition-compatible dataset. The immediate objective is not to produce a PRAI score. It is to establish whether a valid score can eventually be constructed.

## Priority 0: Verify the 2026 Fund Source

**Why this matters:** The 2026 support-for-preschool-education fund attachments contain directly relevant policy-budget parameters, but their issuing notice and original publication URL are not yet recorded.

**Action:** Locate the original notice through an authorised browser session. Record the issuing institution, notice title, publication date, URL, and any associated document number in the raw-source manifest.

**Completion condition:** The attachments move from `user_supplied_local_file_pending_url_provenance` to a documented-source status. This verifies provenance only; the allocation remains a future scenario parameter, not historical expenditure.

## Priority 1: Independent Review of Existing Staging Records

**Why this matters:** Staging records are not yet eligible for `datasets/processed/`.

**Action:** A reviewer who was not the original transcriber compares every staged value with the retained raw source, checks units and definitions, and records the decision in `datasets/metadata/staging_review_tracker.csv`.

**Completion condition:** Each reviewed dataset is marked either `approved_for_processed`, `approved_context_only`, `return_for_correction`, or `hold_for_definition_review` under `docs/Data_Review_Protocol.md`.

## Priority 2: Preschool-Age Population

**Required variable:** Annual provincial or municipal population aged 3–5 or 3–6, with a documented definition and unit.

**Acceptable sources:** Official population-census tables, population-sampling reports, provincial education statistics, or authorised administrative enrolment-demand records.

**Do not use as a substitute:** Total resident population, registered population, birth rate, or the broad 0–14 age group.

## Priority 3: Preschool-Specific Public Expenditure

**Required variable:** Annual public expenditure explicitly identified as preschool or kindergarten expenditure, with a compatible child denominator where per-child intensity is required.

**Acceptable sources:** Education-expenditure statistics, education-department final accounts, finance-department final accounts, or programme documents with a clear expenditure definition.

**Do not use as a substitute:** General education expenditure, general public-budget expenditure, or an unverified future allocation.

## Priority 4: Gansu Source Acquisition

**Action:** Obtain Gansu official yearbooks or education-statistics files through normal authorised browser access. Store originals under `datasets/raw/provincial_china_2015_2025/gansu/`, then register URL, publisher, year, table title, checksum, geographic level, and variable definition before transcription.

## Priority 5: Processed Pilot and Software-Flow Check

Only after the above gates are met for a definition-compatible subset should approved records be copied to `datasets/processed/`. The first pipeline execution should be treated as a reproducibility and software-flow check, not a real policy evaluation.

## Priority 6: Repository Synchronisation

The local branch is ahead of GitHub because recent normal pushes were blocked by network resets. When connectivity returns, run a normal fetch, inspect any remote divergence, merge if necessary, and push. Do not use force push.
