# OpenPreEduLab Research Journal

## Project Information

**Project:** OpenPreEduLab

**Researcher:** Jiajia Zhu

**Started:** July 27, 2026

---

# Research Log

## Entry 001

**Date:** July 27, 2026

### Today's Goal

Initialise the OpenPreEduLab project, define its vision, mission, and long-term direction, and establish the core project document, `Project_Charter.md` v0.1.

### Completed Tasks

The following tasks were completed:

1. Created the initial OpenPreEduLab project structure.
2. Created `Project_Charter.md` and completed version 0.1.
3. Defined the project's central principle:

> Research should not end with publication. Research outputs should become reusable and continuously evolving research infrastructure.

### Research Reflections

During the project's initial development, I reconsidered the role of artificial intelligence in preschool education research.

Current applications of large language models (LLMs) in education are concentrated mainly in teaching assistance, content generation, and text organisation. Their potential contribution to educational research remains underexplored.

I believe that an LLM should be more than a text-generation tool. It should serve as an intelligent assistant within the research workflow, helping researchers with data analysis, model interpretation, literature organisation, and policy simulation while improving research efficiency.

At the same time, artificial intelligence cannot replace researchers in formulating questions, constructing theory, or developing original insights. The core of research innovation remains the researcher's theoretical reasoning and awareness of substantive problems.

OpenPreEduLab therefore seeks to explore a research model based on the following principle:

> Researchers remain the primary agents of inquiry, while artificial intelligence serves an assisting role. Integrating AI with statistical models can improve the efficiency, transparency, and reproducibility of preschool education research.

### Problems Encountered

A concrete implementation strategy for deeply integrating LLMs with statistical models has not yet been established.

Further study is required in the following areas:

- AI-assisted research methods;
- educational data-analysis techniques;
- statistical modelling methods; and
- practical examples of integrating LLMs with data analysis.

### Solutions and Next Steps

The next stage will involve:

1. Developing the overall OpenPreEduLab platform architecture.
2. Defining the data flow among the platform's modules.
3. Specifying the research questions, variable system, and mathematical formulation of the first statistical model: the **Resource Allocation Engine**.

### Lessons Learned

1. A research project must first establish its research questions and theoretical value rather than proceeding immediately to technical development.
2. GitHub is not only a code-hosting platform; it can also support the continuous accumulation, sharing, and iteration of research outputs.
3. Preschool education research can intersect productively with data science and artificial intelligence, creating new research paradigms.

### Plan for the Next Day

1. Design the overall OpenPreEduLab architecture.
2. Define the data flows among the platform's four core modules.
3. Establish the initial research direction of the Resource Allocation Engine.

### Additional Research Notes

OpenPreEduLab officially began today.

By maintaining a continuous record of the research process, I hope to preserve the project's development history and transform each model design, data analysis, and research reflection into a reusable research asset.

---

## Entry 002

**Date:** July 28, 2026

### Today's Goal

Move OpenPreEduLab from a software-prototype release toward a transparent real-data pilot by establishing source governance, collecting authoritative preschool-education records, and preventing unsupported variables from entering the PRAI workflow.

### Completed Tasks

The following tasks were completed:

1. Established a provincial pilot data-governance workflow with separate `raw`, `staging`, and `processed` layers.
2. Created a source registry, variable-source matrix, pilot-source availability audit, data-quality plan, provincial-panel roadmap, review protocol, review tracker, and data-gap register.
3. Archived official statistical-yearbook evidence for Beijing, Shanghai, Guangdong, and Sichuan.
4. Created source-faithful staging records for kindergarten counts, enrolled children, full-time teachers, selected class measures, population context, and general fiscal context where the original tables supported those fields.
5. Preserved missing years rather than interpolating them, and flagged discontinuities for review rather than deleting observations.
6. Identified and documented the principal data gap: no harmonised, annual, provincial series for preschool-age population and preschool-specific public expenditure has yet been verified for the pilot.
7. Archived two user-supplied 2026 support-for-preschool-education fund attachments, recorded their checksums, and extracted pilot-region budget allocations as future policy-scenario parameters.
8. Verified that the 2026 budget components reconcile arithmetically, while explicitly retaining the Guangdong-excluding-Shenzhen geographic-scope limitation.
9. Reviewed the repository structure and confirmed the presence of the allocation, equity, efficiency, forecast, policy-simulation, LLM-interpretation, pipeline, visualisation, demo, and test modules.

### Research Reflections

Today's work clarified that data integrity is not achieved by making a dataset appear complete. It is achieved by making every field traceable to its source, definition, unit, and geographic scope.

The collection process repeatedly showed why a research infrastructure must distinguish between several types of evidence:

- a direct model input;
- a contextual variable;
- a future scenario parameter; and
- an unresolved candidate source.

For example, resident population aged 0–14 and general public-budget expenditure are informative contextual variables, but they cannot stand in for preschool-age population or preschool-specific public expenditure. Similarly, the 2026 support fund is relevant to future policy-simulation design but is not historical actual expenditure.

This distinction protects the substantive validity of the PRAI model. A reproducible workflow should make it difficult to produce an attractive but conceptually invalid score.

### Problems Encountered

1. The Gansu official portals returned access controls to automated requests. No attempt was made to bypass them.
2. Several relevant files were published at district level rather than at the provincial or municipal level required by the current pilot.
3. The Guangdong fund allocation distinguishes Guangdong excluding Shenzhen from Shenzhen, while existing resource data are provincial totals; these records cannot be combined automatically.
4. Several historical statistical tables provide total population or a 0–14 age group, but not the 3–5 or 3–6 preschool-age denominator required by the PRAI design.
5. General education expenditure and general public-budget expenditure are not preschool-specific fiscal measures.
6. Two user-supplied 2026 XLS files required hidden read-only Excel access because standard XLS parsers could not read their legacy named formulas.
7. GitHub synchronisation was intermittently unavailable because of connection resets. Local Git commits were preserved; no force push was used.

### Solutions and Next Steps

1. Complete independent second review for every staging record before any promotion to `datasets/processed/`.
2. Locate authorised sources for a consistent 3–5 or 3–6 preschool-age population denominator.
3. Locate provincial preschool-specific public-expenditure or final-account tables; do not substitute aggregate education expenditure.
4. Obtain Gansu official files through an ordinary browser session, then register their URLs, checksums, definitions, and geographic level.
5. Record the issuing notice and original URL for the 2026 support-fund attachments before treating their provenance as independently verified.
6. Run an end-to-end real-data pipeline only after a small, definition-harmonised and independently reviewed panel is available.
7. Synchronise the local commits with GitHub when network access is restored.

### Lessons Learned

1. Authoritative data are not automatically analytically compatible data.
2. Geographic scope is a substantive research decision, not a formatting detail.
3. A future policy allocation, a budget, and an observed expenditure measure must be represented as different data types.
4. Quality flags and review logs are research assets because they preserve the reasoning behind data inclusion and exclusion.
5. The current priority is data validity, not an interactive interface or additional model complexity.

### Plan for the Next Day

1. Begin independent second review of the existing Beijing, Shanghai, Guangdong, and Sichuan staging tables.
2. Continue targeted collection of preschool-age population and preschool-specific expenditure data.
3. Obtain and register Gansu source files through authorised manual access.
4. Restore GitHub synchronisation when the network connection becomes available.
