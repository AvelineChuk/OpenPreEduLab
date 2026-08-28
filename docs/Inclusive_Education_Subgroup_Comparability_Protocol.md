# Inclusive Education Subgroup Measurement Comparability Readiness Protocol

## 1. Purpose and boundary

This protocol defines a conservative readiness audit for future subgroup
measurement-comparability research. It asks whether complete institutional
response records provide enough transparent group coverage and descriptive
information to design a separately governed differential item functioning
(DIF) or measurement-invariance study.

The audit does not establish measurement invariance, non-invariance, DIF,
bias, fairness, discrimination, or substantive differences between groups. It
is not a child, teacher, institution, or group evaluation tool.

## 2. Permitted comparison groups

`comparison_group` should represent an ethically justified institutional-level
research category, such as an explicitly documented institution type,
administration mode, or sampling stratum. Researchers must document why the
grouping is theoretically relevant and why comparison is ethically appropriate.

Do not use this workflow for child disability labels, diagnoses, family cases,
teacher performance categories, identifiable institutions, or other sensitive
personal classifications. Group labels do not explain why a descriptive
difference appears.

## 3. Data requirements

One row represents one pseudonymous institutional research unit, one instrument
version, one administration round, and one comparison group. All 28 item
responses must be complete, numeric, finite, and inside the declared response
interval. Missing responses are rejected rather than imputed.

Analysis is restricted to one explicitly selected version and administration
round. Versions and rounds are not pooled. At least two groups are required.
Each selected group must contain at least five complete records. This minimum is
a prototype privacy and computation condition, not a scientific sample-size or
power threshold. Future DIF or multi-group factor analysis will generally need
a separately justified and substantially stronger sampling plan.

## 4. Group coverage

The coverage table reports the complete record count and current item count for
each selected group. It does not expose pseudonymous unit IDs. Unequal group
sizes are shown rather than corrected by resampling or weighting.

Coverage is necessary but not sufficient for comparability. Recruitment,
selection, administration, non-response, institutional context, and group
definition may all affect observed patterns.

## 5. Item distribution summaries

For each item and group, the platform reports:

- complete record count;
- arithmetic mean;
- sample standard deviation;
- proportion at the declared source-scale minimum; and
- proportion at the declared source-scale maximum.

These values describe response distributions. They do not show that an item is
biased, valid, fair, equivalent, or appropriate for removal. Endpoint patterns
may reflect context, sampling, administration, response style, instrument
design, or genuine institutional variation.

## 6. Pairwise standardised mean differences

For each pair of groups and item, the raw mean difference is reported as first
group minus second group. When pooled sample variance is positive, the platform
also reports:

`standardised difference = (mean_1 - mean_2) / pooled standard deviation`

If pooled variance is zero, the standardised difference is undefined and is
reported as missing. No automatic magnitude threshold, traffic-light label,
significance test, item flag, group ranking, or fairness conclusion is applied.

A standardised mean difference is not a DIF statistic. It does not condition on
an underlying construct or specify a measurement model. It cannot distinguish
measurement differences from sampling, context, administration, or substantive
institutional differences.

## 7. Correlation-structure difference summaries

For each pair of groups, Pearson item-correlation matrices are calculated when
all items have positive variance in both groups. The upper-triangle differences
are summarised using:

- root mean square correlation difference; and
- maximum absolute correlation difference.

If either group contains a zero-variance item, these summaries are reported as
undefined rather than automatically deleting the item or regularising the
matrix. Correlation-structure differences are descriptive and sample-dependent.
They do not constitute a test of configural, metric, scalar, strict, or other
forms of measurement invariance.

## 8. Research question candidates

The platform supplies bounded questions for future work, including whether
item-response relationships are comparable under an explicit measurement
model, whether distribution differences warrant a governed DIF investigation,
and whether group definitions and sampling are substantively and ethically
appropriate.

These are research question candidates, not findings or hypotheses confirmed
by the platform.

## 9. Future validation

Any empirical comparability conclusion requires a separately governed design.
Depending on instrument properties and response scales, future methods may
include multi-group CFA, ordinal estimators, DIF models, item response theory,
alignment methods, sensitivity analyses, qualitative follow-up, or other
theoretically justified approaches. The method must not be selected solely
because it is available in software.

Future studies must document the construct model, group definitions, estimator,
identification constraints, missing-data strategy, sample-size rationale,
multiple-testing approach, uncertainty, model fit, sensitivity, ethical review,
and interpretation limits. Synthetic data remain for demonstration and testing
only.

## 10. Completion record

A readiness audit record should state the instrument version, round, unit of
analysis, group definition, ethical justification, sampling process, response
scale, group counts, exclusions, distribution summaries, undefined results,
and future study requirements. Completion records a reproducible descriptive
audit; it does not mean measurement comparability has been established.
