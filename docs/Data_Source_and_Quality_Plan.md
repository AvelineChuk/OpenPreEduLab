# Data Source and Quality Plan

## Purpose

This plan governs the acquisition, recording, screening, and use of real-world data for OpenPreEduLab. It is designed to protect **data integrity**, traceability, and reproducibility. It does not treat data cleaning as a mechanism for making inconvenient observations disappear.

## Source Hierarchy

The preferred order of evidence is:

1. official statistics published by the Ministry of Education, National Bureau of Statistics, Ministry of Finance, or authorised provincial and municipal statistical/education authorities;
2. official machine-readable downloads or tables accompanying those publications;
3. institutional administrative data released with clear definitions and reuse conditions; and
4. peer-reviewed supplementary datasets, only when primary official sources are unavailable and provenance is documented.

Commercial databases, unsourced web tables, screenshots without provenance, and manually copied values without a source record must not enter the analytical dataset.

## Data Levels and Intended Uses

| Data level | Appropriate use | Not appropriate for |
| --- | --- | --- |
| National annual statistics | national trends, variable definitions, consistency checks | city-level PRAI, within-province equity, city DEA |
| Provincial annual statistics | province comparison, regional decomposition, context | city-level inference unless data are genuinely city disaggregated |
| City-year statistics | city-level PRAI, equity, DEA, forecast, and simulation inputs | individual or institutional inference |
| Institution-level authorised data | future micro-level research after ethics and governance review | public release without appropriate protection |

## Acquisition Protocol

1. Register each candidate source in `datasets/source_registry.csv` before extraction.
2. Download the original file or page into `datasets/raw/` without modification.
3. Record publisher, URL, retrieval date, geographic level, period, format, reuse conditions, and SHA-256 checksum.
4. Extract data into a staging table that preserves original values and units.
5. Map source fields to the variables in `Data_Dictionary.md` through a documented transformation table.
6. Keep raw, staging, processed, and analytical datasets separate.

## Quality Screening and Extreme-Value Protocol

Extreme values must be **flagged and investigated**, not automatically deleted. Large variation may represent genuine differences in demographic structure, fiscal capacity, geography, or service provision.

The screening workflow is:

1. **Structural checks:** duplicate city-year records, missing identifiers, invalid dates, impossible units, and inconsistent administrative boundaries.
2. **Logical checks:** non-negative counts, qualified teachers not exceeding total teachers, unmet demand not exceeding recorded demand, and denominators greater than zero.
3. **Temporal checks:** abrupt year-to-year changes are flagged against source notes, boundary changes, or revisions.
4. **Distributional checks:** interquartile-range (IQR), median absolute deviation (MAD), and percentile diagnostics flag candidate outliers for review.
5. **Cross-source checks:** compare key values against a second official publication where available.
6. **Decision log:** retain, correct, exclude, or mark missing only with a recorded reason, source evidence, date, and reviewer.

A verified extreme observation remains in the processed dataset. Exclusion is permitted only when the value is demonstrably erroneous, non-comparable, duplicated, or outside the declared study universe. The raw record and exclusion reason must remain auditable.

## Minimum Real-Data Release Standard

No real-data dataset should be used for substantive PRAI, equity, DEA, forecast, or simulation analysis until it has:

- complete source provenance and geographic/time definitions;
- a variable mapping to the data dictionary;
- documented missing-data and extreme-value decisions;
- a reproducible transformation log;
- an authorised reuse status; and
- a methodology review appropriate to the intended research claim.

## Current Status

The repository currently contains synthetic test data and a verified registry of official national education-statistics sources. The national sources are useful for context and definition checks, but they do not yet constitute the city-year panel required for a substantive OpenPreEduLab empirical application.
