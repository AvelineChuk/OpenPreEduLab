# Educational Equity Evaluation

## 1. Purpose and Scope

The Educational Equity Engine evaluates how evenly preschool education resource-allocation conditions are distributed across comparable localities in a common reference year. Its default input is the Preschool Resource Allocation Index (PRAI), although the same tools can be applied separately to a documented financial, teacher-resource, facility, or access indicator.

The engine addresses four descriptive research questions:

- How dispersed are resource-allocation conditions across localities?
- How unequal is the distribution of financial and composite resource conditions?
- How much observed inequality lies within versus between meaningful geographic groups?
- Do observed resource patterns indicate differences in the conditions supporting preschool access?

This is a resource-distribution evaluation tool. It does not independently measure child development, family affordability, service quality, procedural fairness, or causal policy effects. Resource equity is an important condition for opportunity equity, but it is not equivalent to opportunity equity in its entirety.

## 2. Theoretical Basis

Educational equity concerns whether children and communities have sufficiently fair opportunities to access educational provision. In preschool education, those opportunities are shaped by the public resources, professional staff, physical capacity, and demand-responsive provision available in each locality.

PRAI summarises multiple allocation conditions; the Equity Engine evaluates the distribution of those scores. This two-stage design separates a question of **adequacy and resource configuration** from a question of **distributional inequality**. A locality can have a high score relative to others while the overall distribution remains unequal, and a low-inequality distribution can still be inadequate in absolute terms. Both questions must be reported.

For fiscal and teacher-resource research, the same measures should also be run on individual indicators—for example, public expenditure per child, qualified teacher rate, or FTE teachers per 100 children—rather than relying solely on the composite PRAI score.

## 3. Analytical Unit and Preconditions

Equity statistics should be calculated for a set of comparable localities in the same year. The localities must use consistent definitions of preschool age, institution coverage, financial scope, teacher qualification, and geographic boundaries.

For a panel dataset, calculate a separate cross-sectional report for each year. Pooling multiple years without adjustment can confound geographical inequality with temporal change. All evaluated values must be non-negative and have a non-zero mean.

Theil decomposition additionally requires a complete, substantively meaningful group classification, such as province, a pre-specified macro-region, or urban–rural category. Group definitions must be documented before interpretation.

## 4. Coefficient of Variation (CV)

### Definition

The coefficient of variation expresses relative dispersion as the sample standard deviation divided by the mean:

$$
\operatorname{CV} = \frac{s}{\bar{x}}
$$

where \(s\) is the sample standard deviation of the locality-level resource value \(x_i\), and \(\bar{x}\) is the arithmetic mean.

### Interpretation

Lower CV values indicate less relative dispersion and therefore a more even observed distribution. CV is useful for comparing relative variation across indicators with different units, provided the compared populations and time periods are substantively comparable. It is not bounded above and can be sensitive when the mean is close to zero.

## 5. Gini Coefficient

### Definition

For \(n\) localities with sorted non-negative values \(x_{(i)}\), the Gini coefficient is calculated as:

$$
G = \frac{2\sum_{i=1}^{n} i x_{(i)}}{n\sum_{i=1}^{n} x_{(i)}} - \frac{n+1}{n}
$$

### Interpretation

The Gini coefficient equals zero under complete equality in the observed distribution. Larger values indicate greater inequality and approach one as inequality becomes extreme. It provides an intuitive summary of distributional inequality but does not identify which dimension or which groups account for the disparity.

## 6. Theil T Index and Decomposition

### Total inequality

The Theil T index is:

$$
T = \frac{1}{n}\sum_{i=1}^{n}\frac{x_i}{\bar{x}}\ln\!\left(\frac{x_i}{\bar{x}}\right)
$$

where terms with \(x_i=0\) are treated as zero by continuity. Lower values indicate a more equal observed distribution.

### Within-group and between-group inequality

When localities are assigned to groups \(g\), total Theil inequality is additively decomposed:

$$
T = T_{\mathrm{within}} + T_{\mathrm{between}}
$$

$$
T_{\mathrm{within}} = \sum_g \frac{n_g\bar{x}_g}{n\bar{x}}T_g
$$

$$
T_{\mathrm{between}} = \sum_g \frac{n_g\bar{x}_g}{n\bar{x}}\ln\!\left(\frac{\bar{x}_g}{\bar{x}}\right)
$$

where \(n_g\), \(\bar{x}_g\), and \(T_g\) are the number of localities, mean resource value, and Theil index within group \(g\). The within component represents inequality among localities belonging to the same group; the between component represents inequality associated with group mean differences.

The components are descriptive. A large between-group component does not establish that group membership caused the observed difference.

## 7. Provisional Equity Classification

The MVP uses transparent descriptive bands. They are reporting conventions, not universal policy targets, and should be calibrated to the relevant institutional and empirical context before high-stakes use.

| Statistic | Excellent Equity | Moderate Equity | Low Equity |
| --- | --- | --- | --- |
| CV | \(CV\leq0.10\) | \(0.10<CV\leq0.30\) | \(CV>0.30\) |
| Gini | \(G\leq0.20\) | \(0.20<G\leq0.40\) | \(G>0.40\) |
| Theil T | \(T\leq0.10\) | \(0.10<T\leq0.20\) | \(T>0.20\) |

“Excellent Equity” denotes low observed dispersion under the relevant statistic; it does not imply that the overall resource level is adequate. “Low Equity” denotes greater observed inequality; it does not determine the cause of the disparity.

## 8. Equity Report Output

`generate_equity_report()` returns a table containing:

- `indicator`: Coefficient of Variation, Gini Coefficient, Theil Index, and—when grouping data are supplied—within- and between-group Theil components;
- `value`: calculated statistic rounded for reporting;
- `equity_level`: the applicable provisional descriptive classification; and
- `interpretation`: a bounded statement of what the statistic describes.

The default report evaluates `resource_allocation_score` in one selected year. To decompose Theil inequality, merge a documented group column onto the PRAI result table and pass its name as `group_column`.

## 9. Education-Policy Significance

The engine provides a structured way to distinguish three empirical patterns: broad dispersion in allocation conditions (CV), overall distributional inequality (Gini), and the relative contribution of within- and between-group variation (Theil). Used with component-level PRAI results, it can identify where further descriptive and explanatory analysis is needed.

The results should be read alongside absolute resource levels, population need, data quality, and within-locality disparities. They are not policy recommendations and should not be used to rank localities without the underlying component data and methodological context.
