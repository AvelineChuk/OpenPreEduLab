# User Interface Guide

## Purpose

The OpenPreEduLab interface is a local Streamlit research-prototype front end
for the existing allocation and equity modules. It is designed to make a
reproducible software workflow inspectable; it is not a policy-decision or
automatic-reporting system.

## Run locally

From the repository root, install dependencies and run:

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The application opens in a local browser window.

## Available workflow

1. Select the synthetic sample dataset or upload a PRAI-compatible CSV.
2. Inspect the schema and data-governance notice.
3. Calculate the MVP PRAI result using documented equal-dimension weights.
4. Inspect descriptive equity indicators for one selected year.
5. Review ranking, trend, heatmap, and dimension-profile visualisations.
6. Download calculated PRAI results for transparent downstream analysis.

## Data-governance boundary

An uploaded file is not automatically an approved research dataset. The
interface does not establish source provenance, harmonise definitions, impute
missing values, remove outliers, or convert reported teacher headcounts into
FTE values. Real data must follow the repository workflow:

`raw → staging → independent review → processed`

Until a definition-compatible processed dataset exists, interface outputs using
sample or user-provided data are software demonstrations only.
