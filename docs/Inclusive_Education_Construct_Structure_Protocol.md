# Inclusive Education Construct Structure Readiness Protocol

## 1. Purpose and research boundary

This protocol defines a conservative exploratory audit of the current 28-item
inclusive education instrument. It examines whether a selected complete sample
can support item-correlation and principal-component inspection. It does not
confirm the proposed five dimensions, establish construct validity, or replace
theory, content review, cognitive interviews, reliability work, fairness review,
or an independently designed factor-validation study.

The platform reports exploratory structural evidence only. Principal component
analysis (PCA) is not labelled as exploratory factor analysis (EFA) or
confirmatory factor analysis (CFA).

## 2. Data requirements

One row represents one pseudonymous institutional research unit, one instrument
version, and one administration round. All 28 item responses must be complete,
numeric, finite, and within the declared response interval. Missing values are
rejected rather than imputed.

The researcher must explicitly select one instrument version and one
administration round. The platform does not pool versions or rounds. Downloaded
summaries exclude pseudonymous unit IDs.

The prototype requires more complete observations than items. With 28 items,
the selected sample must therefore contain at least 29 complete observations.
This is a software computation condition intended to avoid a necessarily
rank-deficient sample correlation matrix. It is not a universal scientific
sample-size rule and does not demonstrate adequate statistical power,
representativeness, or stability.

## 3. Correlation matrix and readiness checks

The workflow calculates a Pearson item-correlation matrix. Items with zero
variance are rejected because their correlations are undefined. A singular or
numerically rank-deficient correlation matrix is also rejected rather than
repaired with automatic item deletion, regularisation, or a pseudo-inverse.

The readiness summary includes the observation count, item count,
observation-to-item ratio, selected component count, and correlation-matrix
determinant. These values describe the submitted analysis sample only.

## 4. Kaiser-Meyer-Olkin diagnostics

KMO compares squared zero-order correlations with squared partial correlations.
For items i and j:

`KMO = sum(r_ij^2) / [sum(r_ij^2) + sum(p_ij^2)]`

where `r_ij` is the Pearson correlation and `p_ij` is the corresponding partial
correlation derived from the inverse correlation matrix. The platform reports
an overall KMO and item-level KMO values.

No automatic KMO threshold, traffic-light label, pass/fail result, or item
decision is applied. KMO is sample-dependent and does not establish the number,
meaning, or validity of latent constructs.

## 5. Bartlett's test of sphericity

For n observations and p items, the prototype reports:

`chi-square = -[n - 1 - (2p + 5)/6] * ln(det(R))`

with `p(p - 1)/2` degrees of freedom, where R is the item-correlation matrix.
The p-value is calculated from the chi-square survival function.

Bartlett's test examines whether the observed correlation matrix differs from
an identity matrix under its assumptions. It does not prove that a specific
factor model is correct, that five dimensions exist, or that items should be
retained or removed. Large samples may make small correlations statistically
detectable.

## 6. Eigenvalues and exploratory principal components

The platform eigendecomposes the correlation matrix and reports all 28
eigenvalues, explained-variance ratios, and cumulative explained-variance
ratios. The researcher explicitly chooses the number of unrotated principal
components to display. The software does not automatically choose a component
or factor count.

Unrotated component loadings are calculated as:

`loading = eigenvector * sqrt(eigenvalue)`

PCA summarises observed variance; it is not a latent-variable measurement
model. Component-loading signs are arbitrary, and the same component solution
may appear with every sign reversed without changing its statistical meaning.
No rotation, parallel analysis, common-factor extraction, item deletion, or
dimension reassignment is automated in this prototype.

## 7. Interpretation and limitations

Results must be interpreted alongside the conceptual framework, content
validity work, cognitive interviews, instrument version history, feasibility,
reliability, response distributions, sample design, administration procedures,
and missing-data exclusions.

The workflow does not establish:

- construct validity or the proposed five-dimension structure;
- unidimensionality within a dimension;
- measurement invariance or cross-version comparability;
- fairness across institution types, regions, or populations;
- a causal relationship among Policy, Resources, Practices, Participation, and
  Equity; or
- a basis for child diagnosis, teacher evaluation, institution ranking, or
  automatic item decisions.

Synthetic data may be used only for demonstration and software testing. Any
future empirical EFA or CFA requires a preregistered or otherwise governed
analysis plan, an appropriate sample and estimator for the response scale,
independent validation, uncertainty reporting, and documented ethical review.

## 8. Completion record

An exploratory audit record should document the instrument version,
administration round, unit of analysis, sampling process, response scale,
sample size, exclusions, correlation type, selected component count, numerical
errors, outputs, and interpretation limitations. Completion means that the
software audit ran reproducibly; it does not mean that the instrument is
validated.
