# Guangdong Preschool Development Fund Programme Parameter Staging

## Purpose

`datasets/staging/guangdong_preschool_development_fund_programme_2022_2025.csv`
is a source-faithful staging table for the Guangdong central support-for-
preschool-education-development transfer-payment programme.

It contains only 2022, 2024, and 2025 because these years have independently
reviewed raw-source decisions. The absence of 2023 is retained as missing; no
interpolation or carry-forward value is used.

## Variables

| Variable | Meaning | Unit or status |
| --- | --- | --- |
| `programme_funding_10000_yuan` | Annual programme funding recorded in the reviewed report | 10,000 yuan |
| `programme_expenditure_by_end_of_year_10000_yuan` | Reported programme expenditure by the stated year-end date | 10,000 yuan |
| `execution_rate_pct` | Reported or transparently calculated programme execution rate | percent |
| `execution_rate_origin` | Whether the rate is reported or calculated from reviewed source values | metadata |
| `geographic_coverage` | Programme coverage stated in the reviewed source | metadata |

## Permitted use

The completed independent review approves these fields as conditional
policy-simulation parameters for the named programme. They may not be used as
Guangdong's total preschool public expenditure, as a per-child fiscal input, or
as a direct PRAI indicator.

## Required review

The staging table is registered as `GD_PROGRAMME_PERFORMANCE_2022_2025` in
`datasets/metadata/staging_review_tracker.csv`. It was independently reviewed
by `Barnabe-Zihan-Ding` on 29 July 2026 (Issue #7; PR #8). All three rows and
39 staged fields were compared with the reviewed source manifests and retained
PDF hashes. The 2023 row remains intentionally absent, and the 2024 execution
rate retains its calculated origin.

This decision is `approved_scenario_parameter`, not
`approved_for_processed`. No row in this table may be copied to
`datasets/processed/`.
