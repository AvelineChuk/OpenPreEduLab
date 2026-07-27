"""Prompt construction for evidence-bounded research interpretation."""

from __future__ import annotations

import json
from typing import Any, Mapping

import numpy as np
import pandas as pd

SYSTEM_PROMPT = """You are an Educational Policy Research Assistant.
Your role is to interpret structured statistical outputs. You are not a
chatbot, statistical calculator, causal-inference engine, or paper author.
The researcher remains responsible for design, validity, inference, and final writing.

Rules:
1. Use only supplied results and context; do not invent data, sources, effects, or facts.
2. Distinguish descriptive association from causation. Do not use causal language
   without an explicitly supplied causal design and identifying assumptions.
3. Treat scores as model-dependent and state relevant limits.
4. Describe mechanisms only as hypotheses requiring further evidence.
5. Give conditional analytical implications, not recommendations or policy-effect claims.
6. Use concise academic language and preserve uncertainty.

Return exactly these Markdown sections:
## Research Finding
## Possible Mechanisms
## Policy Implications
## Research Limitations
## Future Research
"""


def _json_safe(value: Any) -> Any:
    """Convert common research-result objects into JSON-serialisable values."""
    if isinstance(value, pd.DataFrame):
        return value.replace({np.nan: None}).to_dict(orient="records")
    if isinstance(value, pd.Series):
        return value.replace({np.nan: None}).to_dict()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def build_interpretation_prompt(model_results: Mapping[str, Any], research_context: str | None = None) -> str:
    """Build a structured user prompt from supplied model results only."""
    if not model_results:
        raise ValueError("model_results must contain at least one result block.")
    evidence = json.dumps(_json_safe(model_results), ensure_ascii=False, indent=2)
    context = research_context.strip() if research_context else "No additional research context was supplied."
    return f"""Research context:
{context}

Structured model results (the only empirical evidence available for this interpretation):
```json
{evidence}
```

Interpret the supplied results cautiously. If the data are insufficient to explain a pattern, say so explicitly. Do not calculate new statistics, infer causal effects, or introduce factual claims not present in the evidence."""
