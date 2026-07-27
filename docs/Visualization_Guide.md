# PRAI Visualization Guide

## Purpose

The Visualization Engine converts calculated Preschool Resource Allocation Index (PRAI) results into transparent visual summaries for education-policy research. Its figures are descriptive tools. They display the information present in the supplied data and do not establish causality, evaluate policy effectiveness, or produce recommendations on their own.

All charts should be produced from documented PRAI inputs, normalisation rules, and weighting decisions. Captions and methods sections should identify the study population, time period, scoring specification, and data limitations.

## 1. Resource Allocation Ranking Chart

### Research question

How do localities compare in their composite preschool resource-allocation conditions in a specified year?

### Input and output

The ranking chart receives a PRAI results table with `city`, `year`, and `resource_allocation_score`. It produces a horizontal bar chart for one selected year. The plotting function requires a year when the results table contains multiple years, preventing accidental comparison of scores from different periods in a single ranking.

### Interpretation

Longer bars represent higher composite PRAI scores relative to the selected normalisation and weighting specification. A ranking is not an explanation of why cities differ. The four dimension scores and the underlying indicators must be examined before drawing substantive inferences.

### Use in a paper

Use the chart in a descriptive-results section to introduce cross-locality variation in one period. State clearly whether scores use policy benchmarks or sample-based normalisation. Do not describe a rank difference as evidence of a policy effect without an appropriate research design.

## 2. Trend Analysis Chart

### Research question

How have calculated resource-allocation conditions changed over time within and across selected localities?

### Input and output

The trend chart uses city, year, and PRAI score fields and draws one line per city. Users may select a subset of cities to avoid an unreadable figure when the dataset contains many localities.

### Interpretation

An upward or downward trajectory describes change in the calculated index. Interpretation requires checking whether the change arose from financial, staffing, facility, or demand-responsiveness components, and whether standardisation permits intertemporal comparison. With sample-based min–max normalisation, scores are comparable only within the jointly normalised sample.

### Use in a paper

Use the chart to describe temporal patterns and to identify periods that merit further investigation. When discussing a policy introduced at a particular time, mark the policy timing in the figure or caption only after verifying its date and scope. Do not infer that a coincident change was caused by the policy.

## 3. Dimension Analysis Radar Chart

### Research question

How do the structures of resource allocation differ across selected localities?

### Input and output

The radar chart receives city-year dimension scores on a 0–100 scale for Financial Resources, Human Resources, Material Resources, and Demand Responsiveness. The helper `calculate_dimension_scores()` aggregates the normalised PRAI indicators using the documented equal-within-dimension MVP rule.

The fourth axis is labelled **Demand Responsiveness**, consistent with the PRAI theoretical framework. Capacity pressure is one indicator within that dimension; it should not be interpreted as the entire demand dimension.

### Interpretation

The shape of a city profile indicates its relative pattern across dimensions. A narrow profile in one dimension may suggest an area for diagnostic analysis, but the figure does not identify a cause or determine a policy response. Radar charts are most readable with a small number of cities; use a ranking chart or component table for broader comparisons.

### Use in a paper

Use this figure to complement the composite-score results by showing why similarly ranked localities may have different resource configurations. Report the dimension-construction rule in the methods section and avoid comparing polygon area as a precise quantity.

## 4. City-by-Year Heatmap

### Research question

Which localities show persistent, improving, or deteriorating PRAI score patterns over the observed period?

### Input and output

The heatmap pivots PRAI results into cities as rows and years as columns. Colour intensity and printed values show the score at each city-year observation. The implementation uses matplotlib only and fixes the displayed colour scale to 0–100.

### Interpretation

Repeated lower scores can identify observations that merit more detailed examination; they do not by themselves prove chronic underinvestment or policy failure. Missing observations should be shown and discussed rather than silently treated as low scores. A heatmap is especially useful for detecting patterns that may be obscured in multiple overlapping line charts.

### Use in a paper

Use it as a descriptive overview of panel data or as an appendix figure supporting the presentation of trends. Include the study years, the number of localities, and the meaning of the score scale in the caption.

## Reproducible Reporting Practice

For every figure, retain and report:

- the source dataset and its version;
- the geographic units and time period;
- the PRAI indicator definitions, standardisation procedure, and weights;
- any city or year subset selected for display;
- the plotting function and its key parameters; and
- limitations of data coverage and interpretation.

Figures should be saved through the functions' explicit `output_path` argument at 300 dpi. This avoids hidden output locations and makes the analysis workflow suitable for replication and manuscript preparation.
