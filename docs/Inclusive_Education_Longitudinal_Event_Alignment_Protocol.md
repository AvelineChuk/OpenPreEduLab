# Inclusive Education Longitudinal Policy and Context Event Alignment Protocol

## Purpose

This protocol aligns documented policy, resource, training, curriculum,
administrative, calendar, public-health, and other context events with
longitudinal collection windows. It helps researchers document chronology before
interpreting dimension or Support Gap changes.

Time order and overlap are not evidence of exposure, attribution, policy effect,
mechanism, counterfactual impact, or causality.

## Inputs

The workflow combines the existing longitudinal timing metadata with a versioned
event registry. Each event records an ID, type, start and end date, scope,
evidence source, evidence status, and non-identifying description. Dates use ISO
`YYYY-MM-DD`. Event IDs are unique and end dates cannot precede start dates.

Permitted evidence statuses distinguish primary-source documentation,
secondary-source documentation, researcher records, and pending verification.
These labels describe provenance status; they do not certify truth or causal
relevance.

## Outputs

For each event, the audit reports duration, source metadata, overlapping rounds,
the latest completed round before the event, and the earliest round after it.
For each adjacent round pair it reports events strictly between collection
windows, events overlapping either window, distinct event types, and events
still pending verification.

Event-description text is validated but not reproduced in summaries or exports.

## Interpretation boundary

The workflow does not determine whether institutions experienced an event,
define treatment or exposure, control confounding, identify mechanisms, estimate
effects, select comparison groups, or establish causal assumptions. Multiple
events may overlap, event scope may differ from study scope, and implementation
may vary across institutions.

No automatic effect label, exclusion, adjustment, weight, ranking, significance
test, forecast, or policy conclusion is produced.

## Governance and future validation

Researchers should retain independently reviewable source records, retrieval
dates, scope definitions, and protocol decisions outside public exports. Future
governed studies may require institution-specific exposure data, preregistered
time windows, interrupted-time-series or comparative designs, negative controls,
sensitivity analyses, and explicit causal identification assumptions.

Completion means event chronology was aligned reproducibly. It does not mean an
event caused, explained, improved, or worsened any observed outcome.
