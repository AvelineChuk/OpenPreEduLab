# Policy Simulation Framework

## 1. Purpose and Research Scope

The Policy Simulation Engine is a scenario-based research prototype for examining how explicit changes in preschool education policy parameters, demographic conditions, staff costs, and fiscal capacity may alter a resource system under stated assumptions.

It addresses the question: *when specified conditions change, what are the modelled implications for fiscal requirement, resource allocation, teacher demand, coverage, and fiscal sustainability?*

This is not a forecasting model. Forecasting extrapolates historical trends; policy simulation compares conditional counterfactual states. The present module does not estimate actual future policy effects, causal effects, or policy recommendations.

## 2. Scenario-Based Framework

```text
Policy or contextual scenario
        ↓
Explicit parameter change
        ↓
Prototype resource-system transition rule
        ↓
Comparable outcome indicators
```

The transition rule is the scientific object of scrutiny. Every scenario result is conditional on the rule and parameter values supplied by the researcher.

## 3. Inputs, Parameters, and Outputs

### Baseline inputs

The baseline dataset uses city-year records with per-child government expenditure, enrolment, FTE teachers, licensed places, resident preschool-age population, and resident target-age enrolment. Existing PRAI fields are retained so that scenario-specific resource-allocation scores can be calculated.

### Policy parameters

| Parameter | Meaning |
| --- | --- |
| `subsidy_increase_rate` | Proportional increase in government expenditure per enrolled child. |
| `population_change_rate` | Proportional change in resident preschool-age population; a negative value represents decline. |
| `teacher_cost_increase_rate` | Proportional increase in the teacher-cost component. |
| `baseline_teacher_cost_yuan` | Assumed annual cost per FTE teacher used to calculate the incremental teacher-cost burden. |
| `fiscal_growth_rate` | Proportional change in available fiscal capacity; a negative value represents constraint. |
| `fiscal_capacity_multiplier` | Baseline available fiscal capacity as a multiple of baseline service requirement. This is necessary because the MVP dataset contains no administrative fiscal-capacity measure. |
| `teacher_child_ratio` | Optional FTE teachers per child planning ratio for the population scenario. If omitted, each city’s baseline ratio is retained. |

### Output indicators

| Output | Interpretation |
| --- | --- |
| `fiscal_requirement_yuan` | Modelled cost of maintaining the scenario’s stated service condition, including any incremental teacher cost. |
| `fiscal_capacity_yuan` | Available fiscal capacity under the prototype fiscal assumption. |
| `fiscal_sustainability_ratio` | Fiscal capacity divided by stated fiscal requirement. Values below one indicate that assumed capacity is below the modelled requirement. |
| `resource_allocation_score` | PRAI score recalculated from the scenario data. Scores are jointly normalised across all compared scenarios. |
| `teacher_demand` | FTE teacher requirement under the stated teacher-child planning ratio. |
| `education_coverage_pct` | Resident target-age enrolment relative to resident preschool-age population. |

## 4. Scenario Design and Transition Rules

### Scenario A: Increase Subsidy

`simulate_subsidy_policy()` multiplies government expenditure per child by \(1+\text{subsidy\_increase\_rate}\). Enrolment, staffing, and facilities are held constant. Fiscal requirement increases with the expenditure change; fiscal capacity remains at the specified baseline capacity unless the researcher changes that assumption.

### Scenario B: Declining Population

`simulate_population_change()` multiplies resident preschool-age population and enrolment demand by \(1+\text{population\_change\_rate}\). Existing teachers and facilities remain fixed. Teacher demand is calculated from the explicit planning ratio. This is a demand-side transition rule; it does not assume automatic closure, hiring, or facility adjustment.

### Scenario C: Teacher Cost Increase

`simulate_teacher_cost_change()` holds service volume and physical inputs constant and adds the incremental cost:

\[
\Delta F=\text{FTE teachers}\times\text{baseline teacher cost}\times\text{teacher cost increase rate}
\]

The scenario therefore changes fiscal requirement and fiscal sustainability without asserting a direct change in enrolment or service quality.

### Scenario D: Fiscal Constraint

`simulate_fiscal_constraint()` changes available fiscal capacity by \(1+\text{fiscal\_growth\_rate}\). When assumed capacity falls below the cost of baseline service, per-child government expenditure is proportionally scaled down for the PRAI calculation. The reported fiscal requirement remains the cost of maintaining baseline service, so the sustainability ratio reveals the funding gap. Coverage is held constant in this MVP because no empirically validated mechanism connects reduced funding to enrolment withdrawal.

## 5. Resource Allocation Comparability

Sample-based min–max PRAI normalisation is sensitive to the comparison set. For this reason, `simulate_policy_scenarios()` scores the baseline and all four scenarios jointly. Its output should be used for the scenario comparison chart. Concatenating scores from separately run scenarios is not valid for cross-scenario PRAI comparison.

In substantive research, policy or theoretical benchmarks should replace sample-based scaling wherever possible.

## 6. Interpretation and Research Value

The framework makes the assumptions connecting policy conditions and resource outcomes visible. It can support research questions about fiscal pressure, demographic change, staffing requirements, and the sensitivity of resource-allocation measures to alternative conditions.

Results are conditional scenario outputs, not real-world forecasts. They may change materially when assumptions about fiscal capacity, staffing standards, cost definitions, or transition mechanisms change. The module does not use an LLM, does not conduct policy simulation beyond the specified rules, and does not generate policy recommendations.
