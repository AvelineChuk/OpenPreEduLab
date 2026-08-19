# OpenPreEduLab Continuation README

This document is the short operational handoff for a new Codex conversation.
Read it before changing the repository. It complements, but does not replace,
CODEX_HANDOFF.md.

## Project identity

OpenPreEduLab is an open-source, AI-assisted research infrastructure prototype
for preschool education research. It is research software, not a chatbot,
clinical service, school-management product, validated policy-evaluation system,
or automatic paper-writing system.

The intended workflow is:

Research question / policy -> documented data -> statistical models -> simulation -> bounded AI interpretation -> researcher-reviewed output

The researcher remains responsible for theory, data governance, variable
definitions, model selection, causal design, interpretation, and publication.

## What is implemented

### Core research platform

- Streamlit landing page and research workspace.
- Preschool Resource Allocation Index (PRAI) prototype.
- Equity metrics: coefficient of variation, Gini, and Theil.
- DEA efficiency prototype.
- Population, teacher-demand, and fiscal-requirement forecast prototypes.
- Conditional policy-simulation engine.
- Matplotlib visualisation layer.
- Markdown, Word, and PDF research-report exports.
- Evidence-bounded optional DeepSeek interpretation with visitor-supplied keys.
- Automated tests and GitHub Actions.

### Inclusive Education Research Module

The module follows the conceptual pathway:

Policy -> Resources -> Practices -> Child Participation -> Equity

Implemented functions include:

- synthetic institution-level demonstration data;
- five prototype dimension scores;
- descriptive Gap_RP, Gap_PC, and overall Support Gap;
- radar, pathway, gap-bar, comparison, and heatmap visualisations;
- Researcher Mode with descriptive statistics, correlations, equity analysis,
  gap analysis, and exploratory clustering;
- bounded Research Insights and research-question candidates;
- exploratory scenario interfaces;
- CSV, Markdown, Word, and PDF exports where applicable;
- semantic chart tables, heading hierarchy, focus states, contrast guards,
  narrow-screen overflow protection, and high-zoom reflow safeguards;
- a seven-link Researcher Mode quick-navigation map;
- a six-intent task guide;
- task-to-workflow routing that shows associated methods without ranking them;
- 25 methodological-readiness workflows across five phases;
- content-review, cognitive-interview, versioning, feasibility, reliability,
  construct-structure, subgroup, external-measure, weight-sensitivity,
  Bootstrap, longitudinal, policy-design, reproducibility, reporting,
  traceability, and release-readiness audits.

All readiness workflows are session-only planning or descriptive audits. They
do not turn incomplete evidence into validation, approval, causal effects, or
publication decisions.

## What is not implemented or not complete

- No approved real-data analytical panel exists in datasets/processed/.
- No real inclusive-education conclusion has been produced.
- Synthetic data are not evidence about real kindergartens, children, teachers,
  regions, or policies.
- The Inclusive Education instrument has no completed expert-rating study,
  cognitive-interview study, empirical linking study, governed reliability
  study, or construct/fairness validation study.
- No child-level assessment, diagnosis, disability determination, placement
  recommendation, teacher ranking, or clinical judgement is implemented.
- Support Gap is descriptive/diagnostic only; it is not a causal estimator.
- No account system, collaboration system, knowledge graph, research-agent
  system, or real-data project storage is implemented.
- Inclusive Support and Teacher Development remain design/future-development
  pages, not evaluation engines.
- Physical mobile/tablet review, verifiable browser zoom at 200%, complete
  keyboard traversal, real screen-reader testing, third-party widget contrast
  review, and stakeholder cognitive-load review remain manual work.
- Real-data model validation remains blocked until definition-compatible data
  pass independent review.

## Data and ethical boundaries

The only permitted data progression is:

raw -> staging -> independent review -> processed

At the current handoff:

- datasets/processed/ must contain only .gitkeep;
- unreviewed values must never be copied there;
- raw official files, manifests, checksums, and source URLs must not be
  silently changed;
- missing values must not be silently imputed;
- extreme values must not be silently deleted, smoothed, or fabricated;
- broad age bands must not be relabelled as strict preschool-age populations;
- general education expenditure must not be relabelled as preschool expenditure;
- teacher headcount must not be relabelled as FTE without an approved mapping;
- context-only or conditional scenario records must not be treated as empirical
  model inputs.

## What a Codex agent may do without new design approval

- fix reproducible software bugs;
- improve safe interface wording, accessibility, and error messages;
- add non-destructive validation and regression tests;
- maintain documentation and current-status records;
- generate bounded reports from existing outputs;
- preserve and improve reproducibility without changing documented definitions;
- run tests, compile checks, diff checks, and local Streamlit AppTest checks;
- commit intended project files with a clear scoped message;
- perform a normal fetch and normal push when the user explicitly asks to
  publish and the files are safe to publish.

## What a Codex agent must not do

- do not force-push, reset hard, or discard unrelated user changes;
- do not upload personal papers, ZIP archives, render directories, temporary
  profiles, private screenshots, API keys, reviewer identities, raw archives,
  staging records, or unapproved evidence;
- do not expose personal or child-level data through the public app;
- do not add an external AI provider or transmit data without explicit
  authority and a documented data-governance decision;
- do not claim that synthetic results are real findings;
- do not claim that Support Gap proves a causal mechanism;
- do not diagnose children, determine disability status, normalise children,
  replace teachers, replace researchers, or make clinical judgements;
- do not convert a readiness audit into a score, pass/fail approval, validity
  conclusion, fairness conclusion, or causal conclusion;
- do not start real-data validation before independent review and compatible
  variable definitions;
- do not use a method merely because it makes the interface look complete.

## Rules learned from previous mistakes

1. Inspect the repository and read the handoff before editing.
2. Check status and preserve unrelated dirty files before staging anything.
3. Stage only explicitly intended project files; never use a broad git add .
   when personal materials are present.
4. Treat Windows patch encoding as a risk. After every patch, run
   python -m py_compile on changed Python files and run interface tests.
5. A feature is not complete because it renders once. Test its normal path,
   error path, export path, and route navigation where applicable.
6. Do not insert tests or imports with approximate line context. Run collection
   and compile checks immediately after structural edits.
7. Keep semantic accessibility fallbacks independent of colour or chart
   geometry, and do not claim real device testing from CSS alone.
8. Keep research language bounded: use descriptive, prototype, possible
   interpretation, and research-question candidate where evidence is not
   validated.
9. Do not let a navigation aid imply a required research sequence or readiness
   hierarchy.
10. If a network push fails, keep the local commit, retry a normal push later,
    and report local-versus-remote status honestly. Never force-push.
11. Clean only a test temporary directory after verifying its exact path.
12. Never promote data to datasets/processed/ merely to unblock a demo.

## Verification at this handoff

- Latest complete test collection: 236 tests.
- Latest complete run: 236 passed.
- git diff --check: passed after the latest committed change.
- datasets/processed/: .gitkeep only.
- Current branch: main.
- The latest local inclusive-education commit is
  a2b76c5 Route inclusive research tasks to methods.
- Before publication, check the actual remote divergence again; do not infer
  successful publication from a local commit alone.

## Safe continuation order

1. Read this file and CODEX_HANDOFF.md.
2. Check git status -sb, recent log, remote status, and processed-data
   boundary.
3. If the user requests publication, push only safe committed changes using
   normal git push origin main.
4. If continuing Inclusive Education, prioritise manual accessibility evidence,
   method review, synthetic-data robustness, and documentation accuracy.
5. Do not implement real-data claims, child assessment, or causal prediction
   without a new documented research-design decision and independent review.

## Key links

- Public platform: https://openpreedulab-85aycdefait8stbdivqxpx.streamlit.app/
- Project repository: https://github.com/AvelineChuk/OpenPreEduLab
- Main operational handoff: ../CODEX_HANDOFF.md
- Inclusive Education framework: Inclusive_Education_Framework.md
- Support Gap methodology: Support_Gap_Methodology.md
- Inclusive Education user guide: Inclusive_Education_User_Guide.md
- Accessibility check: Inclusive_Education_Accessibility_Check.md
- Next work plan: Next_Work_Plan.md

