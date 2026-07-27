# Software Validation Report

## Validation Objective

This validation framework assesses whether the implemented OpenPreEduLab v0.1 software modules operate according to their documented interfaces and handling rules. It evaluates data loading, calculation flow, output structure, boundary handling, missing-value handling, and invalid-input rejection.

This is **software validation**, not policy validation. Passing tests does not validate the PRAI construct, confirm the suitability of a DEA specification, establish forecast accuracy, verify policy effects, or support substantive conclusions about preschool education.

## Validation Method

The test suite is organised with `pytest` in `tests/` and uses `datasets/sample_preschool_data.csv` as its source dataset. The sample data are synthetic and are used only to exercise the software workflow.

Each implemented model module has four test categories:

| Module | Normal case | Boundary case | Missing-value case | Invalid-input case |
| --- | --- | --- | --- | --- |
| Resource Allocation | Computes bounded PRAI scores for all city-years | Constant indicator and score-classification thresholds | Missing required CSV field | Duplicate city-year record |
| Equity Evaluation | Produces a complete yearly report | Equal distribution has zero inequality | Missing value in score vector | Negative resource value |
| Efficiency Evaluation | Produces DEA scores for the panel | Two-DMU cross-section | Missing preparation field | Same variable selected as input and output |
| Forecast | Produces population, teacher, and fiscal projections | One-year horizon | Missing population field | Forecast year is not future |
| Policy Simulation | Produces baseline plus four scenarios | Zero population change | Missing baseline field | Population decline at or below 100 percent |

Run the suite from the project root with:

```bash
python -m pytest tests
```

## Expected Results

The expected result is that all tests pass when the code is run with the documented synthetic dataset and required dependencies. In particular, the suite checks that:

- PRAI scores remain within the documented 0–100 interval;
- DEA efficiency scores remain within the implemented 0–1 interval;
- forecast and simulation outputs have the expected records and fields;
- documented boundary behaviour is reproducible; and
- missing or invalid inputs raise explicit errors rather than silently producing results.

## Current Limitations

- The tests use synthetic data and do not assess real-world data quality or external validity.
- Unit tests do not establish the theoretical validity of selected indicators, weights, DEA variables, or scenario transition rules.
- The suite does not yet include performance, cross-platform, security, uncertainty, or regression testing against versioned empirical benchmarks.
- The LLM Interpretation Engine is intentionally excluded from external-call testing because it is provider-agnostic and does not make network requests by default.

## Future Validation Plan

Future validation should include:

1. construct and content validation of PRAI with education-policy and statistical-methods experts;
2. sensitivity analysis for indicators, benchmarks, weights, and DEA specifications;
3. testing against authorised real-world preschool education datasets with documented provenance;
4. forecast back-testing and uncertainty assessment using longer time series;
5. scenario calibration and review of policy-simulation transition mechanisms; and
6. continuous integration, dependency pinning, code coverage, and cross-platform regression checks.

Software tests are necessary for reproducible research infrastructure, but they are only one part of a broader programme of methodological and empirical validation.
