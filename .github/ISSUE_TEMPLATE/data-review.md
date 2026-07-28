---
name: Independent data review
about: Record an independent review of a staging dataset or archived source
title: "[Data Review] <review ID>"
labels: ["data-review", "needs-review"]
assignees: []
---

## Review identifier

- Review ID:
- Review type: `staging dataset` / `raw source`
- Reviewer ID or name:
- Review date:

## Evidence reviewed

- Dataset or source path:
- Official publisher and publication URL:
- Source table, attachment, or page reviewed:
- SHA-256 checked: `yes` / `no` / `not available`

## Required checks

- [ ] I am not the original transcriber, or I have declared this limitation.
- [ ] I checked the source year, geographic scope, and unit.
- [ ] I compared all relevant staged values or visible source values with the retained raw file.
- [ ] I checked that no missing year, geographic aggregation, smoothing, or interpolation was introduced.
- [ ] I checked the proposed use against the source definition.
- [ ] I did not alter the raw source file.

## Findings

Describe any transcription discrepancy, ambiguous definition, unit issue,
coverage limitation, or anomalous value. Do not infer a policy conclusion.

## Proposed decision

For a staging dataset, choose one:

- `approved_for_processed`
- `approved_context_only`
- `return_for_correction`
- `hold_for_definition_review`
- `not_reviewed`

For a raw source, choose one:

- `confirmed_policy_simulation_candidate`
- `confirmed_context_only`
- `confirmed_not_definition_compatible`
- `return_for_correction`
- `hold_for_definition_review`
- `not_reviewed`

## Required follow-up

- [ ] Update the applicable CSV register in `datasets/metadata/` through a reviewed pull request.
- [ ] Keep `datasets/processed/` unchanged unless a staging decision is `approved_for_processed`.
- [ ] Link the pull request or commit that records the decision.
