# Inclusive Education Preliminary Reliability Protocol

## 1. Purpose and boundary

This protocol defines preliminary internal-consistency and repeated-administration stability audits for complete, non-identifying institutional research records. Reliability concerns the consistency of measurements under a stated design. It does not establish content validity, construct validity, unidimensionality, fairness, measurement invariance, external validity, or causal validity.

No coefficient threshold is built into the platform. The software does not automatically retain, revise, move, split, or remove an item.

## 2. Data requirements

One row represents one pseudonymous institutional research unit, one instrument version, and one administration round. All 28 current item responses must be complete, numeric, finite, and inside the declared response interval. Missing values are rejected rather than imputed.

The same unit, version, and round may appear only once. Version labels must not be mixed within a repeated-administration pair. Do not include institution names, child or family records, teacher evaluations, clinical information, or other unnecessary personal data.

## 3. Internal consistency

Internal consistency is calculated separately for each instrument version, administration round, and conceptual dimension. At least three complete responses are required per group.

For a dimension containing k items, Cronbach's alpha is:

`alpha = k / (k - 1) * (1 - sum(item variances) / variance(total score))`

The platform also reports:

- corrected item-total correlation, where an item is correlated with the sum of the other items in its dimension;
- alpha if the item is removed; and
- observed item variance.

If the total score has no variance, alpha is undefined and is reported as missing rather than forced to zero or one.

Alpha is affected by item count, covariance structure, sample heterogeneity, response range, and violations of the assumptions behind its interpretation. A high alpha does not prove unidimensionality, validity, fairness, or absence of redundant wording. A low alpha does not by itself justify deleting an item.

## 4. Repeated-administration stability

Repeated-administration analysis compares two explicitly selected rounds for matched pseudonymous units within one instrument version. At least three matched units are required.

For each dimension, the platform reports:

- first- and second-round means;
- mean change;
- mean absolute change;
- Pearson correlation; and
- two-way mixed, single-measure consistency ICC(3,1).

A matching-coverage table reports first-round, second-round, matched, and unmatched unit counts. Unmatched units are not silently discarded from the coverage record.

Correlation describes rank-order association and does not show agreement in absolute levels. ICC(3,1) reflects consistency for the submitted design and assumptions. Neither coefficient proves temporal validity or rules out real institutional change, learning, recall, administration effects, or sampling error.

## 5. Interpretation rules

Reliability results must be interpreted with the conceptual framework, content review, cognitive interviews, feasibility evidence, version registry, administration procedures, sample size, response distributions, and missing-data exclusions.

The platform does not provide red/amber/green labels, automatic pass/fail thresholds, score correction, item deletion, cross-version conversion, child assessment, or institution ranking.

## 6. Privacy and governance

Use pseudonymous unit IDs and an approved data-governance process. Uploaded reliability records are processed in the current Streamlit session and are not intentionally persisted. Downloadable summaries exclude unit IDs.

If multiple raters rather than repeated administrations are studied, the rater design and appropriate agreement model must be specified separately. This prototype does not infer a rater design from the uploaded data.

## 7. Completion criteria

A preliminary reliability audit is complete only when the instrument version, rounds, unit of analysis, sampling approach, administration interval, response interval, exclusions, coefficient specification, sample size, uncertainty, and limitations are documented. Completion records software output; it does not mean the instrument is validated.
