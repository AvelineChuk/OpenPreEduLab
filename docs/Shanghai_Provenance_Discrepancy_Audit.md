# Shanghai Provenance Discrepancy Audit

## Purpose

Independent reviews in Issues #24, #29, and #30 recorded SHA-256 values that
differ from the Shanghai statistical-yearbook manifest. This audit checks the
repository-held evidence before any manifest correction is considered.

## Repository-held evidence check

On 30 July 2026, the current worktree file hashes were recomputed and compared
with `datasets/raw/provincial_china_2015_2025/shanghai/2025_statistical_yearbook/manifest.csv`.
They matched for every reviewed file:

| Source ID | File | Worktree SHA-256 | Manifest SHA-256 |
| --- | --- | --- | --- |
| `SHANGHAI_2025_C2017` | `C2017_kindergarten_basic.html` | `4ac93b23b584dfb10963c6abb928596959270232d67b4b6761658ebc34afa3cf` | same |
| `SHANGHAI_2025_C0201_HEADER` | `C0201_population_1978_2024_header.html` | `7167d306421840a943253a4dc698034546fd739f033cedddc4fbab646bbd1dfd` | same |
| `SHANGHAI_2025_C0201_MAIN` | `C0201_population_1978_2024_main.html` | `eaf746de0d58becc0ded4d229f5ce89fa535d9f9a4d5fb5f2107cc6c5168da07` | same |
| `SHANGHAI_2025_C0401_HEADER` | `C0401_general_public_budget_1978_2024_header.html` | `ef340591886e8c668684ba1d1e3302587df64f138a80dc38fa2e6a84f98e9838` | same |
| `SHANGHAI_2025_C0401_MAIN` | `C0401_general_public_budget_1978_2024_main.html` | `15b636561673d38e26d7bdd897e624dac5d48a3ec72f4ce6fdf7acc57406587` | same |

Git history also shows that these files have not changed since their original
source-archiving commits. The source values and staging files were not changed
by this audit.

## Interpretation

The hash values cited in the three review notes cannot currently be reproduced
from the repository-held files. They may refer to a different retrieval,
rendered representation, or reviewer-local artefact. This audit does not
invalidate the independent-review findings; it identifies an unresolved
evidence-set discrepancy.

## Required renewed review

The three staging decisions remain `return_for_correction`. A renewed reviewer
must state exactly which file was hashed, provide its retrieval or repository
path, and recompute the SHA-256 from the repository-held raw file before
deciding whether:

1. the original manifest is confirmed;
2. a separately documented raw-file replacement is required; or
3. an earlier reviewer-local artefact caused the mismatch.

No manifest hash, raw file, staging value, or processed dataset may be changed
until that provenance question is resolved.
