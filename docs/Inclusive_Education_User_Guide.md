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
