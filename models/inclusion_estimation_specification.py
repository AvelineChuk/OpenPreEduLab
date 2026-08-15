"""Estimation-specification readiness audits for inclusive policy research.

The workflow records a proposed analysis specification before results are
interpreted. It does not fit a model, estimate an effect, or authorise causal
language.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


SPECIFICATION_COLUMNS: Final[tuple[str, ...]] = (
    "specification_id",
    "design_id",
    "falsification_plan_id",
    "instrument_version",
    "outcome_definition",
    "estimand_definition",
    "analysis_population",
    "unit_of_analysis",
    "time_scale",
    "estimator_family",
    "functional_form",
    "treatment_encoding",
    "comparison_contrast",
    "covariate_adjustment",
    "fixed_effects_structure",
    "dependence_adjustment",
    "standard_error_method",
    "clustering_level",
    "weighting_strategy",
    "missing_data_method",
    "event_time_window",
    "reference_period",
    "multiple_testing_implementation",
    "uncertainty_reporting",
    "software_environment",
    "output_disclosure_boundary",
    "specification_status",
    "researcher_notes",
)

ESTIMATOR_FAMILIES: Final[tuple[str, ...]] = (
    "descriptive_only",
    "linear_model_candidate",
    "generalized_linear_model_candidate",
    "panel_model_candidate",
    "event_study_candidate",
    "interrupted_time_series_candidate",
    "matching_or_weighting_candidate",
    "randomization_inference_candidate",
    "other_prespecified_candidate",
)

SPECIFICATION_STATUSES: Final[tuple[str, ...]] = (
    "not_started",
    "draft",
    "review_pending",
    "preregistered",
)


def create_estimation_specification_template() -> pd.DataFrame:
    """Return a blank non-identifying estimation-specification schema."""
    return pd.DataFrame(
        [{column: "" for column in SPECIFICATION_COLUMNS}],
        columns=SPECIFICATION_COLUMNS,
    )


def load_estimation_specification_csv(source: object) -> pd.DataFrame:
    """Load and validate a UTF-8 estimation-specification CSV."""
    try:
        data = pd.read_csv(source, encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        raise ValueError(
            f"Estimation-specification CSV could not be read: {error}"
        ) from error
    return validate_estimation_specification(data)


def validate_estimation_specification(data: pd.DataFrame) -> pd.DataFrame:
    """Validate complete, non-identifying specification declarations."""
    missing = sorted(set(SPECIFICATION_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(
            f"Estimation specification is missing required columns: {missing}"
        )
    if data.empty:
        raise ValueError("Estimation specification must contain at least one record.")

    validated = data.loc[:, list(SPECIFICATION_COLUMNS)].copy()
    required = [
        column for column in SPECIFICATION_COLUMNS if column != "researcher_notes"
    ]
    for column in required:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(
                f"Estimation-specification field '{column}' must not be blank."
            )
    validated["researcher_notes"] = (
        validated["researcher_notes"].fillna("").astype(str).str.strip()
    )

    if validated["specification_id"].duplicated().any():
        raise ValueError("specification_id values must be unique.")
    invalid_estimators = sorted(
        set(validated["estimator_family"]) - set(ESTIMATOR_FAMILIES)
    )
    if invalid_estimators:
        raise ValueError(f"Unknown estimator families: {invalid_estimators}")
    invalid_statuses = sorted(
        set(validated["specification_status"]) - set(SPECIFICATION_STATUSES)
    )
    if invalid_statuses:
        raise ValueError(f"Unknown specification statuses: {invalid_statuses}")
    return validated


def audit_estimation_specification(
    data: pd.DataFrame,
    instrument_version: str,
) -> dict[str, pd.DataFrame | str]:
    """Summarise declared specifications and unresolved analysis prompts."""
    selected = validate_estimation_specification(data)
    selected = selected[
        selected["instrument_version"].eq(str(instrument_version).strip())
    ]
    if selected.empty:
        raise ValueError("The selected instrument version does not exist.")

    unresolved_values = {"none", "not_assessed", "not_defined", "unknown"}
    prompt_fields = {
        "outcome_definition": "Primary outcome definition is unresolved.",
        "estimand_definition": "Target estimand is unresolved.",
        "analysis_population": "Analysis population is unresolved.",
        "unit_of_analysis": "Unit of analysis is unresolved.",
        "time_scale": "Analysis time scale is unresolved.",
        "functional_form": "Functional form is unresolved.",
        "treatment_encoding": "Treatment or exposure encoding is unresolved.",
        "comparison_contrast": "Comparison contrast is unresolved.",
        "covariate_adjustment": "Covariate-adjustment plan is unresolved.",
        "dependence_adjustment": "Dependence adjustment is unresolved.",
        "standard_error_method": "Standard-error method is unresolved.",
        "clustering_level": "Clustering level is unresolved.",
        "weighting_strategy": "Weighting strategy is unresolved.",
        "missing_data_method": "Missing-data method is unresolved.",
        "event_time_window": "Event-time or analysis window is unresolved.",
        "reference_period": "Reference period is unresolved.",
        "multiple_testing_implementation": (
            "Multiple-testing implementation is unresolved."
        ),
        "uncertainty_reporting": "Uncertainty-reporting plan is unresolved.",
        "software_environment": "Software environment is unresolved.",
        "output_disclosure_boundary": "Output disclosure boundary is unresolved.",
    }

    summaries: list[dict[str, object]] = []
    prompts: list[dict[str, str]] = []
    for row in selected.to_dict(orient="records"):
        current_prompts = [
            message
            for field, message in prompt_fields.items()
            if str(row[field]).lower() in unresolved_values
        ]
        if row["estimator_family"] == "descriptive_only":
            current_prompts.append(
                "Descriptive-only specification does not estimate a causal effect."
            )
        summaries.append(
            {
                "specification_id": row["specification_id"],
                "design_id": row["design_id"],
                "falsification_plan_id": row["falsification_plan_id"],
                "estimator_family": row["estimator_family"],
                "specification_status": row["specification_status"],
                "outcome_defined": str(row["outcome_definition"]).lower()
                not in unresolved_values,
                "estimand_defined": str(row["estimand_definition"]).lower()
                not in unresolved_values,
                "population_defined": str(row["analysis_population"]).lower()
                not in unresolved_values,
                "dependence_adjustment_defined": str(
                    row["dependence_adjustment"]
                ).lower()
                not in unresolved_values,
                "uncertainty_reporting_defined": str(
                    row["uncertainty_reporting"]
                ).lower()
                not in unresolved_values,
                "disclosure_boundary_defined": str(
                    row["output_disclosure_boundary"]
                ).lower()
                not in unresolved_values,
                "documentation_prompt_count": len(current_prompts),
            }
        )
        prompts.extend(
            {
                "specification_id": row["specification_id"],
                "prompt_type": "estimation_specification_prompt",
                "prompt": prompt,
            }
            for prompt in current_prompts
        )

    questions = pd.DataFrame(
        [
            {
                "research_question_candidate": (
                    "What population-level quantity is the proposed analysis intended "
                    "to estimate?"
                ),
                "required_future_evidence": (
                    "Preregistered outcome, estimand, population, and contrast"
                ),
            },
            {
                "research_question_candidate": (
                    "How will clustering, repeated observations, weighting, and missing "
                    "data affect uncertainty?"
                ),
                "required_future_evidence": (
                    "Dependence-aware uncertainty and sensitivity specification"
                ),
            },
            {
                "research_question_candidate": (
                    "Which primary and alternative specifications will be reported "
                    "without selective disclosure?"
                ),
                "required_future_evidence": (
                    "Preregistered reporting and output-disclosure plan"
                ),
            },
        ]
    )
    interpretation = (
        "Estimation-specification readiness evidence only. Completed fields do not "
        "establish identification, model correctness, valid standard errors, policy "
        "effects, or causality. The audit fits no model and produces no coefficient, "
        "effect estimate, p-value, significance label, ranking, approval, or decision."
    )
    return {
        "estimation_specification_summary": pd.DataFrame(summaries),
        "estimation_specification_prompts": pd.DataFrame(prompts),
        "research_question_candidates": questions,
        "interpretation": interpretation,
    }
