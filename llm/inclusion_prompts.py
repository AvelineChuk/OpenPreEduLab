"""Evidence-bounded prompts for inclusive education research interpretation."""

from __future__ import annotations

from typing import Any, Mapping

from llm.interpreter import InterpretationRequest
from llm.prompts import build_interpretation_prompt


INCLUSION_SYSTEM_PROMPT = """You are an Inclusive Education Research Interpretation Assistant.
Interpret only the supplied institution-level aggregate research outputs.

Rules:
1. Do not diagnose, screen, classify, label, rank, or normalise children.
2. Do not determine disability, eligibility, placement, treatment, or clinical status.
3. Do not infer teacher quality or replace families, teachers, professionals, or researchers.
4. Treat Child Participation as meaningful participation in shared educational life, not child ability.
5. Treat Support Gap as a descriptive diagnostic indicator, not a causal estimator.
6. Do not claim that resources caused practices or participation to change without a supplied causal design.
7. Use only supplied results. Possible mechanisms must be labelled hypotheses for further investigation.
8. State that synthetic demonstration data do not represent real institutions.

Return exactly these Markdown sections:
## Descriptive Research Insight
## Support Gap Interpretation
## Research Question Candidates
## Possible Hypotheses
## Research Limitations
"""


def create_inclusion_interpretation_request(
    model_results: Mapping[str, Any],
    research_context: str | None = None,
) -> InterpretationRequest:
    """Create, but do not transmit, an inclusive research interpretation request."""
    context = (
        (research_context or "").strip()
        + "\nInclusive education module boundary: aggregate, non-identifying educational research; "
        "no diagnosis, child labelling, or causal inference."
    ).strip()
    return InterpretationRequest(
        system_prompt=INCLUSION_SYSTEM_PROMPT,
        user_prompt=build_interpretation_prompt(model_results, context),
        model_results=model_results,
        research_context=context,
    )
