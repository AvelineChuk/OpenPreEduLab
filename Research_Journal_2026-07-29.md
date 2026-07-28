# OpenPreEduLab Research Journal

## Project Information

**Project:** OpenPreEduLab

**Researcher:** Jiajia Zhu

**Reporting period:** Afternoon of 28 July 2026 to 29 July 2026

---

# Research Log

## Entry 003

**Date:** 28-29 July 2026

### Today's Goal

Advance the real-data pilot without compromising the project's data-governance
principles. The work focused on verifying official source provenance, separating
programme funding from province-wide expenditure, establishing independent
review procedures, and preparing a limited policy-simulation parameter staging
table.

### Completed Tasks

The following tasks were completed during this reporting period:

1. **Completed the independent-review infrastructure.**
   - Created an independent review packet and assignment sheet for staging
     datasets.
   - Created a separate raw-source review register and review packet for source
     scope decisions.
   - Created a prioritised review queue and a GitHub issue template for
     independent data reviews.
   - Added `CONTRIBUTING.md` so collaborators can follow the same data and code
     standards.

2. **Strengthened GitHub data-governance presentation.**
   - Added `datasets/README.md` and `docs/Data_Catalog.md`.
   - Updated the project README with a Data Governance and Review section.
   - Clarified that real-data pilot records are not model-ready and that
     `datasets/processed/` remains intentionally empty.

3. **Verified and archived additional official evidence.**
   - Verified the official-government republication of the 2026 support for
     preschool education development fund notice and its attachments.
   - Archived Guangdong official central-transfer materials for 2022, 2023,
     2024, and 2025 preschool-development-fund records.
   - Archived Guangdong's 2024 general education-finance statistics and 2017
     provincial final-accounts table as context or screening evidence.
   - Archived the Guangdong 2025 population sample-survey bulletin.

4. **Applied definition-based source screening.**
   - The 2020 national census age table was retained as screening evidence only
     because it provides grouped ages rather than separate ages 3, 4, and 5.
   - The Guangdong 2025 population sample bulletin was retained as screening
     evidence only because it reports the broad 0-14 age group, not ages 3-5 or
     3-6.
   - Guangdong's general education-finance statistics and provincial general
     budget final accounts were retained as context or exclusion evidence; they
     do not provide preschool-specific public expenditure.
   - No broad age group, general education expenditure, or general public-budget
     expenditure was substituted for the required PRAI variables.

5. **Completed independent reviews of three programme sources.**
   Barnabe-Zihan-Ding completed and merged GitHub reviews for the Guangdong
   central support-for-preschool-education-development transfer-payment records:

   | Year | Programme funding (10,000 yuan) | Expenditure (10,000 yuan) | Execution rate | Review outcome |
   | --- | ---: | ---: | ---: | --- |
   | 2022 | 21,000 | 10,725.63 | 51.07% | Confirmed policy-simulation candidate |
   | 2024 | 22,430 | 11,786.21 | 52.55% calculated from reviewed values | Confirmed policy-simulation candidate |
   | 2025 | 169,887 | 158,958.86 | 93.57% | Confirmed policy-simulation candidate |

   These figures describe a named central transfer-payment programme. They do
   not represent Guangdong's total preschool public expenditure and are not
   direct PRAI fiscal-resource inputs.

6. **Prepared a source-faithful staging table for policy simulation.**
   - Created
     `datasets/staging/guangdong_preschool_development_fund_programme_2022_2025.csv`.
   - Preserved 2023 as missing rather than interpolating it.
   - Retained metadata showing that the 2024 execution rate is calculated, not
     directly printed by the source.
   - Registered this table as
     `GD_PROGRAMME_PERFORMANCE_2022_2025` for a separate staging-table review.

7. **Maintained software and repository quality.**
   - Repeatedly ran the pytest software-validation suite; all 20 tests passed.
   - Used normal Git fetch, merge, and push operations only. No force push or
     remote-history rewrite was used.
   - Resolved intermittent GitHub connection resets by preserving local commits
     and synchronising when the connection recovered.

### Research Reflections

The most important methodological outcome of this period is the distinction
between **programme-level financial evidence** and **province-wide fiscal
evidence**. Officially published transfer-payment documents can be highly useful
for policy-simulation parameters, execution analysis, and scenario design. They
cannot, however, be relabelled as the total public resources available to
preschool education in a province.

The review process also demonstrated that reproducibility involves more than
storing source files. A reusable research record must preserve the publisher,
official URL, checksum, unit, year, geographic scope, proposed use, exclusion
rationale, and independent-review decision.

The independent reviews by a collaborator improved the evidentiary status of
the 2022, 2024, and 2025 programme records. Nevertheless, these reviews do not
remove the two binding gaps for a real PRAI panel: a compatible preschool-age
population denominator and preschool-specific public expenditure series.

### Problems Encountered

1. Official population publications located during this period provided broad
   child age groups rather than the required annual 3-5 or 3-6 population
   series.
2. Official general education-finance and provincial final-account tables did
   not provide a preschool-specific expenditure field.
3. The 2023 programme allocation materials use different units and scopes
   across their two attachments; they remain pending independent review.
4. GitHub connections intermittently reset during fetch and push operations.
5. Independent review cannot be replaced by a first-party recheck. First-party
   rechecks were documented as preparatory evidence but never recorded as an
   independent decision.

### Current Data Readiness

At the end of this reporting period:

- 12 staging datasets are registered and pending independent review.
- 8 raw sources are registered for scope review.
- 3 raw programme sources (2022, 2024, and 2025) have completed independent
  review as policy-simulation candidates.
- 5 raw sources remain pending review, including the 2023 allocation source and
  the age-definition and fiscal-definition screening sources.
- `datasets/processed/` contains no real-world analytical input.

The project is therefore ready for further source review and limited
policy-simulation parameter preparation, but not for a real-world PRAI score,
regional ranking, causal claim, or policy-effect evaluation.

### Lessons Learned

1. An official source can be authentic but still be unsuitable for a specific
   research variable.
2. Missing years should remain missing unless a transparent and theory-supported
   method is explicitly designed and validated; they should not be silently
   filled.
3. A calculated field must retain its calculation origin even when the arithmetic
   is straightforward.
4. Independent review is a research-quality mechanism, not merely an
   administrative task.
5. GitHub Issues, Pull Requests, review registers, and checksums can function
   together as a transparent research-audit trail.

### Plan for the Next Work Session

1. Ask the independent reviewer to complete
   `GD_PROGRAMME_PERFORMANCE_2022_2025`, the staging-table review for the three
   confirmed programme records.
2. Complete independent review of `GD_2023_FUND_ALLOCATION`, with explicit
   attention to the two attachments' units and scopes.
3. Continue targeted collection of official annual 3-5 or 3-6 population data
   and preschool-specific public expenditure data; do not accept broad
   substitutes.
4. Keep all real-data outputs out of `datasets/processed/` until their staging
   review and definition mapping are complete.
5. Once a definition-compatible subset is available, perform a documented
   software-flow check of the research pipeline without presenting substantive
   regional conclusions.

### Additional Research Notes

The project moved from source collection toward a more mature data-governance
workflow during this period. The main achievement was not a larger dataset but
a more defensible research record: sources were classified by permitted use,
incompatible substitutes were excluded, and collaborator review was integrated
into GitHub-based quality assurance.
