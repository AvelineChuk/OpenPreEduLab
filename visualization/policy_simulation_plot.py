"""Scenario-comparison plots for the policy simulation research prototype."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_scenario_comparison(comparison: pd.DataFrame, city: str, year: int, output_path: str | Path | None = None) -> tuple[plt.Axes, plt.Axes]:
    """Plot fiscal requirement and PRAI score for baseline and four scenarios.

    The input should be the jointly normalised output of
    ``simulate_policy_scenarios``. The figure reports conditional model
    outputs and must not be interpreted as a factual policy forecast.
    """
    required = {"city", "year", "scenario", "fiscal_requirement_yuan", "resource_allocation_score"}
    missing = sorted(required - set(comparison.columns))
    if missing:
        raise ValueError(f"Scenario comparison is missing required columns: {missing}")
    plot_data = comparison.loc[(comparison["city"] == city) & (comparison["year"] == year)].copy()
    if plot_data.empty:
        raise ValueError(f"No scenario results are available for {city}, {year}.")
    order = ["Baseline", "Increase Subsidy", "Declining Population", "Teacher Cost Increase", "Fiscal Constraint"]
    plot_data["scenario"] = pd.Categorical(plot_data["scenario"], categories=order, ordered=True)
    plot_data = plot_data.sort_values("scenario")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    axes[0].bar(plot_data["scenario"], plot_data["fiscal_requirement_yuan"], color="#3B6EA5")
    axes[0].set_title("Fiscal Requirement by Scenario")
    axes[0].set_ylabel("Fiscal requirement (yuan)")
    axes[1].bar(plot_data["scenario"], plot_data["resource_allocation_score"], color="#4C956C")
    axes[1].set_title("Resource Allocation Score by Scenario")
    axes[1].set_ylabel("PRAI score (0–100)")
    axes[1].set_ylim(0, 100)
    for axis in axes:
        axis.tick_params(axis="x", labelrotation=35)
        axis.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.5)
        axis.set_axisbelow(True)
    fig.suptitle(f"Scenario Comparison: {city}, {year}")
    fig.tight_layout()
    if output_path is not None:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")
    return axes[0], axes[1]
