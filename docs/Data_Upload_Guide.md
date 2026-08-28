# Data Upload Guide

## Purpose

The OpenPreEduLab platform accepts a city-by-year CSV matching the PRAI
prototype schema. Platform checks validate file structure and basic logic; they
do not approve a dataset for substantive research use.

## Start with a template

Download `datasets/templates/prai_input_template.csv` from the platform or the
repository. Do not change column names. Each row represents one city-year
observation. Definitions, units, and theoretical rationale are in
`docs/Data_Dictionary.md`.

## Upload checks

The platform rejects files with missing fields, duplicate city-year pairs,
invalid numeric values, non-positive denominators, or a count of children not
enrolled that exceeds children seeking a place.

## Research-use boundary

A CSV that passes platform validation is not automatically an approved research
dataset. Before reporting results, retain original files and follow:

`raw → staging → independent review → processed`

Do not split broad age groups into a preschool-age denominator, substitute
general education expenditure for preschool-specific expenditure, or relabel
reported teacher headcounts as FTE without a reviewed mapping.
