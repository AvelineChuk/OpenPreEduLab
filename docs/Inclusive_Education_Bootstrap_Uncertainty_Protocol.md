# Inclusive Education Bootstrap Sampling Uncertainty Protocol

## 1. Purpose and boundary

This protocol defines a nonparametric Bootstrap audit for describing the
sampling variability of the five prototype dimension means and three Support
Gap means. Complete institutional records from one instrument version and one
administration round are repeatedly sampled with replacement.

The outputs are prototype uncertainty summaries for the submitted sample and
assumptions. They do not establish population representativeness, construct
validity, measurement invariance, causal effects, policy effects, or model
correctness. The platform does not automatically label a result stable or
unstable.

## 2. Data requirements

One row represents one pseudonymous institutional research unit, one instrument
version, and one administration round. All 28 item responses must be complete,
numeric, finite, and inside the declared response range. Missing values are
rejected rather than imputed.

The researcher explicitly selects one version and one round. Versions and
rounds are not pooled. At least five complete records are required as a
prototype computation condition. This is not a scientific sample-size,
precision, or representativeness threshold.

The ordinary row Bootstrap assumes that the submitted institutional records are
appropriate exchangeable sampling units for the research design. It is not
appropriate without modification when dependence, clustering, stratification,
survey weights, repeated measures, or complex selection processes must be
preserved.

## 3. Scoring assumptions

Item values are linearly converted from the declared source interval to 0–100.
The audit uses the platform's current equal-item dimension scores:

`Dimension Score = arithmetic mean of current dimension items`

It then calculates:

`Gap_RP = Resource Score - Practice Score`

`Gap_PC = Practice Score - Participation Score`

`Overall Gap = Resource Score - Participation Score`

Equal weighting remains a prototype assumption. The Bootstrap audit does not
propagate uncertainty about item definitions, missing data, response error, or
alternative weights. These require separate sensitivity analyses.

## 4. Resampling procedure

For a selected sample of n institutional records:

1. draw n row indices with replacement;
2. calculate five dimension means and three Support Gap means in the resample;
3. repeat for the researcher-selected number of resamples; and
4. summarise the resulting empirical sampling distributions.

The current software permits 100–10,000 resamples. This range is a public
prototype resource-control rule, not a universal methodological standard. More
resamples reduce Monte Carlo variation but cannot repair biased sampling,
measurement problems, or an inappropriate resampling unit.

A local non-negative random seed makes the same data and settings reproducible.
Different seeds may produce slightly different Bootstrap summaries. The seed
does not make the underlying sample representative.

## 5. Reported statistics

For each dimension mean and Support Gap mean, the platform reports:

- original sample point estimate;
- mean of the Bootstrap estimates;
- estimated Bootstrap bias;
- Bootstrap standard error;
- lower and upper percentile interval bounds; and
- declared interval level.

Bias is calculated as:

`Bootstrap bias = mean(Bootstrap estimates) - original point estimate`

The Bootstrap standard error is the sample standard deviation of the Bootstrap
estimates.

For confidence level `1 - alpha`, the percentile interval uses the empirical
`alpha/2` and `1 - alpha/2` quantiles. The interface allows interval levels from
80% to 99%.

## 6. Interpretation limits

Percentile intervals rely on the observed empirical distribution and may have
poor coverage in small, biased, highly discrete, skewed, or dependent samples.
They are not automatically preferable to analytical, studentised, BCa,
clustered, stratified, Bayesian, or design-based intervals.

An interval containing or excluding zero is not automatically a policy or
causal test. A narrow interval does not prove validity or adequate measurement.
A wide interval does not prove that the construct is invalid. Support Gap
intervals remain intervals for descriptive score differences under current
scoring assumptions, not support-conversion causal effects.

The platform does not provide:

- automatic stable/unstable labels;
- significance stars or pass/fail thresholds;
- institution rankings;
- policy-effect conclusions;
- population claims without a justified target population and sampling design;
- raw Bootstrap draws or resampled unit identifiers; or
- correction for clustering, survey design, missingness, or measurement error.

## 7. Privacy and disclosure

Uploaded records are processed in the current Streamlit session and are not
intentionally persisted. Downloaded outputs contain aggregate run settings,
summary statistics, and research questions only. They exclude pseudonymous
unit IDs, individual scores, resampling indices, and raw Bootstrap draws.

## 8. Future methods

Future governed studies may require:

- cluster or multilevel Bootstrap procedures;
- stratified or survey-design resampling;
- block Bootstrap for longitudinal observations;
- BCa or studentised intervals;
- multiple-imputation and Bootstrap integration;
- uncertainty propagation for weights and measurement models;
- simulation-based coverage evaluation; and
- independent-sample replication.

The appropriate method depends on the sampling and dependency structure, not
only on software availability.

## 9. Completion record

A Bootstrap audit record should document the version, round, unit of analysis,
target population, sampling process, exclusions, response scale, scoring
assumptions, record count, number of resamples, interval method and level,
random seed, outputs, dependence limitations, and interpretation boundaries.

Completion means the submitted records were resampled reproducibly under the
stated assumptions. It does not mean the scores, gaps, or substantive
interpretations have been validated.
