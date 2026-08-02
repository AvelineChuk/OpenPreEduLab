# DeepSeek Integration

## Purpose

The optional DeepSeek connection supports the LLM Interpretation stage of the OpenPreEduLab research prototype. Statistical models calculate results; the language model provides a clearly labelled, evidence-bounded interpretation draft. It does not validate data, calculate statistics, establish causality, or replace researcher judgement.

## Access model

OpenPreEduLab uses a **bring-your-own-key** design. A visitor enters an API key from an account they control, selects a supported DeepSeek model, reviews the data-transmission notice, and explicitly submits the request.

The platform does not contain a shared API key and does not promise a free quota. Whether a request is free, trial-funded, or billable is determined only by the visitor's DeepSeek account and current provider terms.

## Data boundary

When the visitor selects **Generate interpretation with DeepSeek**, the following are transmitted to DeepSeek:

- the bounded system prompt;
- the visitor's optional research context; and
- the current model-result blocks used to build the reviewed prompt.

The API key is used only in the request header. It is not committed to GitHub, written to a report or dataset, or intentionally retained by the application after form submission. Researchers should not submit restricted, personally identifiable, or unreviewed evidence to an external provider.

## Research safeguards

- The prompt requires use of supplied results only.
- It distinguishes descriptive association from causal inference.
- It asks for limitations and future research as required output sections.
- The generated text is labelled as a draft requiring researcher review.
- A downloadable record preserves the prompts, provider, selected model, and returned draft; it deliberately excludes the API key.

## Operational limitations

This is an API integration, not an offline model. It needs a valid DeepSeek account, available quota or billing access, network connectivity, and a provider-supported model. Provider availability, pricing, model behaviour, and data-processing terms can change independently of OpenPreEduLab.

