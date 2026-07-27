# LLM Interpretation Engine

## 1. Purpose

Statistical models calculate indices, inequality measures, efficiency scores, forecasts, and conditional scenario outputs. These outputs are numerically dense and require explanation in relation to a research question, model assumptions, and limits of inference.

The LLM Interpretation Engine assists this interpretive task. It is not a statistical model, causal-inference engine, chatbot, or automatic paper-generation tool. Its role is **AI-assisted Research Interpretation**: creating an evidence-bounded draft that researchers inspect, revise, or reject.

## 2. Role in the Research Workflow

```text
Validated data and statistical models
        ↓
Structured model outputs
        ↓
Reviewed prompt and research context
        ↓
LLM interpretation draft
        ↓
Researcher review and accountable research output
```

Statistical models compute. The LLM interprets only the supplied results. Researchers remain responsible for theory, methods, evidence, inference, and final writing.

## 3. Input Design

`build_interpretation_prompt()` accepts a structured mapping of result blocks. Recommended keys are:

- `resource_allocation`: PRAI scores and component results;
- `equity`: CV, Gini, Theil, and any documented decomposition;
- `efficiency`: DEA scores with selected inputs, outputs, orientation, and returns-to-scale assumption; and
- `policy_simulation`: scenario outputs together with all parameter values.

Pandas results are serialised to JSON records. The prompt states that this JSON is the only empirical evidence available to the model. Researchers should transmit only necessary, authorised data and review the request before using any external provider.

## 4. Output Design

The required response structure contains:

1. **Research Finding** — cautious description of supplied results.
2. **Possible Mechanisms** — hypotheses requiring further evidence.
3. **Policy Implications** — conditional analytical implications, not automatic recommendations or claims of policy effect.
4. **Research Limitations** — data, design, measurement, and model limits.
5. **Future Research** — evidence or designs needed to test mechanisms.

## 5. Prompt Design Principles

- **Evidence boundedness:** do not add unsupplied facts, data, citations, or values.
- **Causal discipline:** distinguish descriptive association, conditional scenarios, and causal inference.
- **Method awareness:** treat PRAI, DEA, equity measures, forecasts, and simulations as model-dependent outputs.
- **Uncertainty preservation:** say when the input does not support an explanation.
- **Human accountability:** require researcher review before any language enters a report or manuscript.

## 6. Implementation Boundary

The engine is provider-agnostic. `ResearchInterpretationAssistant` receives an injected client implementing:

```python
generate(system_prompt: str, user_prompt: str) -> str
```

This prevents hidden network calls and leaves provider choice, credentials, model settings, data governance, and logging under researcher control. `create_interpretation_request()` builds a reviewable request without transmitting it. The included demo is dry-run only and intentionally makes no external LLM call.

## 7. Limitations

LLMs can generate fluent text that exceeds evidence, misunderstands methods, or reproduces prompt assumptions. Prompt constraints reduce but cannot eliminate those risks. The engine cannot independently verify data quality, causal identification, or factual claims.

LLM output is not an empirical result, verified citation, or automatic research conclusion. It must be checked against model outputs and methods by a qualified researcher.
