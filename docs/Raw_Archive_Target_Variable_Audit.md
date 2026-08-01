# Raw Archive Target-Variable Audit

## Purpose

This audit checks whether the current immutable raw archive already contains
an unregistered, definition-compatible source for the two binding real-data
PRAI variables: preschool-age population and preschool-specific public
expenditure. It is an archive inventory check, not a policy analysis.

## Audit scope

On 1 August 2026, all archived text-based raw files were searched for the
exact target-age expressions `3-5`, `3-6`, `3至5`, `3至6`, and `学前三年`.
The official *Guangdong Statistical Yearbook 2025* ZIP archive was separately
inspected for its population and finance chapter tables.

## Findings

1. No raw text file contained an unregistered table with an explicit 3-5 or
   3-6 population definition. Exact-age matches occurred only in existing
   screening documentation that records why broad grouped-age sources are
   incompatible.
2. Guangdong Yearbook Table 3-4 contains only the broad groups 0-14, 15-64,
   and 65 and over. It has been registered for independent exclusion review as
   `GD_YEARBOOK_2025_TABLE_3_4_SCREEN`.
3. Guangdong Yearbook Table 8-2 contains general Education expenditure, not a
   preschool or kindergarten sub-item. It has been registered for independent
   exclusion review as `GD_YEARBOOK_2025_TABLE_8_2_SCREEN`.
4. Existing kindergarten tables provide education-supply measures, such as
   institutions, enrolment, and reported teachers. They do not establish a
   strict resident preschool-age denominator or preschool-specific public
   expenditure variable.

## Decision

No additional record is eligible for staging or processed-data use from the
current archive. Source discovery must continue through official external
catalogues, yearbook annexes, and authorised administrative publications. No
age-group splitting, enrolment-based inference, interpolation, or substitution
of general education expenditure is permitted.
