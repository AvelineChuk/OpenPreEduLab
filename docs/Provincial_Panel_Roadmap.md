# Provincial China Panel Roadmap (2015–2025)

## Scope

The first real-data empirical panel is proposed as 31 provincial-level regions in China observed annually from 2015 to 2025. This is a proposed data-development scope, not a completed dataset.

## Why Provincial Level First

Provincial-level data offer a more realistic initial balance between policy relevance, source authority, temporal continuity, and definition consistency than a national city-by-year collection assembled from heterogeneous local websites. The panel can support initial resource-allocation, regional-equity, efficiency, forecast, and scenario analyses after validation.

## Collection Order

1. Population and enrolment denominators.
2. Teacher counts and qualification measures.
3. Kindergarten, place, class, and facility measures.
4. Public financial expenditure and funding-source measures.
5. Expressed demand and unmet-demand measures, only where an authorised comparable source is identified.

## Pilot Source Availability

The five-region pilot begins with Beijing, Shanghai, Guangdong, Sichuan, and Gansu. Official statistics and education portals for the first four regions were accessible during the initial source audit. The Gansu statistics and education portals returned HTTP 412 to automated requests. This is an access limitation, not evidence of unavailable data. Gansu files must be acquired through an ordinary authorised browser session and registered manually; the project will not circumvent access controls.

The audit record is maintained in `datasets/metadata/pilot_source_availability.csv`.

## Release Gates

The panel may advance from raw archive to staging only after source registration and checksum capture. It may advance from staging to processed data only after definition harmonisation, logical checks, extreme-value review, and a documented decision log. It may advance to substantive models only after methodology review and sensitivity analysis.

## Interface Timing

A static GitHub Pages documentation site can be developed during data collection. An interactive analysis interface should begin only after a quality-reviewed provincial pilot is complete and at least one end-to-end real-data validation run has been reproduced. The first interface should display documented, precomputed outputs rather than offer unrestricted automatic inference or unreviewed LLM conclusions.
