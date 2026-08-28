# Inclusive Education Alternative Weight Sensitivity Protocol

## 1. Purpose and boundary

This protocol defines a transparent sensitivity audit for comparing the current
equal-item prototype scores with one or more researcher-declared alternative
item-weight schemes. It asks whether five-dimension and Support Gap summaries
change materially under different, explicitly documented scoring assumptions.

The workflow does not learn weights, optimise an objective, identify item
importance, recommend a best scheme, validate a scheme, or change the
platform's default scoring model. Equal-item weighting remains the documented
v0.1 prototype assumption.

## 2. Why weight sensitivity matters

A weighted composite reflects both observed item values and normative or
empirical decisions about their relative contribution. Different weights may
change dimension levels, institution-level scores, and the descriptive Support
Gap. Sensitivity analysis makes this dependence visible rather than treating
one weighting choice as a scientific fact.

Stability across schemes does not prove construct validity. Sensitivity to a
scheme does not prove that the scheme or any heavily weighted item is correct,
causal, or more important in educational practice.

## 3. Response data

Response records reuse the complete reliability-audit structure: one row per
pseudonymous institutional unit, instrument version, and administration round,
with all 28 item values complete and inside the declared response range.

The researcher explicitly selects one version and one round. Versions and
rounds are not pooled. Item responses are linearly converted to 0–100 before
applying weights. Downloaded summaries exclude pseudonymous unit IDs.

## 4. Weight scheme structure

Every named scheme must include exactly one row for each of the 28 current
items. Required metadata include:

- scheme name;
- research rationale;
- evidence status;
- score column and conceptual dimension;
- item identifier; and
- positive item weight.

Permitted evidence-status records are:

- `theory_candidate`;
- `expert_proposed`;
- `empirical_candidate`; and
- `exploratory_sensitivity`.

These labels record provenance and maturity. They are not quality ratings or
validation conclusions.

Weights must be finite and strictly positive. Within every scheme and
dimension, weights must sum to 1. Item-to-dimension mappings must match the
current instrument registry. Incomplete, duplicated, unknown, mislabelled, or
non-normalised schemes are rejected rather than silently repaired.

## 5. Equal-item baseline

For a dimension containing k items, the baseline weight for every item is:

`w_i = 1 / k`

The baseline dimension score is:

`D_equal = sum(w_i * x_i)`

where each x value is on the standardised 0–100 scale. A submitted equal-weight
scheme should reproduce the baseline subject only to numerical precision. This
identity is covered by automated tests.

## 6. Alternative dimension scores

For researcher-declared weights that sum to 1 within a dimension:

`D_alternative = sum(w_i_alternative * x_i)`

For each scheme and dimension, the platform reports:

- complete record count;
- equal-weight sample mean;
- alternative-weight sample mean;
- mean score change;
- mean absolute institution-level change; and
- maximum absolute institution-level change.

Institution-level differences are aggregated for disclosure control. Unit IDs
and individual score changes are not included in downloadable summaries.

## 7. Support Gap sensitivity

The platform recalculates the existing descriptive indicators under each
weight scheme:

`Gap_RP = Resource Score - Practice Score`

`Gap_PC = Practice Score - Participation Score`

`Overall Gap = Resource Score - Participation Score`

For each gap it reports the equal-weight mean, alternative-weight mean, mean
change, mean absolute institution-level change, and maximum absolute
institution-level change.

Support Gap remains a descriptive diagnostic indicator, not a causal estimator.
A change caused by scoring weights does not show that resources, practices, or
participation changed in the educational setting.

## 8. Interpretation rules

The platform does not provide:

- automatic sensitivity thresholds or traffic-light labels;
- scheme rankings or recommendations;
- data-driven weight optimisation;
- automatic item retention or removal;
- causal or policy-effect conclusions;
- child, teacher, institution, or group evaluation; or
- replacement of theory, expert judgement, or empirical validation.

A scheme with smaller observed changes is not automatically superior. A scheme
with larger observed changes is not automatically invalid. Researchers should
inspect which assumptions changed, why those assumptions are justified, and
whether conclusions replicate in independent samples.

## 9. Future validation

Future weighting work may include theory-led expert elicitation, preregistered
scoring plans, measurement-model evidence, decision-analysis methods,
out-of-sample validation, and uncertainty analysis. Empirical optimisation
requires safeguards against overfitting and circular validation. No method
should be selected merely because software makes it available.

Synthetic records may be used only for demonstration and testing. Any real-data
study must follow repository governance and independent-review requirements.

## 10. Completion record

A sensitivity audit should document the instrument version, round, response
scale, sample, exclusions, scheme name, rationale, evidence status, complete
weight matrix, comparison outputs, undefined results, and interpretation
limits. Completion means the declared assumptions were compared reproducibly;
it does not validate or adopt an alternative weighting scheme.
