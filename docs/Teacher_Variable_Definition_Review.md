# Teacher Variable Definition Review

## Purpose

This note records the definition issue identified in the independently reviewed
Beijing and Guangdong kindergarten-statistics staging tables. It prevents a
source-faithful reported teacher count from being silently treated as a
full-time-equivalent (FTE) teacher measure in empirical analysis.

## Current evidence

The reviewed source tables report `专任教师`, transcribed in staging as
`full_time_teacher_count`. The transcriptions are accurate. However, neither
source provides a documented conversion from the reported count to the model
variable `fte_teacher_count`.

The PRAI, efficiency, forecast, and policy-simulation specifications use FTE
teachers because FTE is intended to represent labour input after accounting for
part-time appointments or other non-equivalent employment arrangements. A
reported teacher headcount cannot be assumed to equal FTE without source-
supported evidence.

## Current decision

The Beijing and Guangdong kindergarten staging tables are retained as
source-faithful records and are marked `hold_for_definition_review`. They must
not be copied to `datasets/processed/`, renamed to `fte_teacher_count`, or used
to calculate real-data PRAI, DEA, forecast, or policy-simulation results.

## Acceptable resolution routes

### Route A: establish an FTE mapping

Locate an official metadata statement, statistical standard, or compatible
labour table that demonstrates either that `专任教师` is already recorded on an
FTE basis or supplies a documented conversion rule. The mapping must state its
reference year, institutional coverage, geography, unit, and formula. It then
requires independent review before use.

### Route B: revise the empirical variable specification

If the project adopts reported `专任教师` as a headcount-based staffing measure,
the change must be explicit and methodologically justified. It requires updates
to the PRAI theory document, data dictionary, model interfaces, tests, and
cross-region comparability rules. This is a research-design decision, not an
automatic fallback.

## Next review question

The next review should determine whether an official, definition-compatible FTE
mapping exists. Until then, the correct analytical state is **definition held**,
not missing-value imputation and not FTE substitution.
