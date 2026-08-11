# Support Gap Methodology

## Purpose

Support Gap identifies descriptive differences between adjacent stages of the
inclusive education research pathway. It asks where reported support appears
less fully reflected in the next calculated dimension.

## Mathematical Definition

For institution or aggregate unit \(i\), let:

- \(R_i\) be Resource Support Score;
- \(P_i\) be Inclusive Practice Score; and
- \(C_i\) be Child Participation Score.

The Resource-to-Practice gap is:

$$
Gap_{RP,i} = R_i - P_i
$$

The Practice-to-Participation gap is:

$$
Gap_{PC,i} = P_i - C_i
$$

The overall support-conversion gap is:

$$
Gap_{Overall,i} = R_i - C_i = Gap_{RP,i} + Gap_{PC,i}
$$

All values are expressed in 0–100 score points.

## Interpretation

A positive adjacent gap means that the earlier stage has a higher calculated
score than the later stage. For example:

```text
Resource = 80
Practice = 58
Participation = 49

Gap_RP = 22
Gap_PC = 9
Overall Gap = 31
```

The larger adjacent gap is Resource to Practice. A permitted interpretation is:

> Available resource support may not be fully reflected in the reported
> inclusive-practice score.

This must be labelled **Hypothesis for further investigation**. It is not a
finding that resources failed or caused participation to change.

Negative values are retained. A negative gap means the later stage score is
higher than the earlier stage score. It does not automatically demonstrate
successful conversion; measurement, weighting, context, and omitted factors
must still be investigated.

## Why It Is Diagnostic Rather Than Causal

The gap is an arithmetic difference between composite scores. It contains no
counterfactual comparison, random assignment, natural experiment, longitudinal
identification, control group, or model of confounding. Therefore it cannot
estimate what participation would have been under a different resource level.

Support Gap may help locate a pattern and formulate a research question. It
cannot establish that:

- resources caused or failed to cause practice;
- practice caused participation;
- an institution is effective or ineffective; or
- a specific intervention should be prescribed.

## Aggregation

The Dashboard reports both institution-level gaps and sample means. Aggregate
means can conceal heterogeneous patterns, so institution tables, dimension
items, and distributions should remain inspectable. The overall gap must always
be accompanied by both adjacent gaps because equal overall values can arise
from different pathway patterns.

## Limitations and Future Validation

Gap magnitudes depend on item definitions, standardisation, weights, response
processes, and measurement error. Future work should examine reliability,
construct validity, sensitivity to weights, subgroup variation, longitudinal
stability, and relationships with independently measured participation. Causal
research requires a separately justified design.
