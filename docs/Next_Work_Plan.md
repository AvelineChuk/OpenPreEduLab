# Next Work Plan: Real-Data Pilot

## Immediate Objective

Advance the provincial pilot from source-faithful staging records to a small, independently reviewed, definition-compatible dataset. The immediate objective is not to produce a PRAI score. It is to establish whether a valid score can eventually be constructed.

## Priority 0: Complete the 2026 Fund Provenance Chain

**Current status:** An official government republication has been verified: Xinxing County Finance Bureau's page for the Ministry of Finance and Ministry of Education notice `Caijiao [2026] No. 68`, with both XLS attachments. The local supplied files and republished files have different binary hashes but identical visible workbook content.

**Action:** Retain the verified republication evidence and, if available, locate the primary Ministry of Finance or Ministry of Education publication URL. Record any primary URL in the raw-source manifest without replacing the archived republication files.

**Completion condition:** The republication evidence remains documented; a primary central-government URL is recorded if available. This verifies provenance only; the allocation remains a future scenario parameter, not historical expenditure.

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
