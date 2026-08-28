# Inclusive Education Longitudinal Measurement Comparability Readiness Protocol

## 1. Purpose

Observed score changes are difficult to interpret unless the instrument has
comparable meaning across time. This protocol provides a conservative readiness
audit of item-response patterns across administration rounds within one
instrument version.

It is not a formal longitudinal measurement-invariance analysis. It does not
establish configural, metric, scalar, strict, partial, approximate, or other
forms of invariance or non-invariance.

## 2. Research boundary

The audit is designed to identify questions for future governed measurement
research. It does not establish:

- measurement invariance, differential item functioning, bias, or fairness;
- validity, reliability, or score equivalence across rounds;
- substantive institutional change, improvement, deterioration, or quality;
- policy effects, mechanisms, counterfactual outcomes, or causality; or
- that an item should be retained, revised, removed, or reweighted.

No child, teacher, family, identifiable institution, or case-level data should
be uploaded.

## 3. Data requirements

The workflow uses the existing complete institutional response schema:

- `pseudonymous_unit_id`;
- `instrument_version`;
- `administration_round`; and
- all 28 inclusive-education item responses.

One version is analysed at a time. At least two rounds are required, and every
round must contain at least five complete records. This minimum is a prototype
privacy and computation condition, not a scientific power or adequacy claim.
Missing item responses are not imputed and versions are not pooled.

## 4. Round coverage and item distributions

For each round, the audit reports complete and unique institutional record
counts. For every item and round it reports:

- arithmetic mean;
- sample standard deviation;
- proportion at the declared source-scale minimum; and
- proportion at the declared source-scale maximum.

Distribution changes may reflect sample composition, administration, timing,
context, response style, measurement change, or substantive institutional
variation. The audit does not select among these explanations.

## 5. Adjacent-round item differences

Rounds are ordered by their positive integer labels. Only adjacent observed
rounds are compared. For every item, the platform reports the raw mean
difference as earlier round minus later round. When pooled variance is positive,
it also reports:

`standardised difference = (earlier mean - later mean) / pooled standard deviation`

If pooled variance is zero, the standardised difference is undefined. No
automatic magnitude threshold, significance test, traffic-light label, item
flag, or comparability decision is applied.

The comparisons use all complete records in each round. They are not adjusted
for retained, exited, or entering institutions. Matched-unit coverage is shown
as context, and results must be reviewed alongside the longitudinal attrition
and panel-composition audit.

## 6. Correlation-structure differences

For each adjacent round pair, Pearson item-correlation matrices are calculated
when all items have positive variance in both rounds. Upper-triangle differences
are summarised using:

- root mean square correlation difference; and
- maximum absolute correlation difference.

If either round contains a zero-variance item, the correlation summaries are
reported as undefined rather than deleting an item or regularising the matrix.
Correlation differences are descriptive and sample-dependent. They are not a
test of factor structure or measurement invariance.

## 7. Relationship to other audits

Interpret this workflow alongside:

- instrument versioning, to confirm that wording, dimensions, scales, and
  weights were not silently changed;
- longitudinal timing and fieldwork metadata, to document intervals and
  implementation differences;
- attrition and panel composition, to describe sample changes; and
- longitudinal panel and paired Bootstrap audits, to describe matched changes
  and their sampling uncertainty.

None of these descriptive audits substitutes for an explicit longitudinal
measurement model.

## 8. Future governed analysis

Depending on response properties and theory, future methods may include
longitudinal CFA, ordinal estimators, item response models, alignment or
approximate invariance methods, and sensitivity analyses. A future study must
document the construct model, estimator, identification constraints, residual
structure, missing-data approach, sample-size rationale, fit assessment,
uncertainty, multiplicity, partial-invariance decisions, ethics, and
interpretation limits.

The method must follow the research design and measurement theory rather than
software availability. PCA, descriptive correlations, or standardised mean
differences must not be relabelled as CFA or measurement invariance.

## 9. Privacy and export

Uploads are processed in the current Streamlit session and are not intentionally
persisted. Exports contain aggregate coverage, item summaries, adjacent-round
differences, correlation-structure summaries, and research-question candidates.
They exclude pseudonymous IDs and institutional trajectories.

## 10. Completion record

A readiness record should document the instrument version, round definitions,
sample and matching coverage, response scale, administration conditions,
attrition context, item distributions, undefined results, correlation summaries,
and future model requirements.

Completion means longitudinal measurement-comparability questions were audited
reproducibly. It does not mean score comparability, invariance, improvement,
policy effects, or causal pathways have been established.
