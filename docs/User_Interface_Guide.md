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

## Platform structure

The application has two connected spaces:

1. **Landing Page** — an editorial introduction to the research challenge,
   workflow, modules, and research philosophy. Select **Launch Platform** to
   enter the workspace.
2. **Research Platform** — a sidebar-based research workspace with an overview,
   data layer, PRAI, equity, visualisation, and module-status pages.

The Landing Page is intentionally a research presentation rather than a
generic data-dashboard entry point. The platform uses a restrained white,
soft-gray, and deep-blue visual system to keep analytical content primary.

## Available workflow

1. Select the synthetic sample dataset or upload a PRAI-compatible CSV in the
   sidebar.
2. Inspect the Data page for schema and research-governance boundaries.
3. Calculate the MVP PRAI result and download it for transparent downstream
   analysis.
4. Inspect descriptive equity indicators and the ranking, trend, heatmap, and
   dimension-profile visualisations.
5. Run the documented prototype interfaces for DEA efficiency, population and
   resource forecasting, and conditional policy scenarios. Their visible
   assumptions remain adjustable and their outputs are exportable.
6. Use **AI Interpretation** either to download a bounded prompt or, after
   explicit consent and with a visitor-controlled DeepSeek key, generate a
   clearly labelled interpretation draft. The resulting interpretation record
   can be downloaded as Markdown, Word, or PDF.
7. Use **Reports** to download the same research-run summary as Markdown,
   Word, or PDF.

These interactive functions demonstrate reproducible software workflows. They
do not validate a dataset, establish causal effects, or turn a prototype output
into a policy conclusion.

## Data-governance boundary

An uploaded file is not automatically an approved research dataset. The
interface does not establish source provenance, harmonise definitions, impute
missing values, remove outliers, or convert reported teacher headcounts into
FTE values. Real data must follow the repository workflow:

`raw → staging → independent review → processed`

Until a definition-compatible processed dataset exists, interface outputs using
sample or user-provided data are software demonstrations only.

## Research report downloads

The **Reports** page creates one bounded research-run summary and lets the
visitor select its presentation format before downloading:

- **Markdown (.md)** for transparent, version-controlled research records;
- **Word (.docx)** for reading, annotation, and sharing with collaborators; or
- **PDF (.pdf)** for a fixed-layout copy.

The three formats contain the same computed summary and research-use note.
Changing the file format does not validate a dataset or turn a prototype run
into a real-world policy finding.
