# Inclusive Education Estimation-Specification Readiness Protocol

## Purpose

This protocol documents how a future inclusive-education policy or context
analysis is proposed to be estimated before results are inspected. It follows
the identification-design and falsification-plan readiness audits but does not
approve either one.

This is a **prototype readiness audit**, not an effect-estimation engine.

## Research problem

A design label alone does not determine the outcome, target estimand, analysis
population, functional form, dependence structure, uncertainty method, or
reporting boundary. Leaving those decisions implicit creates avoidable scope
for selective specifications and unsupported interpretation.

## Required declarations

The non-identifying CSV records:

- links to the proposed design and falsification plan;
- instrument version, outcome, estimand, population, and unit of analysis;
- time scale, estimator family, functional form, treatment encoding, and
  comparison contrast;
- covariates, fixed effects, dependence adjustment, standard errors, and
  clustering;
- weighting, missing-data handling, event window, and reference period;
- multiple-testing implementation and uncertainty reporting;
- software environment, output-disclosure boundary, and preregistration-stage
  status.

`not_applicable` may be used when a field is genuinely inapplicable and the
reason is retained in the governed research record. `not_defined`, `unknown`,
`not_assessed`, and `none` remain visible as unresolved states.

## Statistical basis

An estimand identifies the population-level quantity the study intends to
estimate. The estimator and its uncertainty procedure should be chosen in
relation to that estimand, the sampling or assignment structure, repeated
observations, clustering, weighting, missingness, and the proposed
identification assumptions. Documentation is therefore a prerequisite for
review, not evidence that those choices are correct.

## Outputs

The audit produces:

- a compact specification-readiness summary;
- generic prompts for unresolved declarations; and
- research-question candidates about estimands, dependence, uncertainty, and
  selective reporting.

Exports exclude researcher notes and contain no institution-level response
data, coefficients, effect estimates, p-values, or causal conclusions.

## Interpretation boundary

Completed fields do not establish identification, model correctness, valid
standard errors, policy effects, or causality. The workflow fits no model and
does not select a preferred estimator, optimise a specification, run
significance tests, rank institutions, approve a design, or make a decision.

## Future validation

A governed empirical study would additionally require reviewed data,
preregistration, defensible identification, sample-size and precision planning,
diagnostics, code review, reproducible software records, falsification and
sensitivity analyses, ethical review, and independent methodological review.
