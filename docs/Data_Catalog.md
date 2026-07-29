# Data Catalog

## Purpose

This catalog describes the current research-data assets and their permitted
uses. It is a transparency document, not a claim that the real-data pilot is
complete or that any policy effect has been validated.

## Data layers and readiness

| Layer | Records | Readiness | Permitted use |
| --- | ---: | --- | --- |
| Sample data | `sample_preschool_data.csv` | Demonstration-ready | Tests, notebooks, and software examples only |
| Staging data | 12 datasets | One conditionally approved for policy-simulation parameters; 11 pending independent review | Approved programme table: conditional policy simulation only; all others: source comparison only |
| Raw-source review register | 8 sources | 3 independently reviewed; 5 pending | Scope and provenance review only |
| Processed data | 0 datasets | Not available | None |

## Staging datasets

The current staging register is maintained in
`datasets/metadata/staging_review_tracker.csv`.

| Coverage | Contents | Current analytical status |
| --- | --- | --- |
| Beijing | Kindergarten statistics; population and education-finance context | Pending review; context fields are not preschool-specific substitutions |
| Shanghai | Kindergarten statistics; population and fiscal context | Pending review; incomplete years and definition mapping remain |
| Guangdong | Kindergarten statistics; population and fiscal context | Pending review; general fiscal variables are context only |
| Sichuan | Kindergarten statistics; population context | Pending review; preschool-age population remains unavailable |
| National 2026 fund allocation | Support-for-preschool-development allocation attachment | Scenario-parameter candidate only |
| Guangdong programme performance | 2022, 2024, and 2025 central transfer-payment funding and execution records | Independently reviewed; approved only as a conditional policy-simulation parameter |

## Raw sources requiring scope review

Assignments are maintained in
`datasets/metadata/raw_source_review_register.csv`.

| Source group | Verified status | Permitted provisional use |
| --- | --- | --- |
| 2020 national census grouped-age table | Does not provide separate ages 3, 4, and 5 | Exclusion evidence only |
| Guangdong 2025 population sample survey bulletin | Reports only the broad 0-14 age group | Exclusion evidence only |
| Guangdong 2017 provincial final accounts | Does not list `学前教育` / `20502` | Exclusion evidence only |
| Guangdong 2024 education-finance statistics | General-public-budget education expenditure, not preschool-specific | Context-only cross-validation candidate |
| Guangdong 2023 preschool fund allocation | Central transfer allocation, with separate attachment scopes | Policy-simulation parameter candidate |
| Guangdong 2022, 2024, and 2025 performance reports | Central support-for-preschool-development transfer-payment programme | Independently reviewed programme funding/execution parameter candidates |

The 2022, 2024, and 2025 performance reports are comparable only as records of
the named central transfer-payment programme. They must not be interpreted as a
continuous series of Guangdong's total preschool public expenditure. The 2023
programme performance report has not yet been located and is recorded as a
missing year, not imputed.

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
