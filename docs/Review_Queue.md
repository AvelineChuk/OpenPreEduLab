# Review Queue

## Purpose

This queue orders the current independent-review work. It does not replace the
authoritative registers in `datasets/metadata/`; reviewers must record their
final decisions there.

**Assigned reviewer (pending acceptance and confirmation of independence):**
[`Barnabe-Zihan-Ding`](https://github.com/Barnabe-Zihan-Ding)

## Phase 1: Raw-source scope review

Review raw sources before creating any new transcription or analytical table.

| Priority | Review ID | Current status | Required register |
| --- | --- | --- | --- |
| Completed | `GD_2022_FUND_PERFORMANCE` | Confirmed policy-simulation candidate after independent review | `raw_source_review_register.csv` |
| Completed | `GD_2024_FUND_PERFORMANCE` | Confirmed policy-simulation candidate after independent review | `raw_source_review_register.csv` |
| Completed | `GD_2025_FUND_PERFORMANCE` | Confirmed policy-simulation candidate after independent review | `raw_source_review_register.csv` |
| 1 | `GD_2023_FUND_ALLOCATION` | Confirms allocation-attachment units and limits of use | `raw_source_review_register.csv` |
| 2 | `GD_2024_EDU_FINANCE_CONTEXT` | Confirms general education expenditure remains context-only | `raw_source_review_register.csv` |
| 3 | `GD_2017_FINAL_ACCOUNTS_SCREEN` | Confirms absence of preschool-specific expenditure in the screened table | `raw_source_review_register.csv` |
| 4 | `NBS_2020_GROUPED_AGE_SCREEN` | Confirms that grouped ages cannot be used for a strict preschool-age variable | `raw_source_review_register.csv` |
| 5 | `GD_2025_POP_SAMPLE_SCREEN` | Confirms that the 0-14 group cannot be used for a strict preschool-age variable | `raw_source_review_register.csv` |

## Phase 2: Staging-data value review

After source scope review, compare the 11 staging datasets against their raw
tables. The reviewer must use `staging_review_tracker.csv` and the procedures
in `docs/Data_Review_Protocol.md`.

| Priority | Review IDs | Reason |
| --- | --- | --- |
| 1 | `GD_KG_2015_2024`, `SC_KG_2015_2024`, `BJ_KG_2015_2024`, `SH_KG_2020_2024` | These kindergarten-resource series are closest to PRAI resource variables. |
| 2 | `GD_POP_CONTEXT_2015_2024`, `SC_POP_CONTEXT_2015_2024`, `SH_POP_CONTEXT_2015_2024`, `BJ_CONTEXT_2015_2023` | Confirm context-only boundaries and population-method notes. |
| 3 | `GD_FISCAL_CONTEXT_2015_2024`, `SH_FISCAL_CONTEXT_2015_2024` | Confirm broad fiscal variables remain context-only. |
| 4 | `NATIONAL_2026_FUND_ALLOCATIONS` | Confirm future-scenario status and the Guangdong-excluding-Shenzhen scope. |

## Promotion rule

No task in this queue can create a `datasets/processed/` record by itself. Only
a completed staging review with the decision `approved_for_processed` and a
documented definition-compatible model mapping can authorize that transition.
