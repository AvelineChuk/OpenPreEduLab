"""Software validation for descriptive inclusive-education support gaps."""

import pandas as pd
import pytest

from models.support_gap import calculate_support_gaps, identify_major_support_gap


def test_support_gap_expected_values() -> None:
    """The documented 80 → 58 → 49 example yields gaps of 22, 9, and 31."""
    scores = pd.DataFrame(
        {
            "institution_id": ["SYN-X"],
            "resource_support_score": [80],
            "inclusive_practice_score": [58],
            "child_participation_score": [49],
        }
    )
    result = calculate_support_gaps(scores).iloc[0]
    assert result["gap_resource_practice"] == 22
    assert result["gap_practice_participation"] == 9
    assert result["overall_support_conversion_gap"] == 31


def test_support_gap_retains_negative_values() -> None:
    """Later-stage scores above earlier stages are retained rather than clipped."""
    scores = pd.DataFrame(
        {
            "resource_support_score": [55],
            "inclusive_practice_score": [65],
            "child_participation_score": [70],
        }
    )
    result = calculate_support_gaps(scores).iloc[0]
    assert result["gap_resource_practice"] == -10
    assert result["gap_practice_participation"] == -5
    assert result["overall_support_conversion_gap"] == -15


def test_support_gap_missing_score_is_rejected() -> None:
    """All three pathway stages are required for gap calculation."""
    with pytest.raises(ValueError, match="missing required columns"):
        calculate_support_gaps(pd.DataFrame({"resource_support_score": [80]}))


def test_major_gap_is_hypothesis_not_conclusion() -> None:
    """Major-gap interpretation explicitly retains hypothesis language."""
    result = identify_major_support_gap(
        {"gap_resource_practice": 22, "gap_practice_participation": 9}
    )
    assert result["label"] == "Resource → Practice"
    assert "hypothesis for further investigation" in result["interpretation"]
