# OpenPreEduLab Project History README

**Record date:** 3 August 2026  
**Project status:** OpenPreEduLab v0.1 Research Prototype

## 1. Project purpose

OpenPreEduLab is an open-source, AI-assisted research infrastructure prototype
for preschool education. It connects educational-policy questions, structured
data, statistical modelling, scenario simulation, and evidence-bounded
interpretation. It is not a chatbot, a completed policy evaluation, or a
validated real-world regional study.

The platform follows the research path:

`Policy / Research Question → Data → Statistical Models → Simulation → AI-assisted Interpretation → Research Output`

## 2. Current platform capabilities

The public Streamlit platform is available at:

https://openpreedulab-85aycdefait8stbdivqxpx.streamlit.app/

Current prototype functions include:

- Landing Page and Research Dashboard;
- PRAI resource-allocation scoring, ranking, and result export;
- equity indicators: coefficient of variation, Gini coefficient, and Theil index;
- DEA efficiency prototype;
- population, teacher-demand, and fiscal-requirement forecast prototype;
- scenario-based policy simulation prototype;
- research visualisations: ranking, trend, heatmap, and radar charts;
- data-template and sample-data download;
- AI Interpretation with an evidence-bounded prompt workflow;
- optional visitor-controlled DeepSeek integration;
- Inclusive Education Research Module with five prototype dimensions,
  descriptive Support Gap, Researcher Mode, exploratory scenarios, and bounded
  research exports using synthetic or non-identifying institution-level data;
- research-run summary downloads in Markdown, Word, and PDF;
- AI interpretation-record downloads in Markdown, Word, and PDF.

All interactive model outputs currently use either the repository sample dataset
or a user-provided PRAI-compatible CSV. A valid upload schema does not prove
source provenance, definition compatibility, or analytical validity.

## 3. AI Interpretation boundary

The LLM component is a **Research Interpretation Assistant**. Statistical
models compute; the LLM interprets supplied results under explicit constraints.

- The platform does not contain a shared API key.
- A visitor may use their own DeepSeek API key after confirming external data
  transmission.
- The key is not included in downloaded records.
- Generated text is a researcher-review draft, not an automatically validated
  finding, causal claim, policy recommendation, or paper.
- The sample-data interpretation test was manually reviewed for evidence
  boundaries and cross-model comparison risks.

## 4. Data governance and real-data status

The project uses a strict promotion path:

`raw → staging → independent review → processed`

As of this record date, `datasets/processed/` contains no approved empirical
dataset. It contains only its repository placeholder file. Consequently, the
project must not present PRAI, equity, DEA, forecast, or policy-simulation
outputs as real regional research findings.

### Reviewed staging status

There are 12 reviewed staging datasets:

- 2 approved only as conditional policy-simulation parameters;
- 6 approved only as contextual reference data;
- 4 held for teacher-variable definition review;
- 0 approved for processed analytical use.

### Binding data gaps

The following are still required before a valid real-data PRAI pilot can begin:

1. Annual regional population explicitly defined as ages 3–5 or 3–6;
2. Annual preschool- or kindergarten-specific public expenditure with clear
   scope, unit, and denominator compatibility;
3. An official FTE mapping for reported `专任教师`, or a separately approved
   redesign of the empirical staffing variable;
4. Comparable facility/capacity and qualified-teacher measures.

Broad age groups such as `0–14`, `1–4`, or `5–9` must not be split or used as
a strict preschool-age denominator. General education expenditure must not be
treated as preschool-specific expenditure. Reported teacher headcounts must not
be silently relabelled as FTE.

## 5. Completed review findings

- Shanghai provenance discrepancies were resolved as CRLF/LF byte-representation
  differences. Shanghai population and fiscal records are context-only; its
  kindergarten record remains held for the teacher-definition issue.
- Beijing, Guangdong, Shanghai, and Sichuan kindergarten records remain held
  because `专任教师` has no documented FTE mapping.
- Guangdong 2017, 2019, and 2020 provincial-level final-accounts preschool
  fields were independently confirmed as narrow, provincial-level context
  references only, not Guangdong-wide PRAI fiscal inputs.
- Guangdong Yearbook Table 3-4 is definition-incompatible for a strict
  preschool-age population denominator.
- Guangdong Yearbook Table 8-2 is general education-finance context only, not
  preschool-specific expenditure.

## 6. Recent platform maintenance

Recent repository updates include:

| Commit | Change |
| --- | --- |
| `e60babd` | Document AI interpretation export formats |
| `93f084e` | Add AI interpretation DOCX and PDF downloads |
| `a53f8e8` | Improve upload validation guidance |
| `04e5177` | Update deprecated Streamlit width parameters |
| `2df6f02` | Refresh current data review status |
| `4609d6e` | Align pilot data records with completed reviews |

The landing-to-dashboard warning caused by calling `st.rerun()` inside a button
callback was also corrected locally and verified with the full test suite. Its
GitHub push status should be checked before treating that maintenance item as
released.

## 7. Validation record

Current automated software validation status:

- 48 project tests passed after the Inclusive Education module, report-export,
  AI integration, and interface changes;
- all current Dashboard routes loaded in Streamlit smoke testing;
- DOCX and PDF exports were checked as valid document containers;
- public mobile access returned HTTP 200 without a detected login wall.

Software validation confirms that the prototype workflow functions as designed.
It does not validate policy conclusions, data quality, causal effects, or the
empirical validity of the models.

## 8. Showcase assets

Existing conceptual showcase assets are under `docs/screenshots/`.

The verified real interface screenshot currently available is:

- `docs/screenshots/platform_workflow.png`

Further real screenshots still needed for the GitHub showcase:

- Landing Page;
- Reports download-format selector;
- AI Interpretation download-format selector generated with the corrected,
  evidence-bounded research context.

Screenshots must not reveal API keys, private data, or unreviewed real data.

## 9. Next priorities

1. Acquire and archive definition-compatible official source files through
   normal authorised browser access.
2. Independently review every candidate before any promotion to `processed`.
3. Begin real-data model validation only after an approved, compatible subset
   exists.
4. Complete current interface screenshots and update README / Project Showcase.
5. Continue responsive browser testing and future accessibility review.
6. Continue review and accessibility work for the aggregate Inclusive Education
   prototype without treating its synthetic data as empirical evidence.
7. Design v0.2 Teacher Development only after its theoretical, ethical, and
   data-governance requirements are specified.

## 10. Core principle

OpenPreEduLab prioritises reproducibility, evidence boundaries, and children-
centred educational research over rapid but unsupported outputs.
