# OpenPreEduLab Research Record: 28 July 2026

## Project Information

**Project:** OpenPreEduLab  
**Researcher:** Jiajia Zhu  
**Project Stage:** Real-Data Pilot and Data-Governance Development  
**Record Date:** July 28, 2026

---

# Part I. Research Journal

## Today's Goal

Move OpenPreEduLab from a software-prototype release toward a transparent real-data pilot by establishing source governance, collecting authoritative preschool-education records, and preventing unsupported variables from entering the PRAI workflow.

## Completed Tasks

1. Established a provincial pilot data-governance workflow with separate `raw`, `staging`, and `processed` layers.
2. Created and extended the source registry, variable-source matrix, pilot-source audit, data-quality plan, panel roadmap, review protocol, review tracker, and data-gap register.
3. Archived official yearbook evidence for Beijing, Shanghai, Guangdong, and Sichuan.
4. Created source-faithful staging records for kindergarten counts, enrolled children, full-time teachers, selected class measures, population context, and general fiscal context where original tables directly supported those fields.
5. Preserved unreported years as missing rather than interpolating them; flagged unusual changes for review rather than deleting them.
6. Identified the principal data gap: no harmonised annual provincial series for preschool-age population and preschool-specific public expenditure has yet been verified for the pilot.
7. Archived two user-supplied 2026 support-for-preschool-education fund attachments, captured checksums, and extracted pilot-related allocations as future policy-scenario parameters.
8. Verified arithmetic consistency in the 2026 allocation table and retained the Guangdong-excluding-Shenzhen scope limitation.
9. Confirmed the repository contains the allocation, equity, efficiency, forecast, policy-simulation, LLM-interpretation, pipeline, visualisation, demo, and software-test modules.

## Research Reflections

Today's work clarified that data integrity is not achieved by making a dataset appear complete. It is achieved by making every field traceable to its source, definition, unit, and geographic scope.

The collection process required a clear distinction among direct model inputs, contextual variables, future scenario parameters, and unresolved candidate sources. Resident population aged 0–14 and general public-budget expenditure can support contextual description, but cannot stand in for preschool-age population or preschool-specific public expenditure. Likewise, the 2026 support fund is relevant to future scenario design, but is not historical actual expenditure.

This distinction protects the substantive validity of PRAI. A reproducible workflow should make it difficult to produce an attractive but conceptually invalid score.

## Problems Encountered

1. Gansu official portals returned access controls to automated requests; no access control was bypassed.
2. Several relevant Beijing files were published at district level rather than the municipal level required by the current pilot.
3. The 2026 allocation table lists Guangdong excluding Shenzhen and Shenzhen separately; this does not match existing Guangdong provincial resource totals.
4. Several population tables provide only total population or a 0–14 age band, not the required 3–5 or 3–6 denominator.
5. General education expenditure and general public-budget expenditure are not preschool-specific fiscal measures.
6. Two user-supplied XLS files required hidden read-only Excel access because standard XLS parsers could not process legacy named formulas.
7. GitHub synchronisation was intermittently unavailable because of connection resets. Local commits were preserved and no force push was used.

## Lessons Learned

1. Authoritative data are not automatically analytically compatible data.
2. Geographic scope is a substantive research decision, not a formatting detail.
3. Future policy allocations, budget measures, and observed expenditures are different data types.
4. Quality flags and review logs are reusable research assets.
5. The current priority is data validity, not additional model complexity or an interactive interface.

---

# Part II. Research Day Summary

## 1. Project Status

OpenPreEduLab remains an open-source AI research infrastructure prototype for preschool education research. Its intended workflow is:

`Policy → Data → Statistical Model → Simulation → LLM-assisted Interpretation → Research Output`

The repository includes the PRAI resource-allocation engine; equity, efficiency, forecast, and policy-simulation modules; LLM-assisted interpretation; a research pipeline; visualisation tools; demo materials; and pytest-based software-validation files. The real-data pilot is not yet ready for empirical PRAI scoring, policy evaluation, or causal inference.

## 2. Data-Governance Workflow

The project applies the following layers:

`raw source archive → staging → processed data → model input`

Raw sources are immutable. Staging records are source-faithful but not approved for modelling. Processed data require independent review, definition harmonisation, and a documented mapping decision. Extreme values are flagged and cross-checked; they are not removed automatically. Unreported years are not interpolated.

## 3. Provincial Pilot Evidence

| Region | Evidence archived or staged | Current limitation |
| --- | --- | --- |
| Beijing | Kindergarten series; 0–14 population and all-education-expenditure context; three district-level finance datasets | No preschool-age denominator or preschool-specific municipal expenditure; district data cannot be aggregated to municipal level |
| Shanghai | Kindergarten data for reported years; 2015–2024 resident-population and general-budget context | Kindergarten child definition needs review; no preschool-age denominator or preschool-specific expenditure |
| Guangdong | Kindergarten series for reported years; 0–14 population context; selected general-budget context | No preschool-age denominator or preschool-specific expenditure; incomplete fiscal-year coverage |
| Sichuan | 2015–2024 kindergarten series; resident-population, birth, death, natural-growth, and urbanisation context | No preschool-age denominator or preschool-specific expenditure |
| Gansu | No raw pilot files staged | Official files require authorised manual browser acquisition |

All staging datasets are registered in `datasets/metadata/staging_review_tracker.csv` and require independent second review before promotion to `datasets/processed/`.

## 4. 2026 Support for Preschool Education Development Fund

Two user-supplied XLS attachments were archived under:

`datasets/raw/national_china/2026_preschool_development_fund/`

The budget attachment reports provincial or separately listed 2026 allocations in ten thousand yuan, including expansion-and-quality subsidies and tuition-and-care-fee reduction subsidies. The performance attachment identifies objectives including preschool gross enrolment above 90%, inclusive-kindergarten coverage above 85%, and full coverage of eligible children under relevant fee-reduction support.

Pilot-related allocation rows were staged only as future policy-scenario parameter candidates. Checks confirmed that subsidy components sum to the total allocation and that advanced plus current allocation equals the same total.

Important limitations:

- the original publication URL and issuing notice are still pending;
- the 2026 allocation is not historical actual expenditure; and
- Guangdong excluding Shenzhen and Shenzhen are separate scopes and cannot be automatically combined with Guangdong provincial resource data.

## 5. Validation Completed

The following software and data-handling checks were performed:

- duplicate region-year or scope-year checks;
- missing-value and invalid non-positive value checks for extracted fields;
- arithmetic reconciliation of the 2026 fund allocation;
- SHA-256 checksum capture for newly archived raw files; and
- review-tracker path checks.

These checks validate handling and reproducibility workflow. They do not validate policy effects, causal mechanisms, or empirical conclusions.

## 6. Binding Data Gaps

No pilot region currently has a reviewed and harmonised set of all PRAI dimensions. The binding gaps are:

1. a comparable annual preschool-age population series, preferably for ages 3–5 or 3–6; and
2. a comparable annual preschool-specific public-expenditure series.

Total population, 0–14 population, general education expenditure, and total public-budget expenditure must not be substituted for these variables.

## 7. Next Steps

1. Conduct independent second review of all staging records.
2. Obtain and register Gansu files through authorised browser access.
3. Target preschool-age population and preschool-specific expenditure sources rather than additional aggregate context series.
4. Record the publication URL and issuing notice for the 2026 fund attachments.
5. Build a small processed panel only after variables are definition-compatible and review-approved.
6. Run the real-data pipeline first as a reproducibility and software-flow check.
7. Synchronise local Git commits with GitHub when network access is restored.

## 8. Repository Status

At the time this record was created, the local repository contained the day's work and remained ahead of `origin/main`. GitHub synchronisation had been blocked by connection resets; no remote overwrite, reset, or force push was used.
