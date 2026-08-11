# Inclusive Education Accessibility Check

**Review status:** Automated and code-level prototype review completed; manual
screen-reader and multi-device review remains required.

## Scope

This check covers the Inclusive Education Dashboard, Researcher Mode,
exploratory scenarios, research insight, AI boundary, and export controls. It
does not certify conformance with WCAG or replace review by users with diverse
access needs.

## Checks Completed

- Every input control has a visible Streamlit label or help description.
- The institution upload notice prohibits identifiable child, family, teacher,
  clinical, and case data.
- The Policy → Resources → Practices → Participation → Equity pathway is
  available as text, not only as a chart.
- Five dimension values are displayed numerically in metric cards.
- Support Gap charts contain category labels, a zero reference, and numeric bar
  labels.
- Radar, pathway, and heatmap values are repeated in accessible data tables.
- The Dashboard states explicitly that interpretation does not depend on colour
  alone.
- Researcher Mode provides tables for descriptive statistics, correlations,
  equity indices, gaps, clusters, and institution comparisons.
- Cluster output uses neutral numbers and is accompanied by a non-ranking
  warning.
- AI output carries a visible professional-judgement and empirical-evidence
  warning.
- Export controls have visible format labels and preserve the research-use
  boundary.
- Streamlit AppTest verifies the route, boundary language, non-colour data
  alternative, and download controls.

## Remaining Manual Checks

- Keyboard-only navigation order and visible focus indicators.
- NVDA, Narrator, VoiceOver, or another screen-reader reading order.
- Browser zoom at 200% and text reflow without horizontal loss.
- Mobile and tablet layouts for charts, tabs, tables, and sidebar navigation.
- Contrast measurement for custom CSS, chart palettes, muted captions, and
  focus states.
- User review of plain-language explanations and cognitive load.

## Research and Ethical Boundary

Accessibility does not make the scores diagnostically or empirically valid.
The module remains an aggregate research prototype using synthetic data by
default. It must not assess children, determine disability status, infer
teacher quality, or treat Support Gap as a causal estimate.
