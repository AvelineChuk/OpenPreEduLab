# Data Directory

This directory is organised for transparent research data governance. It does
not currently contain a validated real-world PRAI panel.

## Directory layers

| Location | Purpose | Current status |
| --- | --- | --- |
| `sample_preschool_data.csv` | Synthetic, documented sample data for software demonstrations and tests | Not real-world evidence |
| `raw/` | Immutable copies of official source files, source manifests, and review evidence | Not model-ready |
| `staging/` | Source-faithful transcriptions prepared for independent comparison | One programme-parameter table conditionally approved; two kindergarten tables held for definition review; remaining tables pending independent review |
| `processed/` | Definition-compatible records approved for a specific analytical use | Intentionally empty |
| `metadata/` | Source coverage, review registers, priority worklists, and governance records | Active |

## Required promotion path

```text
Official source
  -> raw archive and checksum
  -> source-scope review
  -> staging transcription and independent comparison
  -> definition harmonisation
  -> processed analytical input
```

No record may skip a stage. In particular, a general education-expenditure
series must not be relabelled as preschool expenditure, and a grouped age table
must not be relabelled as a 3-5 or 3-6 preschool-age population series.

## Current pilot status

The project has one conditionally approved programme-parameter staging dataset,
two source-faithful kindergarten datasets held for teacher-definition review,
nine other staged datasets awaiting independent review, and a separate
raw-source review register for archived sources. The `processed/` layer remains
empty because annual, definition-compatible preschool-age population and
preschool-specific public-expenditure variables have not yet been established.

Some Guangdong central transfer-payment records are retained as potential
policy-simulation parameters. They are programme-specific and must not be used
as province-wide preschool expenditure or PRAI fiscal inputs.

See [Data Catalog](../docs/Data_Catalog.md),
[Data Review Protocol](../docs/Data_Review_Protocol.md), and
[Raw Source Review Packet](../docs/Raw_Source_Review_Packet.md).

## Source rights and reuse

Each archive retains its official publication URL and checksum in a local
manifest. Users must comply with the original publisher's terms and applicable
law. Archiving a source for research traceability does not change its rights or
make it a validated analytical dataset.
