"""Tests for portable research-report exports."""

from reporting.exports import report_to_docx, report_to_pdf


SAMPLE_REPORT = """# OpenPreEduLab Research Run Summary

## Scope

- Observations: 50 city-year records

## Research-use note

This summary is a computational run, not a policy conclusion.
"""


def test_docx_export_is_a_valid_office_container() -> None:
    """Word export should generate an OOXML zip container."""
    document = report_to_docx(SAMPLE_REPORT)
    assert document.startswith(b"PK")
    assert len(document) > 1000


def test_pdf_export_is_a_valid_pdf_document() -> None:
    """PDF export should generate a non-empty PDF payload."""
    document = report_to_pdf(SAMPLE_REPORT)
    assert document.startswith(b"%PDF")
    assert len(document) > 1000
