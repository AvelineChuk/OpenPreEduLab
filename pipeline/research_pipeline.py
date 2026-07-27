"""End-to-end orchestration for the OpenPreEduLab v0.1 research workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import pandas as pd

from llm.interpreter import LLMClient, ResearchInterpretationAssistant, create_interpretation_request
from models.allocation import calculate_prai_score, load_data
from models.efficiency import evaluate_panel_efficiency, prepare_efficiency_data
from models.equity import generate_equity_report
from models.forecast import forecast_fiscal_requirement, forecast_population, forecast_teacher_demand
from models.policy_simulation import simulate_policy_scenarios


DEFAULT_SCENARIO_PARAMETERS: dict[str, float] = {
    "subsidy_increase_rate": 0.10,
    "population_change_rate": -0.08,
    "teacher_cost_increase_rate": 0.08,
    "baseline_teacher_cost_yuan": 80000.0,
    "fiscal_growth_rate": -0.12,
    "fiscal_capacity_multiplier": 1.10,
}


@dataclass
class ResearchResult:
    """Outputs from one complete OpenPreEduLab v0.1 pipeline run."""

    allocation_result: pd.DataFrame
    equity_result: pd.DataFrame
    efficiency_result: pd.DataFrame
    forecast_result: pd.DataFrame
    simulation_result: pd.DataFrame
    llm_interpretation_result: str | None
    output_directory: Path


def _build_equity_results(allocation: pd.DataFrame, raw_data: pd.DataFrame) -> pd.DataFrame:
    """Produce one province-decomposed equity report for each observed year."""
    allocation_with_province = allocation.merge(
        raw_data[["city", "year", "province"]], on=["city", "year"], how="left", validate="one_to_one"
    )
    reports = []
    for year in sorted(allocation_with_province["year"].unique()):
        report = generate_equity_report(allocation_with_province, year=year, group_column="province")
        report.insert(0, "year", year)
        reports.append(report)
    return pd.concat(reports, ignore_index=True)


def _build_forecast_results(raw_data: pd.DataFrame, forecast_years: list[int]) -> pd.DataFrame:
    """Forecast population and translate it into teacher and fiscal requirements."""
    population = forecast_population(raw_data, forecast_years)
    teacher_ratio = float((raw_data["fte_teacher_count"] / raw_data["enrolled_children"]).mean())
    cost_per_child = float(raw_data["government_expenditure_per_child_yuan"].mean())
    teacher = forecast_teacher_demand(population, teacher_ratio)
    fiscal = forecast_fiscal_requirement(population, cost_per_child)
    return population.merge(teacher, on=["city", "year", "future_child_population"], validate="one_to_one").merge(
        fiscal, on=["city", "year", "future_child_population"], validate="one_to_one"
    )


def _write_summary(output_directory: Path, result: ResearchResult, llm_status: str) -> None:
    """Write a provenance-oriented summary without asserting research findings."""
    summary = f"""# OpenPreEduLab v0.1 Research Pipeline Summary

## Run scope

- Allocation observations: {len(result.allocation_result)}
- Equity report rows: {len(result.equity_result)}
- Efficiency observations: {len(result.efficiency_result)}
- Forecast observations: {len(result.forecast_result)}
- Policy-simulation observations: {len(result.simulation_result)}

## Generated outputs

- `allocation_result.csv`
- `equity_result.csv`
- `efficiency_result.csv`
- `forecast_result.csv`
- `simulation_result.csv`

## Interpretation status

{llm_status}

## Research-use note

This summary records a completed computational workflow only. It does not state substantive findings about real localities, establish causal effects, or generate policy recommendations. Interpret each output with its associated model documentation, data definitions, assumptions, and limitations.
"""
    (output_directory / "research_summary.md").write_text(summary, encoding="utf-8")


def run_research_pipeline(
    dataset_path: str | Path,
    output_directory: str | Path | None = None,
    forecast_years: list[int] | None = None,
    scenario_parameters: Mapping[str, float] | None = None,
    llm_client: LLMClient | None = None,
) -> ResearchResult:
    """Run the complete OpenPreEduLab v0.1 research-analysis workflow.

    The workflow loads data, calculates PRAI, evaluates equity and efficiency,
    produces population-linked resource projections, runs four conditional
    policy scenarios, and optionally requests an LLM interpretation. Existing
    model logic is called without modification.

    Parameters
    ----------
    dataset_path:
        CSV file matching the PRAI sample-data schema.
    output_directory:
        Directory for the required result files. Defaults to ``results`` at the
        project root.
    forecast_years:
        Future years for population projections. Defaults to the next two
        calendar years after the observed panel.
    scenario_parameters:
        Optional overrides for the documented prototype scenario assumptions.
    llm_client:
        Optional approved client implementing ``generate(system_prompt,
        user_prompt)``. No external LLM request is made when omitted.

    Returns
    -------
    ResearchResult
        In-memory analysis results and the directory containing written files.
    """
    raw_data = load_data(dataset_path)
    allocation = calculate_prai_score(raw_data)
    equity = _build_equity_results(allocation, raw_data)

    dea_data = prepare_efficiency_data(raw_data)
    efficiency = evaluate_panel_efficiency(
        dea_data,
        input_columns=["total_government_expenditure_yuan", "fte_teacher_count", "usable_indoor_area_sqm"],
        output_columns=["enrolled_children", "age_specific_enrolment_coverage_pct", "qualified_teacher_rate_pct"],
    )

    if forecast_years is None:
        latest_year = int(raw_data["year"].max())
        forecast_years = [latest_year + 1, latest_year + 2]
    forecast = _build_forecast_results(raw_data, forecast_years)

    parameters: dict[str, float] = {**DEFAULT_SCENARIO_PARAMETERS, **(scenario_parameters or {})}
    unknown_parameters = sorted(set(parameters) - set(DEFAULT_SCENARIO_PARAMETERS))
    if unknown_parameters:
        raise ValueError(f"Unknown scenario parameters: {unknown_parameters}")
    simulation = simulate_policy_scenarios(raw_data, **parameters)

    latest_observed_year = int(raw_data["year"].max())
    interpretation_results: dict[str, Any] = {
        "resource_allocation": allocation.loc[allocation["year"] == latest_observed_year],
        "equity": equity.loc[equity["year"] == latest_observed_year],
        "efficiency": efficiency.loc[efficiency["year"] == latest_observed_year],
        "policy_simulation": simulation.loc[simulation["year"] == latest_observed_year],
    }
    llm_interpretation: str | None = None
    if llm_client is not None:
        context = "Pipeline outputs require researcher review; interpret only supplied model results and assumptions."
        llm_interpretation = ResearchInterpretationAssistant(llm_client).interpret(
            interpretation_results, context
        )
        llm_status = "An LLM interpretation was requested through a researcher-supplied client. Review it against the underlying results before use."
    else:
        # Build the request so that prompt construction remains part of the
        # pipeline audit trail, while avoiding an implicit external call.
        create_interpretation_request(
            interpretation_results,
            "No LLM client was configured; this request was created but not sent.",
        )
        llm_status = "No LLM interpretation was generated because no external client was configured."

    target_directory = Path(output_directory) if output_directory else Path(__file__).resolve().parents[1] / "results"
    target_directory.mkdir(parents=True, exist_ok=True)
    result = ResearchResult(
        allocation_result=allocation,
        equity_result=equity,
        efficiency_result=efficiency,
        forecast_result=forecast,
        simulation_result=simulation,
        llm_interpretation_result=llm_interpretation,
        output_directory=target_directory,
    )
    allocation.to_csv(target_directory / "allocation_result.csv", index=False, encoding="utf-8")
    equity.to_csv(target_directory / "equity_result.csv", index=False, encoding="utf-8")
    efficiency.to_csv(target_directory / "efficiency_result.csv", index=False, encoding="utf-8")
    forecast.to_csv(target_directory / "forecast_result.csv", index=False, encoding="utf-8")
    simulation.to_csv(target_directory / "simulation_result.csv", index=False, encoding="utf-8")
    _write_summary(target_directory, result, llm_status)
    return result
