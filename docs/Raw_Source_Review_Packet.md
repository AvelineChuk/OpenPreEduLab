# Raw Source Review Packet

## Purpose

This packet governs independently reviewing raw sources that have been archived
or screened but have **not** been transcribed into `datasets/staging/`. It
complements, rather than replaces, the staging-data process in
`docs/Data_Review_Protocol.md` and `docs/Independent_Review_Packet.md`.

The purpose is to prevent an apparently official source from being used beyond
its documented scope. It is a software and data-governance control, not policy
validation.

## Review Register

The review assignments are recorded in
`datasets/metadata/raw_source_review_register.csv`.

Each reviewer must be independent of the original source-screening or
transcription step. Before deciding, the reviewer must open the archived raw
file and its `README.md` / `manifest.csv`, then verify:

1. publisher and official publication URL;
2. document year, geographic scope, and unit;
3. the visible field or programme scope cited in the manifest;
4. whether the proposed use is narrower than, and consistent with, the source;
5. whether any stated exclusion remains justified.

## Allowed Decisions

Use one of these decisions in the raw-source register:

- `confirmed_policy_simulation_candidate`
- `confirmed_context_only`
- `confirmed_not_definition_compatible`
- `return_for_correction`
- `hold_for_definition_review`
- `not_reviewed`

No raw-source decision by itself authorizes copying values into
`datasets/processed/`. A separate staging record, value-level comparison, and
the existing staging-review protocol remain required.

## Current Safeguard

The Guangdong 2023 and 2025 sources are programme-level central-transfer
materials. Even if confirmed, they can be used only as policy-simulation
parameters. The 2020 census age table, Guangdong 2017 final-accounts table,
and Guangdong 2024 education-finance table remain excluded from strict
preschool fiscal or preschool-age population variables unless a later source
provides a definition-compatible mapping.
