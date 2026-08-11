"""Streamlit interface for the Inclusive Education Research Module."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from llm.deepseek import DeepSeekClient, DeepSeekRequestError, SUPPORTED_MODELS
from llm.inclusion_prompts import create_inclusion_interpretation_request
from models.inclusion import (
    DIMENSION_ITEMS,
    DIMENSION_LABELS,
    ITEM_COLUMNS,
    SCORE_COLUMNS,
    calculate_inclusion_dimension_scores,
    cluster_institutions,
    correlation_matrix,
    descriptive_statistics,
    distributional_equity_report,
    generate_research_insights,
    inspect_inclusion_data,
    simulate_inclusion_scenarios,
    standardize_inclusion_data,
)
from models.support_gap import calculate_support_gaps
from reporting.exports import report_to_docx, report_to_pdf
from visualization.inclusion_charts import (
    plot_dimension_heatmap,
    plot_five_dimension_radar,
    plot_institution_comparison,
    plot_support_gap_bars,
    plot_support_pathway,
)


def _score_card(label: str, value: float, note: str) -> str:
    """Return a score card using the platform's existing CSS language."""
    return (
        "<div class='metric-card'><div class='metric-label'>"
        f"{label}</div><div class='metric-value'>{value:.1f}</div>"
        f"<div class='metric-note'>{note}</div></div>"
    )


def _build_report(
    data: pd.DataFrame,
    scores: pd.DataFrame,
    gaps: pd.DataFrame,
    insights: dict[str, object],
    source_label: str,
    scale_note: str,
) -> str:
    """Build a bounded Markdown research summary for export."""
    means = scores[list(SCORE_COLUMNS)].mean()
    gap_means = gaps[
        ["gap_resource_practice", "gap_practice_participation", "overall_support_conversion_gap"]
    ].mean()
    questions = "\n".join(
        f"- {question}" for question in insights["research_question_candidates"]
    )
    return f"""# OpenPreEduLab Inclusive Education Research Summary

## Scope

- Data source: {source_label}
- Institutions: {len(data)}
- Scale handling: {scale_note}
- Scoring: equal item weights within each prototype dimension

## Five-dimension descriptive profile

- Policy Support Score: {means['policy_support_score']:.2f}
- Resource Support Score: {means['resource_support_score']:.2f}
- Inclusive Practice Score: {means['inclusive_practice_score']:.2f}
- Child Participation Score: {means['child_participation_score']:.2f}
- Equity Score: {means['equity_score']:.2f}

## Support Gap

- Resource → Practice: {gap_means['gap_resource_practice']:.2f}
- Practice → Participation: {gap_means['gap_practice_participation']:.2f}
- Overall Support Conversion Gap: {gap_means['overall_support_conversion_gap']:.2f}
- Major descriptive gap: {insights['major_gap']['label']}

## Research Insight

{insights['insight']}

Possible interpretation: {insights['major_gap']['interpretation']}

## Research Question Candidates

{questions}

## Research-use boundary

This module is designed for educational research and policy analysis. It is not
a diagnostic tool for children, does not determine disability status, and does
not replace professional judgement. Child Participation concerns meaningful
participation rather than child ability. Support Gap is a descriptive diagnostic
indicator, not a causal estimator. Synthetic data are for demonstration and
testing only. All hypotheses and research-question candidates require empirical
and professional review.
"""


def _load_page_data(project_root: Path) -> tuple[pd.DataFrame | None, str, float, float, str]:
    """Render safe data-source controls and return raw data plus scale metadata."""
    sample_path = project_root / "datasets" / "sample_inclusive_data.csv"
    template_path = project_root / "datasets" / "templates" / "inclusive_research_input_template.csv"
    st.markdown("### Research data")
    st.caption(
        "Use synthetic demonstration data or a non-identifying institution-level CSV. "
        "Do not upload child, family, clinical, or identifiable case records."
    )
    source = st.radio(
        "Inclusive research input",
        ["Synthetic demonstration data", "Upload institution-level CSV"],
        horizontal=True,
        key="inclusive_source",
    )
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download synthetic inclusive dataset",
            sample_path.read_bytes(),
            "sample_inclusive_data.csv",
            "text/csv",
            key="inclusive_sample_download",
        )
    with right:
        st.download_button(
            "Download inclusive input template",
            template_path.read_bytes(),
            "inclusive_research_input_template.csv",
            "text/csv",
            key="inclusive_template_download",
        )

    if source == "Synthetic demonstration data":
        return pd.read_csv(sample_path), source, 0.0, 100.0, "Already on the documented 0–100 scale"

    upload = st.file_uploader(
        "Upload inclusive education research CSV",
        type=["csv"],
        key="inclusive_csv_upload",
        help="Files are processed in the current session and are not written to the repository.",
    )
    scale = st.selectbox(
        "Declared source scale",
        ["0–100", "0–1", "Custom range"],
        key="inclusive_scale",
        help="The platform does not guess an instrument scale. Select the documented source range.",
    )
    if scale == "0–100":
        source_min, source_max = 0.0, 100.0
    elif scale == "0–1":
        source_min, source_max = 0.0, 1.0
    else:
        scale_columns = st.columns(2)
        with scale_columns[0]:
            source_min = float(st.number_input("Source minimum", value=1.0, key="inclusive_scale_min"))
        with scale_columns[1]:
            source_max = float(st.number_input("Source maximum", value=5.0, key="inclusive_scale_max"))
    if upload is None:
        st.info("Upload a CSV to start Researcher Mode, or use the synthetic demonstration dataset.")
        return None, source, source_min, source_max, f"Declared source range [{source_min}, {source_max}]"
    try:
        data = pd.read_csv(upload)
    except (OSError, UnicodeDecodeError, pd.errors.ParserError) as error:
        st.error(f"CSV reading failed: {error}")
        return None, source, source_min, source_max, f"Declared source range [{source_min}, {source_max}]"
    return data, source, source_min, source_max, f"Linearly converted from [{source_min}, {source_max}] to [0, 100]"


def render_inclusive_education_page(project_root: Path) -> None:
    """Render the complete non-diagnostic inclusive education research module."""
    st.markdown(
        "<div class='eyebrow'>INCLUSIVE EDUCATION</div>"
        "<h2>From Resources to Participation.</h2>"
        "<p class='section-copy'>An open research infrastructure for studying how policy and institutional support may be reflected in inclusive practices, meaningful child participation, and educational equity. The pathway is conceptual and has not been validated as a causal model.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='quiet-note'><b>Research boundary:</b> This module is not a child assessment, diagnostic, disability-determination, placement, clinical, or teacher-rating tool. Participation is not child ability. Institution-level scores are research-prototype summaries.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("### Research pathway")
    st.markdown("**Policy → Resources → Practices → Child Participation → Equity**")

    raw_data, source_label, source_min, source_max, scale_note = _load_page_data(project_root)
    if raw_data is None:
        return
    with st.expander("Inspect uploaded variables and missing-value check"):
        st.dataframe(inspect_inclusion_data(raw_data), width="stretch", hide_index=True)
        st.dataframe(raw_data.head(20), width="stretch", hide_index=True)

    try:
        standardised = standardize_inclusion_data(raw_data, source_min, source_max)
        scores = calculate_inclusion_dimension_scores(raw_data, source_min, source_max)
        gaps = calculate_support_gaps(scores)
        insights = generate_research_insights(scores, gaps)
    except ValueError as error:
        st.error(f"Inclusive data validation failed: {error}")
        st.info(
            "Required items must be present, numeric, complete, unique by institution_id, "
            "and inside the declared source scale. Missing values are not automatically imputed."
        )
        return

    overview, researcher, scenarios_tab, interpretation = st.tabs(
        ["Dashboard", "Researcher Mode", "Exploratory Scenarios", "Research Insight & Export"]
    )

    with overview:
        means = scores[list(SCORE_COLUMNS)].mean()
        cards = st.columns(5)
        for column, score_name in zip(cards, SCORE_COLUMNS):
            with column:
                st.markdown(
                    _score_card(DIMENSION_LABELS[score_name], means[score_name], "sample mean · prototype"),
                    unsafe_allow_html=True,
                )
        st.caption("Equal item weighting is an explicit prototype assumption requiring future validation.")
        pathway_figure, pathway_axis = plt.subplots(figsize=(11, 4.8))
        plot_support_pathway(scores, ax=pathway_axis)
        st.pyplot(pathway_figure, clear_figure=True)
        left, right = st.columns(2, gap="large")
        with left:
            radar_figure, radar_axis = plt.subplots(figsize=(6.5, 6.5), subplot_kw={"projection": "polar"})
            plot_five_dimension_radar(scores, ax=radar_axis)
            st.pyplot(radar_figure, clear_figure=True)
        with right:
            gap_figure, gap_axis = plt.subplots(figsize=(7, 4.8))
            plot_support_gap_bars(gaps, ax=gap_axis)
            st.pyplot(gap_figure, clear_figure=True)
            major = insights["major_gap"]
            st.markdown(f"**Major Support Gap:** {major['label']} ({major['value']:.1f})")
            st.info(f"Possible interpretation — hypothesis for further investigation: {major['interpretation']}")
        heatmap_figure, heatmap_axis = plt.subplots(figsize=(10, max(5, 0.45 * len(scores))))
        plot_dimension_heatmap(scores, ax=heatmap_axis)
        st.pyplot(heatmap_figure, clear_figure=True)

    with researcher:
        st.markdown("### Researcher Mode")
        st.caption("Select variables and methods. Outputs are descriptive and model-dependent.")
        dimension_selection = st.multiselect(
            "Select dimensions",
            list(SCORE_COLUMNS),
            default=list(SCORE_COLUMNS),
            format_func=lambda value: DIMENSION_LABELS[value],
            key="inclusive_dimensions",
        )
        analysis_data = standardised.merge(scores, on=["institution_id", "institution_type", "region"], validate="one_to_one")
        available_variables = list(ITEM_COLUMNS) + list(SCORE_COLUMNS)
        selected_variables = st.multiselect(
            "Select variables",
            available_variables,
            default=list(dimension_selection) if dimension_selection else list(SCORE_COLUMNS),
            key="inclusive_variables",
        )
        if selected_variables:
            st.markdown("#### Descriptive statistics")
            st.dataframe(descriptive_statistics(analysis_data, selected_variables), width="stretch", hide_index=True)
        if len(selected_variables) >= 2:
            st.markdown("#### Correlation — descriptive association only")
            st.dataframe(correlation_matrix(analysis_data, selected_variables), width="stretch")
        st.markdown("#### Equity analysis")
        equity_dimension = st.selectbox(
            "Dimension for cross-institution inequality",
            list(SCORE_COLUMNS),
            format_func=lambda value: DIMENSION_LABELS[value],
            key="inclusive_equity_dimension",
        )
        st.dataframe(distributional_equity_report(scores, equity_dimension), width="stretch", hide_index=True)
        st.caption("Lower inequality does not establish adequate support; distribution and level must be interpreted together.")
        st.markdown("#### Gap analysis")
        st.dataframe(scores.merge(gaps, on=["institution_id", "institution_type", "region"], validate="one_to_one"), width="stretch", hide_index=True)
        comparison_ids = st.multiselect(
            "Institutions for comparison",
            scores["institution_id"].tolist(),
            default=scores["institution_id"].tolist()[:4],
            key="inclusive_comparison_ids",
        )
        if comparison_ids:
            comparison_figure, comparison_axis = plt.subplots(figsize=(10, max(4.8, len(comparison_ids) * 0.6)))
            plot_institution_comparison(scores, comparison_ids, ax=comparison_axis)
            st.pyplot(comparison_figure, clear_figure=True)
        run_cluster = st.checkbox("Run exploratory cluster analysis", key="inclusive_cluster")
        if run_cluster:
            cluster_count = st.slider("Number of clusters", 2, min(5, len(scores) - 1), 3, key="inclusive_cluster_count")
            cluster_result = cluster_institutions(
                scores,
                score_columns=dimension_selection or SCORE_COLUMNS,
                n_clusters=cluster_count,
            )
            st.dataframe(cluster_result, width="stretch", hide_index=True)
            st.warning("Cluster numbers are neutral exploratory pattern identifiers, not institution quality labels or validated types.")

    with scenarios_tab:
        st.markdown("### Exploratory Scenario Simulation")
        st.caption("Not causal prediction. Each scenario changes one selected item while holding all other reported values fixed.")
        change_points = st.slider("Illustrative item increase (0–100 scale points)", 0, 25, 10, 1, key="inclusive_scenario_change")
        scenario_results = simulate_inclusion_scenarios(standardised, float(change_points))
        st.dataframe(scenario_results, width="stretch", hide_index=True)
        st.bar_chart(
            scenario_results.set_index("scenario")[["resource_support_score", "inclusive_practice_score", "child_participation_score"]]
        )
        st.download_button(
            "Download exploratory scenario comparison",
            scenario_results.to_csv(index=False).encode("utf-8"),
            "inclusive_scenario_comparison.csv",
            "text/csv",
            key="inclusive_scenario_download",
        )

    with interpretation:
        st.markdown("### Research Insight")
        st.write(insights["insight"])
        st.markdown("### Research Question Candidates")
        for question in insights["research_question_candidates"]:
            st.markdown(f"- {question}")
        st.caption("Research questions and hypotheses are candidates for investigation, not validated conclusions.")

        model_results = {
            "dimension_means": insights["score_means"],
            "support_gap_means": insights["gap_means"],
            "major_gap": insights["major_gap"],
            "research_question_candidates": insights["research_question_candidates"],
            "data_status": "Synthetic demonstration data" if source_label == "Synthetic demonstration data" else "User-provided aggregate institution-level data",
        }
        context = st.text_area(
            "Inclusive education research context (optional)",
            placeholder="State the research question, institutional scope, instrument, and interpretation limits.",
            key="inclusive_research_context",
        )
        request = create_inclusion_interpretation_request(model_results, context)
        with st.expander("Preview bounded AI interpretation request"):
            st.markdown("**System prompt**")
            st.code(request.system_prompt, language="text")
            st.markdown("**User prompt**")
            st.code(request.user_prompt, language="markdown")
        request_record = f"# Inclusive Education AI Interpretation Request\n\n## System Prompt\n\n{request.system_prompt}\n\n## User Prompt\n\n{request.user_prompt}\n"
        st.download_button(
            "Download reviewed AI interpretation request",
            request_record.encode("utf-8"),
            "inclusive_ai_interpretation_request.md",
            "text/markdown",
            key="inclusive_request_download",
        )

        with st.form("inclusive_deepseek_form", clear_on_submit=True):
            model = st.selectbox("DeepSeek model", SUPPORTED_MODELS, key="inclusive_deepseek_model")
            api_key = st.text_input("Your DeepSeek API key", type="password", key="inclusive_deepseek_key")
            consent = st.checkbox(
                "I understand that the reviewed aggregate prompt will be sent to DeepSeek.",
                key="inclusive_deepseek_consent",
            )
            submitted = st.form_submit_button("Generate inclusive research interpretation")
        if submitted:
            if not api_key.strip():
                st.error("Enter your own DeepSeek API key.")
            elif not consent:
                st.error("Confirm the external-data transmission notice.")
            else:
                try:
                    response = DeepSeekClient(api_key, model=model).generate(
                        request.system_prompt, request.user_prompt
                    )
                    st.session_state["inclusive_ai_response"] = response
                    st.session_state["inclusive_ai_model"] = model
                except (ValueError, DeepSeekRequestError) as error:
                    st.error(str(error))
        response = st.session_state.get("inclusive_ai_response")
        if response:
            st.warning("AI-generated interpretation. Please verify with professional judgment and empirical evidence.")
            st.markdown(response)
            ai_record = f"""# OpenPreEduLab Inclusive Education AI Interpretation Record

Provider: DeepSeek
Model: {st.session_state.get('inclusive_ai_model', 'unknown')}

## System Prompt

{request.system_prompt}

## User Prompt

{request.user_prompt}

## Generated Draft

{response}

## Researcher-review boundary

This AI-generated draft is not a child diagnosis, disability determination,
teacher evaluation, causal finding, or validated research conclusion. Verify it
with professional judgement and empirical evidence. The API key is not included.
"""
            ai_format = st.selectbox(
                "Inclusive AI interpretation record format",
                ["Markdown (.md)", "Word document (.docx)", "PDF document (.pdf)"],
                key="inclusive_ai_record_format",
            )
            if ai_format == "Markdown (.md)":
                ai_payload, ai_filename, ai_mime = ai_record.encode("utf-8"), "inclusive_ai_interpretation_record.md", "text/markdown"
            elif ai_format == "Word document (.docx)":
                ai_payload, ai_filename, ai_mime = report_to_docx(ai_record), "inclusive_ai_interpretation_record.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                ai_payload, ai_filename, ai_mime = report_to_pdf(ai_record), "inclusive_ai_interpretation_record.pdf", "application/pdf"
            st.download_button(
                f"Download inclusive AI interpretation record ({ai_format})",
                ai_payload,
                ai_filename,
                ai_mime,
                key="inclusive_ai_record_download",
            )

        report = _build_report(raw_data, scores, gaps, insights, source_label, scale_note)
        st.markdown("### Download / Export")
        export_format = st.selectbox(
            "Inclusive research summary format",
            ["Markdown (.md)", "Word document (.docx)", "PDF document (.pdf)"],
            key="inclusive_export_format",
        )
        if export_format == "Markdown (.md)":
            payload, filename, mime = report.encode("utf-8"), "inclusive_research_summary.md", "text/markdown"
        elif export_format == "Word document (.docx)":
            payload, filename, mime = report_to_docx(report), "inclusive_research_summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        else:
            payload, filename, mime = report_to_pdf(report), "inclusive_research_summary.pdf", "application/pdf"
        st.download_button(
            f"Download inclusive research summary ({export_format})",
            payload,
            filename,
            mime,
            key="inclusive_summary_download",
        )
        combined = scores.merge(gaps, on=["institution_id", "institution_type", "region"], validate="one_to_one")
        st.download_button(
            "Download institution scores and support gaps",
            combined.to_csv(index=False).encode("utf-8"),
            "inclusive_scores_and_support_gaps.csv",
            "text/csv",
            key="inclusive_scores_download",
        )
