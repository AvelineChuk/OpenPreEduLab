# Inclusive Education Longitudinal Analysis-Plan Readiness Protocol

## 1. Purpose

Before fitting a longitudinal model, researchers should document what is being
compared, for whom, over which rounds, with what change definition, and under
which missing-data, weighting, dependence, uncertainty, and measurement
assumptions. This workflow makes those decisions explicit.

It is a readiness audit, not a model runner, preregistration service, or causal
identification assessment.

## 2. Required plan fields

Each record describes one analysis plan and includes:

- instrument version and unit of analysis;
- target population scope;
- round comparison and change definition;
- estimand scope;
- missing-data and weighting strategies;
- uncertainty method and dependence structure;
- measurement-comparability basis;
- references to attrition and timing-metadata evidence;
- whether causal language is allowed;
- preregistration status; and
- optional researcher notes.

Required fields must be complete. Plan identifiers must be unique. The allowed
change definitions are `later_minus_earlier`, `earlier_minus_later`,
`round_specific_contrast`, and `not_yet_defined`. Causal-language and
preregistration fields use explicit controlled values.

## 3. Documentation prompts

The audit produces a prompt when:

- the change direction has not been defined;
- a measurement-comparability basis is missing or marked not assessed;
- a missing-data strategy is missing or marked not assessed;
- an uncertainty method is missing or marked not assessed; or
- causal language is enabled without the platform making any identification
  claim.

Prompts are not error scores, approval decisions, exclusions, or evidence that a
plan is invalid. They direct researchers to document design choices before
analysis.

## 4. Interpretation boundary

The audit does not establish:

- that the chosen estimand is substantively appropriate;
- that missing-data, weighting, or dependence assumptions are justified;
- that the sample is representative or sufficiently powered;
- that scores are longitudinally comparable;
- that a model is identified, valid, or correctly specified; or
- any improvement, deterioration, policy effect, or causal relationship.

No model is fitted. No effect estimate, trend label, significance test, forecast,
institution ranking, or automatic method recommendation is produced.

## 5. Relationship to other audits

The plan should reference and be interpreted with the longitudinal panel,
attrition, timing-metadata, paired Bootstrap, and measurement-comparability
audits. Those audits provide descriptive evidence and limitations; references do
not certify that a plan is ready for publication or causal analysis.

## 6. Privacy and governance

Uploads are processed in the current Streamlit session and are not intentionally
persisted. Researcher notes are validated but are not reproduced in summaries
or downloads. Notes must not contain child, family, teacher, identifiable
institution, or researcher personal data.

## 7. Future validation

Governed studies may add preregistration links, protocol versioning, estimand
diagrams, missing-data sensitivity plans, survey-weight documentation,
multilevel specifications, uncertainty simulation, and independent review.
Method selection must follow the research question and design rather than
software availability.

Completion means the declared analysis plan was audited reproducibly. It does
not mean the plan, data, model, measurement properties, or causal claims have
been validated.
