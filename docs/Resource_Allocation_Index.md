# Preschool Resource Allocation Index (PRAI)

## 1. Purpose and Research Question

The Preschool Resource Allocation Index (PRAI) is a proposed composite index for assessing the level of preschool education resource allocation across comparable geographic units, such as counties, districts, municipalities, or provinces, in a specified year.

Its central research question is:

> To what extent does a locality provide financially sustainable, professionally staffed, materially adequate, and demand-responsive preschool education provision for its resident children of preschool age?

PRAI is intended for descriptive comparison, longitudinal monitoring, and the identification of allocation dimensions requiring closer investigation. It is not a measure of educational quality, child development, policy effectiveness, or causal impact. A high PRAI score does not by itself establish that a policy caused better outcomes.

The index is designed to move beyond single-resource indicators, such as expenditure or teacher counts, by examining whether multiple types of resources are available in relation to educational demand.

## 2. Theoretical Framework

### 2.1 Conceptual definition

Preschool resource allocation refers to the organised distribution of public and institutional resources that enables age-appropriate preschool education provision. From an education-policy perspective, allocation should be assessed not only by the quantity of inputs but also by whether those inputs are adequate and accessible relative to the population requiring provision.

PRAI adopts a four-dimensional framework:

1. **Financial resources**: the fiscal capacity and regular financial support available for preschool education.
2. **Human resources**: the availability, professional qualification, and workload conditions of the preschool workforce.
3. **Material resources**: the physical capacity and basic conditions through which preschool education is delivered.
4. **Educational demand responsiveness**: the extent to which provision reaches and accommodates eligible children.

The framework is informed by input-based educational production perspectives, which recognise finance, staff, and facilities as enabling conditions for provision, and by equity-oriented allocation theory, which emphasises that resource adequacy must be assessed against need rather than absolute supply alone. The fourth dimension therefore treats demand as a reference point for allocation, not as a resource in itself.

### 2.2 Unit of analysis and comparability

The recommended unit is a geographically defined administrative area observed in a common reference year. All units included in one comparison should use the same definitions of preschool age, institution type, financial accounting scope, and geographic boundaries.

PRAI should not combine fundamentally incomparable data sources or administrative levels. It should also report its component scores; a single composite score must not replace analysis of the pattern beneath it.

## 3. Proposed Indicator System

The indicator system below is a proposed minimum conceptual structure. Indicator selection should be adapted only when definitions, data quality, and policy context are fully documented.

| First-level dimension | Second-level indicator | Operational meaning | Theoretical rationale |
| --- | --- | --- | --- |
| Financial Resources | Public preschool expenditure per enrolled child | Annual public expenditure on preschool education divided by the number of enrolled children, in comparable prices where multiple years are analysed | Per-child expenditure approximates the fiscal resources available to support provision while adjusting for service scale. |
| Financial Resources | Stable public funding share | Share of preschool expenditure financed through regular public-budget sources | Regular public funding indicates the degree to which provision is supported by predictable public finance rather than unstable or exceptional sources. |
| Human Resources | Qualified teacher rate | Share of preschool teachers meeting the applicable professional qualification requirement | Teacher qualifications represent the professional capacity required to deliver preschool education. |
| Human Resources | Teacher availability | Number of full-time-equivalent preschool teachers per 100 enrolled children | A staffing rate relates workforce supply to the number of children served and is more interpretable than an absolute teacher count. |
| Human Resources | Teacher workload | Average number of enrolled children per full-time-equivalent teacher | Excessive workload can constrain supervision, interaction, and instructional support; it is therefore treated as a pressure indicator. |
| Material Resources | Place availability | Licensed preschool places per 100 resident children in the target preschool-age population | Available places represent the basic physical capacity to provide service relative to potential demand. |
| Material Resources | Space adequacy | Usable indoor educational area per enrolled child | Space per child is a commonly used indicator of facility adequacy and the physical conditions of provision. |
| Material Resources | Average class size | Mean number of children per class | Large classes may limit interaction and supervision; class size is therefore a capacity-pressure indicator. |
| Educational Demand Responsiveness | Age-specific enrolment coverage | Enrolled children of the target age residing in the locality divided by resident children of the target preschool age | Coverage indicates the extent to which the eligible population is reached. Residence-based denominators should be used where possible to avoid distortions from cross-boundary enrolment. |
| Educational Demand Responsiveness | Unmet-demand rate | Estimated eligible children seeking a place but not enrolled divided by eligible children seeking a place | This indicator captures an observed gap between expressed demand and access. It requires a defensible source, such as registration or survey data. |
| Educational Demand Responsiveness | Capacity pressure | Enrolled children divided by licensed preschool places | Occupancy close to a policy-defined operating range may be acceptable, whereas sustained over-capacity provision signals demand-resource mismatch. |

### 3.1 Measurement notes

- All monetary measures should be converted to constant prices when comparing years. Where regional price differences are substantial and a suitable deflator exists, a spatial price adjustment should be considered.
- Full-time-equivalent (FTE) teachers are preferable to headcounts because part-time and non-teaching assignments otherwise distort staffing comparisons.
- “Qualified” must be defined using the applicable jurisdictional standard and reported in the data dictionary.
- Place availability and enrolment coverage should distinguish service provision from children’s residential location whenever data permit.
- The unmet-demand rate should be omitted, rather than imputed casually, when no credible measure of expressed demand exists. Its absence must be reported as a limitation.
- Capacity pressure has a non-linear interpretation. Both persistent over-capacity and substantial under-utilisation may require investigation; the preferred score is therefore defined around an explicit policy-relevant operating range.

## 4. Variable Direction

The direction of each variable follows its substantive meaning, not merely its numerical size.

| Indicator | Direction | Rationale |
| --- | --- | --- |
| Public preschool expenditure per enrolled child | Higher is better, subject to interpretation of efficiency | Greater per-child public support generally indicates greater financial capacity, but very high values may reflect high costs or small scale rather than superior provision. |
| Stable public funding share | Higher is better | A higher share indicates more regular public support. |
| Qualified teacher rate | Higher is better | Greater professional qualification strengthens staffing capacity. |
| Teacher availability | Higher is better | More FTE teachers per child reduces staffing scarcity. |
| Teacher workload | Lower is better | Fewer children per FTE teacher indicates lower workload pressure. |
| Place availability | Higher is better up to a policy-relevant adequacy threshold | More places relative to the eligible population improves capacity, but values far above need should be interpreted alongside utilisation. |
| Space adequacy | Higher is better up to a policy-relevant adequacy threshold | More usable space per child indicates more adequate physical conditions. |
| Average class size | Lower is better | Smaller classes generally reduce capacity pressure, subject to contextual minimum viable class size. |
| Age-specific enrolment coverage | Higher is better up to 100% | A higher share of resident eligible children enrolled indicates better reach; values above 100% require investigation of population mobility or data mismatch. |
| Unmet-demand rate | Lower is better | A lower share signals fewer eligible children unable to access a sought place. |
| Capacity pressure | Target-range indicator | The preferred value lies within a documented operating range rather than at either numerical extreme. |

The number of resident preschool-age children is not assigned a positive or negative direction and is not added directly to PRAI. It is an exposure variable used to construct demand-relative indicators. Treating a larger child population as intrinsically “better” or “worse” would conflate demographic size with allocation quality.

## 5. Standardisation Method

### 5.1 Preferred approach: benchmark-oriented scoring

For policy use and longitudinal comparability, PRAI should use transparent external benchmarks whenever credible standards are available. Let \(x_{ij}\) be the raw value of indicator \(j\) in locality \(i\), and let \(L_j\) and \(U_j\) be documented lower and upper reference values. These may be statutory standards, policy targets, or pre-specified empirical bounds justified in the study protocol.

For a benefit indicator (higher is better):

$$
z_{ij} = \min\!\left\{1,\max\!\left[0,\frac{x_{ij}-L_j}{U_j-L_j}\right]\right\}
$$

For a cost indicator (lower is better):

$$
z_{ij} = \min\!\left\{1,\max\!\left[0,\frac{U_j-x_{ij}}{U_j-L_j}\right]\right\}
$$

where \(z_{ij}\in[0,1]\). Clipping prevents extreme values from exerting disproportionate influence and makes clear that the upper benchmark represents adequate attainment, not unlimited desirability.

For a target-range indicator such as capacity pressure, let \([a_j,b_j]\) be the preferred range and \(L_j<a_j\leq b_j<U_j\) be tolerable outer bounds:

$$
z_{ij} =
\begin{cases}
0, & x_{ij} \leq L_j, \\
\dfrac{x_{ij}-L_j}{a_j-L_j}, & L_j < x_{ij} < a_j, \\
1, & a_j \leq x_{ij} \leq b_j, \\
\dfrac{U_j-x_{ij}}{U_j-b_j}, & b_j < x_{ij} < U_j, \\
0, & x_{ij} \geq U_j.
\end{cases}
$$

All reference values and their policy or theoretical justification must be published with a PRAI application.

### 5.2 Fallback approach: sample-based min–max normalisation

Where external benchmarks do not yet exist, a cross-sectional MVP may use min–max normalisation after pre-specified treatment of outliers, such as winsorising at the 1st and 99th percentiles. The same benefit and cost formulas apply, replacing \(L_j\) and \(U_j\) with the retained sample minimum and maximum.

This fallback is suitable only for relative comparison within the stated sample. Scores from separately normalised samples or years are not directly comparable. It should therefore be replaced by benchmark-oriented scoring as soon as justified reference values are available.

## 6. Weighting Method

Three candidate weighting strategies are considered.

| Method | Principle | Strengths | Limitations |
| --- | --- | --- | --- |
| Equal weight | Assign the same weight to each dimension and, within each dimension, each retained indicator | Transparent, reproducible, easy to audit, and consistent with an early-stage framework without defensible evidence that one dimension is intrinsically more important | May not reflect substantive priorities or empirical variation in all contexts |
| Entropy Weight Method | Assign greater weight to indicators with greater observed dispersion or information content | Data-driven and responsive to observed variation | Statistical variation is not equivalent to educational importance; weights can change substantially with the sample and may privilege noisy indicators |
| Principal Component Analysis (PCA) | Derive weights from covariance structure and retain common variance across indicators | Can reduce dimensionality and identify correlated empirical patterns | Components can be difficult to interpret, are sample-dependent, require adequate sample size and diagnostics, and do not necessarily represent the normative construct of adequate allocation |

### 6.1 MVP weighting decision

The recommended MVP uses **equal dimension weights**. Each of the four first-level dimensions receives a weight of \(1/4\). Within each dimension, the indicators retained after data-quality review receive equal shares of that dimension’s weight.

This choice is appropriate at the foundation stage because PRAI is a theory-led policy-research construct rather than a purely empirical latent variable. Equal weights make normative assumptions visible and avoid implying that cross-sectional dispersion or covariance establishes educational priority.

Entropy weighting and PCA should be used later as robustness checks, not as default replacements. A PRAI report should state whether substantive conclusions change under those alternatives.

## 7. Mathematical Specification

Let \(D=\{F,H,M,R\}\) denote the four dimensions: Financial Resources, Human Resources, Material Resources, and Educational Demand Responsiveness. Let \(J_d\) be the set of indicators retained in dimension \(d\), and let \(n_d=|J_d|\).

The score for locality \(i\) on dimension \(d\) is:

$$
S_{id} = \sum_{j\in J_d} \frac{1}{n_d}z_{ij}
$$

where \(z_{ij}\) is the standardised indicator score defined above.

The equal-weight PRAI is:

$$
\operatorname{PRAI}_{i} = 100 \times \sum_{d\in D}\frac{1}{4}S_{id}
$$

Equivalently:

$$
\operatorname{PRAI}_{i} = 25\left(S_{iF} + S_{iH} + S_{iM} + S_{iR}\right)
$$

Thus, \(\operatorname{PRAI}_{i}\in[0,100]\) when all component scores are available. The four dimension scores must be reported alongside the overall score.

### 7.1 Missing-data rule

An overall PRAI score should not be produced when an entire first-level dimension is missing. If an indicator within a dimension is unavailable, the dimension score may be calculated from the remaining pre-specified indicators only when at least two indicators remain and the omission is disclosed. No missing value should be assigned a favourable score.

For the MVP, any unit failing these minimum requirements should be labelled “insufficient data for composite scoring” and may still be presented in a component-level data table.

## 8. Output Interpretation

PRAI scores are structured summaries of observed allocation conditions relative to stated reference values. They are not rankings of educational quality or administrative performance in a comprehensive sense.

| PRAI range | Interpretive label | Interpretation |
| --- | --- | --- |
| 80–100 | Relatively strong allocation conditions | Most observed indicators meet or approach the documented reference values; component scores should still be examined for hidden weaknesses. |
| 60–79 | Moderate allocation conditions | Provision is partially adequate, but one or more dimensions require targeted attention. |
| 40–59 | Constrained allocation conditions | Multiple indicators fall below reference values; the component profile should guide diagnostic analysis. |
| 0–39 | Substantially constrained allocation conditions | Observed resources and/or demand responsiveness are far below stated reference values; results warrant contextual investigation rather than automatic policy prescription. |

These bands are provisional communication categories, not universal thresholds. They are defensible only when the benchmark values used in standardisation are documented and relevant to the policy setting. Reports should display uncertainty, data limitations, and the four component scores rather than relying on a league table alone.

## 9. Academic Contribution

PRAI offers four potential contributions to preschool education resource-allocation research.

1. **Multi-dimensional conceptualisation.** It integrates finance, workforce, facilities, and demand responsiveness rather than treating any one resource input as a sufficient account of allocation.
2. **Demand-relative evaluation.** It treats the child population and expressed demand as denominators or contextual references, avoiding the conceptual error of interpreting demographic size as allocation quality.
3. **Transparent and reproducible construction.** Indicator definitions, directionality, reference values, standardisation rules, weights, and missing-data rules are specified explicitly. This makes the model inspectable, replicable, and open to revision.
4. **Policy-diagnostic output.** By reporting dimension-level scores as well as a composite score, PRAI can identify whether a locality’s constraint is primarily fiscal, human-resource, material, or demand-responsive. This design creates a bridge from descriptive comparison to later policy-scenario analysis.

The index does not resolve all normative questions about what counts as adequate preschool provision. Instead, it makes those questions explicit, documents the assumptions used to answer them, and provides a common structure through which competing definitions can be tested.

## 10. Recommended Validation Before Use

Before PRAI is used in substantive research or policy comparison, the proposed specification should undergo:

- content validation with preschool education, public-finance, and statistical-methods experts;
- data-quality assessment, including definitional consistency across locations;
- sensitivity analysis for benchmarks, indicator inclusion, and weighting strategies;
- construct validation against related but distinct measures, without assuming that correlation proves validity;
- subgroup and spatial analysis to assess whether the index masks within-area inequality; and
- transparent reporting of uncertainty and limitations.

PRAI is therefore a proposed research model that requires empirical validation and contextual adaptation, not a finished universal measurement standard.
