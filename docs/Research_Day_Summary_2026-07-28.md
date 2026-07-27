# Research Day Summary: 28 July 2026

## 1. Purpose of This Record

This document consolidates the data-development work completed on 28 July 2026 for OpenPreEduLab. It records process, provenance, validation checks, limitations, and project status. It does not report empirical findings or policy conclusions.

## 2. Project Position at the End of the Day

OpenPreEduLab remains an open-source AI research infrastructure prototype for preschool education research. Its intended workflow is:

`Policy → Data → Statistical Model → Simulation → LLM-assisted Interpretation → Research Output`

The repository contains the following software-prototype components:

- Preschool Resource Allocation Engine;
- Educational Equity Evaluation Engine;
- Efficiency Evaluation Engine;
- Forecast Engine;
- Policy Simulation Engine;
- LLM Interpretation Engine;
- Research Pipeline and demonstration materials; and
- pytest-based software-validation files.

The real-data pilot is still in the data-design and source-validation stage. It is not ready for empirical PRAI scoring, policy evaluation, or causal inference.

## 3. Data-Governance Work Completed

The following governance assets were created or extended:

- `datasets/source_registry.csv`;
- `datasets/metadata/variable_source_matrix.csv`;
- `datasets/metadata/pilot_source_availability.csv`;
- `datasets/metadata/pilot_variable_coverage.csv`;
- `datasets/metadata/staging_review_tracker.csv`;
- `docs/Data_Source_and_Quality_Plan.md`;
- `docs/Provincial_Panel_Roadmap.md`;
- `docs/Data_Review_Protocol.md`; and
- `docs/Pilot_Data_Gap_Register.md`.

The working rule is that raw sources are immutable; staging data are source-faithful but not yet approved; processed data require independent review and definition harmonisation. Extreme values are flagged, cross-checked, and retained unless a documented source error is established. No unreported year is interpolated.

## 4. Provincial Pilot Evidence Collected

### Beijing

- Archived official kindergarten, age-structure, and education-expenditure yearbook tables.
- Staged kindergarten counts, class counts, enrolled children, teaching staff, and full-time teachers for 2015–2024, pending independent review.
- Staged 0–14 resident-population and all-education-expenditure context for 2015–2023; these are not PRAI inputs.
- Archived three Beijing district-level education-finance datasets. They are retained for a future district-level extension and are not aggregated into a Beijing municipal observation.

### Shanghai

- Archived official kindergarten records for the reported years 2020, 2023, and 2024, pending definition review of the child-count field.
- Archived population and general public-budget tables with their frame, header, and main-value pages.
- Staged municipal resident-population, registered-population, and general public-budget context for 2015–2024.
- These context variables do not provide a preschool-age denominator or preschool-specific expenditure.

### Guangdong

- Retained the official 2025 Guangdong Statistical Yearbook ZIP and cross-validated selected kindergarten records against the archive Excel table.
- Staged kindergarten counts, children in kindergartens, teaching staff, and full-time teachers for the years reported by the source: 2015, 2022, 2023, and 2024.
- Staged 0–14 resident-population context for 2015–2024.
- Staged provincial general public-budget revenue and expenditure for the years reported by the source: 2015 and 2020–2024.

### Sichuan

- Archived official kindergarten tables for school counts, full-time teachers, and enrolments.
- Staged 2015–2024 kindergarten counts, enrolled children, and full-time teachers, pending independent review.
- Archived population tables and staged 2015–2024 resident population, urbanisation, birth, death, and natural-growth context.
- The population sources do not provide a preschool-age denominator.

### Gansu

- Official statistics and education portals returned automated-access controls.
- No access control was bypassed.
- Gansu files must be obtained through an ordinary authorised browser session and registered before extraction.

## 5. 2026 Support for Preschool Education Development Fund

Two user-supplied XLS attachments were archived under:

`datasets/raw/national_china/2026_preschool_development_fund/`

The budget attachment reports a 2026 support fund in ten thousand yuan, including expansion-and-quality subsidies and tuition-and-care-fee reduction subsidies. The performance attachment identifies national objectives including preschool gross enrolment above 90%, inclusive-kindergarten coverage above 85%, and full coverage of eligible children under relevant fee-reduction support.

The pilot-region allocation rows were staged only as future policy-scenario parameter candidates. Arithmetic checks confirmed that each row's subsidy components sum to the total allocation and that the advanced and current allocations sum to the same total.

Important limitations:

- the attachments are user-supplied and their original publication URL and issuing notice remain to be recorded;
- 2026 allocations are future budget parameters, not historical actual expenditure; and
- Guangdong is listed excluding Shenzhen, while Shenzhen is separate. These records cannot be automatically combined with Guangdong provincial resource data.

## 6. Validation Performed

For newly created staging tables, the following checks were completed:

- unique region-year or scope-year identifiers;
- no missing values in extracted numeric fields;
- no invalid non-positive counts or allocations where positive values are required;
- arithmetic reconciliation for the 2026 support-fund budget components;
- SHA-256 checksum capture for newly archived raw files; and
- tracker-path verification for all staged datasets.

These checks validate software and data-handling workflow. They do not validate educational policy effects, causal mechanisms, or empirical model conclusions.

## 7. Current Data Readiness

The pilot has useful but incomplete evidence for kindergarten supply variables and selected contextual series. No pilot region has a reviewed, harmonised set of all PRAI dimensions.

The two binding gaps are:

1. a comparable annual preschool-age population series, preferably for ages 3–5 or 3–6; and
2. a comparable annual series of preschool-specific public expenditure.

Total population, population aged 0–14, general education expenditure, and total public-budget expenditure must not be substituted for these variables.

## 8. Repository and Synchronisation Status

The local repository contains the day's work in Git commits, including the latest local commit `d2872ab` (`Archive 2026 preschool development fund data`). At the close of the day, local `main` was ahead of `origin/main` by five commits.

GitHub synchronisation was attempted normally but was blocked by network connection resets. No force push, reset, or remote overwrite was used. Local commits and source files remain intact.

## 9. Recommended Next Steps

1. Perform independent second review of all staging records.
2. Obtain Gansu official source files through authorised browser access.
3. Prioritise preschool-age population and preschool-specific expenditure sources over additional aggregate context data.
4. Record the source URL and issuing notice for the 2026 fund attachments.
5. Create a small processed panel only after variables are definition-compatible and review-approved.
6. Run the real-data pipeline only as a reproducibility and software-flow check at first.
7. Synchronise local commits with GitHub when network access is restored.
