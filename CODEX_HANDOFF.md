# OpenPreEduLab — Codex Continuation Guide

**Last updated:** 13 August 2026
**Repository:** `C:\Users\86198\Desktop\OpenPreEduLab`  
**GitHub:** <https://github.com/AvelineChuk/OpenPreEduLab>  
**Branch:** `main`  
**Current version:** v0.1 Research Prototype  
**Public platform:** <https://openpreedulab-85aycdefait8stbdivqxpx.streamlit.app/>

This file is the operational handoff for future Codex sessions. **Read it in
full before taking any action.** It records the project state, the research
boundaries, and the rules that protect data integrity and the user's GitHub
repository.

---

## 1. Project identity and non-negotiable positioning

OpenPreEduLab is an open-source, AI-assisted research infrastructure prototype
for preschool education research. Its intended workflow is:

`Research Question / Policy → Data → Statistical Models → Simulation → AI-assisted Interpretation → Research Output`

It is **not**:

- a general chatbot;
- a completed real-world policy evaluation;
- evidence that any policy has been effective;
- a finished commercial product; or
- an automatic paper-writing system.

The platform is research-first, children-centred, reproducible, and cautious.
Statistical models calculate; the LLM only assists the interpretation of
supplied outputs. Do not market the prototype as a validated deployment.

---

## 2. Mandatory first-session checklist

Before editing, downloading, processing data, or pushing commits:

1. Read this file and `docs/Project_History_README_2026-08-03.md`.
2. Run (using the explicit Git path if `git` is absent from `PATH`):

   ```powershell
   cd C:\Users\86198\Desktop\OpenPreEduLab
   & "C:\Program Files\Git\cmd\git.exe" status -sb
   & "C:\Program Files\Git\cmd\git.exe" log --oneline -8
   ```

3. Inspect whether the worktree is dirty. Preserve unrelated user changes.
4. Before relying on remote status, use normal `fetch` when the network works.
   GitHub connections have intermittently reset in prior sessions; retry normal
   requests carefully, but never force push.
5. Confirm the current data boundary:

   ```powershell
   Get-ChildItem datasets\processed -File
   ```

   At handoff, this directory must contain only `.gitkeep`.
6. Run tests after any code change:

   ```powershell
   python -m pytest tests -q
   ```

---

## 3. Current implementation status

### Implemented and tested

- Landing Page and Streamlit Research Dashboard (`app/streamlit_app.py`);
- data preview, PRAI input template, sample-dataset download, and upload
  validation guidance;
- Preschool Resource Allocation Index (PRAI): validation, normalisation,
  weighting, scores, ranking, and export;
- equity evaluation: CV, Gini, and Theil;
- visualisation: ranking, trend, heatmap, and radar chart;
- DEA efficiency prototype;
- population, teacher-demand, and fiscal-requirement forecast prototypes;
- scenario-based policy-simulation prototype;
- bounded AI Interpretation prompt workflow;
- optional DeepSeek integration using a visitor-controlled API key;
- Inclusive Education Research Module: synthetic institution-level input,
  five-dimension scores, Researcher Mode, descriptive Support Gap, visualisation,
  exploratory scenarios, bounded research insights, and export;
- Research Report export in Markdown, Word (`.docx`), and PDF (`.pdf`);
- AI Interpretation record export in Markdown, Word, and PDF;
- documentation, changelog, citation file, license, tests, and GitHub Actions;
- public Streamlit deployment;
- a verified Workflow interface screenshot at
  `docs/screenshots/platform_workflow.png`.

### Recent verified maintenance

- Inclusive Education now provides accessible numerical alternatives for the
  pathway, radar, Gap, and heatmap views. Automated/code-level review is in
  `docs/Inclusive_Education_Accessibility_Check.md`; keyboard, screen-reader,
  zoom/reflow, contrast, and mobile review remain manual follow-up items.
- Inclusive Education Researcher Mode now includes leave-one-item-out dimension
  sensitivity analysis. This is a robustness check, not item validation or a
  causal analysis.
- The next methodological stage is documented in
  `docs/Inclusive_Education_Content_Validation_Protocol.md`. It is a prospective
  expert-review protocol; no expert ratings or content-validity conclusion
  currently exist.
- Researcher Mode now includes session-only cognitive-interview evidence and
  versioned item-revision audit workflows. They validate and summarize
  human-entered records without simulating interviews or making item decisions;
  no real interviews or revision decisions have been completed.
- Researcher Mode now includes complete instrument-version registration and
  structural comparability auditing. It records item snapshots and flags
  wording, dimension, response-scale, weight, added-item, and removed-item
  changes. It never converts scores or authorises direct comparison; no
  empirical linking study has been completed.
- Researcher Mode now includes a session-only feasibility-pilot and data-
  quality audit. It preserves legitimate item missingness solely to inspect
  completion, missing patterns, endpoints, variation, duration, burden, and
  administration mode. It never imputes missing responses or passes incomplete
  records into five-dimension scoring, and its flags are not validity evidence
  or automatic item-removal rules.
- Researcher Mode now includes preliminary internal-consistency and repeated-
  administration audits for complete, non-identifying records. It reports
  Cronbach alpha, corrected item-total correlations, alpha-if-item-removed,
  matched coverage, Pearson correlation, and ICC(3,1) without automatic
  thresholds or item decisions. It does not establish validity,
  unidimensionality, fairness, or cross-version comparability; no governed
  empirical reliability study has been completed.
- Researcher Mode now includes a session-only construct-structure readiness
  and exploratory principal-components audit for one explicitly selected
  instrument version and administration round. It reports item correlations,
  overall and item-level KMO, Bartlett's test, eigenvalues, and researcher-
  selected unrotated PCA loadings. It does not automate factor-count or item
  decisions, label PCA as EFA/CFA, or validate the proposed five dimensions;
  no governed empirical construct-validation study has been completed.
- Researcher Mode now includes a session-only subgroup measurement-
  comparability readiness audit for complete records from one version and
  round. It reports group coverage, item distributions, descriptive
  standardised mean differences, correlation-structure differences, and
  bounded future research questions. It does not establish measurement
  invariance, DIF, bias, fairness, or substantive group effects and produces
  no automatic thresholds, rankings, group judgements, or item decisions.
- Researcher Mode now includes a session-only external-measure relationship
  readiness audit for complete records from one version and round. It records
  one independent institutional measure and its provenance, then reports
  paired coverage, Pearson and Spearman relationships with the five dimensions,
  and approximate Fisher-z intervals. Expected relationship type is design
  metadata only; the workflow does not establish any form of validity, make
  causal claims, or produce automatic thresholds or decisions.
- Researcher Mode now includes a session-only alternative item-weight
  sensitivity audit. Complete researcher-declared schemes must cover all 28
  items, use positive within-dimension weights summing to one, and document
  rationale and evidence status. The audit compares five-dimension and Support
  Gap summaries with the equal-item baseline without exposing unit IDs. It
  does not learn, optimise, rank, recommend, validate, or adopt weights; the
  platform default remains equal-item weighting.
- Researcher Mode now includes a session-only nonparametric Bootstrap
  sampling-uncertainty audit for complete records from one version and round.
  Researchers select 100-10,000 resamples, an 80%-99% percentile interval
  level, and a reproducible seed. The audit reports point estimates, Bootstrap
  means, bias, standard errors, and percentile bounds for five dimension and
  three Support Gap means without exporting draws or unit IDs. It does not
  establish representativeness, validity, causal effects, or stability labels.
- Researcher Mode now includes a session-only longitudinal panel readiness
  audit for complete institutional records across at least two rounds of one
  instrument version. It reports round and complete-panel coverage, adjacent-
  round matching, dimension and Support Gap summaries, and aggregate matched
  change statistics without exporting unit trajectories. Missing rounds are
  not imputed and versions are not pooled. Time order is not treated as
  evidence of improvement, deterioration, policy effects, or causality.
- Researcher Mode now includes a session-only longitudinal attrition and panel-
  composition audit. For adjacent rounds it reports retained, exited, and
  entered institution counts, retention and entry proportions, and bounded
  aggregate comparisons for the five dimensions and three Support Gaps.
  Comparison statistics are suppressed unless both groups contain at least
  three institutions. The workflow does not infer attrition reasons or missing-
  data mechanisms, diagnose bias, generate weights or imputations, expose unit
  identifiers, or treat standardised differences as causal or quality evidence.
- Researcher Mode now includes a session-only paired longitudinal Bootstrap
  uncertainty audit. Matched institutions are resampled as intact pairs for
  each adjacent observed-round comparison. The audit reports point mean changes,
  Bootstrap means, bias, standard errors, and percentile intervals for five
  dimensions and three Support Gaps without exporting IDs, pair trajectories,
  or resampling draws. It does not establish longitudinal comparability,
  significance, improvement, deterioration, policy effects, or causality.
- Researcher Mode now includes a session-only longitudinal timing and fieldwork
  metadata audit. It validates one non-identifying record per version and round,
  then reports collection windows, observed intervals, overlapping windows, and
  changes in administration mode, recruitment scope, sampling-frame reference,
  round purpose, and event-status documentation. Human-entered event notes are
  not reproduced in outputs. Metadata differences are research prompts, not
  quality, bias, validity, improvement, policy-effect, or causal judgements.
- Researcher Mode now includes a session-only longitudinal measurement-
  comparability readiness audit for complete records across rounds of one
  instrument version. It reports round coverage, item distributions, adjacent-
  round standardised mean differences, matched coverage, and descriptive
  correlation-structure differences. It does not run or claim CFA, DIF, or any
  form of measurement invariance, adjust panel composition, make item decisions,
  or infer bias, validity, substantive change, policy effects, or causality.
- Researcher Mode now includes a session-only longitudinal analysis-plan
  readiness audit. Researchers document the unit, population, round contrast,
  change direction, estimand, missing-data and weighting strategies, uncertainty
  method, dependence structure, measurement-comparability basis, evidence
  references, causal-language setting, and preregistration status. The workflow
  produces bounded documentation prompts but does not select a method, fit a
  model, approve a plan, estimate an effect, or validate causal assumptions.
- Researcher Mode now includes a session-only longitudinal policy and context
  event-alignment audit. It combines round timing metadata with a versioned event
  registry to report event chronology, collection-window overlap, adjacent-round
  event context, scope, source, and verification status without reproducing event
  descriptions. Temporal alignment does not establish exposure, mechanisms,
  attribution, confounding control, counterfactual outcomes, policy effects, or
  causality, and no automatic adjustment or effect conclusion is produced.
- Researcher Mode now includes a session-only event exposure-definition readiness
  audit. It distinguishes registered chronology from institution-level exposure and
  records scope, status, timing, intensity, lag, comparator, and evidence fields.
  Unresolved exposure definitions produce documentation prompts. The workflow does
  not infer treatment, dose, exposure, policy effects, or causality.
- Researcher Mode now includes a session-only identification-design readiness
  audit. It records proposed design labels, treatment and comparison definitions,
  time zero, pre/post periods, identification assumptions, confounding,
  anticipation, interference, baseline evidence, negative controls, sensitivity
  analysis, and causal-claim status. It does not fit an effect model or establish
  identification, valid controls, policy effects, or causality.
- Researcher Mode now includes a session-only falsification and sensitivity-plan
  readiness audit. It records planned pretrend checks, placebo event times,
  negative controls, alternative comparisons, windows and specifications,
  unobserved-confounding and missing-data sensitivity, multiple-testing strategy,
  and interpretation rules. It runs no diagnostic or model, and favourable
  results would not prove identification, policy effects, or causality.
- `dd8b3d2 Fix landing page transition warning`: removed `st.rerun()` from a
- Researcher Mode now includes a session-only estimation-specification readiness
  audit. It records the proposed outcome, estimand, population, unit, time scale,
  estimator family, functional form, treatment encoding, comparison contrast,
  adjustment, dependence, standard-error and clustering methods, weighting,
  missing-data handling, event window, multiplicity, uncertainty, software, and
  output-disclosure boundary. It fits no model and produces no coefficient,
  effect estimate, p-value, significance label, approval, policy effect, or
  causal conclusion.
  button callback. The old Dashboard warning *“Calling st.rerun() within a
  callback is a no-op.”* should not reappear.
- `04e5177 Update Streamlit width parameters`: deprecated
  `use_container_width` uses were replaced with `width="stretch"`.
- `a53f8e8 Improve upload validation guidance`.
- `93f084e Add AI interpretation DOCX and PDF downloads`.
- `e60babd Document AI interpretation export formats`.
- `69765b8 Add project history record and workflow screenshot`.

The most recent validated test result was **208 passed** in one complete pytest
run. Streamlit interface tests loaded all current Dashboard routes, including
Inclusive Education, and explicitly checked the estimation-specification audit
workflow, materials, and download entries.

### Deliberately incomplete / future areas

- Inclusive Support is an honest future-development page, not an implemented
  assessment or recommendation engine.
- Inclusive Education is implemented only as an aggregate research prototype.
  Its included dataset is synthetic, its scores and Support Gap are descriptive,
  and it must not be used for child diagnosis, disability determination, teacher
  ranking, or causal conclusions.
- Teacher Development is an honest future-development page, not an implemented
  teacher-quality evaluation engine.
- A knowledge graph, research agents, accounts, collaboration features, and
  real-data project storage are not implemented.
- No approved real-data empirical PRAI, equity, DEA, forecast, policy, or
  inclusive-education conclusion has been produced.

---

## 4. Data governance: absolute rules

The only permitted progression is:

`raw → staging → independent review → processed`

### Never do the following

- Do **not** write unreviewed values to `datasets/processed/`.
- Do **not** alter official raw files, their manifests, checksums, or source
  URLs after archival.
- Do **not** interpolate, smooth, impute, fabricate, delete, or silently
  “clean” extreme values. Record an anomaly and investigate its source,
  definition, unit, geography, and reference year instead.
- Do **not** treat broad age groups (`0–14`, `1–4`, `5–9`, etc.) as strict
  `3–5` or `3–6` preschool-age population.
- Do **not** treat general education expenditure or general public-budget
  expenditure as preschool-specific expenditure.
- Do **not** treat reported `专任教师` / full-time teacher headcount as FTE without
  an official mapping or a separately approved empirical variable redesign.
- Do **not** call sample results real findings, policy effects, or causal
  evidence.
- Do **not** bypass official-site access controls, CAPTCHAs, authentication, or
  browser restrictions.

### Current data status

`datasets/processed/` is empty except for `.gitkeep`.

Reviewed staging records: 12 total.

- 2: conditional policy-simulation parameters only;
- 6: context-only use;
- 4: held for teacher-variable definition review;
- 0: approved for processed analytical use.

The four definition holds are Beijing, Shanghai, Guangdong, and Sichuan
kindergarten datasets. Their reported teacher field has no verified FTE mapping.

### Binding empirical gaps

Do not start real-data model validation until an approved compatible subset has:

1. annual regional population explicitly defined as ages `3–5` or `3–6`;
2. annual preschool- or kindergarten-specific public expenditure with scope,
   unit, and denominator compatibility;
3. an official FTE mapping, or a documented and approved staffing-variable
   redesign; and
4. compatible facility/capacity and qualified-teacher measures.

Relevant source and review documents:

- `docs/Data_Review_Protocol.md`
- `docs/Raw_Source_Review_Packet.md`
- `docs/Pilot_Data_Gap_Register.md`
- `docs/Preschool_Age_Population_Source_Search.md`
- `docs/Fiscal_Source_Search.md`
- `docs/Teacher_Variable_Definition_Review.md`
- `docs/Data_Catalog.md`
- `docs/Review_Queue.md`

### Already resolved review facts

- Shanghai provenance discrepancy was resolved as an official CRLF/LF
  representation difference. Shanghai population and fiscal series are
  context-only; its kindergarten record remains definition-held.
- Guangdong 2017, 2019, and 2020 provincial-level final-accounts preschool
  fields are provincial-level, single-year, context-only references—not
  Guangdong-wide PRAI fiscal inputs.
- Guangdong Yearbook Table 3-4 is incompatible with strict preschool-age
  population; Table 8-2 is general-education-finance context only.

---

## 5. AI Interpretation and DeepSeek rules

The AI module is designed for evidence-bounded research interpretation.

- Keep the system-prompt restrictions intact: supplied results only, no
  invented facts, no causal claim without a stated causal design, uncertainty
  visible, mechanisms as hypotheses only.
- The public app must never contain a shared DeepSeek key or any other provider
  credential.
- The visitor supplies their own key within the current session and explicitly
  confirms external transmission before any call.
- Do not log, commit, display, export, or transmit API keys.
- Do not silently add a different LLM provider or send user data to any service
  without explicit user authority and a documented data-governance review.
- The AI Interpretation record may be exported as `.md`, `.docx`, or `.pdf`;
  all formats must carry the same prompt, model metadata, generated draft, and
  researcher-review disclaimer, but never the key.

When reviewing generated text, reject or revise drafts that:

- infer associations across distinct model blocks (for example PRAI versus a
  separate simulation coverage output);
- claim real regional findings from the sample dataset;
- use causal or policy-effect language without an actual causal design; or
- invent sources, city characteristics, mechanisms, or policies.

See `docs/DeepSeek_Integration.md` and `docs/LLM_Interpretation.md`.

---

## 6. Platform and deployment operations

### Local run

```powershell
cd C:\Users\86198\Desktop\OpenPreEduLab
python -m pip install -r requirements.txt
streamlit run app\streamlit_app.py
```

### Important dependencies

`requirements.txt` includes the reporting libraries `python-docx` and
`reportlab`. Do not remove them: they provide the Word/PDF exports.

### Deployment safety

- The GitHub repository can remain private while the Streamlit app is public.
- Never expose `datasets/raw/`, `datasets/staging/`, reviewer identifiers,
  unapproved evidence, API keys, or restricted data through a public deployment
  mirror.
- Streamlit Cloud normally redeploys after a push to `main`; allow a few minutes
  and use a hard refresh before diagnosing a missing change.
- Public mobile access was checked successfully with HTTP 200 and no detected
  login wall. This is not a substitute for visual device testing.

### Screenshot/showcase rules

- Existing conceptual assets are under `docs/screenshots/`.
- The verified real Workflow screenshot is
  `docs/screenshots/platform_workflow.png`.
- Further wanted assets: Landing Page, Reports format selector, and AI
  Interpretation format selector.
- Do not use screenshots that show an API key, personal data, an unreviewed
  real dataset, browser warnings, or an AI draft that violates the project’s
  evidence boundary.
- Do not create fake “real platform” screenshots. Use actual browser captures.

---

## 7. Coding and testing rules

### Permitted work without additional research-design approval

- fix reproducible software bugs;
- improve clear user-facing errors, documentation, test coverage, and safe UI
  polish;
- add non-destructive validation checks;
- update current-status documentation from authoritative review registers;
- generate report files from existing bounded outputs;
- improve reproducibility while preserving documented model logic.

### Work requiring a documented design decision or user direction

- changing PRAI indicator definitions, weights, or score interpretation;
- replacing FTE with teacher headcount in real empirical models;
- choosing a real-data pilot geography or time period that changes research
  scope;
- treating a source as analytical rather than context-only;
- adding a new external AI provider, paid service, user account system, or data
  storage service;
- publishing a repository, data, or screenshots that may contain sensitive
  material.

### Required verification after changes

For code changes:

```powershell
python -m pytest tests -q
& "C:\Program Files\Git\cmd\git.exe" diff --check
```

For Streamlit changes, also use `streamlit.testing.v1.AppTest` to test the
affected route. For major app changes, load all Dashboard navigation pages.
Do not claim a feature is complete merely because it renders; verify its output,
error path, and export path as applicable.

Use `apply_patch` for text/code edits. Preserve a dirty worktree. Never use
`git reset --hard`, `git checkout --`, force push, or destructive deletion
unless the user has clearly authorised it.

---

## 8. Git and collaboration rules

Git executable:

```powershell
& "C:\Program Files\Git\cmd\git.exe"
```

Recommended normal flow:

```powershell
& "C:\Program Files\Git\cmd\git.exe" status -sb
& "C:\Program Files\Git\cmd\git.exe" fetch origin
& "C:\Program Files\Git\cmd\git.exe" add <only intended files>
& "C:\Program Files\Git\cmd\git.exe" commit -m "Clear, scoped message"
& "C:\Program Files\Git\cmd\git.exe" push origin main
```

If GitHub resets the connection:

- retain the local commit;
- retry a normal push later;
- do not force push;
- report whether the commit is local-only or has been confirmed pushed;
- do not invent remote or CI results.

Independent reviewer: `Barnabe-Zihan-Ding`. Historical review decisions are
already recorded in the metadata registers. New real-data promotion requires
an independently reviewable record; do not self-certify raw/staging evidence as
approved for processed use.

---

## 9. Priority queue for continuation

Proceed in this order unless the user explicitly changes priorities.

1. **Complete showcase assets:** import only approved real screenshots, update
   README and `docs/Project_Showcase.md`, then verify links and push.
2. **Continue definition-compatible source discovery:** use normal authorised
   browser access to official census/yearbook/finance publications. Archive only
   original, official candidate files with URL, retrieval date, visible table,
   scope, unit, and checksum.
3. **Independent review:** route every candidate through raw → staging → review.
   Do not place candidate values in processed merely to unblock the interface.
4. **Real-data model validation:** only after processed data exists. Validate
   PRAI directions, standardisation, weights/sensitivity, DEA inputs/outputs,
   forecasts, and scenario parameters. Treat the first run as software and
   reproducibility validation, not a policy study.
5. **Platform experience:** continue browser/mobile/accessibility checks,
   meaningful upload feedback, and documentation accuracy.
6. **Inclusive Education maintenance:** continue method review, accessibility
   checks, and synthetic-data validation without promoting records to
   `datasets/processed/`.
7. **v0.2 design:** define theory, ethics, data, and interaction requirements
   for Teacher Development before implementation.

---

## 10. Definition of “done” for the current phase

The v0.1 software prototype is functionally complete. The empirical research
phase is **not** complete until definition-compatible, independently reviewed
real data are present in `datasets/processed/` and the models have been
validated against that data. Accuracy, provenance, reproducibility, and
children-centred research ethics take priority over speed or apparent
completeness.
