# Inclusive Education Research Module User Guide

## Purpose and Boundary

The module supports educational research on the pathway from policy and
resources to practices, participation, and equity. It is not a diagnostic tool,
does not determine disability status, and does not replace professional
judgement.

## Open the Module

Run the platform and select **Inclusive Education** in the sidebar:

```bash
streamlit run app/streamlit_app.py
```

The existing **Inclusive Support** page remains a separate design-and-safety
foundation. **Inclusive Education** is the aggregate research-analysis module.

## Data Input

Choose either:

- **Synthetic demonstration data**, which contain 12 fictional institutions; or
- **Upload institution-level CSV**, using the downloadable template.

Do not upload identifiable child, family, teacher, clinical, or case records.
CSV validation checks required fields, institution-ID uniqueness, numeric
conversion, missing values, finite values, and the declared source range.

## Scale Conversion

Select the documented source scale:

- 0–100;
- 0–1; or
- a custom minimum and maximum.

Custom and 0–1 values are converted linearly to 0–100. The platform does not
infer a scale automatically. Values outside the declared interval fail
validation. Missing scoring values are not imputed.

## Dashboard

The Dashboard provides:

- five mean dimension scores;
- a Policy-to-Equity pathway chart;
- a five-dimension radar chart;
- Resource-to-Practice and Practice-to-Participation gaps;
- the major descriptive gap and a hypothesis-labelled interpretation; and
- an institution-by-dimension heatmap.

Every chart is accompanied by numerical information. Expand **Accessible chart
data tables** to inspect the pathway, Support Gap, and institution-dimension
values without relying on colour or chart geometry. See
`docs/Inclusive_Education_Accessibility_Check.md` for the current automated
review and remaining manual checks.

## Researcher Mode

Researchers can inspect variables and records, select dimensions and variables,
calculate descriptive statistics and Pearson correlations, examine CV/Gini/
Theil distributional inequality, inspect institution-level gaps, compare
institutions, and optionally run exploratory K-means clustering.

Correlation is descriptive association only. Cluster numbers are neutral
pattern identifiers, not validated institution types or performance labels.

Researcher Mode also provides **Dimension sensitivity**. It removes each item
one at a time and compares the resulting dimension mean with the default equal-
item score. Large changes identify a measurement-robustness question; they do
not prove that the excluded item is invalid or causally important.

The current item set has not completed expert content validation. Researchers
planning substantive use should follow the
[Inclusive Education Content Validation Protocol](Inclusive_Education_Content_Validation_Protocol.md)
before treating the dimensions as a validated instrument.

Researcher Mode provides a blank expert content-review CSV. Duplicate the
complete 28-item block for each reviewer. Relevance and clarity use declared
1–4 categories; essentiality uses `essential`, `useful_not_essential`, or
`not_necessary`. The template contains no expert evidence and does not
validate the current item set. A completed CSV may be uploaded in Researcher
Mode. The platform validates the full reviewer-by-item matrix, then displays
item-level I-CVI, clarity I-CVI, and CVR plus dimension-level S-CVI/Ave
summaries. It does not apply automatic retain/remove thresholds. Uploads are
processed in the current session and are not intentionally persisted.

Researcher Mode also provides separate cognitive-interview and item-revision
audit workflows. Cognitive interviews may cover only the items discussed and
report issue and coverage summaries without interview IDs or free text. Item
revision decisions require explicit instrument-version transitions, rationale,
minority-view records, and safeguarding and equity/accessibility review. See
the [Cognitive Interview and Item Revision Protocol](Inclusive_Education_Cognitive_Interview_Protocol.md).

Researcher Mode also provides a complete instrument-version registry and
structural comparability audit. It identifies item, dimension, wording, response-
scale, and weight changes. Structural alignment does not establish empirical
comparability, and structural change does not permit automatic score conversion.
See the [Instrument Versioning and Comparability Protocol](Inclusive_Education_Versioning_Protocol.md).

The feasibility-pilot workflow preserves missing item responses to audit
completion, missingness, endpoint concentration, response variation, duration,
burden, and administration mode. These outputs are implementation and data-
quality questions, not reliability or validity evidence. See the
[Feasibility Pilot and Data Quality Protocol](Inclusive_Education_Feasibility_Protocol.md).

For complete, governed records, the preliminary reliability workflow reports
internal consistency and matched repeated-administration stability by version
and dimension. It applies no automatic pass/fail threshold and does not treat
reliability as validity or unidimensionality evidence. See the
[Preliminary Reliability Protocol](Inclusive_Education_Reliability_Protocol.md).

For one explicitly selected instrument version and administration round, the
construct-structure readiness workflow reports an item-correlation matrix,
overall and item-level KMO, Bartlett's test, correlation-matrix eigenvalues,
and researcher-selected unrotated principal-component loadings. It does not
automatically choose a factor count or make item decisions. PCA is not labelled
as EFA or CFA, and the output does not validate the proposed five dimensions.
See the [Construct Structure Readiness Protocol](Inclusive_Education_Construct_Structure_Protocol.md).

The subgroup measurement-comparability readiness workflow adds an ethically
justified institutional `comparison_group` to complete records from one selected
version and round. It reports group coverage, item distributions, descriptive
standardised mean differences, and correlation-structure difference summaries.
These results do not establish measurement invariance, DIF, bias, fairness, or
substantive group effects. The workflow applies no automatic threshold, ranking,
group judgement, or item decision. See the
[Subgroup Measurement Comparability Readiness Protocol](Inclusive_Education_Subgroup_Comparability_Protocol.md).

The external-measure relationship readiness workflow pairs complete
institutional item records with one documented independent institutional
measure. It reports paired-record coverage, Pearson and Spearman correlations
between the external measure and the five equal-item dimension scores, and an
approximate Fisher-z interval for Pearson correlation. The expected relationship
type is research-design metadata, not an automatic hypothesis test. Correlation
does not establish convergent, discriminant, criterion-related, predictive,
external, or causal validity. See the
[External Measure Relationship Readiness Protocol](Inclusive_Education_External_Measure_Protocol.md).

The alternative item-weight sensitivity workflow compares the current
equal-item baseline with complete researcher-declared weighting schemes. Each
scheme must document its rationale and evidence status and use positive weights
that sum to 1 within every dimension. Outputs describe changes in five-dimension
means, aggregated institution-level score sensitivity, and Support Gap summaries.
The platform does not learn, rank, recommend, validate, or adopt weights, and
the default scoring model remains equal-item weighting. See the
[Alternative Weight Sensitivity Protocol](Inclusive_Education_Weight_Sensitivity_Protocol.md).

The Bootstrap sampling-uncertainty workflow resamples complete institutional
records with replacement for one selected instrument version and round. It
reports the original point estimate, Bootstrap mean, estimated bias, standard
error, and percentile interval for five dimension means and three Support Gap
means. Researchers explicitly select the resample count, interval level, and
random seed. These summaries do not establish representativeness, validity,
causal effects, population parameters, or stability classifications. See the
[Bootstrap Sampling Uncertainty Protocol](Inclusive_Education_Bootstrap_Uncertainty_Protocol.md).

The longitudinal panel readiness workflow audits complete institutional records
across at least two rounds of one instrument version. It reports round coverage,
complete-panel coverage, adjacent-round matching, five-dimension and Support Gap
summaries, and aggregate matched change statistics. Missing rounds are not
imputed, versions are not pooled, and unit-level trajectories are not exported.
Time order and descriptive change do not establish longitudinal measurement
comparability, improvement, deterioration, policy effects, or causality. See the
[Longitudinal Panel Readiness Protocol](Inclusive_Education_Longitudinal_Readiness_Protocol.md).

The longitudinal attrition and panel-composition workflow compares retained,
first-round-only, and second-round-only institutional groups across adjacent
observed rounds. It reports coverage counts and, only when both groups contain
at least three institutions, descriptive dimension and Support Gap mean
differences. Small-group statistics are suppressed. These outputs do not identify
missingness mechanisms, attrition causes, bias, or corrective weights, and the
platform does not impute missing rounds. See the
[Longitudinal Attrition and Panel Composition Protocol](Inclusive_Education_Attrition_Protocol.md).

The paired longitudinal Bootstrap workflow resamples matched institutions as
intact earlier/later-round pairs for each adjacent observed-round comparison.
It reports the point mean change, Bootstrap mean change, estimated bias,
standard error, and percentile interval for the five dimensions and three
Support Gaps. Researchers select the resample count, interval level, and random
seed. Missing rounds are not imputed, versions are not pooled, and pair-level
trajectories or Bootstrap draws are not exported. The intervals do not establish
longitudinal measurement comparability, statistical significance, improvement,
deterioration, policy effects, or causality. See the
[Paired Longitudinal Bootstrap Protocol](Inclusive_Education_Paired_Longitudinal_Bootstrap_Protocol.md).

The longitudinal timing and fieldwork metadata workflow records one
non-identifying metadata row per instrument version and round. It validates
collection dates, administration mode, recruitment scope, sampling-frame
reference, round purpose, and fieldwork-event status. Outputs describe collection
windows, midpoint intervals, overlapping windows, and adjacent-round metadata
changes. Human-entered event notes are not reproduced in summaries or downloads.
These records do not establish data quality, bias, longitudinal comparability,
reasons for score change, improvement, policy effects, or causality. See the
[Longitudinal Timing and Fieldwork Metadata Protocol](Inclusive_Education_Longitudinal_Metadata_Protocol.md).

The longitudinal measurement-comparability readiness workflow compares item
distributions, standardised mean differences, and item-correlation structures
across adjacent rounds of one instrument version. It uses all complete records
in each round and does not adjust for panel composition. These summaries are
descriptive research prompts only: they do not establish configural, metric,
scalar, strict, or other measurement invariance, DIF, bias, validity, substantive
change, improvement, policy effects, or causality. See the
[Longitudinal Measurement Comparability Protocol](Inclusive_Education_Longitudinal_Comparability_Protocol.md).

The longitudinal analysis-plan readiness workflow records the planned unit,
population, round contrast, change direction, estimand, missing-data and weighting
strategies, uncertainty method, dependence structure, measurement-comparability
basis, evidence references, causal-language setting, and preregistration status.
It generates bounded documentation prompts when key decisions remain undefined.
The workflow does not choose a method, fit a model, approve a plan, estimate an
effect, or validate causal assumptions. See the
[Longitudinal Analysis-Plan Readiness Protocol](Inclusive_Education_Longitudinal_Analysis_Plan_Protocol.md).

The longitudinal policy and context event-alignment workflow combines round
timing metadata with a versioned event registry. It describes events overlapping
collection windows, events between adjacent rounds, event types, scope, evidence
sources, and verification status. Event-description text is not reproduced in
outputs. Chronology and overlap do not establish institutional exposure,
mechanisms, attribution, policy effects, counterfactual outcomes, or causality.
See the [Longitudinal Event Alignment Protocol](Inclusive_Education_Longitudinal_Event_Alignment_Protocol.md).

The event exposure-definition workflow distinguishes a registered event from
institution-level exposure. It records exposure scope and status, timing,
intensity, lag, comparator, and evidence references, then generates documentation
prompts when these definitions remain unresolved. It does not infer treatment,
dose, exposure, policy effects, or causality. See the
[Event Exposure Definition Protocol](Inclusive_Education_Event_Exposure_Protocol.md).

The identification-design readiness workflow records the proposed design type,
treatment and comparison definitions, time zero, pre/post periods, identification
assumptions, confounding, anticipation, interference, baseline evidence, negative
controls, sensitivity analysis, and causal-claim status. Design labels are
candidates only and do not establish causal identification. See the
[Identification-Design Readiness Protocol](Inclusive_Education_Identification_Design_Protocol.md).

The falsification and sensitivity-plan workflow records planned pretrend checks,
placebo event times, negative controls, alternative comparison groups, windows
and specifications, unobserved-confounding and missing-data sensitivity,
multiple-testing strategy, and interpretation rules. It does not run tests, and
favourable diagnostics would not prove identification or causality. See the
[Falsification and Sensitivity Plan Protocol](Inclusive_Education_Falsification_Plan_Protocol.md).

The estimation-specification readiness workflow records the proposed outcome,
estimand, analysis population, estimator family, functional form, treatment
encoding, comparison contrast, dependence and standard-error methods,
clustering, weighting, missing-data handling, event window, uncertainty,
software environment, and output-disclosure boundary. It fits no model and
produces no effect estimate or causal conclusion. See the
[Estimation-Specification Readiness Protocol](Inclusive_Education_Estimation_Specification_Protocol.md).

The analysis reproducibility readiness workflow records the data-snapshot
identity and checksum, code commit, environment lock, random-seed policy,
specification-lock and deviation-log status, quality-control status, and output
storage and disclosure boundaries. It executes no code, verifies no result, and
does not treat documentation completeness as methodological validity. See the
[Analysis Reproducibility Readiness Protocol](Inclusive_Education_Analysis_Reproducibility_Protocol.md).

The results-reporting and claim-boundary readiness workflow records primary and
secondary reporting scope, null and uncertain-result handling, uncertainty,
multiplicity, deviations, subgroup privacy, visualization scales, Support Gap
language, causal wording, and human review of AI assistance. It receives no
result values and verifies no finding. See the
[Results Reporting and Claim-Boundary Protocol](Inclusive_Education_Results_Reporting_Protocol.md).

## Exploratory Scenarios

Four interfaces change one item by a researcher-selected number of 0–100 scale
points:

1. Increase Teacher Support;
2. Increase Training Support;
3. Increase Financial Support; and
4. Improve Curriculum Adaptation.

Other reported items remain fixed. Scenario results are arithmetic comparisons,
not causal predictions or forecasts.

## Research Insight and AI

The platform first generates deterministic descriptive insights and research-
question candidates. An optional bounded prompt can then be reviewed and
downloaded without an external call.

Visitors may optionally use a visitor-controlled DeepSeek key after explicit
consent. The prompt prohibits diagnosis, child labelling, disability decisions,
teacher-quality inference, and unsupported causal claims. Generated text is
labelled:

> AI-generated interpretation. Please verify with professional judgment and
> empirical evidence.

## Downloads

Available outputs include:

- institution dimension scores and Support Gaps as CSV;
- exploratory scenario comparison as CSV;
- reviewed AI request as Markdown; and
- research summary as Markdown, Word, or PDF.

Changing an export format does not validate the instrument, data, scores, or
interpretation.
