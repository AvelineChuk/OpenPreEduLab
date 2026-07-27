# Preschool Education Efficiency Evaluation

## 1. Research Objective

The Preschool Education Efficiency Evaluation Engine examines whether observed preschool education inputs are transformed into selected educational service and quality-related outputs efficiently relative to comparable localities.

It addresses a distinct question from the other OpenPreEduLab models:

| Analytical perspective | Core question |
| --- | --- |
| Resource allocation | How adequate are the financial, human, material, and demand-responsive conditions of preschool provision? |
| Educational equity | How evenly are observed resource conditions distributed across localities? |
| Educational efficiency | Given selected inputs, how effectively does a locality produce selected preschool education outputs relative to comparable localities? |

Efficiency is therefore not a measure of how many resources a locality has, nor whether those resources are fairly distributed. It is a relative relationship between inputs and outputs under a stated model.

## 2. Why Data Envelopment Analysis (DEA)

Data Envelopment Analysis is a non-parametric frontier method for comparing decision-making units (DMUs) that use multiple inputs to produce multiple outputs. It is suitable for preschool education research because localities combine heterogeneous resources—finance, teachers, and facilities—to deliver more than one service outcome, and because an explicit production function is often unavailable.

DEA does not require the researcher to pre-specify a single functional form linking inputs to outputs. Instead, it constructs an empirical best-practice frontier from the observed comparison group. Each locality is evaluated against feasible combinations represented by that frontier.

This advantage requires caution. DEA is sensitive to variable selection, measurement error, outliers, and the composition of the comparison group. It identifies relative technical efficiency in the sample; it does not prove management quality, policy effectiveness, or causal mechanisms.

## 3. DEA Framework

### 3.1 Decision-making unit

The default DMU is a **city in a single year**. A panel dataset is evaluated year by year, producing a city-year efficiency score. This avoids treating changes in prices, demographic structure, or system conditions over time as though they were purely cross-sectional differences.

### 3.2 Inputs and outputs

For DMU \(o\), let \(\mathbf{x}_o\) be a vector of \(m\) positive inputs and \(\mathbf{y}_o\) a vector of \(s\) positive outputs. The default engine estimates an input-oriented variable-returns-to-scale (VRS/BCC) DEA model:

$$
\min_{\theta,\boldsymbol{\lambda}} \quad \theta
$$

subject to:

$$
\sum_{j=1}^{n} \lambda_j \mathbf{x}_j \leq \theta\mathbf{x}_o
$$

$$
\sum_{j=1}^{n} \lambda_j \mathbf{y}_j \geq \mathbf{y}_o
$$

$$
\sum_{j=1}^{n} \lambda_j = 1,
\qquad
\lambda_j \geq 0 \quad (j = 1,\ldots,n)
$$

The convexity condition \(\sum_j\lambda_j=1\) creates the VRS/BCC frontier. The engine also permits a constant-returns-to-scale (CRS/CCR) specification, which removes this condition, but VRS is the default because city preschool systems may operate at different scales.

### 3.3 Efficiency score

The estimated score \(\theta\) lies in the interval \((0,1]\):

- \(\theta=1\): the DMU is relatively technically efficient under the selected DEA model and observed comparison set.
- \(\theta<1\): the DMU is relatively inefficient; the model identifies proportional input-reduction potential while holding the selected outputs constant.

The score does not indicate that a locality has achieved an absolute optimum. A score of one means only that no better comparator is identified within the modelled sample.

## 4. Variable Design

Variable selection must be guided by educational theory and data validity. Inputs are resources consumed or committed to preschool provision; outputs are service, access, or quality-related results. A variable should not ordinarily be entered as both an input and an output in the same model.

### 4.1 Proposed inputs

| Input domain | Variable | Educational meaning |
| --- | --- | --- |
| Financial input | Total government preschool expenditure | Public financial resources committed to preschool provision. Total expenditure, rather than expenditure per child, is appropriate when the model also evaluates service volume. Monetary values should be expressed in comparable prices. |
| Human input | Full-time-equivalent preschool teachers | Professional labour available to organise, teach, supervise, and care for enrolled children. FTE counts are preferable to headcounts. |
| Human input, optional | Qualified teacher FTE | Professionally qualified labour capacity. This may be used instead of, rather than in addition to, a qualification-rate output when redundancy would distort the model. |
| Physical input | Usable indoor educational area | Facility space committed to preschool service provision. It should be defined consistently across localities. |
| Physical input, optional | Classroom resources or number of classrooms | Physical capacity used to deliver preschool services. These variables require careful treatment to avoid double-counting facility inputs. |

### 4.2 Proposed outputs

| Output domain | Variable | Educational meaning |
| --- | --- | --- |
| Access output | Enrolled children | Volume of preschool service actually delivered. It should be interpreted jointly with population need and quality indicators. |
| Coverage output | Age-specific enrolment coverage | Reach of provision among resident children in the target preschool-age group. Residence-based definitions reduce distortion from cross-boundary enrolment. |
| Public coverage output, optional | Public or publicly supported preschool coverage rate | Access to publicly supported provision among eligible children. It requires a clearly documented definition of public provision. |
| Quality-related output | Qualified teacher rate | Professional qualification composition of the workforce, used as a limited observable quality proxy. It does not measure teaching process quality or child development. |

The sample-data helper in `models/efficiency.py` uses total government expenditure, FTE teachers, and indoor area as inputs; enrolment, age-specific coverage, and qualified teacher rate as outputs. This is an illustrative MVP specification for synthetic data, not a validated empirical specification.

## 5. Implementation Design

The module provides three reusable functions:

- `prepare_efficiency_data()`: derives a minimal DEA-ready dataset from the PRAI sample-data schema;
- `calculate_dea_efficiency()`: estimates input-oriented DEA for one cross-sectional set of DMUs; and
- `evaluate_panel_efficiency()`: applies the DEA model separately to every year in a city-year panel and returns `city`, `year`, and `efficiency_score`.

The implementation uses linear programming and requires strictly positive input and output values. Input orientation is chosen because local governments commonly face the question of whether existing financial, human, and facility commitments can produce comparable service outputs with less resource use. This choice must be reconsidered if the research question instead concerns feasible output expansion under fixed inputs.

## 6. Interpretation and Educational Policy Significance

DEA can organise descriptive evidence about the relationship between preschool investments and observable service outputs. Used alongside allocation and equity results, it can distinguish a locality with limited resources from one that has lower relative output for its observed input combination.

However, the engine must not be used as an automatic performance ranking tool. A low score can reflect unobserved need, service for children requiring additional support, geographic costs, population dispersion, data-quality problems, or a poorly specified model. A high score can coexist with inadequate absolute provision or inequitable access.

For research reporting, retain the selected variables, units, data sources, price adjustments, DMU set, returns-to-scale assumption, orientation, exclusions, and sensitivity analyses. The present engine provides efficiency evaluation only; it does not conduct policy simulation or produce policy recommendations.
