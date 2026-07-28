# Staging Pre-Audit: 28 July 2026

## Purpose

This pre-audit checks structural integrity of the current staging layer before independent source review. It is a data-handling and reproducibility check. It does not approve variables for modelling, validate policy effects, or replace the independent-review process in `docs/Data_Review_Protocol.md`.

## Scope

The audit covered all 11 CSV files in `datasets/staging/` and the corresponding entries in `datasets/metadata/staging_review_tracker.csv`.

## Structural Results

| Dataset group | Files | Rows | Identifier check | Missing numeric cells | Status |
| --- | ---: | ---: | --- | ---: | --- |
| Beijing kindergarten and context | 2 | 19 | No duplicate `region, reference_year` | 0 | Pending independent review |
| Shanghai kindergarten, population, and fiscal context | 3 | 23 | No duplicate `region, reference_year` | 0 | Pending independent review |
| Guangdong kindergarten, population, and fiscal context | 3 | 20 | No duplicate `region, reference_year` | 0 | Pending independent review; kindergarten table also archive-Excel cross-validated |
| Sichuan kindergarten and population context | 2 | 20 | No duplicate `region, reference_year` | 0 | Pending independent review |
| National 2026 fund allocations | 1 | 6 | No duplicate `reference_year, scope_label` | 0 | Pending independent review |

No CSV file was found in `datasets/processed/`.

## Value Checks

1. Positive-count and budget fields contained no invalid non-positive values.
2. The only negative values found were four observations of `natural_growth_rate_per_thousand` in the Sichuan population context table. Negative natural growth is a valid demographic outcome and is retained.
3. The 2026 fund allocation table had already passed component and allocation reconciliation checks: the two subsidy components equal the total allocation, and advanced plus current allocation equals the same total for every staged row.
4. All 11 tracker records remain `pending_independent_review` with decision `not_reviewed`.

## Interpretation

The staging layer is structurally consistent enough for independent review. It is not ready for promotion to processed data. In particular:

- kindergarten datasets still require source and definition review;
- contextual population and fiscal variables remain ineligible as substitutes for preschool-age population or preschool-specific expenditure;
- the 2026 fund allocations remain scenario-parameter candidates rather than historical expenditure; and
- the Guangdong-excluding-Shenzhen allocation scope must not be combined automatically with Guangdong provincial resource data.

## Required Follow-Up

1. Assign an independent reviewer for each tracker row.
2. Compare staged values with retained raw sources and record decisions in the review tracker.
3. Correct any confirmed transcription or unit issues through a documented Git commit.
4. Promote only approved, definition-compatible fields to `datasets/processed/`.
