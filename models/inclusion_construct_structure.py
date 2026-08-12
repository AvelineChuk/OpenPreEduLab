"""Exploratory construct-structure readiness audits for inclusive education.

The workflow reports item correlations, KMO diagnostics, Bartlett's test,
correlation-matrix eigenvalues, and unrotated principal-component loadings for
one explicitly selected instrument version and administration round. It is not
confirmatory factor analysis and does not validate the five-dimension model.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_reliability import (
    create_reliability_audit_template,
    load_reliability_audit_csv,
    validate_reliability_audit_data,
)


def create_construct_structure_template() -> pd.DataFrame:
    """Return the complete-response schema shared with reliability studies."""
    return create_reliability_audit_template()


def load_construct_structure_csv(
    source: object,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> pd.DataFrame:
    """Load a UTF-8 CSV and apply the complete-response validation rules."""
    return load_reliability_audit_csv(source, source_min, source_max)


def _select_analysis_sample(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    source_min: float,
    source_max: float,
) -> pd.DataFrame:
    """Validate and select one version-round sample without retaining unit IDs."""
    validated = validate_reliability_audit_data(data, source_min, source_max)
    version = str(instrument_version).strip()
    if not version:
        raise ValueError("instrument_version must not be blank.")
    try:
        round_number = int(administration_round)
    except (TypeError, ValueError) as error:
        raise ValueError("administration_round must be a positive integer.") from error
    if round_number < 1 or round_number != administration_round:
        raise ValueError("administration_round must be a positive integer.")
    selected = validated[
        validated["instrument_version"].eq(version)
        & validated["administration_round"].eq(round_number)
    ]
    if selected.empty:
        raise ValueError("The selected instrument version and administration round do not exist.")
    return selected.loc[:, list(ITEM_COLUMNS)].copy()


def _kmo_diagnostics(correlation: np.ndarray) -> tuple[float, np.ndarray]:
    """Return overall and item-level Kaiser-Meyer-Olkin statistics."""
    inverse = np.linalg.inv(correlation)
    scale = np.sqrt(np.outer(np.diag(inverse), np.diag(inverse)))
    partial = -inverse / scale
    np.fill_diagonal(partial, 0.0)
    correlations = correlation.copy()
    np.fill_diagonal(correlations, 0.0)
    correlation_sq = correlations**2
    partial_sq = partial**2
    item_numerator = correlation_sq.sum(axis=0)
    item_denominator = item_numerator + partial_sq.sum(axis=0)
    item_kmo = np.divide(
        item_numerator,
        item_denominator,
        out=np.full_like(item_numerator, np.nan),
        where=item_denominator > 0,
    )
    overall_denominator = float(correlation_sq.sum() + partial_sq.sum())
    overall = float(correlation_sq.sum() / overall_denominator) if overall_denominator > 0 else np.nan
    return overall, item_kmo


def audit_construct_structure(
    data: pd.DataFrame,
    instrument_version: str,
    administration_round: int,
    n_components: int,
    source_min: float = 0.0,
    source_max: float = 100.0,
) -> dict[str, pd.DataFrame | str]:
    """Audit exploratory structure readiness for one version and round.

    The prototype requires more complete observations than items so that a
    full-rank item correlation matrix is possible. The researcher explicitly
    chooses the number of unrotated principal components; the software does not
    select a factor count or make item-retention decisions.
    """
    items = _select_analysis_sample(
        data,
        instrument_version,
        administration_round,
        source_min,
        source_max,
    )
    observation_count, item_count = items.shape
    if observation_count <= item_count:
        raise ValueError(
            "Construct-structure audit requires more complete observations than items "
            f"as a prototype computation condition; received {observation_count} "
            f"observations and {item_count} items."
        )
    if not isinstance(n_components, (int, np.integer)) or isinstance(n_components, bool):
        raise ValueError("n_components must be an integer.")
    if n_components < 1 or n_components > item_count:
        raise ValueError(f"n_components must be between 1 and {item_count}.")

    variances = items.var(axis=0, ddof=1)
    zero_variance_items = variances.index[variances <= 0].tolist()
    if zero_variance_items:
        raise ValueError(f"Zero-variance items cannot be analysed: {zero_variance_items}")

    correlation_frame = items.corr(method="pearson")
    correlation = correlation_frame.to_numpy(dtype=float)
    eigenvalues_ascending, eigenvectors_ascending = np.linalg.eigh(correlation)
    tolerance = max(item_count, 1) * np.finfo(float).eps * max(
        1.0, float(np.abs(eigenvalues_ascending).max())
    )
    if float(eigenvalues_ascending.min()) <= tolerance:
        raise ValueError(
            "The item correlation matrix is singular or numerically rank-deficient; "
            "review duplicate or linearly dependent items and the selected sample."
        )

    determinant = float(np.prod(eigenvalues_ascending))
    if not np.isfinite(determinant) or determinant <= 0:
        raise ValueError("The item correlation matrix determinant is not positive and finite.")

    overall_kmo, item_kmo = _kmo_diagnostics(correlation)
    bartlett_df = item_count * (item_count - 1) // 2
    bartlett_chi_square = -(
        observation_count - 1 - (2 * item_count + 5) / 6
    ) * np.log(determinant)
    bartlett_p_value = float(chi2.sf(bartlett_chi_square, bartlett_df))

    order = np.argsort(eigenvalues_ascending)[::-1]
    eigenvalues = eigenvalues_ascending[order]
    eigenvectors = eigenvectors_ascending[:, order]
    explained_ratio = eigenvalues / eigenvalues.sum()
    loadings = eigenvectors[:, :n_components] * np.sqrt(eigenvalues[:n_components])

    item_dimensions = {
        item: DIMENSION_LABELS[score_column]
        for score_column, dimension_items in DIMENSION_ITEMS.items()
        for item in dimension_items
    }
    readiness = pd.DataFrame(
        [{
            "instrument_version": str(instrument_version).strip(),
            "administration_round": int(administration_round),
            "observation_count": observation_count,
            "item_count": item_count,
            "observation_item_ratio": round(observation_count / item_count, 4),
            "selected_component_count": int(n_components),
            "correlation_matrix_determinant": determinant,
            "overall_kmo": round(overall_kmo, 6) if np.isfinite(overall_kmo) else np.nan,
            "bartlett_chi_square": round(float(bartlett_chi_square), 6),
            "bartlett_degrees_of_freedom": bartlett_df,
            "bartlett_p_value": bartlett_p_value,
        }]
    )
    item_summary = pd.DataFrame(
        {
            "item": list(ITEM_COLUMNS),
            "conceptual_dimension": [item_dimensions[item] for item in ITEM_COLUMNS],
            "item_kmo": np.round(item_kmo, 6),
            "item_variance": np.round(variances.loc[list(ITEM_COLUMNS)].to_numpy(), 6),
        }
    )
    eigenvalue_summary = pd.DataFrame(
        {
            "component": np.arange(1, item_count + 1),
            "eigenvalue": np.round(eigenvalues, 6),
            "explained_variance_ratio": np.round(explained_ratio, 6),
            "cumulative_explained_variance_ratio": np.round(np.cumsum(explained_ratio), 6),
        }
    )
    loading_summary = pd.DataFrame(
        loadings,
        columns=[f"component_{index}" for index in range(1, n_components + 1)],
    )
    loading_summary.insert(0, "conceptual_dimension", [item_dimensions[item] for item in ITEM_COLUMNS])
    loading_summary.insert(0, "item", list(ITEM_COLUMNS))
    loading_summary.iloc[:, 2:] = loading_summary.iloc[:, 2:].round(6)

    interpretation = (
        "Exploratory structural evidence only. KMO and Bartlett statistics are reported "
        "without an automatic pass/fail threshold. Principal components are not latent "
        "factors or confirmatory factor analysis, loading signs are arbitrary, and these "
        "results do not validate the five-dimension structure. Component retention and "
        "item decisions remain documented researcher decisions requiring future validation."
    )
    return {
        "readiness_summary": readiness,
        "item_kmo_summary": item_summary,
        "correlation_matrix": correlation_frame.round(6),
        "eigenvalue_summary": eigenvalue_summary,
        "component_loading_summary": loading_summary,
        "interpretation": interpretation,
    }
