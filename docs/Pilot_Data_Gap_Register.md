# Provincial Pilot Data Gap Register

## Purpose

This register reports the coverage of the first five-region pilot against the variables required by the Preschool Resource Allocation Index (PRAI). It is a transparent collection-status record, not a statement that a source does or does not exist.

The machine-readable record is `datasets/metadata/pilot_variable_coverage.csv`.

## Current Finding

The pilot has independently reviewed source-faithful evidence for selected
education-supply variables, including kindergarten count, enrolled children,
and reported `专任教师` counts. These records remain in the staging layer. Four
kindergarten datasets are held because reported teacher counts have no
documented FTE mapping. Shanghai provenance review has been resolved; its
population and fiscal series are approved for context-only use. No region
currently has a documented, harmonised set of all PRAI dimensions.

The archive also contains provincial or municipal context series for Beijing, Shanghai, Guangdong, and Sichuan, such as total or 0–14 resident population and general public-budget aggregates. These support descriptive context, source review, and later calibration work. They do not satisfy the PRAI requirement for preschool-age population or preschool-specific public expenditure and must not be substituted for those variables.

In particular, the current archive does not yet contain a validated annual series for:

- preschool-age population using a consistent age definition;
- preschool-specific public expenditure and a compatible child denominator;
- facility or capacity measures with a common definition; and
- qualified-teacher measures comparable across regions.

Consequently, the pilot is **not ready for real-data PRAI scoring**, regional
equity estimates, DEA efficiency analysis, forecasting, or policy simulation.

## Collection Priorities

1. **Preschool-age population and enrolment denominator.** Locate provincial statistical-yearbook or education-statistics tables reporting a consistent 3–5 or 3–6 age group. Record definition and unit before extraction.
2. **Preschool-specific public expenditure.** Locate provincial finance or education-department tables that explicitly identify preschool expenditure. Do not substitute total education expenditure.
3. **Facility and class measures.** Locate table-level records for classes, approved places, or usable area and retain the exact source definition.
4. **Teacher qualification.** Collect only measures with a documented qualification standard and compatible calculation base.
5. **Gansu source acquisition.** Obtain official files through an ordinary authorised browser session, preserve the downloaded originals, then register filenames, URLs, dates, and checksums before transcription.

## Advancement Rule

A field can advance from staging to processed data only after independent source review, definition harmonisation, and documented variable mapping. A region can be included in an empirical PRAI pilot only when each selected PRAI dimension has a comparable, approved observation for the same reference year.

## Interpretation of Empty Cells

`not_collected_in_current_archive` means the project has not yet preserved and reviewed a usable record. It does not mean the indicator is unavailable in official statistics. No missing year should be interpolated during this collection stage.
