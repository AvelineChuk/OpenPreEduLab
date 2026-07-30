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
