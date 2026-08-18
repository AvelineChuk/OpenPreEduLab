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
- A public desktop keyboard review confirmed arrow-key navigation from
  Workflow to Inclusive Education, arrow-key tab switching into Researcher
  Mode, and keyboard operation of the readiness phase selector.
- Buttons, links, inputs, tabs, and other focusable controls now receive a
  three-pixel blue focus ring with a white separation ring. Sidebar radio
  labels and selectbox containers receive the same visible treatment when
  their nested input has keyboard focus.
- Code-level high-zoom guards now allow the landing hero title to wrap, scale
  large headings responsively, prevent metric and module cards from enforcing
  excess width, and contain preformatted content within a local scroll region.
- The in-app browser zoom shortcut was attempted, but its viewport remained at
  1280 pixels. These CSS protections and automated checks are therefore not
  presented as completed 200% browser evidence.
- The module heading hierarchy now begins with one page-level H1. Research
  pathway and research data are H2 sections, with tab content and method
  workflows nested beneath them.
- The three chart-alternative datasets now render as static semantic tables
  instead of interactive dataframe canvases. Researcher Mode retains
  interactive dataframes where sorting and exploration are part of the task.
- Researcher Mode now begins with a semantic navigation landmark linking seven
  major task areas: method map, core analysis, instrument foundations,
  longitudinal readiness, policy-design readiness, reproducibility and
  release, and Support Gap analysis. No workflow is hidden or presented as a
  required validation sequence.

- A plain-language research-task guide now states the relevant area, expected
  data or documentation, and interpretation boundary for six common research
  intentions. It reduces navigation burden without assigning readiness scores,
  prescribing methods, approving studies, or imposing a fixed sequence.

## Remaining Manual Checks

- Full keyboard-only traversal of every long Researcher Mode workflow and
  confirmation of focus order across all currently rendered controls.
- NVDA, Narrator, VoiceOver, or another screen-reader reading order.
- Physical browser zoom at 200% and confirmation of text reflow without
  horizontal loss on supported desktop browsers. This requires a browser
  surface whose zoom level can be changed and verified.
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
