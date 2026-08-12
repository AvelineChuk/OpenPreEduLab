"""Prospective expert content-review utilities for inclusive education items.

The functions create a blank review structure and calculate transparent content
validity summaries from completed expert ratings. They do not establish that an
item or instrument is valid, and they do not replace qualitative review,
ethical governance, or later empirical validation.
"""

from __future__ import annotations

from typing import Final

import numpy as np
import pandas as pd

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS


RATING_COLUMNS: Final[tuple[str, ...]] = (
    "reviewer_id",
    "reviewer_role",
    "score_column",
    "dimension",
    "item",
    "relevance_rating",
    "clarity_rating",
    "essential_rating",
    "qualitative_comment",
    "recommended_action",
    "conflict_of_interest_disclosure",
)

ESSENTIAL_CATEGORIES: Final[tuple[str, ...]] = (
    "essential",
    "useful_not_essential",
    "not_necessary",
)

RECOMMENDED_ACTIONS: Final[tuple[str, ...]] = (
    "retain",
    "revise",
    "move",
    "split",
    "remove",
)


def create_content_validity_review_template() -> pd.DataFrame:
    """Return one blank expert-review row per current inclusion item.

    Researchers should duplicate the item block for each eligible reviewer and
    fill every rating. Blank template rows are not content-validity evidence.
    """
    rows: list[dict[str, object]] = []
    for score_column, items in DIMENSION_ITEMS.items():
        for item in items:
            rows.append(
                {
                    "reviewer_id": "",
                    "reviewer_role": "",
                    "score_column": score_column,
                    "dimension": DIMENSION_LABELS[score_column],
                    "item": item,
                    "relevance_rating": "",
                    "clarity_rating": "",
                    "essential_rating": "",
                    "qualitative_comment": "",
                    "recommended_action": "",
                    "conflict_of_interest_disclosure": "",
                }
            )
    return pd.DataFrame(rows, columns=RATING_COLUMNS)


def validate_content_validity_ratings(ratings: pd.DataFrame) -> pd.DataFrame:
    """Validate a complete reviewer-by-item matrix without imputing ratings."""
    missing_columns = sorted(set(RATING_COLUMNS) - set(ratings.columns))
    if missing_columns:
        raise ValueError(f"Content-review data are missing required columns: {missing_columns}")
    if ratings.empty:
        raise ValueError("Content-review data must contain completed expert ratings.")

    validated = ratings.loc[:, list(RATING_COLUMNS)].copy()
    text_columns = (
        "reviewer_id",
        "reviewer_role",
        "score_column",
        "dimension",
        "item",
        "essential_rating",
        "recommended_action",
        "conflict_of_interest_disclosure",
    )
    for column in text_columns:
        validated[column] = validated[column].fillna("").astype(str).str.strip()
        if validated[column].eq("").any():
            raise ValueError(f"Content-review field '{column}' must not be blank.")

    for column in ("relevance_rating", "clarity_rating"):
        validated[column] = pd.to_numeric(validated[column], errors="coerce")
        values = validated[column].to_numpy(dtype=float)
        if not np.isfinite(values).all() or not validated[column].isin([1, 2, 3, 4]).all():
            raise ValueError(f"{column} must use integer categories 1, 2, 3, or 4.")
        validated[column] = validated[column].astype(int)

    invalid_essential = sorted(set(validated["essential_rating"]) - set(ESSENTIAL_CATEGORIES))
    if invalid_essential:
        raise ValueError(f"Unknown essential_rating categories: {invalid_essential}")
    invalid_actions = sorted(set(validated["recommended_action"]) - set(RECOMMENDED_ACTIONS))
    if invalid_actions:
        raise ValueError(f"Unknown recommended_action categories: {invalid_actions}")

    expected_mapping = {
        item: (score_column, DIMENSION_LABELS[score_column])
        for score_column, items in DIMENSION_ITEMS.items()
        for item in items
    }
    if set(validated["item"]) != set(ITEM_COLUMNS):
        missing_items = sorted(set(ITEM_COLUMNS) - set(validated["item"]))
        unexpected_items = sorted(set(validated["item"]) - set(ITEM_COLUMNS))
        raise ValueError(
            "Each reviewer must rate the complete current item set; "
            f"missing items={missing_items}, unexpected items={unexpected_items}."
        )
    for row in validated.itertuples(index=False):
        expected_score, expected_dimension = expected_mapping[row.item]
        if row.score_column != expected_score or row.dimension != expected_dimension:
            raise ValueError(f"Item-to-dimension mapping is invalid for '{row.item}'.")

    if validated.duplicated(["reviewer_id", "item"]).any():
        raise ValueError("Each reviewer may rate each item only once.")
    reviewer_item_counts = validated.groupby("reviewer_id")["item"].nunique()
    if not reviewer_item_counts.eq(len(ITEM_COLUMNS)).all():
        raise ValueError("Every reviewer must rate every current inclusion item exactly once.")
    return validated


def calculate_content_validity_summaries(
    ratings: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Calculate item and dimension summaries without pass/fail thresholds.

    Ratings of 3 or 4 count toward relevance and clarity I-CVI. CVR uses the
    declared ``essential`` category. Results are descriptive evidence inputs,
    not automatic item-retention decisions or proof of instrument validity.
    """
    validated = validate_content_validity_ratings(ratings)
    working = validated.assign(
        relevant=validated["relevance_rating"].ge(3).astype(int),
        clear=validated["clarity_rating"].ge(3).astype(int),
        essential=validated["essential_rating"].eq("essential").astype(int),
    )
    grouped = working.groupby(["score_column", "dimension", "item"], sort=False)
    item_summary = grouped.agg(
        reviewer_count=("reviewer_id", "nunique"),
        relevance_i_cvi=("relevant", "mean"),
        clarity_i_cvi=("clear", "mean"),
        essential_count=("essential", "sum"),
    ).reset_index()
    item_summary["cvr"] = (
        item_summary["essential_count"] - item_summary["reviewer_count"] / 2
    ) / (item_summary["reviewer_count"] / 2)
    numeric = ["relevance_i_cvi", "clarity_i_cvi", "cvr"]
    item_summary[numeric] = item_summary[numeric].round(4)

    dimension_summary = item_summary.groupby(
        ["score_column", "dimension"], sort=False
    ).agg(
        item_count=("item", "count"),
        reviewer_count=("reviewer_count", "min"),
        relevance_s_cvi_ave=("relevance_i_cvi", "mean"),
        clarity_s_cvi_ave=("clarity_i_cvi", "mean"),
        mean_cvr=("cvr", "mean"),
    ).reset_index()
    dimension_summary[["relevance_s_cvi_ave", "clarity_s_cvi_ave", "mean_cvr"]] = (
        dimension_summary[["relevance_s_cvi_ave", "clarity_s_cvi_ave", "mean_cvr"]].round(4)
    )
    return {"item_summary": item_summary, "dimension_summary": dimension_summary}