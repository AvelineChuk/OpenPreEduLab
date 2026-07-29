# Correction Record: Guangdong 2017 Provincial-Level Final Accounts

## Purpose

This record documents the correction required by the independent review in
Issue #13 and PR #14. It preserves the original review decision rather than
overwriting it in the raw-source review register.

## Identified error

The original README and `manifest.csv` stated that the archived 2017 table did
not contain a `学前教育` (preschool education) field. This was incorrect. The
retained PDF contains a `学前教育` row on page 6.

## Corrected evidence statement

The table is titled as a 2017 Guangdong **provincial-level** general-public-
budget expenditure final-accounts table. Its stated unit is 10,000 yuan. The
preschool-education row reports:

| Field | Value (10,000 yuan) |
| --- | ---: |
| 2017 budget | 4,816 |
| Adjusted budget | 4,816 |
| Final accounts | 4,778 |

## Scope and analytical boundary

The values cover Guangdong provincial-level (`省本级`) expenditure only. They
are not a consolidated Guangdong-wide preschool-expenditure total and must not
be represented as such. The source is a single-year record and is not a
complete fiscal panel.

No value from this source has been copied to `datasets/staging/` or
`datasets/processed/`. It is not a PRAI fiscal input and is not available for
substantive analysis.

## Correction actions

The source README and manifest were corrected to record the preschool field,
the provincial-level geographic scope, and the pending re-review status. The
archived PDF and its checksum were not modified.

## Required re-review

An independent reviewer must verify the corrected README and manifest against
the retained PDF, confirm the page, unit, values, and geographic scope, and
decide whether the source can be retained only as a narrowly defined
provincial-level fiscal reference or needs further definition review. A new
review record must preserve the original `return_for_correction` decision as
part of the audit trail.
