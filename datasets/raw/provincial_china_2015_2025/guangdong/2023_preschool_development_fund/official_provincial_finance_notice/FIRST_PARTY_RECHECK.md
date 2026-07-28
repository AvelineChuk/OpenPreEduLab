# First-Party Recheck: GD_2023_FUND_ALLOCATION

## Status and independence limitation

This is a first-party reproducibility recheck by the source archivist. It is
**not** an independent review and does not change the source's
`pending_assignment` status in `datasets/metadata/raw_source_review_register.csv`.

## Evidence checked

- Official publication page:
  <https://czt.gd.gov.cn/tzgg/content/post_4190959.html>
- Official attachment 1:
  `official_attachment_1_allocation.xlsx`
- Official attachment 2:
  `official_attachment_2_performance.xls`
- Attachment 1 SHA-256:
  `81EA7177DD5B1406D0E87269F4BB8D2C6E812FB80F5C3D61F3EFCBEA03C436AB`
- Attachment 2 SHA-256:
  `00D54347D765E3B83AF212E076D3671E15CAF37CAA75926CC96946BCBFE9669F`

## Rechecked visible content

| Attachment | Verified field | Value | Unit | Scope |
| --- | --- | ---: | --- | --- |
| 1 | Supplementary allocation total | 41,000,000.00 | yuan | Listed Guangdong local units |
| 2 | Annual fund total | 17,430.0 | 10,000 yuan | Guangdong annual transfer-payment performance target |
| 2 | Advanced allocation | 13,330.0 | 10,000 yuan | Component of annual total |
| 2 | Supplementary allocation | 4,100.0 | 10,000 yuan | Component of annual total |

Arithmetic check for attachment 2: `13,330.0 + 4,100.0 = 17,430.0`.

## Scope decision retained

Attachment 1 is a 2023 supplementary central-fund allocation table and uses
yuan. Attachment 2 is an annual performance-target table and uses 10,000 yuan.
The two attachments have different scopes and must not be added together. The
records can only be considered as policy-simulation parameter candidates after
independent review; they are not Guangdong's total preschool public expenditure
or PRAI fiscal input.

## Required independent-review action

An independent reviewer must open both official attachments, verify the source
identity, visible values, units, and scope restriction, then record an allowed
decision in `raw_source_review_register.csv`.
