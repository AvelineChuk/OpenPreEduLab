# OpenPreEduLab v0.1 Pipeline Guide

## 1. Pipeline Logic

The v0.1 pipeline connects existing OpenPreEduLab modules into one reproducible workflow:

```text
Validated city-year dataset
        ↓
PRAI resource-allocation calculation
        ↓
Equity evaluation and DEA efficiency evaluation
        ↓
Population-linked teacher and fiscal projections
        ↓
Four conditional policy scenarios
        ↓
Optional evidence-bounded LLM interpretation
        ↓
Documented result files and research summary
```

The pipeline is an orchestration layer. It does not introduce a new research model or modify calculations performed by the existing modules.

## 2. Module Roles

| Module | Input | Output used by pipeline |
| --- | --- | --- |
| Resource Allocation Engine | Raw city-year data | PRAI score by city and year |
| Equity Evaluation Engine | PRAI score plus province metadata | CV, Gini, Theil, and province decomposition by year |
| Efficiency Evaluation Engine | Raw resource and service variables | Year-specific DEA efficiency score |
| Forecast Engine | Historical preschool-age population | Future population, conditional teacher demand, and fiscal need |
| Policy Simulation Engine | Raw baseline data and stated parameters | Baseline and four conditional scenario comparisons |
| LLM Interpretation Engine | Structured latest-year model outputs | Optional reviewed interpretation request or text response |

## 3. Inputs and Outputs

`run_research_pipeline()` requires a dataset matching the schema in `Data_Dictionary.md`. By default it writes to the project-level `results/` directory:

- `allocation_result.csv`
- `equity_result.csv`
- `efficiency_result.csv`
- `forecast_result.csv`
- `simulation_result.csv`
- `research_summary.md`

The default forecast horizon is the two years immediately after the final observed year. The default scenario parameters are prototype assumptions for workflow demonstration only: 10% subsidy increase, 8% population decline, 8% teacher-cost increase, annual base teacher cost of 80,000 yuan, 12% fiscal-capacity reduction, and a fiscal-capacity multiplier of 1.10. Researchers should replace all of these with documented study-specific assumptions.

## 4. LLM Interpretation Boundary

No external LLM call occurs unless the caller supplies an approved `llm_client`. Without one, the pipeline creates a reviewable interpretation request but records that no interpretation was generated. This default protects against implicit data transmission and ensures that the pipeline remains usable in offline or restricted research settings.

## 5. Use in Education Research

The pipeline can organise a descriptive research workflow from data preparation through allocation, distributional equity, relative efficiency, demographic-resource projections, and conditional policy scenarios. It is suitable for prototype analysis, method development, and reproducible demonstration.

Before substantive use, researchers should verify data provenance, population and institutional definitions, price adjustments, model assumptions, benchmark choices, comparison groups, and scenario transition mechanisms. The generated files are computational outputs, not self-validating research findings, causal evidence, or policy recommendations.
