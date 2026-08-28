"""Descriptive support-conversion gaps for inclusive education research.

Support gaps compare adjacent stages in the conceptual pathway from resources
to practices and participation. They are diagnostic indicators for locating
patterns that merit further investigation; they are not causal estimators.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd


REQUIRED_SCORE_COLUMNS: tuple[str, ...] = (
    "resource_support_score",
    "inclusive_practice_score",
    "child_participation_score",
)


def calculate_support_gaps(dimension_scores: pd.DataFrame) -> pd.DataFrame:
    """Calculate signed resource-to-practice and practice-to-participation gaps.

    ``gap_resource_practice`` equals Resource Support minus Inclusive Practice.
    ``gap_practice_participation`` equals Inclusive Practice minus Child
    Participation. ``overall_support_conversion_gap`` equals Resource Support
    minus Child Participation and therefore preserves the direction of the
    full pathway difference.

    Positive values indicate that the earlier stage has a higher score than
    the later stage. Negative values are retained because they may also be
    substantively informative. No value is a causal effect estimate.
    """
    missing = sorted(set(REQUIRED_SCORE_COLUMNS) - set(dimension_scores.columns))
    if missing:
        raise ValueError(f"Dimension scores are missing required columns: {missing}")

    values = dimension_scores.loc[:, list(REQUIRED_SCORE_COLUMNS)].apply(
        pd.to_numeric, errors="coerce"
    )
    if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
        raise ValueError("Support-gap inputs must be finite numeric scores.")
    if not values.apply(lambda column: column.between(0, 100)).all().all():
        raise ValueError("Support-gap inputs must lie on the 0–100 scale.")

    identifiers = [
        column
        for column in ("institution_id", "institution_type", "region")
        if column in dimension_scores.columns
    ]
    result = dimension_scores.loc[:, identifiers].copy()
    result["gap_resource_practice"] = (
        values["resource_support_score"] - values["inclusive_practice_score"]
    ).round(4)
    result["gap_practice_participation"] = (
        values["inclusive_practice_score"] - values["child_participation_score"]
    ).round(4)
    result["overall_support_conversion_gap"] = (
        values["resource_support_score"] - values["child_participation_score"]
    ).round(4)
    return result


def identify_major_support_gap(gap_values: Mapping[str, float] | pd.Series) -> dict[str, object]:
    """Identify the larger positive adjacent-stage gap for descriptive reporting.

    Returns a label, value, cautious interpretation, and a research-question
    candidate. If neither adjacent gap is positive, the result states that no
    positive conversion gap is visible under the current scoring assumptions.
    """
    resource_practice = float(gap_values["gap_resource_practice"])
    practice_participation = float(gap_values["gap_practice_participation"])
    if not np.isfinite([resource_practice, practice_participation]).all():
        raise ValueError("Support-gap values must be finite numeric values.")

    if max(resource_practice, practice_participation) <= 0:
        return {
            "label": "No positive adjacent-stage gap",
            "value": max(resource_practice, practice_participation),
            "interpretation": (
                "The aggregate scores do not show an earlier pathway stage scoring "
                "above its adjacent later stage. This does not establish successful "
                "support conversion and should be checked against component data."
            ),
            "research_question": (
                "Which contextual or measurement factors may explain the observed "
                "alignment across resources, practices, and participation?"
            ),
        }

    if resource_practice >= practice_participation:
        return {
            "label": "Resource → Practice",
            "value": resource_practice,
            "interpretation": (
                "Available resource support may not be fully reflected in the "
                "reported inclusive-practice score. This is a hypothesis for further investigation."
            ),
            "research_question": (
                "Why might stronger resource support not be fully translated into "
                "inclusive educational practices?"
            ),
        }
    return {
        "label": "Practice → Participation",
        "value": practice_participation,
        "interpretation": (
            "Reported inclusive practices may not be fully reflected in the "
            "reported child-participation score. This is a hypothesis for further investigation."
        ),
        "research_question": (
            "What conditions may shape whether inclusive practices are reflected "
            "in meaningful participation in shared educational life?"
        ),
    }
