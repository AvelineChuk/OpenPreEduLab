# PRAI Sample Data Dictionary

## 1. Purpose and Dataset Status

This document specifies the data design for `datasets/sample_preschool_data.csv`, a synthetic panel dataset for testing the proposed Preschool Resource Allocation Index (PRAI).

The file is **not an official statistical dataset** and must not be used to make factual claims about the named cities, provinces, or public policy. City and province names are used only to make the test data interpretable. All values are illustrative and were constructed to represent plausible contrasts in preschool education resource conditions in China.

The unit of observation is **city × year**. The sample contains ten cities observed annually from 2021 to 2025, for a total of 50 observations.

## 2. Data Requirement Analysis

PRAI is calculated from ratios and rates. The table below identifies the raw data required for each proposed PRAI indicator. Variables marked “derived” are calculated from fields in the sample dataset rather than entered independently.

| Dimension | PRAI indicator | Required variable(s) | Data meaning | Unit |
| --- | --- | --- | --- | --- |
| Financial Resources | Public preschool expenditure per enrolled child | `government_expenditure_per_child_yuan` | Public preschool expenditure intensity after adjustment for enrolled children | yuan per enrolled child per year |
| Financial Resources | Stable public funding share | `stable_public_funding_share_pct` | Share of preschool expenditure from regular public-budget sources | percent |
| Human Resources | Qualified teacher rate | `qualified_teacher_rate_pct` | Teachers meeting the applicable qualification standard | percent of teachers |
| Human Resources | Teacher availability | `fte_teacher_count`, `enrolled_children` | Full-time-equivalent teacher supply relative to enrolment; derived as teachers per 100 children | FTE teachers per 100 enrolled children |
| Human Resources | Teacher workload | `fte_teacher_count`, `enrolled_children` | Enrolment relative to full-time-equivalent teacher supply; derived as children per FTE teacher | children per FTE teacher |
| Material Resources | Place availability | `licensed_preschool_places`, `resident_preschool_age_population` | Licensed capacity relative to resident children in the target age group; derived as places per 100 children | licensed places per 100 resident children |
| Material Resources | Space adequacy | `usable_indoor_area_sqm`, `enrolled_children` | Usable indoor educational space relative to enrolled children; derived as area per child | square metres per enrolled child |
| Material Resources | Average class size | `enrolled_children`, `class_count` | Average number of enrolled children per class | children per class |
| Educational Demand Responsiveness | Age-specific enrolment coverage | `resident_target_age_children_enrolled`, `resident_preschool_age_population` | Resident eligible children enrolled relative to the resident target-age population | percent |
| Educational Demand Responsiveness | Unmet-demand rate | `eligible_children_seeking_but_not_enrolled`, `eligible_children_seeking_place` | Eligible children seeking but not obtaining a place relative to those seeking a place | percent |
| Educational Demand Responsiveness | Capacity pressure | `enrolled_children`, `licensed_preschool_places` | Enrolment relative to licensed places | percent occupancy |

### 2.1 Derived variables for PRAI calculation

For locality \(i\) and year \(t\), define:

- \(E_{it}\): enrolled children;
- \(T_{it}^{\mathrm{FTE}}\): full-time-equivalent teachers;
- \(K_{it}\): licensed preschool places;
- \(P_{it}\): resident preschool-age population;
- \(A_{it}\): usable indoor educational area;
- \(C_{it}\): number of classes;
- \(Q_{it}\): resident target-age children enrolled;
- \(S_{it}\): eligible children seeking a preschool place; and
- \(U_{it}\): eligible children seeking a place but not enrolled.

The model-ready indicators are derived as follows.

**FTE teachers per 100 enrolled children**

$$
R_{it}^{\mathrm{teacher}}
= 100\frac{T_{it}^{\mathrm{FTE}}}{E_{it}}
$$

**Enrolled children per FTE teacher**

$$
W_{it}^{\mathrm{teacher}}
= \frac{E_{it}}{T_{it}^{\mathrm{FTE}}}
$$

**Licensed places per 100 resident preschool-age children**

$$
R_{it}^{\mathrm{places}}
= 100\frac{K_{it}}{P_{it}}
$$

**Usable indoor area per enrolled child**

$$
R_{it}^{\mathrm{area}}
= \frac{A_{it}}{E_{it}}
$$

**Average class size**

$$
\overline{C}_{it}^{\mathrm{size}}
= \frac{E_{it}}{C_{it}}
$$

**Age-specific enrolment coverage**

$$
R_{it}^{\mathrm{coverage}}
= 100\frac{Q_{it}}{P_{it}}
$$

**Unmet-demand rate**

$$
R_{it}^{\mathrm{unmet}}
= 100\frac{U_{it}}{S_{it}}
$$

**Capacity pressure**

$$
R_{it}^{\mathrm{capacity}}
= 100\frac{E_{it}}{K_{it}}
$$

## 3. CSV Schema

| Variable name | Description | Unit | Data type | Role |
| --- | --- | --- | --- | --- |
| `city` | Name of the city-level study unit | text | string | Identifier |
| `province` | Province-level location of the city | text | string | Identifier/context |
| `year` | Calendar year of observation | year | integer | Time identifier |
| `government_expenditure_per_child_yuan` | Annual public preschool expenditure per enrolled child | yuan per child per year | integer | Financial Resources input |
| `stable_public_funding_share_pct` | Expenditure share from stable public-budget sources | percent | numeric | Financial Resources input |
| `qualified_teacher_rate_pct` | Proportion of teachers satisfying the defined qualification criterion | percent | numeric | Human Resources input |
| `fte_teacher_count` | Number of full-time-equivalent preschool teachers | FTE teachers | integer | Human Resources input |
| `enrolled_children` | Number of children enrolled in preschool institutions in the locality | children | integer | Denominator/input |
| `licensed_preschool_places` | Number of licensed preschool places | places | integer | Material Resources input |
| `usable_indoor_area_sqm` | Usable indoor educational area across included institutions | square metres | integer | Material Resources input |
| `class_count` | Number of preschool classes in included institutions | classes | integer | Material Resources input |
| `resident_preschool_age_population` | Resident children in the stated target preschool-age group | children | integer | Demand exposure/denominator |
| `resident_target_age_children_enrolled` | Resident target-age children who are enrolled in preschool | children | integer | Demand Responsiveness input |
| `eligible_children_seeking_place` | Eligible children with recorded or credibly estimated demand for a preschool place | children | integer | Demand Responsiveness denominator |
| `eligible_children_seeking_but_not_enrolled` | Eligible children seeking a place but not enrolled | children | integer | Demand Responsiveness numerator |

## 4. Panel Data Design

### 4.1 Structure

The sample uses a balanced panel of **10 cities × 5 years (2021–2025)**:

- Beijing, Beijing
- Shanghai, Shanghai
- Guangzhou, Guangdong
- Shenzhen, Guangdong
- Hangzhou, Zhejiang
- Nanjing, Jiangsu
- Wuhan, Hubei
- Chengdu, Sichuan
- Zhengzhou, Henan
- Lanzhou, Gansu

Each `city`–`year` pair must be unique. In a production dataset, `city`, `province`, and `year` should be supplemented by a stable administrative-code field to avoid ambiguity caused by name changes or boundary adjustments.

### 4.2 Why a panel design is required

A city × year panel enables PRAI to support both cross-sectional and longitudinal research.

- **Cross-sectional comparison** identifies differences in allocation conditions across localities at a common point in time.
- **Trend analysis** shows whether financial, workforce, material, and demand-responsive conditions improve or deteriorate over time.
- **Demographic responsiveness** can be examined by comparing changes in resident child population with changes in places, staffing, and expenditure.
- **Policy analysis** can align later policy changes or fiscal interventions with pre-existing resource trajectories, while avoiding the mistaken assumption that temporal association alone establishes causality.
- **Validation and robustness checks** require repeated observations to assess whether index patterns are stable or driven by one exceptional year.

## 5. Sample Data Generation Logic

The sample is purposefully structured rather than randomly generated. It encodes four plausible patterns that a PRAI test dataset should contain.

### 5.1 Regional fiscal and professional-resource differences

The eastern cities in the sample (Beijing, Shanghai, Guangzhou, Shenzhen, Hangzhou, and Nanjing) are assigned comparatively higher public expenditure per child, stable funding shares, and teacher-qualification rates. This creates realistic variation for testing Financial and Human Resources indicators without claiming that the values represent official statistics.

Wuhan and Chengdu occupy intermediate positions. Zhengzhou and Lanzhou have lower expenditure intensity, lower stable public funding shares, and lower qualification rates in the sample. The gradient is deliberately imperfect: no single dimension is made identical across all cities, so the composite index must aggregate genuinely multi-dimensional information.

### 5.2 Demographic change and demand

The sample assigns declining target-age populations to Beijing, Shanghai, Nanjing, Wuhan, Zhengzhou, and Lanzhou. Guangzhou, Shenzhen, Hangzhou, and Chengdu experience simulated growth in the target-age population. Enrolment, capacity, and workforce counts change with these trends, but not at identical rates.

This design makes it possible to test whether PRAI distinguishes a locality with high absolute resources from one whose provision is well aligned with changing demand. Population counts are denominators and exposure variables; they do not receive a favourable or unfavourable score by themselves.

### 5.3 Capacity and access pressure

Licensed places are generally above enrolled children, but the gap differs across cities. The sample includes higher unmet-demand rates in Zhengzhou and Lanzhou, lower rates in several eastern cities, and changing occupancy as enrolment and capacity evolve. These differences permit testing of coverage, unmet demand, and capacity-pressure measures.

### 5.4 Workforce and facility conditions

FTE teacher counts, class counts, and indoor area are set in relation to enrolment rather than independently. This permits meaningful calculation of teacher availability, workload, average class size, and indoor area per child. Cities are intentionally assigned different staffing and facility profiles so that a high financial score need not imply a uniformly high PRAI score.

## 6. Data Quality and Governance Requirements for Future Real Data

Before replacing the sample with real data, each field should be accompanied by a source, collection date, geographic definition, preschool-age definition, inclusion criteria for institution types, and any transformation applied. Financial data require price-year documentation; workforce data require a qualification definition and FTE conversion rule; and all demand variables require a defensible method for identifying the resident eligible population and unmet demand.

The dataset should not contain personally identifiable information. Aggregate city-year data are preferred for the PRAI MVP. Any more granular records must comply with applicable legal, ethical, and institutional data-governance requirements.

## 7. Relationship to the PRAI Model

This dataset supplies the raw variables specified in [Resource_Allocation_Index.md](Resource_Allocation_Index.md). It does not contain PRAI scores, normalised values, chosen benchmarks, or weights. Those are analytical outputs that should be generated only after the study defines its comparison sample, benchmark rationale, missing-data treatment, and weighting decision.
