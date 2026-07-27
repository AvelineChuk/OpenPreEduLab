"""Provider-agnostic orchestration for evidence-bounded LLM interpretation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from llm.prompts import SYSTEM_PROMPT, build_interpretation_prompt


class LLMClient(Protocol):
    """Minimal interface required by the Research Interpretation Assistant."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return a text response for the supplied prompts."""


@dataclass(frozen=True)
class InterpretationRequest:
    """A reviewable request before any external LLM call is made."""

    system_prompt: str
    user_prompt: str
    model_results: Mapping[str, Any]
    research_context: str | None = None


def create_interpretation_request(model_results: Mapping[str, Any], research_context: str | None = None) -> InterpretationRequest:
    """Create, but do not send, a bounded research-interpretation request."""
    return InterpretationRequest(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=build_interpretation_prompt(model_results, research_context),
        model_results=model_results,
        research_context=research_context,
    )


class ResearchInterpretationAssistant:
    """Generate interpretations through a researcher-configured LLM client."""

    def __init__(self, client: LLMClient) -> None:
        """Initialise the assistant with an injected client; no hidden calls occur."""
        self._client = client

    def interpret(self, model_results: Mapping[str, Any], research_context: str | None = None) -> str:
        """Send structured results to the configured client and return its text.

        This method does not calculate, validate, or alter statistical results.
        Researchers must review the returned language against the evidence.
        """
        request = create_interpretation_request(model_results, research_context)
        response = self._client.generate(request.system_prompt, request.user_prompt)
        if not isinstance(response, str) or not response.strip():
            raise ValueError("The LLM client returned an empty or non-text interpretation.")
        return response.strip()
