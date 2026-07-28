# Independent Review Packet: Provincial Pilot Staging Data

## Purpose

This packet supports the independent second review required before any staging record can advance to `datasets/processed/`. It should be used together with `docs/Data_Review_Protocol.md` and `datasets/metadata/staging_review_tracker.csv`.

The reviewer must not be the original transcriber. The review validates source fidelity and definition compatibility; it does not establish empirical policy conclusions.

## Required Review Steps

For each listed dataset:

1. Open the referenced raw source file.
2. Compare every staged value with the source table.
3. Check the year, geographic scope, unit, and variable definition.
4. Check that no unreported year has been created and no value has been silently transformed.
5. Confirm that all quality flags remain appropriate.
6. Record the reviewer ID, date, method, decision, and notes in `datasets/metadata/staging_review_tracker.csv`.

## Review Register

| Review ID | Staging dataset | Raw evidence | Key review issue |
| --- | --- | --- | --- |
| `BJ_KG_2015_2024` | `beijing_kindergarten_statistics_2015_2024.csv` | Beijing 2025 Yearbook, Table 20-2 | Verify kindergarten, class, enrolment, staff, and full-time-teacher transcriptions; inspect flagged enrolment changes. |
| `BJ_CONTEXT_2015_2023` | `beijing_context_population_education_finance_2015_2023.csv` | Beijing 2025 Yearbook, Tables 3-3 and 20-16 | Confirm units and census/sampling notes; retain context-only status. |
| `SH_KG_2020_2024` | `shanghai_kindergarten_statistics_2020_2024.csv` | Shanghai 2025 Yearbook, Table 20.17 | Check ten-thousand-person conversion and whether reported child count is comparable to `enrolled_children`. |
| `GD_KG_2015_2024` | `guangdong_kindergarten_statistics_2015_2024.csv` | Guangdong 2025 Yearbook, Table 19-3 Continued | Independently compare against the archived Excel table; do not infer unreported years. |
| `SC_KG_2015_2024` | `sichuan_kindergarten_statistics_2015_2024.csv` | Sichuan 2025 Yearbook, Tables 20-1, 20-2, and 20-3 | Compare three source tables; inspect 2023–2024 decline flags and confirm no staff total was inferred. |
| `GD_POP_CONTEXT_2015_2024` | `guangdong_population_age_structure_2015_2024.csv` | Guangdong 2025 Yearbook, Table 3-4 | Confirm 0–14 values and retain the non-preschool-age limitation. |
| `GD_FISCAL_CONTEXT_2015_2024` | `guangdong_fiscal_context_selected_years_2015_2024.csv` | Guangdong 2025 Yearbook, Table 8-3 | Confirm provincial-total row and selected reported years; retain the aggregate-fiscal limitation. |
| `SC_POP_CONTEXT_2015_2024` | `sichuan_population_main_indicators_2015_2024.csv` | Sichuan 2025 Yearbook, Table 3-1 | Confirm annual values and census/survey-method note; negative natural growth must remain. |
| `SH_POP_CONTEXT_2015_2024` | `shanghai_population_context_2015_2024.csv` | Shanghai 2025 Yearbook, Table 2.1 header and main table | Confirm column mapping between the separate header and main-table files. |
| `SH_FISCAL_CONTEXT_2015_2024` | `shanghai_fiscal_context_2015_2024.csv` | Shanghai 2025 Yearbook, Table 4.1 header and main table | Confirm revenue, tax, non-tax, and expenditure column mapping. |
| `NATIONAL_2026_FUND_ALLOCATIONS` | `national_2026_preschool_development_fund_pilot_allocations.csv` | Official government republication of `财教〔2026〕68号` and retained attachments | Confirm visible values against official-republication XLS; preserve future-scenario status and Guangdong-excluding-Shenzhen scope flag. |

## Permitted Decisions

Use only the following decisions in the tracker:

- `approved_for_processed`
- `approved_context_only`
- `return_for_correction`
- `hold_for_definition_review`
- `not_reviewed`

`approved_for_processed` is appropriate only for a source-faithful field with a documented, definition-compatible model mapping. Context-only data must be recorded as `approved_context_only`, not promoted to a PRAI input.

## Current Safeguard

No row should be copied to `datasets/processed/` until the corresponding tracker decision is complete and a reviewer has documented the evidence used.
