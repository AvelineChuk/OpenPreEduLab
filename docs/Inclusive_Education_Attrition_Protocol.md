# Inclusive Education Longitudinal Attrition and Panel Composition Protocol

## 1. Purpose and boundary

This protocol defines a descriptive audit of retention, exit, entry, and panel
composition across adjacent observed administration rounds of one Inclusive
Education instrument version.

The audit supports questions about whether longitudinal coverage may be
selective. It does not establish why institutions leave or enter, whether data
are missing completely at random, missing at random, or missing not at random,
whether longitudinal estimates are biased, or which weighting or imputation
method should be used.

## 2. Data requirements

One row represents one pseudonymous institutional unit, one instrument version,
and one positive-integer administration round. All 28 item responses must be
complete, numeric, finite, and inside the declared response interval.

Stable pseudonymous IDs are used internally to link adjacent rounds. They must
not contain institution names or other directly identifying information.
Analysis is restricted to one explicitly selected version; versions are not
pooled.

At least two rounds are required. Unlike the longitudinal readiness audit, this
workflow does not fail merely because an exit or entry group is small. It
reports group counts but suppresses descriptive score statistics unless both
groups in a comparison contain at least three institutions.

The three-institution rule is a prototype disclosure and computation condition,
not a scientific sample-size, privacy, or inferential threshold.

## 3. Adjacent-round panel groups

For adjacent observed rounds t and t+1, institutions are classified internally
as:

- retained: observed in both rounds;
- first-round only: observed at t but not at t+1; and
- second-round only: observed at t+1 but not at t.

Nonconsecutive labels, such as rounds 1, 3, and 6, are treated as adjacent
observed pairs 1→3 and 3→6. The audit does not assume equal time intervals.

The coverage summary reports:

- first- and second-round unit counts;
- retained count;
- first-round-only count;
- second-round-only count;
- retention proportion; and
- entry proportion in the second round.

These are linkage summaries. “Exit” does not necessarily mean withdrawal from
education, closure, dropout, or adverse institutional change. “Entry” may
reflect recruitment, replacement, eligibility changes, delayed participation,
or data-linkage differences.

## 4. Scoring

Item responses are linearly converted to 0–100. The current equal-item scores
are calculated for Policy Support, Resource Support, Inclusive Practices, Child
Participation, and Equity. The audit also calculates the three descriptive
Support Gap indicators.

These scoring assumptions remain prototypes. Composition comparisons should be
interpreted alongside content, reliability, construct, weighting, subgroup,
uncertainty, and longitudinal-comparability evidence.

## 5. Composition comparisons

The audit performs two descriptive comparisons for each adjacent round pair:

1. retained versus first-round-only institutions, using their first-round
   scores; and
2. retained versus second-round-only institutions, using their second-round
   scores.

For each dimension and Support Gap, when both groups contain at least three
institutions, the platform reports:

- group counts;
- reference and comparison group means;
- raw mean difference, defined as reference minus comparison; and
- pooled-standard-deviation standardised mean difference.

If pooled variance is zero, the standardised difference is undefined and is
reported as missing. If either group is smaller than three, means and
differences are suppressed and the output records the suppression reason.

A standardised difference is not an attrition model, probability of response,
causal effect, significance test, or evidence that an institution left because
of its score.

## 6. Interpretation risks

Observed composition differences may reflect:

- recruitment and eligibility changes;
- institutional consent or administrative burden;
- data-linkage errors;
- timing and fieldwork conditions;
- geographic or organisational context;
- measurement error or response styles;
- chance in small samples; or
- mechanisms related or unrelated to the measured constructs.

Absence of an observed difference does not prove that attrition is ignorable.
Presence of a difference does not establish attrition bias or identify an
appropriate correction.

## 7. Prohibited automatic actions

The platform does not:

- infer a missingness mechanism;
- estimate response probabilities;
- generate attrition or inverse-probability weights;
- impute missing rounds;
- delete retained or unmatched records;
- label institutions, rounds, or samples as biased;
- rank institutions;
- infer improvement, deterioration, or quality; or
- make causal or policy-effect claims.

## 8. Future methods

Future governed studies may require collection of non-sensitive participation
status and fieldwork reasons, logistic response models, inverse-probability
weighting, multiple imputation, pattern-mixture or selection models, delta
adjustments, refreshment samples, multilevel missing-data models, and formal
sensitivity analysis.

Every method requires explicit missingness assumptions, adequate sample size,
diagnostics, uncertainty, disclosure review, and substantive justification.
No correction should be applied merely because a descriptive difference is
visible.

## 9. Privacy and governance

Uploaded records are processed in the current Streamlit session and are not
intentionally persisted. Downloaded summaries exclude pseudonymous IDs and
individual trajectories. Small-group score summaries are suppressed.

Researchers remain responsible for data minimisation, linkage governance,
ethical approval, lawful processing, retention rules, and disclosure-risk
review.

## 10. Completion record

An attrition-readiness record should document the version, round definitions,
dates and intervals, recruitment and follow-up process, unit identifiers,
linkage rules, group counts, suppressed comparisons, descriptive differences,
known fieldwork reasons, missingness assumptions not yet tested, and future
analysis requirements.

Completion means panel composition was audited reproducibly. It does not mean
attrition is random, harmless, corrected, or causally explained.
