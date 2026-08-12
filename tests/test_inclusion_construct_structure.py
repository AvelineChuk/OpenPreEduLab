"""Tests for exploratory inclusive construct-structure audits."""

from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_construct_structure import (
    audit_construct_structure,
    create_construct_structure_template,
    load_construct_structure_csv,
)


def _structure_data(observation_count: int = 48) -> pd.DataFrame:
    rng = np.random.default_rng(20260812)
    latent = rng.normal(size=(observation_count, 5))
    rows = []
    for observation_index in range(observation_count):
        row = {
            "pseudonymous_unit_id": f"unit_{observation_index + 1}",
            "instrument_version": "inclusive_items_v0.1",
            "administration_round": 1,
        }
        for item_index, item in enumerate(ITEM_COLUMNS):
            dimension_index = min(item_index // 6, 4)
            value = 50 + 10 * latent[observation_index, dimension_index] + rng.normal(0, 7)
            row[item] = float(np.clip(value, 0, 100))
        rows.append(row)
    return pd.DataFrame(rows)


def test_construct_template_and_utf8_bom_csv_roundtrip() -> None:
    template = create_construct_structure_template()
    assert set(ITEM_COLUMNS).issubset(template.columns)
    payload = BytesIO(_structure_data().to_csv(index=False).encode("utf-8-sig"))
    loaded = load_construct_structure_csv(payload)
    assert len(loaded) == 48


@pytest.mark.parametrize("invalid_value", [np.nan, "not_numeric", 101.0])
def test_construct_csv_rejects_missing_non_numeric_and_out_of_range(invalid_value: object) -> None:
    data = _structure_data()
    if isinstance(invalid_value, str):
        data[ITEM_COLUMNS[0]] = data[ITEM_COLUMNS[0]].astype(object)
    data.loc[0, ITEM_COLUMNS[0]] = invalid_value
    with pytest.raises(ValueError):
        load_construct_structure_csv(BytesIO(data.to_csv(index=False).encode("utf-8-sig")))


def test_construct_audit_reports_readiness_kmo_bartlett_eigenvalues_and_loadings() -> None:
    audit = audit_construct_structure(_structure_data(), "inclusive_items_v0.1", 1, 5)
    readiness = audit["readiness_summary"].iloc[0]
    assert readiness["observation_count"] == 48
    assert readiness["item_count"] == len(ITEM_COLUMNS)
    assert 0 <= readiness["overall_kmo"] <= 1
    assert readiness["bartlett_degrees_of_freedom"] == len(ITEM_COLUMNS) * (len(ITEM_COLUMNS) - 1) // 2
    assert np.isfinite(readiness["bartlett_chi_square"])
    assert 0 <= readiness["bartlett_p_value"] <= 1
    assert len(audit["eigenvalue_summary"]) == len(ITEM_COLUMNS)
    assert audit["component_loading_summary"].shape == (len(ITEM_COLUMNS), 7)
    assert audit["correlation_matrix"].shape == (len(ITEM_COLUMNS), len(ITEM_COLUMNS))
    assert audit["item_kmo_summary"]["item_kmo"].between(0, 1).all()
    assert "not validate" in audit["interpretation"]


def test_construct_audit_requires_explicit_existing_version_and_round() -> None:
    data = _structure_data()
    second = data.copy()
    second["instrument_version"] = "inclusive_items_v0.2"
    second["administration_round"] = 2
    mixed = pd.concat([data, second], ignore_index=True)
    audit = audit_construct_structure(mixed, "inclusive_items_v0.2", 2, 3)
    assert audit["readiness_summary"].iloc[0]["instrument_version"] == "inclusive_items_v0.2"
    with pytest.raises(ValueError, match="do not exist"):
        audit_construct_structure(mixed, "inclusive_items_v0.1", 2, 3)


def test_construct_audit_rejects_insufficient_sample_and_zero_variance_item() -> None:
    with pytest.raises(ValueError, match="more complete observations than items"):
        audit_construct_structure(_structure_data(len(ITEM_COLUMNS)), "inclusive_items_v0.1", 1, 3)
    data = _structure_data()
    data[ITEM_COLUMNS[0]] = 50.0
    with pytest.raises(ValueError, match="Zero-variance items"):
        audit_construct_structure(data, "inclusive_items_v0.1", 1, 3)


def test_construct_audit_rejects_singular_correlation_matrix() -> None:
    data = _structure_data()
    data[ITEM_COLUMNS[1]] = data[ITEM_COLUMNS[0]]
    with pytest.raises(ValueError, match="singular or numerically rank-deficient"):
        audit_construct_structure(data, "inclusive_items_v0.1", 1, 3)


@pytest.mark.parametrize("component_count", [0, len(ITEM_COLUMNS) + 1, 2.5, True])
def test_construct_audit_rejects_invalid_component_count(component_count: object) -> None:
    with pytest.raises(ValueError, match="n_components"):
        audit_construct_structure(
            _structure_data(), "inclusive_items_v0.1", 1, component_count  # type: ignore[arg-type]
        )


def test_construct_outputs_exclude_ids_and_automatic_decision_fields() -> None:
    audit = audit_construct_structure(_structure_data(), "inclusive_items_v0.1", 1, 4)
    prohibited = {"pseudonymous_unit_id", "pass", "fail", "item_decision", "remove_item"}
    for key in (
        "readiness_summary",
        "item_kmo_summary",
        "correlation_matrix",
        "eigenvalue_summary",
        "component_loading_summary",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
