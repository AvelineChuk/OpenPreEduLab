# Inclusive Education Analysis Reproducibility Readiness Protocol

## 1. Purpose

This protocol records whether a future inclusive-education analysis has a
traceable data snapshot, code version, software environment, specification
lock, random-seed policy, quality-control record, and output boundary.

It is a **prototype documentation audit**. It does not execute code, inspect a
repository, open a data snapshot, reproduce a result, or approve an analysis.

## 2. Research problem

Even a clearly written estimation specification may be difficult to reproduce
if the exact data, code, dependencies, deviations, and disclosure rules are not
recorded. This workflow asks what evidence would be needed for another
researcher to reconstruct the planned execution without relying on memory or
undocumented local files.

## 3. Required record

Each CSV row represents one non-identifying execution record linked to one
estimation specification and instrument version. It records:

- immutable data-snapshot identity, date, and checksum;
- code-repository reference and exact commit;
- environment-lock reference and software environment;
- random-seed policy;
- specification-lock and deviation-log status;
- execution, quality-control, and review status;
- output-storage and disclosure boundaries.

Free-text researcher notes are validated but excluded from audit outputs.

## 4. Audit logic

The audit uses explicit missing-state terms such as not_recorded, not_defined,
and pending. It reports unresolved documentation prompts and boolean
documentation indicators. It does not calculate a readiness score, pass/fail
label, ranking, or recommendation.

If a specification is recorded as amended, a traceable deviation-log reference
is expected. A completed record still does not demonstrate that the deviation
was justified or that the resulting analysis is valid.

## 5. Interpretation boundary

The workflow produces no coefficient, effect estimate, p-value, significance
label, model ranking, policy-effect estimate, or causal conclusion. A complete
record does not verify:

- source-data accuracy or representativeness;
- code correctness;
- estimator or standard-error validity;
- identification assumptions;
- result reproducibility;
- substantive or causal interpretation.

## 6. Data governance

Records must not include child identifiers, institution-level outcome rows,
credentials, private repository tokens, restricted paths, or confidential
review notes. Public exports are limited to documentation summaries, prompts,
and research-question candidates.

No record created by this workflow is promoted to datasets/processed/.

## 7. Future validation

A governed future reproducibility study would require an authorised data
snapshot, independently reviewable code and environment locks, a preregistered
specification, controlled execution, documented quality checks, and a separate
review of allowed outputs. Successful rerunning would be evidence about
computational reproducibility only; it would not establish validity or
causality.
