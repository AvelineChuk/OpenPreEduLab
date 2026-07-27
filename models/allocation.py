"""Preschool Resource Allocation Index (PRAI) calculation utilities.

This module implements the MVP specification in
``docs/Resource_Allocation_Index.md``.  The default scoring method gives each
of the four PRAI dimensions equal weight and distributes a dimension's weight
equally among its available indicators.  Entropy weights are available only
as an optional sensitivity-analysis method.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


DIMENSION_INDICATORS: Mapping[str, tuple[str, ...]] = {
    "financial": (
        "government_expenditure_per_child_yuan",
        "stable_public_funding_share_pct",
    ),
    "human": (
        "qualified_teacher_rate_pct",
        "teacher_fte_per_100_children",
        "children_per_fte_teacher",
    ),
    "material": (
        "licensed_places_per_100_resident_children",
        "usable_indoor_area_per_child_sqm",
        "average_class_size",
    ),
    "demand_responsiveness": (
        "age_specific_enrolment_coverage_pct",
        "unmet_demand_rate_pct",
        "capacity_pressure_pct",
    ),
}

POSITIVE_INDICATORS: tuple[str, ...] = (
    "government_expenditure_per_child_yuan",
    "stable_public_funding_share_pct",
    "qualified_teacher_rate_pct",
    "teacher_fte_per_100_children",
    "licensed_places_per_100_resident_children",
    "usable_indoor_area_per_child_sqm",
    "age_specific_enrolment_coverage_pct",
)

NEGATIVE_INDICATORS: tuple[str, ...] = (
    "children_per_fte_teacher",
    "average_class_size",
    "unmet_demand_rate_pct",
)

TARGET_INDICATORS: Mapping[str, tuple[float, float]] = {
    # The sample dataset has no external policy benchmark.  This occupancy
    # range is an explicit MVP assumption and should be replaced by a
    # jurisdiction-specific operating range in substantive research.
    "capacity_pressure_pct": (85.0, 95.0),
}

REQUIRED_COLUMNS: tuple[str, ...] = (
    "city",
    "province",
    "year",
    "government_expenditure_per_child_yuan",
    "stable_public_funding_share_pct",
    "qualified_teacher_rate_pct",
    "fte_teacher_count",
    "enrolled_children",
    "licensed_preschool_places",
    "usable_indoor_area_sqm",
    "class_count",
    "resident_preschool_age_population",
    "resident_target_age_children_enrolled",
    "eligible_children_seeking_place",
    "eligible_children_seeking_but_not_enrolled",
)


def load_data(file_path: str | Path) -> pd.DataFrame:
    """Load and validate a PRAI input CSV file.

    Parameters
    ----------
    file_path:
        Path to a city-by-year CSV following the schema in
        ``docs/Data_Dictionary.md``.

    Returns
    -------
    pandas.DataFrame
        The validated raw input data.

    Raises
    ------
    ValueError
        If required fields are absent, city-year pairs are duplicated, or
        required numeric fields contain missing values.
    """
    data = pd.read_csv(file_path)
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing_columns:
        raise ValueError(f"Input data are missing required columns: {missing_columns}")

    if data.duplicated(subset=["city", "year"]).any():
        raise ValueError("Input data contain duplicate city-year observations.")

    numeric_columns = [column for column in REQUIRED_COLUMNS if column not in {"city", "province"}]
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors="coerce")
    missing_numeric = data[numeric_columns].isna().any()
    if missing_numeric.any():
        invalid_columns = missing_numeric[missing_numeric].index.tolist()
        raise ValueError(f"Required numeric fields contain missing or invalid values: {invalid_columns}")

    count_columns = (
        "fte_teacher_count",
        "enrolled_children",
        "licensed_preschool_places",
        "usable_indoor_area_sqm",
        "class_count",
        "resident_preschool_age_population",
        "resident_target_age_children_enrolled",
        "eligible_children_seeking_place",
        "eligible_children_seeking_but_not_enrolled",
    )
    if (data[list(count_columns)] <= 0).any().any():
        raise ValueError("Count and denominator fields must be greater than zero.")
    if (data["eligible_children_seeking_but_not_enrolled"] > data["eligible_children_seeking_place"]).any():
        raise ValueError("Children not enrolled cannot exceed children seeking a place.")

    return data.copy()


def prepare_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Derive PRAI model indicators from validated city-year input data.

    The derived rates follow the equations stated in ``Data_Dictionary.md``.
    Population is used as an exposure denominator, rather than as a positive
    or negative component of the allocation score.

    Parameters
    ----------
    data:
        Validated raw PRAI input data.

    Returns
    -------
    pandas.DataFrame
        Identifier fields and the eleven unnormalised PRAI indicators.
    """
    required = set(REQUIRED_COLUMNS)
    missing_columns = sorted(required - set(data.columns))
    if missing_columns:
        raise ValueError(f"Cannot derive indicators; missing columns: {missing_columns}")

    indicators = data.loc[:, ["city", "province", "year"]].copy()
    indicators["government_expenditure_per_child_yuan"] = data[
        "government_expenditure_per_child_yuan"
    ]
    indicators["stable_public_funding_share_pct"] = data["stable_public_funding_share_pct"]
    indicators["qualified_teacher_rate_pct"] = data["qualified_teacher_rate_pct"]
    indicators["teacher_fte_per_100_children"] = (
        100 * data["fte_teacher_count"] / data["enrolled_children"]
    )
    indicators["children_per_fte_teacher"] = (
        data["enrolled_children"] / data["fte_teacher_count"]
    )
    indicators["licensed_places_per_100_resident_children"] = (
        100 * data["licensed_preschool_places"] / data["resident_preschool_age_population"]
    )
    indicators["usable_indoor_area_per_child_sqm"] = (
        data["usable_indoor_area_sqm"] / data["enrolled_children"]
    )
    indicators["average_class_size"] = data["enrolled_children"] / data["class_count"]
    indicators["age_specific_enrolment_coverage_pct"] = (
        100
        * data["resident_target_age_children_enrolled"]
        / data["resident_preschool_age_population"]
    )
    indicators["unmet_demand_rate_pct"] = (
        100
        * data["eligible_children_seeking_but_not_enrolled"]
        / data["eligible_children_seeking_place"]
    )
    indicators["capacity_pressure_pct"] = (
        100 * data["enrolled_children"] / data["licensed_preschool_places"]
    )
    return indicators


def normalize_indicators(
    indicators: pd.DataFrame,
    positive_indicators: Sequence[str] = POSITIVE_INDICATORS,
    negative_indicators: Sequence[str] = NEGATIVE_INDICATORS,
    target_indicators: Mapping[str, tuple[float, float]] = TARGET_INDICATORS,
) -> pd.DataFrame:
    """Normalise PRAI indicators to the closed interval from zero to one.

    Positive indicators use sample min-max scaling. Negative indicators are
    reverse-scaled so lower raw values receive higher scores. Target-range
    indicators receive a score of one inside their stated range and decline
    linearly toward the observed sample minimum and maximum outside it.

    This is the sample-based fallback normalisation allowed for the MVP in
    ``Resource_Allocation_Index.md``. Scores are comparable only within the
    jointly normalised sample; external policy benchmarks should replace this
    approach when they are available.

    Parameters
    ----------
    indicators:
        DataFrame containing the unnormalised PRAI indicator columns.
    positive_indicators:
        Columns for which higher values represent stronger allocation.
    negative_indicators:
        Columns for which lower values represent stronger allocation.
    target_indicators:
        Mapping of target-range columns to ``(lower_target, upper_target)``.

    Returns
    -------
    pandas.DataFrame
        Identifier columns plus normalised PRAI indicator columns.
    """
    score_columns = list(positive_indicators) + list(negative_indicators) + list(target_indicators)
    missing_columns = sorted(set(score_columns) - set(indicators.columns))
    if missing_columns:
        raise ValueError(f"Cannot normalise missing indicators: {missing_columns}")

    normalised = indicators.loc[:, ["city", "province", "year"]].copy()

    for column in positive_indicators:
        values = indicators[[column]].astype(float)
        if values[column].nunique(dropna=False) == 1:
            normalised[column] = 0.5
        else:
            normalised[column] = MinMaxScaler().fit_transform(values).ravel()

    for column in negative_indicators:
        values = indicators[[column]].astype(float)
        if values[column].nunique(dropna=False) == 1:
            normalised[column] = 0.5
        else:
            normalised[column] = 1 - MinMaxScaler().fit_transform(values).ravel()

    for column, (lower_target, upper_target) in target_indicators.items():
        if lower_target > upper_target:
            raise ValueError(f"Target range for {column} has lower bound above upper bound.")

        values = indicators[column].astype(float)
        sample_min, sample_max = values.min(), values.max()
        score = pd.Series(1.0, index=values.index, dtype=float)
        below_target = values < lower_target
        above_target = values > upper_target

        if sample_min < lower_target:
            score.loc[below_target] = (
                (values.loc[below_target] - sample_min) / (lower_target - sample_min)
            )
        if sample_max > upper_target:
            score.loc[above_target] = (
                (sample_max - values.loc[above_target]) / (sample_max - upper_target)
            )
        normalised[column] = score.clip(lower=0, upper=1)

    return normalised


def calculate_weights(
    normalised_indicators: pd.DataFrame,
    method: str = "equal",
) -> pd.Series:
    """Calculate weights for PRAI indicators.

    The default ``equal`` method implements the PRAI MVP: each of the four
    dimensions has weight 0.25, and each indicator within a dimension shares
    its dimension's weight equally. The optional ``entropy`` method produces
    sample-dependent global entropy weights for sensitivity analysis.

    Parameters
    ----------
    normalised_indicators:
        Output of :func:`normalize_indicators`.
    method:
        Either ``"equal"`` or ``"entropy"``.

    Returns
    -------
    pandas.Series
        Indicator weights that sum to one.
    """
    indicator_columns = [
        indicator for indicators in DIMENSION_INDICATORS.values() for indicator in indicators
    ]
    missing_columns = sorted(set(indicator_columns) - set(normalised_indicators.columns))
    if missing_columns:
        raise ValueError(f"Cannot calculate weights; missing columns: {missing_columns}")

    if method == "equal":
        weights: dict[str, float] = {}
        dimension_weight = 1 / len(DIMENSION_INDICATORS)
        for dimension_indicators in DIMENSION_INDICATORS.values():
            indicator_weight = dimension_weight / len(dimension_indicators)
            weights.update({indicator: indicator_weight for indicator in dimension_indicators})
        return pd.Series(weights, name="weight")

    if method == "entropy":
        values = normalised_indicators[indicator_columns].to_numpy(dtype=float)
        # A small positive constant makes zero-valued min-max scores valid in
        # the entropy calculation without changing their substantive ordering.
        adjusted = values + 1e-12
        proportions = adjusted / adjusted.sum(axis=0, keepdims=True)
        sample_size = proportions.shape[0]
        entropy = -(proportions * np.log(proportions)).sum(axis=0) / np.log(sample_size)
        diversification = 1 - entropy
        if np.isclose(diversification.sum(), 0):
            return pd.Series(1 / len(indicator_columns), index=indicator_columns, name="weight")
        return pd.Series(
            diversification / diversification.sum(), index=indicator_columns, name="weight"
        )

    raise ValueError("method must be either 'equal' or 'entropy'.")


def calculate_prai_score(
    data: pd.DataFrame,
    weight_method: str = "equal",
) -> pd.DataFrame:
    """Calculate a 0–100 Preschool Resource Allocation Index score.

    Parameters
    ----------
    data:
        Raw city-year data matching the PRAI sample-data schema.
    weight_method:
        ``"equal"`` implements the documented MVP specification. ``"entropy"``
        is available for sensitivity analysis and is not the default model.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with ``city``, ``year``, and ``resource_allocation_score``.
    """
    indicators = prepare_indicators(data)
    normalised = normalize_indicators(indicators)
    weights = calculate_weights(normalised, method=weight_method)
    score = normalised[weights.index].mul(weights, axis="columns").sum(axis=1) * 100

    return pd.DataFrame(
        {
            "city": data["city"].to_numpy(),
            "year": data["year"].to_numpy(),
            "resource_allocation_score": score.round(2).to_numpy(),
        }
    )


def evaluate_level(score: float | pd.Series) -> str | pd.Series:
    """Assign a simplified PRAI allocation level to one or more scores.

    Scores of 80–100 are labelled ``High Allocation``, scores from 60 up to
    80 are labelled ``Medium Allocation``, and scores below 60 are labelled
    ``Low Allocation``. These operational labels condense the more detailed
    interpretive bands in ``Resource_Allocation_Index.md`` and do not replace
    examination of dimension-level results.

    Parameters
    ----------
    score:
        A scalar score or pandas Series of scores expected to lie in [0, 100].

    Returns
    -------
    str or pandas.Series
        Allocation label(s) corresponding to the supplied score(s).
    """
    if isinstance(score, pd.Series):
        return pd.Series(
            np.select(
                [score >= 80, score >= 60],
                ["High Allocation", "Medium Allocation"],
                default="Low Allocation",
            ),
            index=score.index,
            name="allocation_level",
        )

    if score >= 80:
        return "High Allocation"
    if score >= 60:
        return "Medium Allocation"
    return "Low Allocation"
