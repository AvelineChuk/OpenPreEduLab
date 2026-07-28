# First-Party Recheck: GD_2022_FUND_PERFORMANCE

## Status and independence limitation

This is a first-party reproducibility recheck by the source archivist. It is
**not** an independent review and does not change the source's
`pending_assignment` status in `datasets/metadata/raw_source_review_register.csv`.

## Evidence checked

- Official publication page:
  <https://edu.gd.gov.cn/gkmlpt/content/4/4232/post_4232754.html>
- Official attachment:
  `official_2022_preschool_development_fund_self_evaluation.pdf`
- SHA-256:
  `05FE0B8AE98EAD2D47AEBA5BCDBCC8B01A9CA0DEC7B23C179DE59BD45A15A6E7`
- Visual evidence: retained rendered pages 1, 2, and 3.

## Rechecked values

| Field | Source page | Value | Unit | Check |
| --- | ---: | ---: | --- | --- |
| Programme funding | 1 | 21,000 | 10,000 yuan | Quoted visible value |
| Advanced allocation | 1 | 15,570 | 10,000 yuan | Quoted visible value |
| Additional allocation | 1 | 5,430 | 10,000 yuan | Quoted visible value |
| Programme expenditure by December 2022 | 3 | 10,725.63 | 10,000 yuan | Quoted visible value |
| Programme execution rate | 3 | 51.07 | percent | Quoted visible value |

Arithmetic check: `15,570 + 5,430 = 21,000`; and
`10,725.63 / 21,000 * 100 = 51.07%` after rounding to two decimals.

## Scope decision retained

The report is explicitly a central support-for-preschool-education-development
transfer-payment performance report. It supports only a programme-level funding
or execution parameter after independent review. It must not be relabelled as
Guangdong's total preschool public expenditure or used directly as a PRAI fiscal
input.

## Required independent-review action

An independent reviewer must compare the PDF and retained page renders against
the values above, verify the official publisher and scope, and then record an
allowed decision in `raw_source_review_register.csv`.
