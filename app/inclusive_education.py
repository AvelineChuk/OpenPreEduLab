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
    calculate_dimension_sensitivity,
    cluster_institutions,
    correlation_matrix,
    descriptive_statistics,
    distributional_equity_report,
    generate_research_insights,
    inspect_inclusion_data,
    simulate_inclusion_scenarios,
    standardize_inclusion_data,
)
from models.inclusion_cognitive_interviews import (
    create_cognitive_interview_template,
    create_item_revision_log_template,
    load_cognitive_interview_csv,
    load_item_revision_log_csv,
    summarize_cognitive_interviews,
    summarize_item_revision_log,
)
from models.inclusion_construct_structure import (
    audit_construct_structure,
    create_construct_structure_template,
    load_construct_structure_csv,
)
from models.inclusion_feasibility import (
    audit_feasibility_pilot,
    create_feasibility_pilot_template,
    load_feasibility_pilot_csv,
)
from models.inclusion_reliability import (
    calculate_internal_consistency,
    calculate_repeated_administration_stability,
    create_reliability_audit_template,
    load_reliability_audit_csv,
)
from models.inclusion_versioning import (
    audit_instrument_version_comparability,
    create_instrument_version_registry_template,
    load_instrument_version_registry_csv,
)
from models.inclusion_content_validity import (
    calculate_content_validity_summaries,
    create_content_validity_review_template,
    load_content_validity_ratings_csv,
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
        st.caption(
            "All chart values are also available in the accessible tables below; "
            "the research interpretation does not depend on colour alone."
        )
        with st.expander("Accessible chart data tables"):
            pathway_table = pd.DataFrame(
                {
                    "pathway_stage": [DIMENSION_LABELS[column] for column in SCORE_COLUMNS],
                    "mean_score_0_100": [round(float(means[column]), 2) for column in SCORE_COLUMNS],
                }
            )
            gap_table = pd.DataFrame(
                {
                    "support_gap": [
                        "Resource → Practice",
                        "Practice → Participation",
                        "Overall Resource → Participation",
                    ],
                    "mean_signed_gap_points": [
                        round(float(gaps["gap_resource_practice"].mean()), 2),
                        round(float(gaps["gap_practice_participation"].mean()), 2),
                        round(float(gaps["overall_support_conversion_gap"].mean()), 2),
                    ],
                }
            )
            st.markdown("**Research pathway values**")
            st.dataframe(pathway_table, width="stretch", hide_index=True)
            st.markdown("**Support Gap values**")
            st.dataframe(gap_table, width="stretch", hide_index=True)
            st.markdown("**Institution-by-dimension values**")
            st.dataframe(
                scores.loc[:, ["institution_id", *SCORE_COLUMNS]],
                width="stretch",
                hide_index=True,
            )

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
        st.markdown("#### Dimension sensitivity")
        st.caption(
            "Leave-one-item-out analysis checks whether a dimension mean is highly "
            "dependent on one item. It does not validate the item or imply causality."
        )
        sensitivity = calculate_dimension_sensitivity(raw_data, source_min, source_max)
        st.dataframe(sensitivity, width="stretch", hide_index=True)
        st.download_button(
            "Download dimension sensitivity analysis",
            sensitivity.to_csv(index=False).encode("utf-8"),
            "inclusive_dimension_sensitivity.csv",
            "text/csv",
            key="inclusive_sensitivity_download",
        )
        st.markdown("#### Expert content-review materials")
        st.caption(
            "Prospective validation materials only. No expert ratings have been "
            "collected, and downloading this template does not validate the item set."
        )
        review_template = create_content_validity_review_template()
        with st.expander("Review template instructions"):
            st.markdown(
                "Duplicate the complete 28-item block for every eligible reviewer. "
                "Use relevance and clarity ratings 1–4; use essential, "
                "useful_not_essential, or not_necessary for essential_rating; and "
                "record qualitative comments, recommendations, roles, and conflicts. "
                "Do not enter identifiable child or family information."
            )
        st.download_button(
            "Download blank expert content-review template",
            review_template.to_csv(index=False).encode("utf-8-sig"),
            "inclusive_content_review_template.csv",
            "text/csv",
            key="inclusive_content_review_template_download",
        )
        completed_review_upload = st.file_uploader(
            "Upload completed expert content-review CSV",
            type=["csv"],
            key="inclusive_content_review_upload",
            help=(
                "Processed only in the current session. Use pseudonymous reviewer IDs "
                "and do not include child, family, or unnecessary personal information."
            ),
        )
        if completed_review_upload is not None:
            try:
                completed_ratings = load_content_validity_ratings_csv(completed_review_upload)
                validity_summaries = calculate_content_validity_summaries(completed_ratings)
            except ValueError as error:
                st.error(f"Expert content-review validation failed: {error}")
                st.info(
                    "Every reviewer must rate all 28 current items exactly once. "
                    "Missing ratings are not imputed and no automatic validity decision is made."
                )
            else:
                reviewer_count = completed_ratings["reviewer_id"].nunique()
                st.success(
                    f"Validated a complete matrix from {reviewer_count} declared reviewer(s)."
                )
                st.warning(
                    "These are descriptive content-review summaries, not proof that the "
                    "instrument is valid and not automatic retain/remove decisions."
                )
                st.markdown("**Item-level content-review summaries**")
                st.dataframe(
                    validity_summaries["item_summary"],
                    width="stretch",
                    hide_index=True,
                )
                st.markdown("**Dimension-level content-review summaries**")
                st.dataframe(
                    validity_summaries["dimension_summary"],
                    width="stretch",
                    hide_index=True,
                )
                st.download_button(
                    "Download item-level content-review summaries",
                    validity_summaries["item_summary"].to_csv(index=False).encode("utf-8-sig"),
                    "inclusive_content_review_item_summary.csv",
                    "text/csv",
                    key="inclusive_content_review_item_summary_download",
                )
                st.download_button(
                    "Download dimension-level content-review summaries",
                    validity_summaries["dimension_summary"].to_csv(index=False).encode("utf-8-sig"),
                    "inclusive_content_review_dimension_summary.csv",
                    "text/csv",
                    key="inclusive_content_review_dimension_summary_download",
                )
        st.markdown("#### Cognitive interview and item revision audit")
        st.caption(
            "Human-generated evidence only. The platform does not simulate interviews "
            "or infer retain, revise, move, split, or remove decisions."
        )
        with st.expander("Cognitive interview evidence workflow"):
            cognitive_template = create_cognitive_interview_template()
            st.markdown(
                "Record non-identifying observations for the items actually discussed. "
                "Partial item coverage is allowed and must remain visible in the coverage summary."
            )
            st.download_button(
                "Download cognitive interview record template",
                cognitive_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_cognitive_interview_template.csv",
                "text/csv",
                key="inclusive_cognitive_interview_template_download",
            )
            cognitive_upload = st.file_uploader(
                "Upload cognitive interview record CSV",
                type=["csv"],
                key="inclusive_cognitive_interview_upload",
                help="Session-only processing. Do not include names, contact details, or case records.",
            )
            if cognitive_upload is not None:
                try:
                    cognitive_records = load_cognitive_interview_csv(cognitive_upload)
                    cognitive_summaries = summarize_cognitive_interviews(cognitive_records)
                except ValueError as error:
                    st.error(f"Cognitive-interview validation failed: {error}")
                else:
                    st.warning(
                        "Issue counts describe recorded interview evidence. They are not item-validity "
                        "scores and do not determine revision decisions."
                    )
                    st.markdown("**Interview issue summary**")
                    st.dataframe(cognitive_summaries["issue_summary"], width="stretch", hide_index=True)
                    st.markdown("**Interview coverage summary**")
                    st.dataframe(cognitive_summaries["coverage_summary"], width="stretch", hide_index=True)
                    st.download_button(
                        "Download cognitive interview issue summary",
                        cognitive_summaries["issue_summary"].to_csv(index=False).encode("utf-8-sig"),
                        "inclusive_cognitive_interview_issue_summary.csv",
                        "text/csv",
                        key="inclusive_cognitive_issue_summary_download",
                    )
                    st.download_button(
                        "Download cognitive interview coverage summary",
                        cognitive_summaries["coverage_summary"].to_csv(index=False).encode("utf-8-sig"),
                        "inclusive_cognitive_interview_coverage_summary.csv",
                        "text/csv",
                        key="inclusive_cognitive_coverage_summary_download",
                    )
        with st.expander("Item revision decision audit workflow"):
            revision_template = create_item_revision_log_template()
            st.markdown(
                "Research teams must record explicit version transitions, rationale, minority views, "
                "and safeguarding and equity/accessibility review status."
            )
            st.download_button(
                "Download item revision log template",
                revision_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_item_revision_log_template.csv",
                "text/csv",
                key="inclusive_item_revision_template_download",
            )
            revision_upload = st.file_uploader(
                "Upload item revision decision CSV",
                type=["csv"],
                key="inclusive_item_revision_upload",
                help="Session-only processing. Decisions must be entered by the responsible research team.",
            )
            if revision_upload is not None:
                try:
                    revision_records = load_item_revision_log_csv(revision_upload)
                    revision_summary = summarize_item_revision_log(revision_records)
                except ValueError as error:
                    st.error(f"Item-revision validation failed: {error}")
                else:
                    st.warning(
                        "The summary reports human-entered decisions. The platform did not generate "
                        "or validate the substantive decision."
                    )
                    st.dataframe(revision_summary, width="stretch", hide_index=True)
                    st.download_button(
                        "Download item revision decision summary",
                        revision_summary.to_csv(index=False).encode("utf-8-sig"),
                        "inclusive_item_revision_decision_summary.csv",
                        "text/csv",
                        key="inclusive_item_revision_summary_download",
                    )
        st.markdown("#### Instrument version registry and comparability audit")
        st.caption(
            "Structural audit only. The platform never converts scores or assumes that "
            "two instrument versions are empirically comparable."
        )
        with st.expander("Instrument version and comparability workflow"):
            version_template = create_instrument_version_registry_template()
            st.markdown(
                "Register complete active-item snapshots for each version. Weights must sum "
                "to 1 within every version and dimension."
            )
            st.download_button(
                "Download instrument version registry template",
                version_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_instrument_version_registry_template.csv",
                "text/csv",
                key="inclusive_version_registry_template_download",
            )
            version_upload = st.file_uploader(
                "Upload instrument version registry CSV",
                type=["csv"],
                key="inclusive_version_registry_upload",
                help="Session-only structural metadata. Do not include institution or child records.",
            )
            if version_upload is not None:
                try:
                    version_registry = load_instrument_version_registry_csv(version_upload)
                except ValueError as error:
                    st.error(f"Instrument-version registry validation failed: {error}")
                else:
                    version_options = version_registry["instrument_version"].drop_duplicates().tolist()
                    st.success(
                        f"Validated {len(version_options)} registered instrument version(s)."
                    )
                    if len(version_options) < 2:
                        st.info("Register at least two versions to run a comparability audit.")
                    else:
                        version_columns = st.columns(2)
                        with version_columns[0]:
                            source_version = st.selectbox(
                                "Source instrument version",
                                version_options,
                                key="inclusive_source_instrument_version",
                            )
                        with version_columns[1]:
                            target_version = st.selectbox(
                                "Target instrument version",
                                version_options,
                                index=1,
                                key="inclusive_target_instrument_version",
                            )
                        if source_version == target_version:
                            st.error("Select two different instrument versions for the audit.")
                        else:
                            version_audit = audit_instrument_version_comparability(
                                version_registry,
                                source_version,
                                target_version,
                            )
                            st.warning(str(version_audit["interpretation"]))
                            st.dataframe(
                                version_audit["transition_summary"],
                                width="stretch",
                                hide_index=True,
                            )
                            st.markdown("**Dimension structure comparison**")
                            st.dataframe(
                                version_audit["dimension_summary"],
                                width="stretch",
                                hide_index=True,
                            )
                            st.markdown("**Shared-item structural changes**")
                            st.dataframe(
                                version_audit["item_change_summary"],
                                width="stretch",
                                hide_index=True,
                            )
                            st.download_button(
                                "Download version transition summary",
                                version_audit["transition_summary"].to_csv(index=False).encode("utf-8-sig"),
                                "inclusive_version_transition_summary.csv",
                                "text/csv",
                                key="inclusive_version_transition_summary_download",
                            )
                            st.download_button(
                                "Download dimension structure comparison",
                                version_audit["dimension_summary"].to_csv(index=False).encode("utf-8-sig"),
                                "inclusive_version_dimension_comparison.csv",
                                "text/csv",
                                key="inclusive_version_dimension_summary_download",
                            )
                            st.download_button(
                                "Download shared-item structural changes",
                                version_audit["item_change_summary"].to_csv(index=False).encode("utf-8-sig"),
                                "inclusive_version_item_changes.csv",
                                "text/csv",
                                key="inclusive_version_item_changes_download",
                            )
        st.markdown("#### Feasibility pilot and data-quality audit")
        st.caption(
            "Collection-process audit only. Missingness is preserved for analysis and is "
            "never imputed into five-dimension scores."
        )
        with st.expander("Feasibility pilot and data-quality workflow"):
            feasibility_template = create_feasibility_pilot_template()
            st.markdown(
                "Use one non-identifying administration record per institutional pilot. "
                "Do not include child, family, teacher, clinical, or case data."
            )
            st.download_button(
                "Download feasibility pilot template",
                feasibility_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_feasibility_pilot_template.csv",
                "text/csv",
                key="inclusive_feasibility_template_download",
            )
            feasibility_upload = st.file_uploader(
                "Upload feasibility pilot CSV",
                type=["csv"],
                key="inclusive_feasibility_upload",
                help="Session-only processing. Item missingness is retained, not imputed.",
            )
            feasibility_scale = st.selectbox(
                "Feasibility pilot response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_feasibility_scale",
            )
            if feasibility_scale == "0–100":
                feasibility_min, feasibility_max = 0.0, 100.0
            elif feasibility_scale == "0–1":
                feasibility_min, feasibility_max = 0.0, 1.0
            else:
                feasibility_scale_columns = st.columns(2)
                with feasibility_scale_columns[0]:
                    feasibility_min = float(
                        st.number_input(
                            "Feasibility scale minimum",
                            value=1.0,
                            key="inclusive_feasibility_min",
                        )
                    )
                with feasibility_scale_columns[1]:
                    feasibility_max = float(
                        st.number_input(
                            "Feasibility scale maximum",
                            value=5.0,
                            key="inclusive_feasibility_max",
                        )
                    )
            threshold_columns = st.columns(2)
            with threshold_columns[0]:
                endpoint_threshold = st.slider(
                    "Endpoint follow-up threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.15,
                    step=0.05,
                    key="inclusive_endpoint_threshold",
                )
            with threshold_columns[1]:
                missing_threshold = st.slider(
                    "Missingness follow-up threshold",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.10,
                    step=0.05,
                    key="inclusive_missing_threshold",
                )
            st.caption(
                "Thresholds are researcher-declared prototype flags, not psychometric "
                "standards and not automatic item-removal rules."
            )
            if feasibility_upload is not None:
                try:
                    feasibility_data = load_feasibility_pilot_csv(
                        feasibility_upload,
                        feasibility_min,
                        feasibility_max,
                    )
                    feasibility_audit = audit_feasibility_pilot(
                        feasibility_data,
                        feasibility_min,
                        feasibility_max,
                        endpoint_threshold,
                        missing_threshold,
                    )
                except ValueError as error:
                    st.error(f"Feasibility-pilot validation failed: {error}")
                else:
                    st.warning(str(feasibility_audit["interpretation"]))
                    st.markdown("**Administration summary**")
                    st.dataframe(
                        feasibility_audit["administration_summary"],
                        width="stretch",
                        hide_index=True,
                    )
                    st.markdown("**Item data-quality summary**")
                    st.dataframe(
                        feasibility_audit["item_quality_summary"],
                        width="stretch",
                        hide_index=True,
                    )
                    st.markdown("**Missing-item count distribution**")
                    st.dataframe(
                        feasibility_audit["missing_count_distribution"],
                        width="stretch",
                        hide_index=True,
                    )
                    st.markdown("**Administration-mode summary**")
                    st.dataframe(
                        feasibility_audit["administration_mode_summary"],
                        width="stretch",
                        hide_index=True,
                    )
                    for summary_key, file_name, label in (
                        ("administration_summary", "inclusive_feasibility_administration_summary.csv", "Download feasibility administration summary"),
                        ("item_quality_summary", "inclusive_feasibility_item_quality.csv", "Download feasibility item data-quality summary"),
                        ("missing_count_distribution", "inclusive_feasibility_missing_distribution.csv", "Download feasibility missing-count distribution"),
                        ("administration_mode_summary", "inclusive_feasibility_mode_summary.csv", "Download feasibility administration-mode summary"),
                    ):
                        st.download_button(
                            label,
                            feasibility_audit[summary_key].to_csv(index=False).encode("utf-8-sig"),
                            file_name,
                            "text/csv",
                            key=f"inclusive_{summary_key}_download",
                        )
        st.markdown("#### Preliminary reliability and repeated-administration audit")
        st.caption(
            "Reliability evidence only. Coefficients do not establish validity, "
            "unidimensionality, fairness, or cross-version comparability."
        )
        with st.expander("Reliability and repeated-administration workflow"):
            reliability_template = create_reliability_audit_template()
            st.download_button(
                "Download reliability audit template",
                reliability_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_reliability_audit_template.csv",
                "text/csv",
                key="inclusive_reliability_template_download",
            )
            reliability_upload = st.file_uploader(
                "Upload reliability audit CSV",
                type=["csv"],
                key="inclusive_reliability_upload",
                help=(
                    "Use complete, non-identifying institutional records. Missing item "
                    "responses are rejected and never imputed."
                ),
            )
            reliability_scale = st.selectbox(
                "Reliability audit response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_reliability_scale",
            )
            if reliability_scale == "0–100":
                reliability_min, reliability_max = 0.0, 100.0
            elif reliability_scale == "0–1":
                reliability_min, reliability_max = 0.0, 1.0
            else:
                reliability_scale_columns = st.columns(2)
                with reliability_scale_columns[0]:
                    reliability_min = float(
                        st.number_input(
                            "Reliability scale minimum",
                            value=1.0,
                            key="inclusive_reliability_min",
                        )
                    )
                with reliability_scale_columns[1]:
                    reliability_max = float(
                        st.number_input(
                            "Reliability scale maximum",
                            value=5.0,
                            key="inclusive_reliability_max",
                        )
                    )
            if reliability_upload is not None:
                try:
                    reliability_data = load_reliability_audit_csv(
                        reliability_upload,
                        reliability_min,
                        reliability_max,
                    )
                    internal_consistency = calculate_internal_consistency(
                        reliability_data,
                        reliability_min,
                        reliability_max,
                    )
                except ValueError as error:
                    st.error(f"Reliability-audit validation failed: {error}")
                else:
                    st.warning(str(internal_consistency["interpretation"]))
                    st.markdown("**Dimension internal-consistency summary**")
                    st.dataframe(
                        internal_consistency["dimension_summary"],
                        width="stretch",
                        hide_index=True,
                    )
                    st.markdown("**Item internal-consistency diagnostics**")
                    st.dataframe(
                        internal_consistency["item_summary"],
                        width="stretch",
                        hide_index=True,
                    )
                    st.download_button(
                        "Download dimension internal-consistency summary",
                        internal_consistency["dimension_summary"].to_csv(index=False).encode("utf-8-sig"),
                        "inclusive_internal_consistency_dimensions.csv",
                        "text/csv",
                        key="inclusive_internal_consistency_dimension_download",
                    )
                    st.download_button(
                        "Download item internal-consistency diagnostics",
                        internal_consistency["item_summary"].to_csv(index=False).encode("utf-8-sig"),
                        "inclusive_internal_consistency_items.csv",
                        "text/csv",
                        key="inclusive_internal_consistency_item_download",
                    )
                    reliability_versions = (
                        reliability_data["instrument_version"].drop_duplicates().tolist()
                    )
                    selected_reliability_version = st.selectbox(
                        "Version for repeated-administration audit",
                        reliability_versions,
                        key="inclusive_reliability_version",
                    )
                    version_rounds = sorted(
                        reliability_data.loc[
                            reliability_data["instrument_version"].eq(
                                selected_reliability_version
                            ),
                            "administration_round",
                        ].unique()
                    )
                    if len(version_rounds) < 2:
                        st.info(
                            "At least two rounds within one version are required for a "
                            "repeated-administration audit."
                        )
                    else:
                        round_columns = st.columns(2)
                        with round_columns[0]:
                            first_reliability_round = st.selectbox(
                                "First administration round",
                                version_rounds,
                                key="inclusive_first_reliability_round",
                            )
                        with round_columns[1]:
                            second_reliability_round = st.selectbox(
                                "Second administration round",
                                version_rounds,
                                index=1,
                                key="inclusive_second_reliability_round",
                            )
                        if first_reliability_round == second_reliability_round:
                            st.error("Select two different rounds for stability analysis.")
                        else:
                            try:
                                stability = calculate_repeated_administration_stability(
                                    reliability_data,
                                    selected_reliability_version,
                                    int(first_reliability_round),
                                    int(second_reliability_round),
                                    reliability_min,
                                    reliability_max,
                                )
                            except ValueError as error:
                                st.error(f"Repeated-administration audit failed: {error}")
                            else:
                                st.warning(str(stability["interpretation"]))
                                st.dataframe(
                                    stability["matching_coverage_summary"],
                                    width="stretch",
                                    hide_index=True,
                                )
                                st.dataframe(
                                    stability["dimension_stability_summary"],
                                    width="stretch",
                                    hide_index=True,
                                )
                                st.download_button(
                                    "Download repeated-administration coverage summary",
                                    stability["matching_coverage_summary"].to_csv(index=False).encode("utf-8-sig"),
                                    "inclusive_repeated_administration_coverage.csv",
                                    "text/csv",
                                    key="inclusive_reliability_coverage_download",
                                )
                                st.download_button(
                                    "Download repeated-administration stability summary",
                                    stability["dimension_stability_summary"].to_csv(index=False).encode("utf-8-sig"),
                                    "inclusive_repeated_administration_stability.csv",
                                    "text/csv",
                                    key="inclusive_reliability_stability_download",
                                )
        st.markdown("#### Construct structure readiness and exploratory components audit")
        st.caption(
            "Exploratory structural evidence only. This workflow is not confirmatory "
            "factor analysis and does not validate the five-dimension structure."
        )
        with st.expander("Construct structure readiness and exploratory components workflow"):
            construct_template = create_construct_structure_template()
            st.download_button(
                "Download construct structure audit template",
                construct_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_construct_structure_audit_template.csv",
                "text/csv",
                key="inclusive_construct_structure_template_download",
            )
            construct_upload = st.file_uploader(
                "Upload construct structure audit CSV",
                type=["csv"],
                key="inclusive_construct_structure_upload",
                help=(
                    "Use complete, non-identifying records. Analysis is restricted to one "
                    "explicitly selected instrument version and administration round."
                ),
            )
            construct_scale = st.selectbox(
                "Construct structure audit response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_construct_structure_scale",
            )
            if construct_scale == "0–100":
                construct_min, construct_max = 0.0, 100.0
            elif construct_scale == "0–1":
                construct_min, construct_max = 0.0, 1.0
            else:
                construct_scale_columns = st.columns(2)
                with construct_scale_columns[0]:
                    construct_min = float(
                        st.number_input(
                            "Construct structure scale minimum",
                            value=1.0,
                            key="inclusive_construct_structure_min",
                        )
                    )
                with construct_scale_columns[1]:
                    construct_max = float(
                        st.number_input(
                            "Construct structure scale maximum",
                            value=5.0,
                            key="inclusive_construct_structure_max",
                        )
                    )
            if construct_upload is not None:
                try:
                    construct_data = load_construct_structure_csv(
                        construct_upload,
                        construct_min,
                        construct_max,
                    )
                except ValueError as error:
                    st.error(f"Construct-structure validation failed: {error}")
                else:
                    construct_versions = construct_data["instrument_version"].drop_duplicates().tolist()
                    selected_construct_version = st.selectbox(
                        "Version for construct structure audit",
                        construct_versions,
                        key="inclusive_construct_structure_version",
                    )
                    construct_rounds = sorted(
                        construct_data.loc[
                            construct_data["instrument_version"].eq(selected_construct_version),
                            "administration_round",
                        ].unique()
                    )
                    selected_construct_round = st.selectbox(
                        "Administration round for construct structure audit",
                        construct_rounds,
                        key="inclusive_construct_structure_round",
                    )
                    construct_component_count = st.number_input(
                        "Exploratory principal component count",
                        min_value=1,
                        max_value=len(ITEM_COLUMNS),
                        value=min(5, len(ITEM_COLUMNS)),
                        step=1,
                        key="inclusive_construct_structure_components",
                        help="Researcher-selected. The software does not determine the factor count.",
                    )
                    try:
                        construct_audit = audit_construct_structure(
                            construct_data,
                            selected_construct_version,
                            int(selected_construct_round),
                            int(construct_component_count),
                            construct_min,
                            construct_max,
                        )
                    except ValueError as error:
                        st.error(f"Construct-structure audit failed: {error}")
                    else:
                        st.warning(str(construct_audit["interpretation"]))
                        for title, summary_key in (
                            ("Readiness and Bartlett summary", "readiness_summary"),
                            ("Item-level KMO and variance", "item_kmo_summary"),
                            ("Item correlation matrix", "correlation_matrix"),
                            ("Correlation-matrix eigenvalues", "eigenvalue_summary"),
                            ("Unrotated principal-component loadings", "component_loading_summary"),
                        ):
                            st.markdown(f"**{title}**")
                            st.dataframe(construct_audit[summary_key], width="stretch")
                        for label, summary_key, file_name in (
                            ("Download construct readiness summary", "readiness_summary", "inclusive_construct_readiness.csv"),
                            ("Download item KMO summary", "item_kmo_summary", "inclusive_construct_item_kmo.csv"),
                            ("Download item correlation matrix", "correlation_matrix", "inclusive_construct_correlations.csv"),
                            ("Download eigenvalue summary", "eigenvalue_summary", "inclusive_construct_eigenvalues.csv"),
                            ("Download exploratory component loadings", "component_loading_summary", "inclusive_construct_component_loadings.csv"),
                        ):
                            st.download_button(
                                label,
                                construct_audit[summary_key].to_csv(index=False).encode("utf-8-sig"),
                                file_name,
                                "text/csv",
                                key=f"inclusive_{summary_key}_download",
                            )
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
