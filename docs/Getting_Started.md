# Getting Started with OpenPreEduLab

## 1. Clone the Repository

```bash
git clone <your-repository-url>
cd OpenPreEduLab
```

Replace `<your-repository-url>` with the repository address shown on GitHub.

## 2. Install Dependencies

OpenPreEduLab v0.1 requires Python 3.10 or later. Install the packages used by the implemented modules:

```bash
python -m pip install numpy pandas scipy scikit-learn matplotlib
```

The core workflow does not require an external LLM account or API key. The LLM Interpretation Engine remains inactive unless a researcher explicitly supplies an approved client.

## 3. Prepare a Dataset

Start with `datasets/sample_preschool_data.csv`, which is synthetic test data. For substantive work, prepare an authorised city-year CSV matching [Data_Dictionary.md](Data_Dictionary.md).

Key requirements include:

- one unique observation for each `city` and `year`;
- consistent definitions of preschool age, institution scope, finance, and teacher qualification;
- non-negative, valid count and resource fields; and
- documented sources, transformations, geographic boundaries, and price-year treatment.

Do not treat the sample dataset or its computed outputs as evidence about real places.

## 4. Run the Research Pipeline

From the project root, run:

```bash
python -c "from pipeline.research_pipeline import run_research_pipeline; run_research_pipeline('datasets/sample_preschool_data.csv')"
```

The pipeline runs PRAI, equity, efficiency, forecast, and policy-simulation modules and writes the following files to `results/`:

- `allocation_result.csv`
- `equity_result.csv`
- `efficiency_result.csv`
- `forecast_result.csv`
- `simulation_result.csv`
- `research_summary.md`

The pipeline uses documented prototype assumptions for forecasts and scenarios. Pass study-specific `forecast_years` and `scenario_parameters` when conducting a research application.

## 5. Run the LLM Interpretation Demo

The bundled demo shows how structured model results are transformed into a reviewable prompt:

```bash
python demo/llm_interpretation_demo.py
```

It is intentionally a dry run. It does not contact an external LLM and does not generate an interpretation. Before connecting an external provider, review the input data, prompt, data-governance requirements, and the limitations in [LLM_Interpretation.md](LLM_Interpretation.md).

## 6. Interpret Results Responsibly

Treat all outputs as model-dependent analytical artefacts:

- PRAI describes resource-allocation conditions under stated indicators, normalisation, and weights.
- CV, Gini, and Theil describe observed distributional inequality; they do not establish causes.
- DEA reports relative efficiency within the selected comparison set and specification.
- Forecast outputs are linear-trend projections conditional on historical data and planning assumptions.
- Simulation outputs are conditional scenarios, not factual policy forecasts.
- LLM text is a draft for researcher review, not an empirical result or automatic research conclusion.

Read the associated method documentation before reporting any result in a paper, presentation, or policy discussion.
