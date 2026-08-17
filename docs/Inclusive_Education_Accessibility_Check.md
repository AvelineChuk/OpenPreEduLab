# Inclusive Education Accessibility Check

**Review status:** Automated, code-level, and public desktop-browser prototype
review completed; manual screen-reader and physical multi-device review
remains required.

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
- A public desktop-browser review at a 1280-pixel viewport confirmed that the
  sidebar, Methodological Readiness Navigator, phase selector, and catalog
  download control render without application errors or page-level horizontal
  overflow. Data tables retain small internal scroll regions rather than
  widening the full page.
- Narrow-screen CSS now keeps the sidebar recovery control visible, constrains
  the sidebar to the available viewport, gives buttons a 44-pixel minimum
  target height, and provides local horizontal overflow for tabs, tables, and
  charts. An AppTest regression guard verifies that these rules remain present.
- Key dashboard small-text colours were measured against their declared light
  backgrounds. Dashboard subtitles and module descriptions now use #5f6e82,
  which exceeds the 4.5:1 reference against white; an automated regression
  test preserves this minimum.
- Dimension heatmap labels now select light or dark text from the actual cell
  colour instead of using a fixed score threshold. Tests cover both the light
  and dark ends of the heatmap scale.

## Remaining Manual Checks

- Keyboard-only navigation order and visible focus indicators.
- NVDA, Narrator, VoiceOver, or another screen-reader reading order.
- Browser zoom at 200% and text reflow without horizontal loss on supported
  desktop browsers.
- Physical mobile and tablet interaction review for charts, tabs, tables, and
  sidebar navigation. The current in-app browser remained fixed at 1280 pixels,
  so the CSS and automated guard are not presented as real-device evidence.
- Browser-assisted contrast review remains required for third-party Streamlit
  widgets, interactive focus states, disabled controls, and image overlays.
- User review of plain-language explanations and cognitive load.

## Research and Ethical Boundary

Accessibility does not make the scores diagnostically or empirically valid.
The module remains an aggregate research prototype using synthetic data by
default. It must not assess children, determine disability status, infer
teacher quality, or treat Support Gap as a causal estimate.
