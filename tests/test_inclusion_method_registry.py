"""Tests for the Inclusive Education methodological-readiness registry."""

import pytest

from models.inclusion_method_registry import (
    PHASE_ORDER,
    RESEARCH_TASK_ORDER,
    filter_method_readiness_catalog,
    method_readiness_catalog,
    research_task_guidance,
)


def test_catalog_is_ordered_complete_and_unique() -> None:
    """The navigator should expose every declared readiness workflow once."""
    catalog = method_readiness_catalog()
    assert len(catalog) == 25
    assert catalog["workflow"].is_unique
    assert tuple(catalog["phase"].drop_duplicates()) == PHASE_ORDER
    assert catalog.notna().all().all()


def test_phase_filter_preserves_declared_stage() -> None:
    """Filtering should not score, rank, or silently mix research phases."""
    for phase in PHASE_ORDER:
        filtered = filter_method_readiness_catalog(phase)
        assert not filtered.empty
        assert filtered["phase"].eq(phase).all()
    assert len(filter_method_readiness_catalog("All phases")) == 25


def test_unknown_phase_fails_closed() -> None:
    """Undeclared stages must not be silently accepted."""
    with pytest.raises(ValueError, match="Unknown methodological-readiness phase"):
        filter_method_readiness_catalog("Validated causal findings")


def test_catalog_retains_methodological_boundaries() -> None:
    """Every workflow must carry an explicit protocol and interpretation limit."""
    catalog = method_readiness_catalog()
    assert catalog["protocol_document"].str.endswith(".md").all()
    assert catalog["interpretation_boundary"].str.len().ge(20).all()
    combined = " ".join(catalog["interpretation_boundary"]).lower()
    assert "does not establish identification" in combined
    assert "no model, coefficient, p-value, or effect estimate" in combined
    assert "does not inspect, approve, upload, or publish files" in combined

def test_research_task_guide_covers_distinct_user_intents() -> None:
    """Each plain-language task should point to an area, inputs, and a boundary."""
    assert len(RESEARCH_TASK_ORDER) == 6
    assert len(set(RESEARCH_TASK_ORDER)) == len(RESEARCH_TASK_ORDER)
    for task in RESEARCH_TASK_ORDER:
        guidance = research_task_guidance(task)
        assert guidance["task"] == task
        assert guidance["relevant_area"]
        assert len(guidance["data_needed"]) >= 30
        assert len(guidance["boundary"]) >= 40


def test_unknown_research_task_fails_closed() -> None:
    """The guide must not invent advice for an undeclared research task."""
    with pytest.raises(ValueError, match="Unknown inclusive-education research task"):
        research_task_guidance("Diagnose a child")
