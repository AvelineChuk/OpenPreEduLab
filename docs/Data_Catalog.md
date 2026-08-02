# Data Catalog

## Purpose

This catalog describes the current research-data assets and their permitted
uses. It is a transparency document, not a claim that the real-data pilot is
complete or that any policy effect has been validated.

## Data layers and readiness

| Layer | Records | Readiness | Permitted use |
| --- | ---: | --- | --- |
| Sample data | `sample_preschool_data.csv` | Demonstration-ready | Tests, notebooks, and software examples only |
| Staging data | 12 datasets | Two conditionally approved for policy-simulation parameters; six approved context-only; four held for definition review | No staging dataset is approved for processed analytical use |
| Raw-source review register | 13 records | Five context-only decisions, three definition-incompatible decisions, four policy-simulation candidate decisions, and one retained return-for-correction audit record | Scope and provenance review only |
| Processed data | 0 datasets | Not available | None |

## Staging datasets

The current staging register is maintained in
`datasets/metadata/staging_review_tracker.csv`.

| Coverage | Contents | Current analytical status |
| --- | --- | --- |
| Beijing | Kindergarten statistics; population and education-finance context | Kindergarten values held for teacher-definition review; population and finance records approved context-only |
| Shanghai | Kindergarten statistics; population and fiscal context | Kindergarten values held for teacher-definition review; population and fiscal records approved context-only |
| Guangdong | Kindergarten statistics; population and fiscal context | Kindergarten values held for teacher-definition review; population and fiscal records approved context-only |
| Sichuan | Kindergarten statistics; population context | Kindergarten values held for teacher-definition review; population record approved context-only |
| National 2026 fund allocation | Support-for-preschool-development allocation attachment | Independently reviewed; approved only as a conditional policy-simulation parameter |
| Guangdong programme performance | 2022, 2024, and 2025 central transfer-payment funding and execution records | Independently reviewed; approved only as a conditional policy-simulation parameter |

## Raw sources requiring scope review

Assignments are maintained in
`datasets/metadata/raw_source_review_register.csv`.

| Source group | Verified status | Permitted provisional use |
| --- | --- | --- |
| 2020 national census grouped-age table | Uses 0, 1-4, and 5-9 age groups; no compatible 3-5 or 3-6 group | Independently confirmed exclusion evidence only |
| Guangdong 2025 population sample survey bulletin | Reports only broad 0-14 and 0-15 age groups | Independently confirmed exclusion evidence only |
| Guangdong Statistical Yearbook 2025, Table 3-4 | Reports only 0-14, 15-64, and 65-and-over permanent-population groups | Independently confirmed definition-incompatible exclusion evidence only |
| Guangdong Statistical Yearbook 2025, Table 8-2 | Reports general education expenditure without a preschool/kindergarten sub-item | Independently confirmed general-education context only |
| Guangdong 2017 provincial-level final accounts | Contains a `学前教育` row and covers Guangdong provincial-level expenditure rather than a Guangdong-wide total | Correction independently re-reviewed; context-only narrow fiscal reference, not an analytical input |
| Guangdong 2024 education-finance statistics | General-public-budget education expenditure, not preschool-specific | Independently reviewed; context-only cross-validation candidate |
| Guangdong 2020 provincial-level final accounts | Contains a `学前教育` row in a provincial-level final-accounts table | Raw candidate pending independent scope review; not an analytical input |
| Guangdong 2019 provincial-level final accounts | Contains a `学前教育` row in a provincial-level final-accounts table | Raw candidate pending independent scope review; not an analytical input |
| Guangdong 2023 preschool fund allocation | Central transfer allocation, with separate attachment scopes | Independently reviewed policy-simulation parameter candidate only |
| Guangdong 2022, 2024, and 2025 performance reports | Central support-for-preschool-development transfer-payment programme | Independently reviewed programme funding/execution parameter candidates |

The 2022, 2024, and 2025 performance reports are comparable only as records of
the named central transfer-payment programme. They must not be interpreted as a
continuous series of Guangdong's total preschool public expenditure. The 2023
programme performance report has not yet been located and is recorded as a
missing year, not imputed.

The 2023 allocation source was independently reviewed in Issue #9 and merged
through PR #10 on 29 July 2026. Its 41,000,000 yuan municipal-allocation
attachment equals the 4,100 (10,000 yuan) supplementary component reported in
the separate annual-total attachment; the two values must not be added together.
The source is approved only as a conditional central transfer-payment parameter
for policy simulation, not as Guangdong's total preschool expenditure or a PRAI
fiscal input.

The 2017 provincial-level final-accounts screening was returned for correction
in Issue #13 and PR #14. The correction was independently re-reviewed in Issue
#33 and PR #34. The retained PDF includes a preschool-education row, but it is
limited to Guangdong provincial-level expenditure rather than a Guangdong-wide
total. It remains outside analytical data layers as a single-year,
context-only fiscal reference.

The 2020 provincial-level final-accounts source is separately archived because
it visibly reports a preschool-education row. It remains pending independent
scope review and is limited by its provincial-level, single-year, non-per-child
coverage. It must not be treated as a Guangdong-wide fiscal total or a PRAI
input.

Beijing, Guangdong, and Sichuan kindergarten staging tables were independently
reviewed on 30 July 2026. Their reported values are source-faithful, but the
source term `专任教师` has not been shown to be a full-time-equivalent (FTE)
measure. The three tables are therefore held for definition review and remain
outside `datasets/processed/`.

The compiled Guangdong programme table was independently reviewed in Issue #7
and merged through PR #8 on 29 July 2026. The approval confirms transcription
and scope for conditional policy-simulation use only. It is not an
`approved_for_processed` dataset and does not establish a PRAI fiscal input.

## Binding data limitations

The following variables remain unavailable for a valid multi-year provincial
PRAI pilot:

1. annual population explicitly aged 3-5 or 3-6, using a documented compatible
   definition;
2. annual public expenditure explicitly identified as preschool or kindergarten
   expenditure, with a documented geographic scope and unit.

Until both variables are available and independently reviewed, `datasets/processed/`
must remain empty and real-data model outputs must not be presented as
substantive findings.

## Review and reproducibility

Every source archive includes a `manifest.csv` with an official URL, retrieval
date, scope, and SHA-256 checksum. Reviewers must follow
`docs/Data_Review_Protocol.md` for staging datasets and
`docs/Raw_Source_Review_Packet.md` for archived source-scope decisions.
