"""Export bounded research summaries to Markdown, DOCX, and PDF."""

from __future__ import annotations

from io import BytesIO
from typing import Iterator
import html


def _markdown_blocks(markdown: str) -> Iterator[tuple[str, str]]:
    """Yield simple heading, bullet, and paragraph blocks from report Markdown."""
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            yield "title", line[2:].strip()
        elif line.startswith("## "):
            yield "heading", line[3:].strip()
        elif line.startswith("- "):
            yield "bullet", line[2:].strip()
        else:
            yield "paragraph", line


def report_to_docx(markdown: str) -> bytes:
    """Return a Word document containing the supplied research report."""
    try:
        from docx import Document
        from docx.shared import Pt
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("DOCX export is unavailable because python-docx is not installed.") from error

    document = Document()
    document.styles["Normal"].font.name = "Aptos"
    document.styles["Normal"].font.size = Pt(10.5)
    for kind, text in _markdown_blocks(markdown):
        if kind == "title":
            document.add_heading(text, level=0)
        elif kind == "heading":
            document.add_heading(text, level=1)
        elif kind == "bullet":
            document.add_paragraph(text, style="List Bullet")
        else:
            document.add_paragraph(text)
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def report_to_pdf(markdown: str) -> bytes:
    """Return a readable PDF containing the supplied research report."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("PDF export is unavailable because reportlab is not installed.") from error

    font_name = "STSong-Light"
    try:
        pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    except (KeyError, TypeError):
        font_name = "Helvetica"
    styles = getSampleStyleSheet()
    body = ParagraphStyle("OpenPreEduLabBody", parent=styles["BodyText"], fontName=font_name, fontSize=10, leading=15, spaceAfter=7)
    title = ParagraphStyle("OpenPreEduLabTitle", parent=styles["Title"], fontName=font_name, fontSize=20, leading=26, spaceAfter=18)
    heading = ParagraphStyle("OpenPreEduLabHeading", parent=styles["Heading2"], fontName=font_name, fontSize=13, leading=18, spaceBefore=10, spaceAfter=7)
    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    story = []
    for kind, text in _markdown_blocks(markdown):
        safe_text = html.escape(text)
        if kind == "title":
            story.append(Paragraph(safe_text, title))
        elif kind == "heading":
            story.append(Paragraph(safe_text, heading))
        elif kind == "bullet":
            story.append(Paragraph(f"• {safe_text}", body))
        else:
            story.append(Paragraph(safe_text, body))
    story.append(Spacer(1, 0.1 * cm))
    document.build(story)
    return output.getvalue()
