"""Tests for inclusive alternative-weight sensitivity audits."""

from io import BytesIO

import numpy as np
import pandas as pd
import pytest

from models.inclusion import DIMENSION_ITEMS, DIMENSION_LABELS, ITEM_COLUMNS
from models.inclusion_weight_sensitivity import (
    audit_weight_sensitivity,
    create_weight_scheme_template,
    load_weight_scheme_csv,
    validate_weight_schemes,
)


def _responses(record_count: int = 8) -> pd.DataFrame:
    rows = []
    for unit_index in range(record_count):
        row = {
            "pseudonymous_unit_id": f"unit_{unit_index + 1}",
            "instrument_version": "inclusive_items_v0.1",
            "administration_round": 1,
        }
        for item_index, item in enumerate(ITEM_COLUMNS):
            row[item] = float(20 + unit_index * 7 + item_index * 0.8)
        rows.append(row)
    return pd.DataFrame(rows)


def _scheme(name: str = "Theory emphasis") -> pd.DataFrame:
    rows = []
    for score_column, items in DIMENSION_ITEMS.items():
        raw = np.arange(1, len(items) + 1, dtype=float)
        weights = raw / raw.sum()
        for item, weight in zip(items, weights, strict=True):
            rows.append(
                {
                    "scheme_name": name,
                    "scheme_rationale": "Prospective theory-led sensitivity only",
                    "evidence_status": "theory_candidate",
                    "score_column": score_column,
                    "dimension": DIMENSION_LABELS[score_column],
                    "item": item,
                    "item_weight": weight,
                }
            )
    return pd.DataFrame(rows)


def test_weight_template_and_utf8_bom_roundtrip() -> None:
    template = create_weight_scheme_template()
    assert len(template) == len(ITEM_COLUMNS)
    assert set(template["item"]) == set(ITEM_COLUMNS)
    loaded = load_weight_scheme_csv(
        BytesIO(_scheme().to_csv(index=False).encode("utf-8-sig"))
    )
    assert len(loaded) == len(ITEM_COLUMNS)


def test_weight_validation_rejects_missing_duplicate_unknown_and_nonpositive_weights() -> None:
    incomplete = _scheme().iloc[:-1]
    with pytest.raises(ValueError, match="exactly the current 28 items"):
        validate_weight_schemes(incomplete)
    duplicate = pd.concat([_scheme(), _scheme().iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="only once"):
        validate_weight_schemes(duplicate)
    invalid_status = _scheme()
    invalid_status["evidence_status"] = "validated_weight"
    with pytest.raises(ValueError, match="Unknown weight evidence statuses"):
        validate_weight_schemes(invalid_status)
    nonpositive = _scheme()
    nonpositive.loc[0, "item_weight"] = 0
    with pytest.raises(ValueError, match="finite positive"):
        validate_weight_schemes(nonpositive)


def test_weight_validation_rejects_mapping_label_and_sum_errors() -> None:
    wrong_mapping = _scheme()
    wrong_mapping.loc[0, "score_column"] = "resource_support_score"
    with pytest.raises(ValueError, match="wrong score_column"):
        validate_weight_schemes(wrong_mapping)
    wrong_label = _scheme()
    wrong_label.loc[0, "dimension"] = "Wrong label"
    with pytest.raises(ValueError, match="inconsistent dimension label"):
        validate_weight_schemes(wrong_label)
    wrong_sum = _scheme()
    wrong_sum.loc[0, "item_weight"] += 0.1
    with pytest.raises(ValueError, match="sum to 1"):
        validate_weight_schemes(wrong_sum)


def test_weight_audit_reports_scheme_dimension_gap_and_questions() -> None:
    audit = audit_weight_sensitivity(
        _responses(), _scheme(), "inclusive_items_v0.1", 1
    )
    scheme_summary = audit["weight_scheme_summary"]
    dimensions = audit["dimension_sensitivity_summary"]
    gaps = audit["support_gap_sensitivity_summary"]
    assert len(scheme_summary) == 1
    assert not scheme_summary.iloc[0]["default_scoring_changed"]
    assert len(dimensions) == 5
    assert len(gaps) == 3
    assert dimensions["alternative_weight_mean"].between(0, 100).all()
    assert gaps["mean_absolute_institution_change"].ge(0).all()
    assert len(audit["research_question_candidates"]) == 3
    assert "best scheme" in audit["interpretation"]
    assert "no automatic threshold, ranking, or scheme recommendation" in audit["interpretation"]


def test_equal_weight_scheme_reproduces_baseline_exactly() -> None:
    scheme = create_weight_scheme_template()
    scheme["scheme_name"] = "Equal weight replication"
    scheme["scheme_rationale"] = "Mathematical baseline replication test"
    scheme["evidence_status"] = "exploratory_sensitivity"
    audit = audit_weight_sensitivity(
        _responses(), scheme, "inclusive_items_v0.1", 1
    )
    assert audit["dimension_sensitivity_summary"]["mean_score_change"].abs().lt(1e-8).all()
    assert audit["support_gap_sensitivity_summary"]["mean_gap_change"].abs().lt(1e-8).all()


def test_weight_audit_supports_multiple_schemes_and_declared_source_scale() -> None:
    first = _scheme("Theory emphasis")
    second = _scheme("Expert proposal")
    second["scheme_rationale"] = "Prospective expert proposal for sensitivity"
    second["evidence_status"] = "expert_proposed"
    responses = _responses()
    responses[list(ITEM_COLUMNS)] = responses[list(ITEM_COLUMNS)] / 100
    audit = audit_weight_sensitivity(
        responses,
        pd.concat([first, second], ignore_index=True),
        "inclusive_items_v0.1",
        1,
        source_min=0,
        source_max=1,
    )
    assert len(audit["weight_scheme_summary"]) == 2
    assert len(audit["dimension_sensitivity_summary"]) == 10


def test_weight_audit_selects_one_version_and_round() -> None:
    first = _responses()
    second = _responses()
    second["instrument_version"] = "inclusive_items_v0.2"
    second["administration_round"] = 2
    data = pd.concat([first, second], ignore_index=True)
    audit = audit_weight_sensitivity(data, _scheme(), "inclusive_items_v0.2", 2)
    assert audit["weight_scheme_summary"].iloc[0]["instrument_version"] == "inclusive_items_v0.2"
    with pytest.raises(ValueError, match="do not exist"):
        audit_weight_sensitivity(data, _scheme(), "inclusive_items_v0.1", 2)


def test_weight_outputs_exclude_ids_rankings_and_recommendations() -> None:
    audit = audit_weight_sensitivity(
        _responses(), _scheme(), "inclusive_items_v0.1", 1
    )
    prohibited = {
        "pseudonymous_unit_id",
        "institution_rank",
        "scheme_rank",
        "recommended_scheme",
        "best_weight",
        "item_importance",
        "pass",
        "fail",
    }
    for key in (
        "weight_scheme_summary",
        "dimension_sensitivity_summary",
        "support_gap_sensitivity_summary",
        "research_question_candidates",
    ):
        assert prohibited.isdisjoint(audit[key].columns)
