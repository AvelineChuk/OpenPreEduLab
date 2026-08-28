# Inclusive Education Longitudinal Panel Readiness Protocol

## 1. Purpose and boundary

This protocol defines a descriptive readiness audit for institutional records
collected across multiple administration rounds of one Inclusive Education
instrument version. It examines round coverage, adjacent-round matching,
complete-panel coverage, five-dimension summaries, Support Gap summaries, and
matched changes.

The audit is not a longitudinal growth model, measurement-invariance test,
causal model, policy-effect analysis, or institution evaluation. Time order
alone does not establish that an earlier resource, practice, or policy measure
caused a later participation or equity score.

## 2. Data structure

One row represents one pseudonymous institutional research unit, one instrument
version, and one positive-integer administration round. All 28 item responses
must be complete, numeric, finite, and inside the declared response range.

A stable pseudonymous unit ID is required to match the same institution across
rounds. The identifier must not contain an institution name or other directly
identifying information. Each unit, version, and round combination may appear
only once.

Analysis is restricted to one explicitly selected instrument version. Records
from different versions are not pooled because structural alignment and
longitudinal score comparability require separate evidence.

## 3. Prototype computation conditions

The selected version must contain at least two observed rounds. Every round
must contain at least three complete institutional records. Every pair of
adjacent observed rounds must contain at least three matched institutions.

These are prototype software conditions, not scientific sample-size,
statistical-power, privacy, or panel-quality thresholds. A substantive
longitudinal study requires its own sampling and precision rationale.

Administration rounds are ordered by their positive integer values. If the
observed rounds are 1, 3, and 6, the audit treats 1→3 and 3→6 as adjacent
observed comparisons. It does not assume equal calendar spacing. Researchers
must document actual dates, intervals, policy periods, and fieldwork events
outside this first-version schema.

## 4. Scoring

Item responses are linearly converted from the declared source interval to
0–100. The current equal-item prototype scores are calculated for:

- Policy Support;
- Resource Support;
- Inclusive Practices;
- Child Participation; and
- Equity.

The audit also calculates:

`Gap_RP = Resource Score - Practice Score`

`Gap_PC = Practice Score - Participation Score`

`Overall Gap = Resource Score - Participation Score`

Equal weighting and Support Gap definitions remain explicit prototype
assumptions. They must be interpreted alongside the separate weighting,
construct, comparability, and uncertainty audits.

## 5. Round coverage and descriptive summaries

For each observed round, the platform reports complete record and unique unit
counts. For each of the five dimensions and three gaps it reports:

- record count;
- mean;
- sample standard deviation;
- minimum; and
- maximum.

Round means may involve different institutions when the panel is unbalanced.
They must not be interpreted as within-institution change without checking the
matched summaries.

## 6. Adjacent-round matching

For every pair of adjacent observed rounds, the audit reports:

- first- and second-round unit counts;
- matched unit count;
- matched proportion relative to each round;
- first-round-only count; and
- second-round-only count.

The first-round retention proportion is the matched count divided by the
first-round unit count. The second-round matched proportion is the matched count
divided by the second-round unit count. These quantities describe linkage
coverage, not attrition causes or data quality by themselves.

Unmatched records are not silently removed from the coverage summary. Missing
rounds are not imputed.

## 7. Matched change summaries

For each adjacent round pair and statistic, the platform calculates
institution-level change as:

`change = second-round value - first-round value`

It reports:

- matched first- and second-round means;
- mean change;
- mean absolute change;
- sample standard deviation of change;
- minimum change; and
- maximum change.

The downloaded tables contain aggregate summaries and exclude unit IDs and
individual trajectories.

Positive or negative change is not automatically labelled improvement or
deterioration. For example, a lower positive Support Gap may appear different
under alternative weights, changing item interpretation, sampling composition,
or measurement non-comparability.

## 8. Complete-panel coverage

The complete-panel unit count is the number of pseudonymous institutions
observed in every selected round. The all-observed unit count is the union of
institutions observed in at least one round.

`complete-panel coverage = complete-panel units / all-observed units`

This describes panel completeness only. It does not establish that attrition is
random, harmless, representative, or unrelated to institutional conditions.

## 9. Interpretation risks

Observed longitudinal patterns may reflect:

- changing institutional composition or selective attrition;
- real contextual change;
- administration timing or mode;
- respondent or response-style change;
- instrument interpretation change;
- regression to the mean;
- measurement error;
- policy, economic, demographic, or organisational events; or
- ordinary sampling variability.

The platform does not provide automatic trend classifications, significance
tests, growth parameters, lagged effects, forecasts, policy-effect estimates,
or causal pathways. It also does not establish longitudinal measurement
invariance.

## 10. Future development

Future governed research may require:

- explicit collection dates and interval lengths;
- reasons for entry, exit, and missing rounds;
- longitudinal measurement-invariance analysis;
- attrition weighting or sensitivity analysis;
- repeated-measures uncertainty methods;
- multilevel growth models;
- time-varying policy and context variables;
- block or cluster Bootstrap methods; and
- causal designs with explicit identification assumptions.

These methods require adequate samples, theory, ethics, governance, and model
diagnostics. They must not be selected solely because software can run them.

## 11. Completion record

A longitudinal readiness record should document the version, unit definition,
round meanings, dates, intervals, recruitment, response scale, exclusions,
round counts, matching coverage, complete-panel coverage, scoring assumptions,
matched changes, missingness, fieldwork events, and interpretation limitations.

Completion means the available panel structure and descriptive changes were
audited reproducibly. It does not mean longitudinal comparability, improvement,
policy effects, or causal relationships have been established.
