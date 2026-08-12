"""Tests for external-measure relationship readiness audits."""

from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from models.inclusion import ITEM_COLUMNS
from models.inclusion_external_measure import (
    audit_external_measure_relationships,
    create_external_measure_template,
    load_external_measure_csv,
    validate_external_measure_data,
)


def _external_data(record_count: int = 12) -> pd.DataFrame:
    rng = np.random.default_rng(20260812)
    rows = []
    for unit_index in range(record_count):
        external_value = 25 + unit_index * 4 + rng.normal(0, 2)
        row = {
            "pseudonymous_unit_id": f"unit_{unit_index + 1}",
            "instrument_version": "inclusive_items_v0.1",
            "administration_round": 1,
            "external_measure_name": "Independent institutional participation climate",
            "external_measure_source": "Governed external institutional instrument v1",
            "expected_relationship_type": "convergent_candidate",
            "external_measure_value": external_value,
        }
        for item_index, item in enumerate(ITEM_COLUMNS):
            row[item] = float(
                np.clip(30 + unit_index * 3 + item_index * 0.2 + rng.normal(0, 4), 0, 100)
            )
        rows.append(row)
    return pd.DataFrame(rows)


def test_external_template_and_utf8_bom_roundtrip() -> None:
    template = create_external_measure_template()
    assert "external_measure_value" in template.columns
    assert set(ITEM_COLUMNS).issubset(template.columns)
    loaded = load_external_measure_csv(
        BytesIO(_external_data().to_csv(index=False).encode("utf-8-sig"))
    )
    assert len(loaded) == 12


def test_external_validation_rejects_blank_metadata_invalid_type_and_value() -> None:
    data = _external_data()
    data.loc[0, "external_measure_source"] = ""
    with pytest.raises(ValueError, match="must not be blank"):
        validate_external_measure_data(data)
    data = _external_data()
    data["expected_relationship_type"] = "validated_convergent_measure"
    with pytest.raises(ValueError, match="Unknown expected relationship types"):
        validate_external_measure_data(data)
    data = _external_data()
    data.loc[0, "external_measure_value"] = np.nan
    with pytest.raises(ValueError, match="complete finite numeric values"):
        validate_external_measure_data(data)


def test_external_audit_reports_coverage_relationships_intervals_and_questions() -> None:
    audit = audit_external_measure_relationships(
        _external_data(), "inclusive_items_v0.1", 1
    )
    coverage = audit["external_measure_coverage_summary"].iloc[0]
    relationships = audit["dimension_relationship_summary"]
    assert coverage["complete_record_count"] == 12
    assert coverage["external_measure_variance_positive"]
    assert len(relationships) == 5
    assert relationships["correlation_defined"].all()
    assert relationships["pearson_correlation"].between(-1, 1).all()
    assert relationships["spearman_correlation"].between(-1, 1).all()
    assert (
        relationships["pearson_fisher_95_ci_lower"]
        <= relationships["pearson_correlation"]
    ).all()
    assert (
        relationships["pearson_correlation"]
        <= relationships["pearson_fisher_95_ci_upper"]
    ).all()
    assert len(audit["research_question_candidates"]) == 3
    assert "do not establish convergent" in audit["interpretation"]


def test_external_audit_requires_one_version_round_and_consistent_measure() -> None:
    data = _external_data()
    second = _external_data()
    second["instrument_version"] = "inclusive_items_v0.2"
    second["administration_round"] = 2
    mixed = pd.concat([data, second], ignore_index=True)
    audit = audit_external_measure_relationships(mixed, "inclusive_items_v0.2", 2)
    assert audit["external_measure_coverage_summary"].iloc[0][
        "instrument_version"
    ] == "inclusive_items_v0.2"
    with pytest.raises(ValueError, match="do not exist"):
        audit_external_measure_relationships(mixed, "inclusive_items_v0.1", 2)
    inconsistent = _external_data()
    inconsistent.loc[0, "external_measure_name"] = "Another measure"
    with pytest.raises(ValueError, match="exactly one consistent"):
        audit_external_measure_relationships(inconsistent, "inclusive_items_v0.1", 1)


def test_external_audit_rejects_insufficient_records() -> None:
    with pytest.raises(ValueError, match="at least 5 complete records"):
        audit_external_measure_relationships(
            _external_data(record_count=4), "inclusive_items_v0.1", 1
        )


def test_external_audit_handles_zero_variance_transparently() -> None:
    data = _external_data()
    data["external_measure_value"] = 50.0
    audit = audit_external_measure_relationships(data, "inclusive_items_v0.1", 1)
    coverage = audit["external_measure_coverage_summary"].iloc[0]
    relationships = audit["dimension_relationship_summary"]
    assert not coverage["external_measure_variance_positive"]
    assert not relationships["correlation_defined"].any()
    assert relationships["pearson_correlation"].isna().all()
    assert relationships["spearman_correlation"].isna().all()


def test_external_audit_supports_declared_non_100_item_scale() -> None:
    data = _external_data()
    data[list(ITEM_COLUMNS)] = data[list(ITEM_COLUMNS)] / 100
    audit = audit_external_measure_relationships(
        data, "inclusive_items_v0.1", 1, source_min=0, source_max=1
    )
    assert audit["dimension_relationship_summary"]["dimension_mean"].between(0, 100).all()


def test_external_outputs_exclude_ids_and_validity_decision_fields() -> None:
    audit = audit_external_measure_relationships(
        _external_data(), "inclusive_items_v0.1", 1
    )
    prohibited = {
        "pseudonymous_unit_id",
        "pass",
        "fail",
        "validity_status",
        "hypothesis_supported",
        "item_decision",
        "institution_rank",
    }
    for key in (
        "external_measure_coverage_summary",
        "dimension_relationship_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
