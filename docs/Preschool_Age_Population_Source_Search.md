# Preschool-Age Population Source Search

## Purpose

This document records the controlled search for a definition-compatible
preschool-age population denominator. It distinguishes a source that was not
found in a particular search from a source that is demonstrably incompatible.

## Required variable

The real-data PRAI pilot requires an annual regional population explicitly
defined as ages 3-5 or 3-6. The geographic scope, reference date, unit, and
resident-versus-registered-population definition must be documented.

## Confirmed exclusion evidence

The National Bureau of Statistics' *China Population Census Yearbook 2020*,
Table 1-5, is an official provincial table but reports only the groups `0`,
`1-4`, and `5-9`. Its values cross the required age boundaries. It must not be
split, interpolated, or used as a strict preschool-age denominator. The archive
and independent review are registered as `NBS_2020_GROUPED_AGE_SCREEN`.

## Search record

Machine-readable search outcomes are in
`datasets/metadata/preschool_age_population_source_search_log.csv`.

The Guangdong Government public-search queries `学前三年 适龄人口` and
`学龄前儿童 人口` returned no relevant results on 30 July 2026. These negative
search outcomes do not establish non-existence and do not authorise a proxy.

The Guangdong Provincial Statistics Bureau site search and accessible topic
archive were also checked on 30 July 2026. Neither exposed a relevant
population-census age table. This is recorded as a navigation and search result
only; it does not demonstrate that a provincial tabulation is unavailable.

The Guangdong Provincial Department of Education public search was checked with
education-planning terminology. It did not return a definition-compatible
population table; the only `3至6周岁` results concerned curriculum or child
development. These results are not demographic evidence.

The National Bureau of Statistics official site search was checked on 31 July
2026 using `广东 3-5岁 人口`, `广东 3至5岁 人口`, and `广东 学前三年 适龄人口`.
It did not return a Guangdong table with an explicit 3-5 or 3-6 population
definition. This is a search result only; it neither establishes non-existence
nor permits the use of broad grouped-age data.

The archived official *Guangdong Statistical Yearbook 2025* was also checked
on 31 July 2026. Table 3-4, *Age Composition and Dependency Ratio of Permanent
Population*, reports 2015-2024 values only for `0-14`, `15-64`, and `65 and
over`. It does not provide single-year ages or a 3-5/3-6 group. The source has
been registered as `GD_YEARBOOK_2025_TABLE_3_4_SCREEN` and independently
confirmed as exclusion evidence on 1 August 2026; it may not be used as a
preschool-age denominator.

## Next official channels

1. Provincial population-census yearbooks or tabulation annexes that may publish
   a table beyond the national grouped-age release.
2. Provincial statistical or education authorities' planning appendices that
   explicitly publish the target-age population and its reference date.
3. Authorised administrative or census tabulations with a documented single-age
   or 3-5/3-6 definition.

Any candidate must be registered before extraction, archived without
modification, independently reviewed, and checked against the project variable
definition. A broad age group, enrolment count, gross-enrolment-rate inversion,
or demographic interpolation is not an acceptable substitute.

The Gansu Provincial Bureau of Statistics official *Gansu Statistical Yearbook
2025* was acquired through a normal browser session on 6 August 2026. Its
archive entry `zk/html/02-04.xls`, *Age Composition and Dependency Ratio of
Population*, reports only `0-14`, `15-64`, and `65 and over` groups for
2001-2024. It is recorded as `GANSU_YEARBOOK_2025_TABLE_2_4_SCREEN` and cannot
provide a strict 3-5 or 3-6 denominator without unsupported decomposition.
Independent source review remains pending.
