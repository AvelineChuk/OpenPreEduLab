# OpenPreEduLab v0.1.0

Release date: 2026-07-28

## Overview

OpenPreEduLab is an open-source AI research infrastructure prototype for preschool education research. It is intended to support data analysis, statistical modelling, policy simulation, and AI-assisted interpretation in preschool education research.

## Core Features

- Preschool Resource Allocation Index (PRAI) and Resource Allocation Engine.
- Educational Equity Evaluation using CV, Gini, and Theil measures.
- Input-oriented DEA Efficiency Evaluation Engine.
- Forecast Engine for population-linked teacher and fiscal requirements.
- Scenario-based Policy Simulation Framework.
- Matplotlib-based research visualisations.
- Provider-agnostic, evidence-bounded LLM Interpretation Module.
- End-to-end Research Pipeline, synthetic sample dataset, and dry-run demo.

## Research Workflow

```text
Dataset
  ↓
Data Processing
  ↓
Statistical Modeling
  ↓
Policy Simulation
  ↓
LLM Interpretation
  ↓
Research Output
```

The workflow is researcher-led. Statistical modules calculate documented outputs; the optional LLM layer interprets supplied results only and does not run by default.

## Current Limitations

This version is an early research prototype.

- It is a research prototype.
- It uses sample datasets for functional demonstration, not real-world evidence.
- Models require validation with real education data.
- Policy simulations depend on further calibration.
- Forecasts and policy simulations are conditional model outputs, not factual predictions or causal estimates.
- The project is not a commercial deployment or an automated policy decision system.

## Future Roadmap

### v0.2

- Integration with real-world preschool education datasets.
- Improved model validation.

### v0.3

- Knowledge graph integration.
- AI research agent exploration.

## Citation

Please use [CITATION.cff](CITATION.cff) when citing OpenPreEduLab in academic work.
