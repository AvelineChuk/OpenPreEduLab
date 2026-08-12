# Inclusive Education Content Validation Protocol

## 1. Purpose and status

This protocol defines the next methodological stage for the aggregate Inclusive Education Research Module. It is a **prospective validation plan**, not evidence that the current dimensions or items are valid. No expert ratings have yet been collected, and synthetic demonstration data cannot provide content-validity evidence.

The review concerns the conceptual pathway:

`Policy -> Resources -> Practices -> Child Participation -> Equity`

The arrows remain conceptual. Content review cannot establish causal effects.

## 2. Validation questions

The review should examine whether each item is relevant to its dimension, clear across preschool settings, observable at institution level, non-diagnostic and non-stigmatising, distinguishable from neighbouring items, appropriate for studying meaningful participation rather than child normalisation, and feasible without unnecessary personal data.

The panel should identify missing constructs, overlap, ambiguous terminology, context-dependent assumptions, and possible harms from score interpretation.

## 3. Proposed review panel

A future panel should combine preschool inclusive-education research, early-childhood practice, non-clinical special-education support, educational measurement, education policy, child-rights or safeguarding expertise, and family or disability-community perspectives. Participation should be accessible, supported, compensated where appropriate, and non-tokenistic.

Panel size, eligibility, conflicts of interest, geographic coverage, and language adaptation must be declared before ratings are collected. Reviewers must not receive identifiable child records.

## 4. Review materials

Each reviewer should receive a version-controlled packet containing the research questions, five dimension definitions, every item and its unit of analysis, proposed response scale, permitted and prohibited interpretations, Support Gap methodology, synthetic-data disclaimer, and a structured rating and comment form.

The child-participation boundary must remain prominent: items concern opportunities for and experiences of participation, not children's normality, ability, diagnosis, compliance, or worth.

## 5. Rating procedure

The initial round should independently rate each item's relevance and clarity using a declared four-category ordinal scale. This scale is a protocol choice, not a scientific fact. Reviewers should also comment and may recommend retain, revise, move, split, add, or remove.

Separate prompts should cover dimension coverage, item overlap, cultural and policy dependence, likely data source, feasibility, equity and accessibility, and risks of diagnostic, ranking, deficit-based, or causal misuse.

At least one moderated round should examine disagreements. Any Delphi-style process must preserve rating distributions, minority views, and revision reasons; consensus must not be manufactured by deleting dissent.

## 6. Prototype quantitative summaries

Quantitative summaries support, but do not replace, documented expert reasoning.

Item-level content validity index:

`I-CVI_j = n_relevant,j / N_j`

Scale-level average content validity index:

`S-CVI/Ave = (1 / k) * sum(I-CVI_j)`

If reviewers separately judge whether an item is essential, Lawshe's content validity ratio may be reported:

`CVR_j = (n_e,j - N_j / 2) / (N_j / 2)`

Any critical value must be chosen from a cited method appropriate to the realised panel size, not hard-coded or treated as proof of validity. Missing ratings, exclusions, and denominator changes must be reported; ratings must not be imputed.

## 7. Decision rules and audit trail

Decision rules must be registered before ratings are collected. No item should be kept or deleted from one threshold alone. Records should preserve the instrument version, rating distributions, eligible denominators, qualitative concerns, minority views, decision, rationale, safeguarding and equity implications, responsible reviewers, and need for another round.

Every change creates a new instrument version. Historical wording and decision records must remain reproducible.

The platform provides `inclusive_content_review_template.csv` as a blank data structure. Researchers must duplicate its complete 28-item block for each reviewer. The software validation layer rejects missing item ratings, duplicate reviewer-item rows, invalid categories, and item-dimension mismatches. It calculates numerical summaries without an automatic retain/remove decision. A completed CSV can be analysed in Researcher Mode; the upload is processed in the current session, and downloadable statistical summaries exclude reviewer identifiers, roles, comments, recommendations, and conflict disclosures. The research team remains responsible for safeguarding the original review record and interpreting qualitative dissent.

## 8. Ethical and governance requirements

Content review does not authorise identifiable or clinical child-data collection. Recruitment, consent, compensation, accessibility, confidentiality, and conflict-of-interest arrangements require prior governance approval.

The panel must reject items or interpretations that diagnose, label, rank, normalise, determine disability or placement, infer teacher quality, or replace professional and family judgement.

## 9. Completion criteria

Content review is complete only when panel composition, materials, ratings, comments, analysis, decisions, and the revised instrument version have an auditable record. This permits description of a content-review process; it does not establish reliability, construct validity, measurement invariance, external validity, or causal validity.

## 10. Subsequent validation stages

After content review and separate ethics and data-governance approval, future work may include cognitive interviews, feasibility testing, reliability analysis where theoretically appropriate, construct analysis, measurement-invariance assessment, alternative-weight sensitivity, and validation against independent measures. Real-data studies must follow repository review rules and cannot enter `datasets/processed/` without independent approval.