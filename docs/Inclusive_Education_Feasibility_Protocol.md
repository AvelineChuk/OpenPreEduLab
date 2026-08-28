# Inclusive Education Feasibility Pilot and Data Quality Protocol

## 1. Purpose and boundary

This protocol governs software-level review of whether the aggregate Inclusive Education instrument can be administered and recorded as intended. It describes completion, missingness, observed response distributions, duration, burden, and administration modes.

It does not establish reliability, content validity, construct validity, measurement invariance, external validity, or causal validity. It does not assess children or institutions and does not automatically remove, rescore, or impute items.

## 2. Unit of observation and privacy

One row represents one non-identifying institutional pilot administration. Use a pseudonymous administration ID, instrument version, broad administration mode, completion status, duration, burden rating, and item responses.

Do not include names, contact details, child or family records, teacher-level evaluations, clinical information, photographs, case narratives, or other unnecessary personal data. Uploaded records are processed in the current Streamlit session and are not intentionally persisted.

## 3. Missingness is preserved

The formal five-dimension scoring workflow rejects missing item values. The feasibility workflow deliberately preserves legitimate missingness because incomplete responses are part of the implementation question. Missing values are never silently imputed and incomplete pilot rows are not passed into five-dimension scoring.

Non-empty non-numeric text is an error, not missing data. Observed values must be finite and fall within the researcher-declared response interval.

## 4. Completion status

The software checks administration status against observed item completion:

- `complete`: all 28 current items have observed responses;
- `partial`: at least one but fewer than 28 items have observed responses; and
- `abandoned`: no item response is observed.

Duration must be positive. Burden uses a declared prototype category from 1 to 5. These categories describe implementation burden only and are not quality ratings of people or institutions.

## 5. Descriptive audit outputs

The audit reports:

- administration, complete, partial, and abandoned counts;
- completion rate by instrument version;
- duration and burden summaries;
- average number of answered items;
- item missing counts and rates;
- floor and ceiling endpoint concentration among observed responses;
- observed means, standard deviations, and unique-value counts;
- distributions of missing-item counts; and
- administration-mode summaries.

Floor and ceiling rates use observed responses as their denominator. Missing rates use all submitted administrations as their denominator.

## 6. Follow-up flags

Researchers explicitly select endpoint and missingness flag thresholds. Default interface values are prototype convenience parameters, not universal psychometric standards. Flags indicate questions for further investigation only.

A missingness, endpoint, or no-variation flag must not automatically trigger item removal, wording changes, score correction, diagnosis, ranking, or a validity claim. Possible explanations include limited sample size, homogeneous settings, administration procedures, unclear wording, response-scale design, or genuine concentration.

## 7. Interpretation and future validation

Feasibility evidence should be interpreted with administration notes, cognitive interviews, content-review records, version metadata, participant coverage, and research context. A small feasibility pilot may detect software and implementation problems but cannot establish stable distributional properties.

Future work may require a governed pilot sample, pre-specified recruitment and administration procedures, qualitative follow-up, reliability assessment where theoretically appropriate, construct analysis, measurement-invariance work, and external validation.

## 8. Completion criteria

A feasibility round is complete only when the instrument version, administration procedures, response interval, missing-data rules, flag thresholds, coverage, limitations, and follow-up decisions are documented. Completion means the pilot process has an auditable record; it does not mean the instrument is validated. If complete governed responses are available, preliminary consistency analysis should follow the [Preliminary Reliability Protocol](Inclusive_Education_Reliability_Protocol.md).
