# Preschool Education Forecast Model

## 1. Research Objective

The Preschool Education Forecast Engine provides a transparent prototype for projecting future preschool-age child population and translating those projections into conditional teacher and fiscal resource requirements.

Its central question is:

> Given observed historical education and demographic data, what future child population and associated preschool resource requirements would be projected under explicitly stated trend and planning assumptions?

Forecasting is relevant to preschool education research because population change, enrolment demand, staffing needs, and fiscal commitments evolve over time. A static allocation assessment can describe present conditions, but it cannot by itself examine whether those conditions may remain adequate as the target-age population changes.

The engine is a forecasting tool, not a policy-simulation engine. It extrapolates data trends and applies transparent planning assumptions; it does not estimate the causal effect of a policy change.

## 2. Forecast Framework

```text
Historical city-year data
        ↓
Trend assessment and data-quality review
        ↓
Transparent forecast model
        ↓
Future child-population projection
        ↓
Teacher-demand and fiscal-need projections under stated assumptions
```

The sequence separates the demographic forecast from the resource translation. Population is forecast from historical values. Teacher and fiscal requirements are then conditional arithmetic projections, not independently estimated time-series forecasts.

## 3. Model Selection

| Method | Strengths | Limitations for the MVP |
| --- | --- | --- |
| Linear regression | Transparent parameters, works with short annual series, readily fitted separately by city, and supports straightforward inspection of trend direction | Assumes a linear trend and cannot represent turning points, cohort dynamics, shocks, or seasonal structure |
| ARIMA | Can represent serial correlation and temporal dynamics in sufficiently long, stable time series | Requires substantially more observations for identification and diagnostics; five annual observations are inadequate for a credible MVP ARIMA application |
| Exponential smoothing | Useful for level and trend forecasting and can adapt to recent observations | Requires time-series diagnostics and sufficient observations; its smoothing parameters may be unstable with a very short annual series |

### MVP decision

The MVP uses separate city-level **linear regression** models:

$$
P_{it} = \alpha_i + \beta_i t + \varepsilon_{it}
$$

where \(P_{it}\) is the preschool-age child population in city \(i\) in year \(t\). The projected population is:

$$
\widehat{P}_{i,t+h} = \widehat{\alpha}_i + \widehat{\beta}_i(t+h)
$$

This decision prioritises transparency and reproducibility over apparent sophistication. The sample dataset contains only five annual observations per city, so ARIMA and exponential-smoothing models would create an unjustified impression of precision. Negative extrapolations are truncated at zero because population cannot be negative.

Linear trend extrapolation is a baseline, not a demographic projection model. It should be replaced or supplemented by cohort-component methods, fertility and migration information, or longer validated time series when such data become available.

## 4. Variable Design

### 4.1 Population forecast

| Role | Variable | Meaning | Unit |
| --- | --- | --- | --- |
| Input | `year` | Observation year | year |
| Input | `resident_preschool_age_population` | Resident children in the defined target preschool-age group | children |
| Output | `future_child_population` | Projected resident target-age population | children |

The preschool-age definition must remain consistent across historical and future periods. Boundary changes, census revisions, and migration-related definition changes should be recorded before fitting a trend.

### 4.2 Teacher-demand projection

| Role | Variable | Meaning | Unit |
| --- | --- | --- | --- |
| Input | `future_child_population` | Projected preschool-age child population | children |
| Assumption | `teacher_child_ratio` | Planned FTE teachers per child | FTE teachers per child |
| Output | `future_teacher_demand` | Projected FTE teacher requirement | FTE teachers |

$$
\widehat{T}_{it} = \widehat{P}_{it} \times r_T
$$

where \(r_T\) is a documented planning assumption. For example, \(r_T=0.065\) represents 6.5 FTE teachers per 100 children. This assumption should reflect a specified staffing standard, not an undocumented historical average.

### 4.3 Fiscal-resource projection

| Role | Variable | Meaning | Unit |
| --- | --- | --- | --- |
| Input | `future_child_population` | Projected preschool-age child population | children |
| Assumption | `cost_per_child` | Annual fiscal cost under a stated scope and price year | currency per child per year |
| Output | `future_fiscal_need` | Projected annual fiscal requirement | currency per year |

$$
\widehat{F}_{it} = \widehat{P}_{it} \times c_t
$$

where \(c_t\) is the stated cost-per-child assumption. It must specify whether it represents public expenditure, operating cost, or another fiscal category, and must use a documented price year for comparisons over time.

## 5. Implementation and Outputs

The module provides:

- `forecast_population()`, which produces city-year `future_child_population` projections for user-specified future years;
- `forecast_teacher_demand()`, which translates those projections into `future_teacher_demand` under a scalar or city-specific `teacher_child_ratio`; and
- `forecast_fiscal_requirement()`, which translates those projections into `future_fiscal_need` under a scalar or city-specific `cost_per_child`.

The forecast-plot utility displays historical population and model projections with different line styles. The plot does not calculate the forecast and does not attach causal interpretations to an observed trend.

## 6. Educational Policy Significance and Limits

Forecasts can help researchers describe the temporal resource implications of demographic change and make the assumptions linking population to staffing or fiscal need explicit. They are particularly relevant where enrolment demand may fall, grow, or shift geographically.

Their interpretation is conditional. A projection may be inaccurate because fertility, migration, economic conditions, institutional access, data definitions, or policy context change. A short historical series cannot support confident long-horizon claims. Researchers should report the forecast horizon, model specification, input data, planning assumptions, uncertainty assessment, and any alternative scenarios used for sensitivity analysis.

This MVP does not perform policy simulation, causal forecasting, uncertainty-interval estimation, or automatic policy recommendations.
