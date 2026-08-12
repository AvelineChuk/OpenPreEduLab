# Inclusive Education External Measure Relationship Readiness Protocol

## 1. Purpose and boundary

This protocol defines a conservative readiness audit for studying relationships
between the five prototype Inclusive Education dimensions and one independently
sourced, non-identifying institutional measure. It helps researchers inspect
paired-record coverage, descriptive associations, and uncertainty before
designing a governed validation study.

The audit does not establish convergent validity, discriminant validity,
criterion-related validity, predictive validity, external validity, or causal
validity. Correlation with another variable is not sufficient evidence that
either measure is valid.

## 2. External measure requirements

The external variable must have:

- a clear institutional-level construct definition;
- a documented name and source;
- provenance independent enough to evaluate common-method risk;
- a justified timing relationship with the inclusive education instrument;
- an ethically and legally permitted linkage process; and
- complete finite numeric values for the selected audit records.

Do not use child diagnoses, disability classifications, family case data,
teacher performance labels, clinical decisions, or personally identifying
information as an external measure. The workflow is not designed to predict or
classify children, teachers, or institutions.

## 3. Expected relationship metadata

The researcher records one design category:

- `convergent_candidate`;
- `discriminant_candidate`;
- `criterion_related_candidate`; or
- `exploratory_related_measure`.

This field documents the proposed research design. The software does not use it
to choose a threshold, test a directional hypothesis, or declare that evidence
supports or contradicts validity. The underlying theory and operational
definitions must be documented outside the CSV.

## 4. Data structure

One row represents one pseudonymous institutional research unit, one instrument
version, one administration round, the complete 28-item response block, and one
external-measure value. Every row in a selected version and round must use the
same external measure name, source, and expected relationship type.

Missing item or external-measure values are rejected rather than imputed. The
analysis requires at least five complete paired records as a prototype
computation condition. This is not a scientific power, precision, or validation
threshold. A substantive validation study requires its own sample-size and
precision rationale.

## 5. Five-dimension scores

Item responses are linearly converted from the declared source interval to
0–100. Each current dimension score is then the equal-item arithmetic mean.
Equal weighting remains a prototype assumption requiring independent review and
sensitivity analysis.

The external measure is not automatically rescaled because its original units
may carry substantive meaning. Researchers must document the unit, direction,
range, and interpretation.

## 6. Association summaries

For each dimension the platform reports:

- paired complete record count;
- dimension mean and sample standard deviation;
- Pearson correlation;
- an approximate two-sided 95% Fisher-z interval for Pearson correlation;
- Spearman rank correlation; and
- whether correlation is defined.

For sample size n and Pearson correlation r, the interval uses:

`z = arctanh(r)`

`standard error = 1 / sqrt(n - 3)`

and transforms the normal-approximation limits back with `tanh`. When a
dimension or external measure has zero variance, correlations and intervals are
reported as undefined. Perfect correlations are reported with a degenerate
interval rather than numerical infinity.

Pearson correlation describes linear association; Spearman correlation
describes monotonic rank association. Neither is evidence of causation,
agreement, prediction quality, construct identity, or absence of confounding.
The approximate interval relies on assumptions and may be unstable in small or
non-representative samples.

## 7. Interpretation risks

Observed relationships may reflect:

- overlapping item content or common-method variance;
- institution selection or restricted range;
- administration timing or shared respondents;
- response styles and data-processing choices;
- measurement error in either instrument;
- contextual variables or omitted confounders; or
- chance and sampling uncertainty.

A large correlation does not automatically demonstrate convergence. A small
correlation does not automatically demonstrate discrimination or invalidate an
instrument. Criterion-related claims require a defensible criterion, temporal
design, and analysis plan. Predictive and causal language requires a separately
appropriate design.

## 8. Research question candidates

The platform generates bounded questions concerning external-measure
independence and provenance, stability under alternative scoring assumptions,
and potential common-method, timing, context, or selection explanations. These
are research question candidates, not validated findings.

## 9. Privacy and governance

Uploaded records are processed in the current Streamlit session and are not
intentionally persisted. Downloaded summaries exclude pseudonymous unit IDs and
individual external-measure values. Researchers remain responsible for linkage
governance, data minimisation, consent or other legal basis, disclosure risk,
and independent review.

## 10. Future validation

A future validation study should preregister or otherwise govern its theory,
external measure, expected pattern, sample, timing, exclusions, scoring,
missing-data handling, uncertainty, multiple comparisons, sensitivity checks,
and interpretation rules. Replication with an independent sample is preferred.

Synthetic data are suitable only for software demonstration and testing. A
successful readiness audit means the descriptive workflow ran reproducibly; it
does not mean any form of validity has been established.
