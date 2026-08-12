"""Validation for the prospective inclusive content-review workflow."""

from io import BytesIO

import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_content_validity import (
    calculate_content_validity_summaries,
    create_content_validity_review_template,
    load_content_validity_ratings_csv,
    validate_content_validity_ratings,
)


def _completed_panel(reviewer_count: int = 4) -> pd.DataFrame:
    template = create_content_validity_review_template()
    blocks = []
    for index in range(reviewer_count):
        block = template.copy()
        block["reviewer_id"] = f"reviewer_{index + 1}"
        block["reviewer_role"] = "declared_expert_role"
        block["relevance_rating"] = 4 if index < 3 else 2
        block["clarity_rating"] = 3
        block["essential_rating"] = "essential" if index < 3 else "useful_not_essential"
        block["recommended_action"] = "retain"
        block["conflict_of_interest_disclosure"] = "none_declared"
        blocks.append(block)
    return pd.concat(blocks, ignore_index=True)


def test_content_review_template_has_one_blank_row_per_item() -> None:
    template = create_content_validity_review_template()
    assert len(template) == len(ITEM_COLUMNS)
    assert template["item"].is_unique
    assert template["reviewer_id"].eq("").all()
    assert template["relevance_rating"].eq("").all()


def test_content_validity_summaries_use_declared_formulas() -> None:
    summaries = calculate_content_validity_summaries(_completed_panel())
    item_summary = summaries["item_summary"]
    dimension_summary = summaries["dimension_summary"]
    assert len(item_summary) == len(ITEM_COLUMNS)
    assert len(dimension_summary) == 5
    assert item_summary["reviewer_count"].eq(4).all()
    assert item_summary["relevance_i_cvi"].eq(0.75).all()
    assert item_summary["clarity_i_cvi"].eq(1.0).all()
    assert item_summary["cvr"].eq(0.5).all()
    assert "decision" not in item_summary.columns


def test_content_review_rejects_missing_item_and_duplicate_rating() -> None:
    panel = _completed_panel()
    with pytest.raises(ValueError, match="Every reviewer must rate"):
        validate_content_validity_ratings(panel.drop(index=0))
    duplicate = pd.concat([panel, panel.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="only once"):
        validate_content_validity_ratings(duplicate)


def test_content_review_rejects_range_and_mapping_errors() -> None:
    panel = _completed_panel()
    panel.loc[0, "relevance_rating"] = 5
    with pytest.raises(ValueError, match="integer categories"):
        validate_content_validity_ratings(panel)

    panel = _completed_panel()
    panel.loc[0, "dimension"] = "Wrong Dimension"
    with pytest.raises(ValueError, match="mapping is invalid"):
        validate_content_validity_ratings(panel)

def test_content_review_csv_loader_supports_utf8_bom() -> None:
    panel = _completed_panel()
    payload = BytesIO(panel.to_csv(index=False).encode("utf-8-sig"))
    loaded = load_content_validity_ratings_csv(payload)
    assert len(loaded) == len(panel)
    assert loaded["reviewer_id"].nunique() == 4


def test_content_review_csv_loader_rejects_blank_template_and_missing_column() -> None:
    blank = create_content_validity_review_template()
    with pytest.raises(ValueError, match="must not be blank"):
        load_content_validity_ratings_csv(
            BytesIO(blank.to_csv(index=False).encode("utf-8-sig"))
        )

    panel = _completed_panel().drop(columns=["clarity_rating"])
    with pytest.raises(ValueError, match="missing required columns"):
        load_content_validity_ratings_csv(
            BytesIO(panel.to_csv(index=False).encode("utf-8-sig"))
        )

def test_content_review_rejects_inconsistent_reviewer_role() -> None:
    panel = _completed_panel()
    panel.loc[0, "reviewer_role"] = "different_role"
    with pytest.raises(ValueError, match="consistent reviewer_role"):
        validate_content_validity_ratings(panel)
