# Review Queue

## Purpose

This queue records work remaining after the first complete independent-review
round. The authoritative historical decisions remain in
`datasets/metadata/raw_source_review_register.csv` and
`datasets/metadata/staging_review_tracker.csv`.

## Completed review round

All previously archived raw-source scope records and all 12 staging datasets
received an independent review. No dataset was promoted to
`datasets/processed/`.

| Outcome | Records | Permitted state |
| --- | ---: | --- |
| Conditional policy-simulation parameter | 2 staging datasets | Scenario parameter only |
| Context-only | 6 staging datasets; 5 raw-source references | Contextual analysis only |
| Definition held | 4 kindergarten datasets | No FTE substitution or processed use |
| Provenance discrepancy | Resolved for 3 Shanghai staging datasets | Shanghai population and fiscal: context-only; kindergarten: definition held |

## Completed priority 0: Guangdong raw-source scope reviews

| Review ID | Required action |
| --- | --- |
| `GD_2019_FINAL_ACCOUNTS_SCREEN`, `GD_2020_FINAL_ACCOUNTS_SCREEN` | Verify each official PDF hash, Table 5 location, 10,000-yuan unit, preschool-education values, and Guangdong provincial-level rather than Guangdong-wide scope. |
| `GD_YEARBOOK_2025_TABLE_3_4_SCREEN` | Verify the official ZIP hash, `directory/03/html/03-04.htm` entry, table title, unit, and the visible `0-14`, `15-64`, and `65 and over` headers. Confirm that it cannot supply a strict 3-5 or 3-6 denominator. |
| `GD_YEARBOOK_2025_TABLE_8_2_SCREEN` | Verify the official ZIP hash, `directory/08/html/08-02.htm` entry, title, unit, the visible general `Education expenditure` row, and the absence of a preschool/kindergarten sub-item. Confirm that it cannot supply a preschool-specific fiscal input. |

All four records were independently completed on 2026-08-01. The two final-
accounts sources were confirmed as narrow provincial-level context references;
Table 3-4 was confirmed definition-incompatible; and Table 8-2 was confirmed
general-education context only.

The source is a single-year context-reference candidate only. It must not be
staged, processed, or used as a PRAI fiscal input unless a later study design
establishes a definition-compatible use.

## Completed priority 1: Shanghai provenance discrepancy

| Review IDs | Required action |
| --- | --- |
| `SH_KG_2020_2024`, `SH_POP_CONTEXT_2015_2024`, `SH_FISCAL_CONTEXT_2015_2024` | Resolve the discrepancy between the reviewer-cited hashes and the repository-held files, then obtain renewed independent review. |

See `docs/Shanghai_Provenance_Discrepancy_Audit.md` and
`docs/Shanghai_Provenance_Correction_Queue.md`. No manifest, raw file, or
staging value may be changed until the evidence-set discrepancy is explained.

Renewed review on 2026-08-01 explained the discrepancy as official CRLF versus
worktree LF byte representation. Population and fiscal records are context-only;
the kindergarten record remains held for variable-definition review.

## Active priority 2: teacher-variable definition

| Review IDs | Required action |
| --- | --- |
| `BJ_KG_2015_2024`, `GD_KG_2015_2024`, `SC_KG_2015_2024` | Establish an official FTE mapping for `专任教师`, or formally revise the empirical staffing variable and its cross-region comparability rules. |

See `docs/Teacher_Variable_Definition_Review.md`. This is a research-design
question; reported teacher counts must not be silently relabelled as FTE.

## Active priority 3: binding model-data gaps

The project still lacks two definition-compatible variables for a real PRAI
pilot:

1. annual 3-5 or 3-6 preschool-age population, with a documented consistent
   definition; and
2. annual preschool- or kindergarten-specific public expenditure, with a
   documented geographic scope and unit.

Source discovery, archival, and review for those variables must follow the
existing data-governance path. Until then, `datasets/processed/` remains empty
and no substantive real-data PRAI results may be produced.

For the preschool-age population search boundary and prior outcomes, see
`docs/Preschool_Age_Population_Source_Search.md`.
