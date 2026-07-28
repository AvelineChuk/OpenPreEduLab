# Contributing to OpenPreEduLab

OpenPreEduLab is an academic open-source research prototype. Contributions are
welcome when they improve reproducibility, source transparency, statistical
validity, or documentation.

## Before contributing

1. Read the project [README](README.md),
   [Data Catalog](docs/Data_Catalog.md), and relevant model documentation.
2. Keep the distinction between implemented software, sample-data demonstration,
   and real-world empirical evidence explicit.
3. Do not present a model output as a validated policy finding without a
   documented research design and reviewed data.

## Data contributions

Follow the data promotion path:

```text
official source -> raw archive -> review -> staging -> independent review -> processed input
```

- Preserve raw files and record official URLs, scope, unit, retrieval date, and
  SHA-256 checksums.
- Do not silently remove extreme values, interpolate missing observations, or
  replace preschool-specific variables with broad population or education
  variables.
- Use `docs/Data_Review_Protocol.md` for staging data and
  `docs/Raw_Source_Review_Packet.md` for archived source-scope decisions.
- Open an **Independent data review** issue when requesting or recording a
  review. The template is available under GitHub's New issue menu.

## Code contributions

- Keep functions modular and documented.
- Add or update pytest coverage for behaviour changes.
- Run `python -m pytest tests -q` before opening a pull request.
- Do not change model assumptions or indicator definitions without updating the
  corresponding research documentation.

## Pull requests

Describe the research or reproducibility problem addressed, the files changed,
the checks run, and any remaining limitation. Small, scoped pull requests are
preferred.
