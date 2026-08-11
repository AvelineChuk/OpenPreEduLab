# Inclusive Education Research Framework

## 1. Background

The Inclusive Education Research Module extends OpenPreEduLab from resource
allocation toward the study of how policy and institutional support may be
reflected in inclusive practices and children's meaningful participation in
shared preschool life. It is educational research infrastructure, not a child
assessment, diagnosis, placement, or clinical service.

The module uses the conceptual pathway:

`Policy -> Resources -> Practices -> Child Participation -> Equity`

This pathway is a research framework. It has not been validated as a causal
model, and the arrows must not be interpreted as estimated effects.

## 2. Research Problems

The prototype supports five questions:

1. Do institutions report the policy and resource support needed for inclusion?
2. Are reported resources reflected in reported inclusive practices?
3. Are practices accompanied by meaningful participation in play, groups,
   peer interaction, communication, autonomy, and belonging?
4. Where are the largest descriptive support-conversion gaps?
5. How do explicit exploratory support scenarios change calculated profiles?

## 3. Conceptual Framework

The framework moves from inputs toward participation without treating children
as outcomes to be normalised. Policy and resources are enabling conditions;
practice describes institutional activity; participation concerns access to
shared educational life; equity concerns whether appropriate support and fair
participation opportunities are reported.

The module does not establish that one stage causes another. Associations,
correlations, gaps, clusters, and scenarios identify questions for further
research.

## 4. Five Dimensions

### Policy Support

- Policy Clarity
- Implementation Requirements
- Professional Support
- Resource Guarantee
- Evaluation Mechanism

### Resource Support

- Teacher Resources
- Special Education Support
- Financial Resources
- Material Resources
- Environmental Resources
- Training Resources
- Family and Community Resources

### Inclusive Practices

- Curriculum Adaptation
- Instructional Adaptation
- Individualized Support
- Behavior Support
- Peer Support
- Family Collaboration
- Teacher Reflection

### Child Participation

- Play Participation
- Group Activity Participation
- Peer Interaction
- Communication
- Autonomy
- Sense of Belonging

Child Participation is not a child-ability score. It is an aggregate research
description of meaningful participation in shared educational activities.

### Equity

- Support Equity
- Participation Equity
- Resource Equity

Equity does not mean identical support. It concerns appropriate support in
relation to need and fair opportunities for participation and development.

## 5. Support Gap

The module calculates Resource-to-Practice, Practice-to-Participation, and
overall Resource-to-Participation gaps. The complete mathematical specification
and interpretation rules are in
[Support Gap Methodology](Support_Gap_Methodology.md).

Support Gap is a descriptive diagnostic indicator. It is not a causal
estimator, treatment effect, risk score, or proof of institutional failure.

## 6. Research Logic

The first release separates four activities:

1. validate and standardise institution-level aggregate inputs;
2. calculate transparent equal-item dimension scores;
3. describe distributions, associations, gaps, and exploratory clusters; and
4. generate bounded insights, research-question candidates, and scenarios.

Deterministic insight rules operate before any optional LLM request. The LLM
receives calculated aggregate outputs only and cannot alter statistical results.

## 7. Data Structure

The unit of observation is one non-identifying institution record for one
declared observation period. Required identifiers are synthetic or approved
institution IDs, institution type, and broad region. The demonstration file is
`datasets/sample_inclusive_data.csv`.

All items are converted to a common 0–100 scale. Accepted conversion modes are:

- documented 0–100 values: unchanged;
- documented 0–1 values: multiplied by 100; or
- a researcher-declared custom interval: linear conversion using its stated
  minimum and maximum.

The platform does not guess a scale, automatically impute missing values, or
silently clip values outside the declared range. Transformation choices must
remain visible in exported research records.

## 8. Limitations

- Equal item weighting is a prototype assumption.
- The synthetic sample is structured for software testing, not empirical claims.
- Institution-level aggregates can mask within-institution variation.
- Correlation does not establish causation.
- K-means clusters are sample-dependent exploratory patterns.
- Scenario outputs change one reported item while holding others fixed and are
  not behavioural or policy forecasts.
- Content, construct, measurement-invariance, sensitivity, and external
  validation have not yet been completed.

## 9. Ethical Considerations

The public module must not receive names, contact details, clinical records,
individual education plans, disability determinations, photographs, or other
identifiable child, family, teacher, or case information. Uploaded CSVs are
processed in the current Streamlit session and are not intentionally persisted.

Scores must not be used to rank children, determine disability, make placement
or eligibility decisions, infer teacher quality, or replace professional and
family judgement. Any future individual-level research requires separate legal,
ethical, safeguarding, consent, security, retention, and governance approval.

## 10. Future Development

Future validation should include expert content review, instrument provenance,
reliability assessment, measurement invariance, alternative weights, missing-
data protocols, multilevel designs, longitudinal analysis, and independently
reviewed real-data studies. Causal questions require an explicit identification
strategy rather than interpretation of the conceptual arrows.
