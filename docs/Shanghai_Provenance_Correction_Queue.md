# Shanghai Raw-Provenance Correction Queue

## Purpose

This queue records the three Shanghai staging datasets returned during
independent review because the SHA-256 values of retained HTML evidence do not
match the corresponding manifests. The staged numeric values were compared
successfully with the retained pages, but that does not repair the provenance
failure.

## Required corrections

Before changing a manifest, consult
`docs/Shanghai_Provenance_Discrepancy_Audit.md`. The repository-held files
currently reproduce the manifest hashes, while the review notes cite a distinct
evidence set. This contradiction requires explicit renewed-review resolution.

| Review ID | Dataset | Review issue | Required action | Analytical status |
| --- | --- | --- | --- | --- |
| `SH_KG_2020_2024` | `datasets/staging/shanghai_kindergarten_statistics_2020_2024.csv` | #24 | Restore the originally archived source matching the manifest, or update the manifest through a documented, reproducible provenance correction. Recheck the child-count mapping and teacher definition. | `return_for_correction` |
| `SH_POP_CONTEXT_2015_2024` | `datasets/staging/shanghai_population_context_2015_2024.csv` | #29 | Restore or correctly register both retained header and main-table hashes, with an explanation of the evidence change. | `return_for_correction` |
| `SH_FISCAL_CONTEXT_2015_2024` | `datasets/staging/shanghai_fiscal_context_2015_2024.csv` | #30 | Restore or correctly register both retained header and main-table hashes, with an explanation of the evidence change. | `return_for_correction` |

## Correction rules

1. Do not overwrite or delete the current retained evidence.
2. Record the official URL, retrieval date, file role, previous hash, corrected
   hash, and reason for the discrepancy.
3. Do not alter staging values merely to resolve a hash mismatch.
4. Submit the correction for a new independent review before changing the
   staging decision.
5. Keep all three datasets out of `datasets/processed/` until provenance and
   remaining definition questions are resolved.
