"""Dry-run demonstration of the LLM Interpretation Engine.

It builds model results and a reviewable prompt from synthetic data, but makes
no external LLM call and generates no interpretation by default.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llm.interpreter import ResearchInterpretationAssistant, create_interpretation_request
from models.allocation import calculate_prai_score, load_data
from models.equity import generate_equity_report
from models.efficiency import evaluate_panel_efficiency, prepare_efficiency_data
from models.policy_simulation import simulate_policy_scenarios


class PreviewOnlyClient:
    """Safe demo client that prevents accidental external LLM requests."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Stop before generation; replace only with an approved provider client."""
        raise RuntimeError(
            "No external LLM call was made. Supply an approved client implementing "
            "generate(system_prompt, user_prompt) to generate an interpretation."
        )


def main() -> None:
    """Demonstrate Model Results -> LLM Prompt -> Research Interpretation setup."""
    data = load_data(PROJECT_ROOT / "datasets" / "sample_preschool_data.csv")
    prai = calculate_prai_score(data)
    equity = generate_equity_report(prai, year=2025)
    dea_data = prepare_efficiency_data(data)
    efficiency = evaluate_panel_efficiency(
        dea_data,
        ["total_government_expenditure_yuan", "fte_teacher_count", "usable_indoor_area_sqm"],
        ["enrolled_children", "age_specific_enrolment_coverage_pct", "qualified_teacher_rate_pct"],
    )
    scenarios = simulate_policy_scenarios(data, 0.10, -0.08, 0.08, 80000, -0.12)
    model_results = {
        "resource_allocation": prai.loc[prai["year"] == 2025],
        "equity": equity,
        "efficiency": efficiency.loc[efficiency["year"] == 2025],
        "policy_simulation": scenarios.loc[scenarios["year"] == 2025],
    }
    request = create_interpretation_request(
        model_results,
        "Synthetic demonstration data only; do not treat any output as evidence about real cities or policies.",
    )
    print("Model Results -> LLM Prompt -> Research Interpretation")
    print("\nPrompt preview:\n")
    print(request.user_prompt)
    print("\nNo LLM interpretation has been generated in this dry-run demo.")
    _ = ResearchInterpretationAssistant(PreviewOnlyClient())


if __name__ == "__main__":
    main()
