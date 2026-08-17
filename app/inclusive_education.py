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
from models.inclusion_attrition import audit_longitudinal_attrition
from models.inclusion_bootstrap import audit_bootstrap_uncertainty
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
from models.inclusion_external_measure import (
    audit_external_measure_relationships,
    create_external_measure_template,
    load_external_measure_csv,
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
from models.inclusion_longitudinal import audit_longitudinal_panel_readiness
from models.inclusion_longitudinal_bootstrap import (
    audit_paired_longitudinal_bootstrap,
)
from models.inclusion_longitudinal_metadata import (
    audit_longitudinal_metadata,
    create_longitudinal_metadata_template,
    load_longitudinal_metadata_csv,
)
from models.inclusion_longitudinal_comparability import (
    audit_longitudinal_comparability,
)
from models.inclusion_longitudinal_plan import (
    audit_longitudinal_plan,
    create_longitudinal_plan_template,
    load_longitudinal_plan_csv,
)
from models.inclusion_longitudinal_events import (
    audit_longitudinal_event_alignment,
    create_longitudinal_event_template,
    load_longitudinal_event_csv,
)
from models.inclusion_event_exposure import (
    audit_event_exposure_definitions,
    create_event_exposure_template,
    load_event_exposure_csv,
)
from models.inclusion_identification_design import (
    audit_identification_design,
    create_identification_design_template,
    load_identification_design_csv,
)
from models.inclusion_falsification_plan import (
    audit_falsification_plan,
    create_falsification_plan_template,
    load_falsification_plan_csv,
)
from models.inclusion_estimation_specification import (
    audit_estimation_specification,
    create_estimation_specification_template,
    load_estimation_specification_csv,
)
from models.inclusion_analysis_reproducibility import (
    audit_analysis_reproducibility,
    create_analysis_reproducibility_template,
    load_analysis_reproducibility_csv,
)
from models.inclusion_results_reporting import (
    audit_results_reporting,
    create_results_reporting_template,
    load_results_reporting_csv,
)
from models.inclusion_claim_traceability import (
    audit_claim_traceability,
    create_claim_traceability_template,
    load_claim_traceability_csv,
)
from models.inclusion_release_readiness import (
    audit_release_readiness,
    create_release_readiness_template,
    load_release_readiness_csv,
)
from models.inclusion_method_registry import (
    PHASE_ORDER,
    filter_method_readiness_catalog,
    method_readiness_catalog,
)
from models.inclusion_subgroup_comparability import (
    audit_subgroup_comparability,
    create_subgroup_comparability_template,
    load_subgroup_comparability_csv,
)
from models.inclusion_weight_sensitivity import (
    audit_weight_sensitivity,
    create_weight_scheme_template,
    load_weight_scheme_csv,
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
    st.markdown("## Research data")
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
        "<h1>From Resources to Participation.</h1>"
        "<p class='section-copy'>An open research infrastructure for studying how policy and institutional support may be reflected in inclusive practices, meaningful child participation, and educational equity. The pathway is conceptual and has not been validated as a causal model.</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='quiet-note'><b>Research boundary:</b> This module is not a child assessment, diagnostic, disability-determination, placement, clinical, or teacher-rating tool. Participation is not child ability. Institution-level scores are research-prototype summaries.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("## Research pathway")
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
            st.table(pathway_table.set_index("pathway_stage"))
            st.markdown("**Support Gap values**")
            st.table(gap_table.set_index("support_gap"))
            st.markdown("**Institution-by-dimension values**")
            st.table(
                scores.loc[:, ["institution_id", *SCORE_COLUMNS]].set_index("institution_id")
            )

    with researcher:
        st.markdown("### Researcher Mode")
        st.caption("Select variables and methods. Outputs are descriptive and model-dependent.")
        st.markdown("#### Methodological readiness navigator")
        st.caption(
            "This catalog organises prototype workflows by research stage. "
            "It is not a score, validation result, approval sequence, or causal evidence."
        )
        navigator_phase = st.selectbox(
            "Readiness navigator phase",
            ["All phases", *PHASE_ORDER],
            key="inclusive_readiness_navigator_phase",
        )
        navigator_catalog = filter_method_readiness_catalog(navigator_phase)
        st.dataframe(navigator_catalog, width="stretch", hide_index=True)
        st.download_button(
            "Download methodological readiness catalog",
            method_readiness_catalog().to_csv(index=False).encode("utf-8-sig"),
            "inclusive_methodological_readiness_catalog.csv",
            "text/csv",
            key="inclusive_readiness_catalog_download",
        )
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
        st.markdown("#### Subgroup measurement comparability readiness audit")
        st.caption(
            "Readiness evidence only. Descriptive group differences do not establish "
            "measurement invariance, DIF, bias, fairness, or substantive group effects."
        )
        with st.expander("Subgroup measurement comparability readiness workflow"):
            subgroup_template = create_subgroup_comparability_template()
            st.download_button(
                "Download subgroup comparability audit template",
                subgroup_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_subgroup_comparability_template.csv",
                "text/csv",
                key="inclusive_subgroup_comparability_template_download",
            )
            subgroup_upload = st.file_uploader(
                "Upload subgroup comparability audit CSV",
                type=["csv"],
                key="inclusive_subgroup_comparability_upload",
                help=(
                    "comparison_group must use ethically justified institutional-level "
                    "categories. Do not upload child, family, teacher, clinical, or case data."
                ),
            )
            subgroup_scale = st.selectbox(
                "Subgroup comparability audit response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_subgroup_comparability_scale",
            )
            if subgroup_scale == "0–100":
                subgroup_min, subgroup_max = 0.0, 100.0
            elif subgroup_scale == "0–1":
                subgroup_min, subgroup_max = 0.0, 1.0
            else:
                subgroup_scale_columns = st.columns(2)
                with subgroup_scale_columns[0]:
                    subgroup_min = float(
                        st.number_input(
                            "Subgroup comparability scale minimum",
                            value=1.0,
                            key="inclusive_subgroup_comparability_min",
                        )
                    )
                with subgroup_scale_columns[1]:
                    subgroup_max = float(
                        st.number_input(
                            "Subgroup comparability scale maximum",
                            value=5.0,
                            key="inclusive_subgroup_comparability_max",
                        )
                    )
            if subgroup_upload is not None:
                try:
                    subgroup_data = load_subgroup_comparability_csv(
                        subgroup_upload,
                        subgroup_min,
                        subgroup_max,
                    )
                except ValueError as error:
                    st.error(f"Subgroup-comparability validation failed: {error}")
                else:
                    subgroup_versions = (
                        subgroup_data["instrument_version"].drop_duplicates().tolist()
                    )
                    selected_subgroup_version = st.selectbox(
                        "Version for subgroup comparability audit",
                        subgroup_versions,
                        key="inclusive_subgroup_comparability_version",
                    )
                    subgroup_rounds = sorted(
                        subgroup_data.loc[
                            subgroup_data["instrument_version"].eq(
                                selected_subgroup_version
                            ),
                            "administration_round",
                        ].unique()
                    )
                    selected_subgroup_round = st.selectbox(
                        "Administration round for subgroup comparability audit",
                        subgroup_rounds,
                        key="inclusive_subgroup_comparability_round",
                    )
                    try:
                        subgroup_audit = audit_subgroup_comparability(
                            subgroup_data,
                            selected_subgroup_version,
                            int(selected_subgroup_round),
                            subgroup_min,
                            subgroup_max,
                        )
                    except ValueError as error:
                        st.error(f"Subgroup-comparability audit failed: {error}")
                    else:
                        st.warning(str(subgroup_audit["interpretation"]))
                        for title, summary_key in (
                            ("Group coverage", "group_coverage_summary"),
                            ("Group item distributions", "group_item_distribution_summary"),
                            ("Pairwise item differences", "pairwise_item_difference_summary"),
                            (
                                "Correlation-structure differences",
                                "correlation_structure_difference_summary",
                            ),
                            (
                                "Research question candidates",
                                "research_question_candidates",
                            ),
                        ):
                            st.markdown(f"**{title}**")
                            st.dataframe(
                                subgroup_audit[summary_key],
                                width="stretch",
                                hide_index=True,
                            )
                        for label, summary_key, file_name in (
                            (
                                "Download subgroup coverage summary",
                                "group_coverage_summary",
                                "inclusive_subgroup_coverage.csv",
                            ),
                            (
                                "Download subgroup item distributions",
                                "group_item_distribution_summary",
                                "inclusive_subgroup_item_distributions.csv",
                            ),
                            (
                                "Download pairwise item differences",
                                "pairwise_item_difference_summary",
                                "inclusive_subgroup_item_differences.csv",
                            ),
                            (
                                "Download correlation-structure differences",
                                "correlation_structure_difference_summary",
                                "inclusive_subgroup_correlation_differences.csv",
                            ),
                            (
                                "Download subgroup research questions",
                                "research_question_candidates",
                                "inclusive_subgroup_research_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                subgroup_audit[summary_key].to_csv(index=False).encode(
                                    "utf-8-sig"
                                ),
                                file_name,
                                "text/csv",
                                key=f"inclusive_subgroup_{summary_key}_download",
                            )
        st.markdown("#### External measure relationship readiness audit")
        st.caption(
            "Relationship-readiness evidence only. Correlation does not establish "
            "construct, criterion-related, predictive, or causal validity."
        )
        with st.expander("External measure relationship readiness workflow"):
            external_template = create_external_measure_template()
            st.download_button(
                "Download external measure audit template",
                external_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_external_measure_template.csv",
                "text/csv",
                key="inclusive_external_measure_template_download",
            )
            external_upload = st.file_uploader(
                "Upload external measure audit CSV",
                type=["csv"],
                key="inclusive_external_measure_upload",
                help=(
                    "Use one independently sourced, non-identifying institutional measure. "
                    "Do not upload child, family, teacher, clinical, or case data."
                ),
            )
            external_scale = st.selectbox(
                "External measure audit item response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_external_measure_scale",
            )
            if external_scale == "0–100":
                external_min, external_max = 0.0, 100.0
            elif external_scale == "0–1":
                external_min, external_max = 0.0, 1.0
            else:
                external_scale_columns = st.columns(2)
                with external_scale_columns[0]:
                    external_min = float(
                        st.number_input(
                            "External measure audit item scale minimum",
                            value=1.0,
                            key="inclusive_external_measure_min",
                        )
                    )
                with external_scale_columns[1]:
                    external_max = float(
                        st.number_input(
                            "External measure audit item scale maximum",
                            value=5.0,
                            key="inclusive_external_measure_max",
                        )
                    )
            if external_upload is not None:
                try:
                    external_data = load_external_measure_csv(
                        external_upload,
                        external_min,
                        external_max,
                    )
                except ValueError as error:
                    st.error(f"External-measure validation failed: {error}")
                else:
                    external_versions = (
                        external_data["instrument_version"].drop_duplicates().tolist()
                    )
                    selected_external_version = st.selectbox(
                        "Version for external measure audit",
                        external_versions,
                        key="inclusive_external_measure_version",
                    )
                    external_rounds = sorted(
                        external_data.loc[
                            external_data["instrument_version"].eq(
                                selected_external_version
                            ),
                            "administration_round",
                        ].unique()
                    )
                    selected_external_round = st.selectbox(
                        "Administration round for external measure audit",
                        external_rounds,
                        key="inclusive_external_measure_round",
                    )
                    try:
                        external_audit = audit_external_measure_relationships(
                            external_data,
                            selected_external_version,
                            int(selected_external_round),
                            external_min,
                            external_max,
                        )
                    except ValueError as error:
                        st.error(f"External-measure audit failed: {error}")
                    else:
                        st.warning(str(external_audit["interpretation"]))
                        st.markdown("**External measure and paired-record coverage**")
                        st.dataframe(
                            external_audit["external_measure_coverage_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Five-dimension relationship summary**")
                        st.dataframe(
                            external_audit["dimension_relationship_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Research question candidates**")
                        st.dataframe(
                            external_audit["research_question_candidates"],
                            width="stretch",
                            hide_index=True,
                        )
                        for label, summary_key, file_name in (
                            (
                                "Download external measure coverage summary",
                                "external_measure_coverage_summary",
                                "inclusive_external_measure_coverage.csv",
                            ),
                            (
                                "Download dimension relationship summary",
                                "dimension_relationship_summary",
                                "inclusive_external_dimension_relationships.csv",
                            ),
                            (
                                "Download external measure research questions",
                                "research_question_candidates",
                                "inclusive_external_measure_research_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                external_audit[summary_key].to_csv(index=False).encode(
                                    "utf-8-sig"
                                ),
                                file_name,
                                "text/csv",
                                key=f"inclusive_external_{summary_key}_download",
                            )
        st.markdown("#### Alternative item-weight sensitivity audit")
        st.caption(
            "Sensitivity evidence only. Researcher-declared weights do not identify a best "
            "scheme and do not change the platform's equal-item default scoring model."
        )
        with st.expander("Alternative item-weight sensitivity workflow"):
            st.download_button(
                "Download complete response template for weight sensitivity",
                create_reliability_audit_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_weight_sensitivity_responses_template.csv",
                "text/csv",
                key="inclusive_weight_sensitivity_responses_template_download",
            )
            weight_template = create_weight_scheme_template()
            st.download_button(
                "Download alternative weight scheme template",
                weight_template.to_csv(index=False).encode("utf-8-sig"),
                "inclusive_alternative_weight_scheme_template.csv",
                "text/csv",
                key="inclusive_weight_scheme_template_download",
            )
            weight_response_upload = st.file_uploader(
                "Upload complete responses for weight sensitivity",
                type=["csv"],
                key="inclusive_weight_sensitivity_responses_upload",
                help="Complete, non-identifying institutional records only.",
            )
            weight_scheme_upload = st.file_uploader(
                "Upload alternative weight scheme CSV",
                type=["csv"],
                key="inclusive_weight_scheme_upload",
                help=(
                    "Every named scheme must contain all 28 current items and positive "
                    "weights summing to 1 within each dimension."
                ),
            )
            weight_scale = st.selectbox(
                "Weight sensitivity response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_weight_sensitivity_scale",
            )
            if weight_scale == "0–100":
                weight_min, weight_max = 0.0, 100.0
            elif weight_scale == "0–1":
                weight_min, weight_max = 0.0, 1.0
            else:
                weight_scale_columns = st.columns(2)
                with weight_scale_columns[0]:
                    weight_min = float(
                        st.number_input(
                            "Weight sensitivity scale minimum",
                            value=1.0,
                            key="inclusive_weight_sensitivity_min",
                        )
                    )
                with weight_scale_columns[1]:
                    weight_max = float(
                        st.number_input(
                            "Weight sensitivity scale maximum",
                            value=5.0,
                            key="inclusive_weight_sensitivity_max",
                        )
                    )
            if weight_response_upload is not None and weight_scheme_upload is not None:
                try:
                    weight_response_data = load_reliability_audit_csv(
                        weight_response_upload,
                        weight_min,
                        weight_max,
                    )
                    weight_scheme_data = load_weight_scheme_csv(weight_scheme_upload)
                except ValueError as error:
                    st.error(f"Weight-sensitivity validation failed: {error}")
                else:
                    weight_versions = (
                        weight_response_data["instrument_version"]
                        .drop_duplicates()
                        .tolist()
                    )
                    selected_weight_version = st.selectbox(
                        "Version for weight sensitivity audit",
                        weight_versions,
                        key="inclusive_weight_sensitivity_version",
                    )
                    weight_rounds = sorted(
                        weight_response_data.loc[
                            weight_response_data["instrument_version"].eq(
                                selected_weight_version
                            ),
                            "administration_round",
                        ].unique()
                    )
                    selected_weight_round = st.selectbox(
                        "Administration round for weight sensitivity audit",
                        weight_rounds,
                        key="inclusive_weight_sensitivity_round",
                    )
                    try:
                        weight_audit = audit_weight_sensitivity(
                            weight_response_data,
                            weight_scheme_data,
                            selected_weight_version,
                            int(selected_weight_round),
                            weight_min,
                            weight_max,
                        )
                    except ValueError as error:
                        st.error(f"Weight-sensitivity audit failed: {error}")
                    else:
                        st.warning(str(weight_audit["interpretation"]))
                        for title, summary_key in (
                            ("Declared weight schemes", "weight_scheme_summary"),
                            ("Five-dimension sensitivity", "dimension_sensitivity_summary"),
                            ("Support Gap sensitivity", "support_gap_sensitivity_summary"),
                            ("Research question candidates", "research_question_candidates"),
                        ):
                            st.markdown(f"**{title}**")
                            st.dataframe(
                                weight_audit[summary_key],
                                width="stretch",
                                hide_index=True,
                            )
                        for label, summary_key, file_name in (
                            (
                                "Download weight scheme summary",
                                "weight_scheme_summary",
                                "inclusive_weight_scheme_summary.csv",
                            ),
                            (
                                "Download dimension weight sensitivity",
                                "dimension_sensitivity_summary",
                                "inclusive_dimension_weight_sensitivity.csv",
                            ),
                            (
                                "Download Support Gap weight sensitivity",
                                "support_gap_sensitivity_summary",
                                "inclusive_support_gap_weight_sensitivity.csv",
                            ),
                            (
                                "Download weight sensitivity research questions",
                                "research_question_candidates",
                                "inclusive_weight_sensitivity_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                weight_audit[summary_key].to_csv(index=False).encode(
                                    "utf-8-sig"
                                ),
                                file_name,
                                "text/csv",
                                key=f"inclusive_weight_{summary_key}_download",
                            )
        st.markdown("#### Bootstrap sampling uncertainty audit")
        st.caption(
            "Prototype resampling evidence only. Intervals do not establish validity, "
            "representativeness, causal effects, or policy effects."
        )
        with st.expander("Bootstrap sampling uncertainty workflow"):
            st.download_button(
                "Download Bootstrap audit response template",
                create_reliability_audit_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_bootstrap_response_template.csv",
                "text/csv",
                key="inclusive_bootstrap_template_download",
            )
            bootstrap_upload = st.file_uploader(
                "Upload Bootstrap audit response CSV",
                type=["csv"],
                key="inclusive_bootstrap_upload",
                help=(
                    "Use complete, non-identifying institutional records from a documented "
                    "sampling design. Uploaded records are processed in the current session."
                ),
            )
            bootstrap_scale = st.selectbox(
                "Bootstrap audit response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_bootstrap_scale",
            )
            if bootstrap_scale == "0–100":
                bootstrap_min, bootstrap_max = 0.0, 100.0
            elif bootstrap_scale == "0–1":
                bootstrap_min, bootstrap_max = 0.0, 1.0
            else:
                bootstrap_scale_columns = st.columns(2)
                with bootstrap_scale_columns[0]:
                    bootstrap_min = float(
                        st.number_input(
                            "Bootstrap scale minimum",
                            value=1.0,
                            key="inclusive_bootstrap_min",
                        )
                    )
                with bootstrap_scale_columns[1]:
                    bootstrap_max = float(
                        st.number_input(
                            "Bootstrap scale maximum",
                            value=5.0,
                            key="inclusive_bootstrap_max",
                        )
                    )
            bootstrap_setting_columns = st.columns(3)
            with bootstrap_setting_columns[0]:
                bootstrap_resamples = int(
                    st.number_input(
                        "Bootstrap resamples",
                        min_value=100,
                        max_value=10000,
                        value=1000,
                        step=100,
                        key="inclusive_bootstrap_resamples",
                    )
                )
            with bootstrap_setting_columns[1]:
                bootstrap_confidence_percent = int(
                    st.slider(
                        "Bootstrap interval level (%)",
                        min_value=80,
                        max_value=99,
                        value=95,
                        step=1,
                        key="inclusive_bootstrap_confidence",
                    )
                )
            with bootstrap_setting_columns[2]:
                bootstrap_seed = int(
                    st.number_input(
                        "Bootstrap random seed",
                        min_value=0,
                        value=42,
                        step=1,
                        key="inclusive_bootstrap_seed",
                    )
                )
            if bootstrap_upload is not None:
                try:
                    bootstrap_data = load_reliability_audit_csv(
                        bootstrap_upload,
                        bootstrap_min,
                        bootstrap_max,
                    )
                except ValueError as error:
                    st.error(f"Bootstrap-audit validation failed: {error}")
                else:
                    bootstrap_versions = (
                        bootstrap_data["instrument_version"].drop_duplicates().tolist()
                    )
                    selected_bootstrap_version = st.selectbox(
                        "Version for Bootstrap audit",
                        bootstrap_versions,
                        key="inclusive_bootstrap_version",
                    )
                    bootstrap_rounds = sorted(
                        bootstrap_data.loc[
                            bootstrap_data["instrument_version"].eq(
                                selected_bootstrap_version
                            ),
                            "administration_round",
                        ].unique()
                    )
                    selected_bootstrap_round = st.selectbox(
                        "Administration round for Bootstrap audit",
                        bootstrap_rounds,
                        key="inclusive_bootstrap_round",
                    )
                    try:
                        bootstrap_audit = audit_bootstrap_uncertainty(
                            bootstrap_data,
                            selected_bootstrap_version,
                            int(selected_bootstrap_round),
                            n_resamples=bootstrap_resamples,
                            confidence_level=bootstrap_confidence_percent / 100,
                            random_seed=bootstrap_seed,
                            source_min=bootstrap_min,
                            source_max=bootstrap_max,
                        )
                    except ValueError as error:
                        st.error(f"Bootstrap audit failed: {error}")
                    else:
                        st.warning(str(bootstrap_audit["interpretation"]))
                        st.markdown("**Bootstrap run settings**")
                        st.dataframe(
                            bootstrap_audit["bootstrap_run_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Dimension and Support Gap uncertainty summary**")
                        st.dataframe(
                            bootstrap_audit["bootstrap_interval_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Research question candidates**")
                        st.dataframe(
                            bootstrap_audit["research_question_candidates"],
                            width="stretch",
                            hide_index=True,
                        )
                        for label, summary_key, file_name in (
                            (
                                "Download Bootstrap run summary",
                                "bootstrap_run_summary",
                                "inclusive_bootstrap_run_summary.csv",
                            ),
                            (
                                "Download Bootstrap uncertainty summary",
                                "bootstrap_interval_summary",
                                "inclusive_bootstrap_uncertainty.csv",
                            ),
                            (
                                "Download Bootstrap research questions",
                                "research_question_candidates",
                                "inclusive_bootstrap_research_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                bootstrap_audit[summary_key].to_csv(index=False).encode(
                                    "utf-8-sig"
                                ),
                                file_name,
                                "text/csv",
                                key=f"inclusive_bootstrap_{summary_key}_download",
                            )
        st.markdown("#### Longitudinal panel readiness audit")
        st.caption(
            "Descriptive longitudinal readiness only. Time order does not establish "
            "causality, policy effects, improvement, or deterioration."
        )
        with st.expander("Longitudinal panel readiness workflow"):
            st.download_button(
                "Download longitudinal panel response template",
                create_reliability_audit_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_longitudinal_panel_template.csv",
                "text/csv",
                key="inclusive_longitudinal_template_download",
            )
            longitudinal_upload = st.file_uploader(
                "Upload longitudinal panel response CSV",
                type=["csv"],
                key="inclusive_longitudinal_upload",
                help=(
                    "Use stable pseudonymous institutional IDs across rounds within one "
                    "instrument version. Do not upload child, family, teacher, or case data."
                ),
            )
            longitudinal_scale = st.selectbox(
                "Longitudinal panel response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_longitudinal_scale",
            )
            if longitudinal_scale == "0–100":
                longitudinal_min, longitudinal_max = 0.0, 100.0
            elif longitudinal_scale == "0–1":
                longitudinal_min, longitudinal_max = 0.0, 1.0
            else:
                longitudinal_scale_columns = st.columns(2)
                with longitudinal_scale_columns[0]:
                    longitudinal_min = float(
                        st.number_input(
                            "Longitudinal scale minimum",
                            value=1.0,
                            key="inclusive_longitudinal_min",
                        )
                    )
                with longitudinal_scale_columns[1]:
                    longitudinal_max = float(
                        st.number_input(
                            "Longitudinal scale maximum",
                            value=5.0,
                            key="inclusive_longitudinal_max",
                        )
                    )
            if longitudinal_upload is not None:
                try:
                    longitudinal_data = load_reliability_audit_csv(
                        longitudinal_upload,
                        longitudinal_min,
                        longitudinal_max,
                    )
                except ValueError as error:
                    st.error(f"Longitudinal-panel validation failed: {error}")
                else:
                    longitudinal_versions = (
                        longitudinal_data["instrument_version"].drop_duplicates().tolist()
                    )
                    selected_longitudinal_version = st.selectbox(
                        "Version for longitudinal panel audit",
                        longitudinal_versions,
                        key="inclusive_longitudinal_version",
                    )
                    try:
                        longitudinal_audit = audit_longitudinal_panel_readiness(
                            longitudinal_data,
                            selected_longitudinal_version,
                            longitudinal_min,
                            longitudinal_max,
                        )
                    except ValueError as error:
                        st.error(f"Longitudinal panel audit failed: {error}")
                    else:
                        st.warning(str(longitudinal_audit["interpretation"]))
                        for title, summary_key in (
                            ("Panel completeness", "longitudinal_panel_summary"),
                            ("Round coverage", "round_coverage_summary"),
                            ("Round score summaries", "round_statistic_summary"),
                            ("Adjacent-round matching", "adjacent_round_matching_summary"),
                            ("Adjacent matched changes", "adjacent_round_change_summary"),
                            ("Research question candidates", "research_question_candidates"),
                        ):
                            st.markdown(f"**{title}**")
                            st.dataframe(
                                longitudinal_audit[summary_key],
                                width="stretch",
                                hide_index=True,
                            )
                        for label, summary_key, file_name in (
                            (
                                "Download longitudinal panel summary",
                                "longitudinal_panel_summary",
                                "inclusive_longitudinal_panel_summary.csv",
                            ),
                            (
                                "Download longitudinal round coverage",
                                "round_coverage_summary",
                                "inclusive_longitudinal_round_coverage.csv",
                            ),
                            (
                                "Download longitudinal round statistics",
                                "round_statistic_summary",
                                "inclusive_longitudinal_round_statistics.csv",
                            ),
                            (
                                "Download adjacent-round matching summary",
                                "adjacent_round_matching_summary",
                                "inclusive_longitudinal_adjacent_matching.csv",
                            ),
                            (
                                "Download adjacent-round change summary",
                                "adjacent_round_change_summary",
                                "inclusive_longitudinal_adjacent_changes.csv",
                            ),
                            (
                                "Download longitudinal research questions",
                                "research_question_candidates",
                                "inclusive_longitudinal_research_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                longitudinal_audit[summary_key].to_csv(index=False).encode(
                                    "utf-8-sig"
                                ),
                                file_name,
                                "text/csv",
                                key=f"inclusive_longitudinal_{summary_key}_download",
                            )
        st.markdown("#### Longitudinal attrition and panel composition audit")
        st.caption(
            "Attrition-readiness evidence only. Descriptive differences do not identify "
            "missingness mechanisms, bias, causes, or corrective weights."
        )
        with st.expander("Longitudinal attrition and panel composition workflow"):
            st.download_button(
                "Download attrition audit response template",
                create_reliability_audit_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_attrition_audit_template.csv",
                "text/csv",
                key="inclusive_attrition_template_download",
            )
            attrition_upload = st.file_uploader(
                "Upload attrition audit response CSV",
                type=["csv"],
                key="inclusive_attrition_upload",
                help=(
                    "Use stable pseudonymous institutional IDs across rounds. Small-group "
                    "statistics are suppressed; no missing values are imputed."
                ),
            )
            attrition_scale = st.selectbox(
                "Attrition audit response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_attrition_scale",
            )
            if attrition_scale == "0–100":
                attrition_min, attrition_max = 0.0, 100.0
            elif attrition_scale == "0–1":
                attrition_min, attrition_max = 0.0, 1.0
            else:
                attrition_scale_columns = st.columns(2)
                with attrition_scale_columns[0]:
                    attrition_min = float(
                        st.number_input(
                            "Attrition audit scale minimum",
                            value=1.0,
                            key="inclusive_attrition_min",
                        )
                    )
                with attrition_scale_columns[1]:
                    attrition_max = float(
                        st.number_input(
                            "Attrition audit scale maximum",
                            value=5.0,
                            key="inclusive_attrition_max",
                        )
                    )
            if attrition_upload is not None:
                try:
                    attrition_data = load_reliability_audit_csv(
                        attrition_upload,
                        attrition_min,
                        attrition_max,
                    )
                except ValueError as error:
                    st.error(f"Attrition-audit validation failed: {error}")
                else:
                    attrition_versions = (
                        attrition_data["instrument_version"].drop_duplicates().tolist()
                    )
                    selected_attrition_version = st.selectbox(
                        "Version for attrition audit",
                        attrition_versions,
                        key="inclusive_attrition_version",
                    )
                    try:
                        attrition_audit = audit_longitudinal_attrition(
                            attrition_data,
                            selected_attrition_version,
                            attrition_min,
                            attrition_max,
                        )
                    except ValueError as error:
                        st.error(f"Attrition audit failed: {error}")
                    else:
                        st.warning(str(attrition_audit["interpretation"]))
                        st.markdown("**Adjacent-round retention, exit, and entry coverage**")
                        st.dataframe(
                            attrition_audit["attrition_coverage_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Panel composition comparisons**")
                        st.dataframe(
                            attrition_audit["panel_composition_comparison_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Research question candidates**")
                        st.dataframe(
                            attrition_audit["research_question_candidates"],
                            width="stretch",
                            hide_index=True,
                        )
                        for label, summary_key, file_name in (
                            (
                                "Download attrition coverage summary",
                                "attrition_coverage_summary",
                                "inclusive_attrition_coverage.csv",
                            ),
                            (
                                "Download panel composition comparisons",
                                "panel_composition_comparison_summary",
                                "inclusive_panel_composition_comparisons.csv",
                            ),
                            (
                                "Download attrition research questions",
                                "research_question_candidates",
                                "inclusive_attrition_research_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                attrition_audit[summary_key].to_csv(index=False).encode(
                                    "utf-8-sig"
                                ),
                                file_name,
                                "text/csv",
                                key=f"inclusive_attrition_{summary_key}_download",
                            )
        st.markdown("#### Paired longitudinal Bootstrap uncertainty audit")
        st.caption(
            "Prototype uncertainty for matched mean changes only. Intervals do not establish "
            "longitudinal comparability, significance, improvement, policy effects, or causality."
        )
        with st.expander("Paired longitudinal Bootstrap uncertainty workflow"):
            st.download_button(
                "Download paired longitudinal Bootstrap response template",
                create_reliability_audit_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_paired_longitudinal_bootstrap_template.csv",
                "text/csv",
                key="inclusive_paired_bootstrap_template_download",
            )
            paired_bootstrap_upload = st.file_uploader(
                "Upload paired longitudinal Bootstrap response CSV",
                type=["csv"],
                key="inclusive_paired_bootstrap_upload",
                help=(
                    "Use stable pseudonymous institutional IDs across rounds within one "
                    "instrument version. Pair-level records and Bootstrap draws are not exported."
                ),
            )
            paired_bootstrap_scale = st.selectbox(
                "Paired longitudinal Bootstrap response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_paired_bootstrap_scale",
            )
            if paired_bootstrap_scale == "0–100":
                paired_bootstrap_min, paired_bootstrap_max = 0.0, 100.0
            elif paired_bootstrap_scale == "0–1":
                paired_bootstrap_min, paired_bootstrap_max = 0.0, 1.0
            else:
                paired_bootstrap_scale_columns = st.columns(2)
                with paired_bootstrap_scale_columns[0]:
                    paired_bootstrap_min = float(
                        st.number_input(
                            "Paired longitudinal Bootstrap scale minimum",
                            value=1.0,
                            key="inclusive_paired_bootstrap_min",
                        )
                    )
                with paired_bootstrap_scale_columns[1]:
                    paired_bootstrap_max = float(
                        st.number_input(
                            "Paired longitudinal Bootstrap scale maximum",
                            value=5.0,
                            key="inclusive_paired_bootstrap_max",
                        )
                    )
            paired_bootstrap_settings = st.columns(2)
            with paired_bootstrap_settings[0]:
                paired_bootstrap_resamples = int(
                    st.number_input(
                        "Paired longitudinal Bootstrap resamples",
                        min_value=100,
                        max_value=10000,
                        value=1000,
                        step=100,
                        key="inclusive_paired_bootstrap_resamples",
                    )
                )
            with paired_bootstrap_settings[1]:
                paired_bootstrap_seed = int(
                    st.number_input(
                        "Paired longitudinal Bootstrap random seed",
                        min_value=0,
                        value=42,
                        step=1,
                        key="inclusive_paired_bootstrap_seed",
                    )
                )
            paired_bootstrap_confidence_percent = st.slider(
                "Paired longitudinal Bootstrap interval level (%)",
                min_value=80,
                max_value=99,
                value=95,
                step=1,
                key="inclusive_paired_bootstrap_confidence",
            )
            if paired_bootstrap_upload is not None:
                try:
                    paired_bootstrap_data = load_reliability_audit_csv(
                        paired_bootstrap_upload,
                        paired_bootstrap_min,
                        paired_bootstrap_max,
                    )
                except ValueError as error:
                    st.error(f"Paired longitudinal Bootstrap validation failed: {error}")
                else:
                    paired_bootstrap_versions = (
                        paired_bootstrap_data["instrument_version"]
                        .drop_duplicates()
                        .tolist()
                    )
                    selected_paired_bootstrap_version = st.selectbox(
                        "Version for paired longitudinal Bootstrap audit",
                        paired_bootstrap_versions,
                        key="inclusive_paired_bootstrap_version",
                    )
                    try:
                        paired_bootstrap_audit = audit_paired_longitudinal_bootstrap(
                            paired_bootstrap_data,
                            selected_paired_bootstrap_version,
                            n_resamples=paired_bootstrap_resamples,
                            confidence_level=paired_bootstrap_confidence_percent / 100,
                            random_seed=paired_bootstrap_seed,
                            source_min=paired_bootstrap_min,
                            source_max=paired_bootstrap_max,
                        )
                    except ValueError as error:
                        st.error(f"Paired longitudinal Bootstrap audit failed: {error}")
                    else:
                        st.warning(str(paired_bootstrap_audit["interpretation"]))
                        st.markdown("**Paired Bootstrap run settings**")
                        st.dataframe(
                            paired_bootstrap_audit["paired_bootstrap_run_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Matched mean-change uncertainty summary**")
                        st.dataframe(
                            paired_bootstrap_audit["paired_bootstrap_interval_summary"],
                            width="stretch",
                            hide_index=True,
                        )
                        st.markdown("**Research question candidates**")
                        st.dataframe(
                            paired_bootstrap_audit["research_question_candidates"],
                            width="stretch",
                            hide_index=True,
                        )
                        for label, summary_key, file_name in (
                            (
                                "Download paired Bootstrap run summary",
                                "paired_bootstrap_run_summary",
                                "inclusive_paired_bootstrap_run_summary.csv",
                            ),
                            (
                                "Download paired Bootstrap uncertainty summary",
                                "paired_bootstrap_interval_summary",
                                "inclusive_paired_bootstrap_uncertainty.csv",
                            ),
                            (
                                "Download paired Bootstrap research questions",
                                "research_question_candidates",
                                "inclusive_paired_bootstrap_research_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                paired_bootstrap_audit[summary_key]
                                .to_csv(index=False)
                                .encode("utf-8-sig"),
                                file_name,
                                "text/csv",
                                key=f"inclusive_paired_bootstrap_{summary_key}_download",
                            )
        st.markdown("#### Longitudinal timing and fieldwork metadata audit")
        st.caption(
            "Research-record readiness only. Timing and implementation metadata do not "
            "establish data quality, explain score changes, or identify policy effects."
        )
        with st.expander("Longitudinal timing and fieldwork metadata workflow"):
            st.download_button(
                "Download longitudinal metadata template",
                create_longitudinal_metadata_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_longitudinal_metadata_template.csv",
                "text/csv",
                key="inclusive_longitudinal_metadata_template_download",
            )
            longitudinal_metadata_upload = st.file_uploader(
                "Upload longitudinal timing and fieldwork metadata CSV",
                type=["csv"],
                key="inclusive_longitudinal_metadata_upload",
                help=(
                    "Provide one non-identifying record per version and round. Fieldwork "
                    "notes are validated but are not reproduced in summaries or downloads."
                ),
            )
            if longitudinal_metadata_upload is not None:
                try:
                    longitudinal_metadata = load_longitudinal_metadata_csv(
                        longitudinal_metadata_upload
                    )
                except ValueError as error:
                    st.error(f"Longitudinal metadata validation failed: {error}")
                else:
                    longitudinal_metadata_versions = (
                        longitudinal_metadata["instrument_version"]
                        .drop_duplicates()
                        .tolist()
                    )
                    selected_longitudinal_metadata_version = st.selectbox(
                        "Version for longitudinal metadata audit",
                        longitudinal_metadata_versions,
                        key="inclusive_longitudinal_metadata_version",
                    )
                    try:
                        longitudinal_metadata_audit = audit_longitudinal_metadata(
                            longitudinal_metadata,
                            selected_longitudinal_metadata_version,
                        )
                    except ValueError as error:
                        st.error(f"Longitudinal metadata audit failed: {error}")
                    else:
                        st.warning(str(longitudinal_metadata_audit["interpretation"]))
                        for title, summary_key in (
                            ("Metadata overview", "longitudinal_metadata_overview"),
                            ("Round metadata", "round_metadata_summary"),
                            (
                                "Adjacent-round metadata comparison",
                                "adjacent_round_metadata_comparison",
                            ),
                            ("Research question candidates", "research_question_candidates"),
                        ):
                            st.markdown(f"**{title}**")
                            st.dataframe(
                                longitudinal_metadata_audit[summary_key],
                                width="stretch",
                                hide_index=True,
                            )
                        for label, summary_key, file_name in (
                            (
                                "Download longitudinal metadata overview",
                                "longitudinal_metadata_overview",
                                "inclusive_longitudinal_metadata_overview.csv",
                            ),
                            (
                                "Download longitudinal round metadata summary",
                                "round_metadata_summary",
                                "inclusive_longitudinal_round_metadata.csv",
                            ),
                            (
                                "Download adjacent-round metadata comparison",
                                "adjacent_round_metadata_comparison",
                                "inclusive_longitudinal_metadata_comparison.csv",
                            ),
                            (
                                "Download longitudinal metadata research questions",
                                "research_question_candidates",
                                "inclusive_longitudinal_metadata_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                longitudinal_metadata_audit[summary_key]
                                .to_csv(index=False)
                                .encode("utf-8-sig"),
                                file_name,
                                "text/csv",
                                key=f"inclusive_longitudinal_metadata_{summary_key}_download",
                            )
        st.markdown("#### Longitudinal measurement-comparability readiness audit")
        st.caption(
            "Descriptive readiness evidence only. Round differences do not establish "
            "measurement invariance, bias, improvement, policy effects, or causality."
        )
        with st.expander("Longitudinal measurement-comparability readiness workflow"):
            st.download_button(
                "Download longitudinal comparability response template",
                create_reliability_audit_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_longitudinal_comparability_template.csv",
                "text/csv",
                key="inclusive_longitudinal_comparability_template_download",
            )
            longitudinal_comparability_upload = st.file_uploader(
                "Upload longitudinal comparability response CSV",
                type=["csv"],
                key="inclusive_longitudinal_comparability_upload",
                help=(
                    "Use complete institutional records from at least two rounds of one "
                    "instrument version. No scores or item responses are imputed."
                ),
            )
            longitudinal_comparability_scale = st.selectbox(
                "Longitudinal comparability response scale",
                ["0–100", "0–1", "Custom range"],
                key="inclusive_longitudinal_comparability_scale",
            )
            if longitudinal_comparability_scale == "0–100":
                longitudinal_comparability_min, longitudinal_comparability_max = 0.0, 100.0
            elif longitudinal_comparability_scale == "0–1":
                longitudinal_comparability_min, longitudinal_comparability_max = 0.0, 1.0
            else:
                longitudinal_comparability_columns = st.columns(2)
                with longitudinal_comparability_columns[0]:
                    longitudinal_comparability_min = float(
                        st.number_input(
                            "Longitudinal comparability scale minimum",
                            value=1.0,
                            key="inclusive_longitudinal_comparability_min",
                        )
                    )
                with longitudinal_comparability_columns[1]:
                    longitudinal_comparability_max = float(
                        st.number_input(
                            "Longitudinal comparability scale maximum",
                            value=5.0,
                            key="inclusive_longitudinal_comparability_max",
                        )
                    )
            if longitudinal_comparability_upload is not None:
                try:
                    longitudinal_comparability_data = load_reliability_audit_csv(
                        longitudinal_comparability_upload,
                        longitudinal_comparability_min,
                        longitudinal_comparability_max,
                    )
                except ValueError as error:
                    st.error(f"Longitudinal comparability validation failed: {error}")
                else:
                    longitudinal_comparability_versions = (
                        longitudinal_comparability_data["instrument_version"]
                        .drop_duplicates()
                        .tolist()
                    )
                    selected_longitudinal_comparability_version = st.selectbox(
                        "Version for longitudinal comparability audit",
                        longitudinal_comparability_versions,
                        key="inclusive_longitudinal_comparability_version",
                    )
                    try:
                        longitudinal_comparability_audit = audit_longitudinal_comparability(
                            longitudinal_comparability_data,
                            selected_longitudinal_comparability_version,
                            longitudinal_comparability_min,
                            longitudinal_comparability_max,
                        )
                    except ValueError as error:
                        st.error(f"Longitudinal comparability audit failed: {error}")
                    else:
                        st.warning(str(longitudinal_comparability_audit["interpretation"]))
                        for title, summary_key in (
                            ("Round coverage", "round_coverage_summary"),
                            ("Round item distributions", "round_item_distribution_summary"),
                            (
                                "Adjacent-round item differences",
                                "adjacent_round_item_difference_summary",
                            ),
                            (
                                "Adjacent-round correlation differences",
                                "adjacent_round_correlation_difference_summary",
                            ),
                            ("Research question candidates", "research_question_candidates"),
                        ):
                            st.markdown(f"**{title}**")
                            st.dataframe(
                                longitudinal_comparability_audit[summary_key],
                                width="stretch",
                                hide_index=True,
                            )
                        for label, summary_key, file_name in (
                            (
                                "Download longitudinal comparability round coverage",
                                "round_coverage_summary",
                                "inclusive_longitudinal_comparability_coverage.csv",
                            ),
                            (
                                "Download longitudinal item distributions",
                                "round_item_distribution_summary",
                                "inclusive_longitudinal_item_distributions.csv",
                            ),
                            (
                                "Download adjacent-round item differences",
                                "adjacent_round_item_difference_summary",
                                "inclusive_longitudinal_item_differences.csv",
                            ),
                            (
                                "Download adjacent-round correlation differences",
                                "adjacent_round_correlation_difference_summary",
                                "inclusive_longitudinal_correlation_differences.csv",
                            ),
                            (
                                "Download longitudinal comparability research questions",
                                "research_question_candidates",
                                "inclusive_longitudinal_comparability_questions.csv",
                            ),
                        ):
                            st.download_button(
                                label,
                                longitudinal_comparability_audit[summary_key]
                                .to_csv(index=False)
                                .encode("utf-8-sig"),
                                file_name,
                                "text/csv",
                                key=f"inclusive_longitudinal_comparability_{summary_key}_download",
                            )
        st.markdown("#### Longitudinal analysis-plan readiness audit")
        st.caption(
            "Documentation readiness only. This workflow does not fit a model, select a method, "
            "or establish causal identification."
        )
        with st.expander("Longitudinal analysis-plan readiness workflow"):
            st.download_button(
                "Download longitudinal analysis-plan template",
                create_longitudinal_plan_template().to_csv(index=False).encode("utf-8-sig"),
                "inclusive_longitudinal_analysis_plan_template.csv",
                "text/csv",
                key="inclusive_longitudinal_plan_template_download",
            )
            longitudinal_plan_upload = st.file_uploader(
                "Upload longitudinal analysis-plan CSV",
                type=["csv"],
                key="inclusive_longitudinal_plan_upload",
                help=(
                    "Record the declared estimand, comparison, missing-data, weighting, "
                    "uncertainty, dependence, and measurement-comparability decisions."
                ),
            )
            if longitudinal_plan_upload is not None:
                try:
                    longitudinal_plan_data = load_longitudinal_plan_csv(
                        longitudinal_plan_upload
                    )
                except ValueError as error:
                    st.error(f"Longitudinal analysis-plan validation failed: {error}")
                else:
                    longitudinal_plan_audit = audit_longitudinal_plan(longitudinal_plan_data)
                    st.warning(str(longitudinal_plan_audit["interpretation"]))
                    for title, summary_key in (
                        ("Plan summary", "longitudinal_plan_summary"),
                        ("Method documentation prompts", "method_documentation_prompts"),
                        ("Research question candidates", "research_question_candidates"),
                    ):
                        st.markdown(f"**{title}**")
                        st.dataframe(
                            longitudinal_plan_audit[summary_key],
                            width="stretch",
                            hide_index=True,
                        )
                    for label, summary_key, file_name in (
                        (
                            "Download longitudinal plan summary",
                            "longitudinal_plan_summary",
                            "inclusive_longitudinal_plan_summary.csv",
                        ),
                        (
                            "Download method documentation prompts",
                            "method_documentation_prompts",
                            "inclusive_longitudinal_plan_prompts.csv",
                        ),
                        (
                            "Download longitudinal plan research questions",
                            "research_question_candidates",
                            "inclusive_longitudinal_plan_questions.csv",
                        ),
                    ):
                        st.download_button(
                            label,
                            longitudinal_plan_audit[summary_key]
                            .to_csv(index=False)
                            .encode("utf-8-sig"),
                            file_name,
                            "text/csv",
                            key=f"inclusive_longitudinal_plan_{summary_key}_download",
                        )
        st.markdown("#### Longitudinal policy and context event alignment audit")
        st.caption(
            "Chronology evidence only. Event timing and overlap do not establish exposure, "
            "policy effects, mechanisms, or causality."
        )
        with st.expander("Longitudinal policy and context event alignment workflow"):
            event_template_columns = st.columns(2)
            with event_template_columns[0]:
                st.download_button(
                    "Download event-alignment metadata template",
                    create_longitudinal_metadata_template().to_csv(index=False).encode("utf-8-sig"),
                    "inclusive_event_alignment_metadata_template.csv",
                    "text/csv",
                    key="inclusive_event_metadata_template_download",
                )
            with event_template_columns[1]:
                st.download_button(
                    "Download longitudinal event registry template",
                    create_longitudinal_event_template().to_csv(index=False).encode("utf-8-sig"),
                    "inclusive_longitudinal_event_registry_template.csv",
                    "text/csv",
                    key="inclusive_event_registry_template_download",
                )
            event_metadata_upload = st.file_uploader(
                "Upload event-alignment round metadata CSV",
                type=["csv"],
                key="inclusive_event_metadata_upload",
            )
            event_registry_upload = st.file_uploader(
                "Upload longitudinal policy and context event CSV",
                type=["csv"],
                key="inclusive_event_registry_upload",
                help="Use non-identifying descriptions. Description text is not reproduced in outputs.",
            )
            if event_metadata_upload is not None and event_registry_upload is not None:
                try:
                    event_metadata = load_longitudinal_metadata_csv(event_metadata_upload)
                    event_registry = load_longitudinal_event_csv(event_registry_upload)
                except ValueError as error:
                    st.error(f"Event-alignment validation failed: {error}")
                else:
                    versions = sorted(
                        set(event_metadata["instrument_version"])
                        & set(event_registry["instrument_version"])
                    )
                    if not versions:
                        st.error("Event alignment requires a shared instrument version in both files.")
                    else:
                        selected_event_version = st.selectbox(
                            "Version for event-alignment audit",
                            versions,
                            key="inclusive_event_alignment_version",
                        )
                        try:
                            event_audit = audit_longitudinal_event_alignment(
                                event_metadata,
                                event_registry,
                                selected_event_version,
                            )
                        except ValueError as error:
                            st.error(f"Event-alignment audit failed: {error}")
                        else:
                            st.warning(str(event_audit["interpretation"]))
                            for title, summary_key in (
                                ("Event alignment", "event_alignment_summary"),
                                (
                                    "Adjacent-round event context",
                                    "adjacent_round_event_context_summary",
                                ),
                                ("Research question candidates", "research_question_candidates"),
                            ):
                                st.markdown(f"**{title}**")
                                st.dataframe(event_audit[summary_key], width="stretch", hide_index=True)
                            for label, summary_key, file_name in (
                                ("Download event alignment summary", "event_alignment_summary", "inclusive_event_alignment.csv"),
                                ("Download adjacent-round event context", "adjacent_round_event_context_summary", "inclusive_adjacent_round_event_context.csv"),
                                ("Download event-alignment research questions", "research_question_candidates", "inclusive_event_alignment_questions.csv"),
                            ):
                                st.download_button(
                                    label,
                                    event_audit[summary_key].to_csv(index=False).encode("utf-8-sig"),
                                    file_name,
                                    "text/csv",
                                    key=f"inclusive_event_{summary_key}_download",
                                )
        st.markdown("#### Event exposure definition readiness audit")
        st.caption("Exposure documentation only. Registered events are not assumed to be institution-level treatment or causal exposure.")
        with st.expander("Event exposure definition readiness workflow"):
            st.download_button("Download event exposure-definition template", create_event_exposure_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_event_exposure_template.csv", "text/csv", key="inclusive_event_exposure_template_download")
            exposure_upload = st.file_uploader("Upload event exposure-definition CSV", type=["csv"], key="inclusive_event_exposure_upload")
            if exposure_upload is not None:
                try:
                    exposure_data = load_event_exposure_csv(exposure_upload)
                except ValueError as error:
                    st.error(f"Event-exposure validation failed: {error}")
                else:
                    exposure_versions = exposure_data["instrument_version"].drop_duplicates().tolist()
                    selected_exposure_version = st.selectbox("Version for event-exposure audit", exposure_versions, key="inclusive_event_exposure_version")
                    exposure_audit = audit_event_exposure_definitions(exposure_data, selected_exposure_version)
                    st.warning(str(exposure_audit["interpretation"]))
                    for title, key in (("Exposure definitions", "event_exposure_summary"), ("Definition prompts", "exposure_definition_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(exposure_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download event exposure summary", "event_exposure_summary", "inclusive_event_exposure_summary.csv"), ("Download exposure prompts", "exposure_definition_prompts", "inclusive_event_exposure_prompts.csv"), ("Download exposure research questions", "research_question_candidates", "inclusive_event_exposure_questions.csv")):
                        st.download_button(label, exposure_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_event_exposure_{key}_download")
        st.markdown("#### Identification-design readiness audit")
        st.caption("Design documentation only. Selecting a design label does not establish causal identification.")
        with st.expander("Identification-design readiness workflow"):
            st.download_button("Download identification-design template", create_identification_design_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_identification_design_template.csv", "text/csv", key="inclusive_identification_template_download")
            identification_upload = st.file_uploader("Upload identification-design CSV", type=["csv"], key="inclusive_identification_upload")
            if identification_upload is not None:
                try:
                    identification_data = load_identification_design_csv(identification_upload)
                except ValueError as error:
                    st.error(f"Identification-design validation failed: {error}")
                else:
                    identification_versions = identification_data["instrument_version"].drop_duplicates().tolist()
                    selected_identification_version = st.selectbox("Version for identification-design audit", identification_versions, key="inclusive_identification_version")
                    identification_audit = audit_identification_design(identification_data, selected_identification_version)
                    st.warning(str(identification_audit["interpretation"]))
                    for title, key in (("Design summary", "identification_design_summary"), ("Identification prompts", "identification_design_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(identification_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download identification-design summary", "identification_design_summary", "inclusive_identification_design_summary.csv"), ("Download identification prompts", "identification_design_prompts", "inclusive_identification_prompts.csv"), ("Download identification research questions", "research_question_candidates", "inclusive_identification_questions.csv")):
                        st.download_button(label, identification_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_identification_{key}_download")
        st.markdown("#### Falsification and sensitivity plan readiness audit")
        st.caption("Plan documentation only. Favourable diagnostics would not prove causal identification.")
        with st.expander("Falsification and sensitivity plan readiness workflow"):
            st.download_button("Download falsification-plan template", create_falsification_plan_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_falsification_plan_template.csv", "text/csv", key="inclusive_falsification_template_download")
            falsification_upload = st.file_uploader("Upload falsification and sensitivity plan CSV", type=["csv"], key="inclusive_falsification_upload")
            if falsification_upload is not None:
                try:
                    falsification_data = load_falsification_plan_csv(falsification_upload)
                except ValueError as error:
                    st.error(f"Falsification-plan validation failed: {error}")
                else:
                    falsification_versions = falsification_data["instrument_version"].drop_duplicates().tolist()
                    selected_falsification_version = st.selectbox("Version for falsification-plan audit", falsification_versions, key="inclusive_falsification_version")
                    falsification_audit = audit_falsification_plan(falsification_data, selected_falsification_version)
                    st.warning(str(falsification_audit["interpretation"]))
                    for title, key in (("Plan summary", "falsification_plan_summary"), ("Plan prompts", "falsification_plan_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(falsification_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download falsification-plan summary", "falsification_plan_summary", "inclusive_falsification_plan_summary.csv"), ("Download falsification-plan prompts", "falsification_plan_prompts", "inclusive_falsification_plan_prompts.csv"), ("Download falsification research questions", "research_question_candidates", "inclusive_falsification_questions.csv")):
                        st.download_button(label, falsification_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_falsification_{key}_download")
        st.markdown("#### Estimation-specification readiness audit")
        st.caption("Specification documentation only. The workflow fits no model and estimates no policy or context effect.")
        with st.expander("Estimation-specification readiness workflow"):
            st.download_button("Download estimation-specification template", create_estimation_specification_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_estimation_specification_template.csv", "text/csv", key="inclusive_estimation_specification_template_download")
            estimation_upload = st.file_uploader("Upload estimation-specification CSV", type=["csv"], key="inclusive_estimation_specification_upload")
            if estimation_upload is not None:
                try:
                    estimation_data = load_estimation_specification_csv(estimation_upload)
                except ValueError as error:
                    st.error(f"Estimation-specification validation failed: {error}")
                else:
                    estimation_versions = estimation_data["instrument_version"].drop_duplicates().tolist()
                    selected_estimation_version = st.selectbox("Version for estimation-specification audit", estimation_versions, key="inclusive_estimation_specification_version")
                    estimation_audit = audit_estimation_specification(estimation_data, selected_estimation_version)
                    st.warning(str(estimation_audit["interpretation"]))
                    for title, key in (("Specification summary", "estimation_specification_summary"), ("Specification prompts", "estimation_specification_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(estimation_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download estimation-specification summary", "estimation_specification_summary", "inclusive_estimation_specification_summary.csv"), ("Download estimation-specification prompts", "estimation_specification_prompts", "inclusive_estimation_specification_prompts.csv"), ("Download estimation research questions", "research_question_candidates", "inclusive_estimation_specification_questions.csv")):
                        st.download_button(label, estimation_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_estimation_specification_{key}_download")
        st.markdown("#### Analysis reproducibility readiness audit")
        st.caption("Execution-record documentation only. The workflow runs no code and verifies no result.")
        with st.expander("Analysis reproducibility readiness workflow"):
            st.download_button("Download analysis reproducibility template", create_analysis_reproducibility_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_analysis_reproducibility_template.csv", "text/csv", key="inclusive_analysis_reproducibility_template_download")
            reproducibility_upload = st.file_uploader("Upload analysis reproducibility CSV", type=["csv"], key="inclusive_analysis_reproducibility_upload")
            if reproducibility_upload is not None:
                try:
                    reproducibility_data = load_analysis_reproducibility_csv(reproducibility_upload)
                except ValueError as error:
                    st.error(f"Analysis-reproducibility validation failed: {error}")
                else:
                    reproducibility_versions = reproducibility_data["instrument_version"].drop_duplicates().tolist()
                    selected_reproducibility_version = st.selectbox("Version for analysis reproducibility audit", reproducibility_versions, key="inclusive_analysis_reproducibility_version")
                    reproducibility_audit = audit_analysis_reproducibility(reproducibility_data, selected_reproducibility_version)
                    st.warning(str(reproducibility_audit["interpretation"]))
                    for title, key in (("Reproducibility summary", "analysis_reproducibility_summary"), ("Reproducibility prompts", "analysis_reproducibility_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(reproducibility_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download analysis reproducibility summary", "analysis_reproducibility_summary", "inclusive_analysis_reproducibility_summary.csv"), ("Download reproducibility prompts", "analysis_reproducibility_prompts", "inclusive_analysis_reproducibility_prompts.csv"), ("Download reproducibility research questions", "research_question_candidates", "inclusive_analysis_reproducibility_questions.csv")):
                        st.download_button(label, reproducibility_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_analysis_reproducibility_{key}_download")
        st.markdown("#### Results reporting and claim-boundary readiness audit")
        st.caption("Reporting-plan documentation only. The workflow receives no result values and verifies no finding.")
        with st.expander("Results reporting and claim-boundary readiness workflow"):
            st.download_button("Download results-reporting template", create_results_reporting_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_results_reporting_template.csv", "text/csv", key="inclusive_results_reporting_template_download")
            reporting_upload = st.file_uploader("Upload results-reporting plan CSV", type=["csv"], key="inclusive_results_reporting_upload")
            if reporting_upload is not None:
                try:
                    reporting_data = load_results_reporting_csv(reporting_upload)
                except ValueError as error:
                    st.error(f"Results-reporting validation failed: {error}")
                else:
                    reporting_versions = reporting_data["instrument_version"].drop_duplicates().tolist()
                    selected_reporting_version = st.selectbox("Version for results-reporting audit", reporting_versions, key="inclusive_results_reporting_version")
                    reporting_audit = audit_results_reporting(reporting_data, selected_reporting_version)
                    st.warning(str(reporting_audit["interpretation"]))
                    for title, key in (("Reporting summary", "results_reporting_summary"), ("Reporting prompts", "results_reporting_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(reporting_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download results-reporting summary", "results_reporting_summary", "inclusive_results_reporting_summary.csv"), ("Download results-reporting prompts", "results_reporting_prompts", "inclusive_results_reporting_prompts.csv"), ("Download reporting research questions", "research_question_candidates", "inclusive_results_reporting_questions.csv")):
                        st.download_button(label, reporting_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_results_reporting_{key}_download")
        st.markdown("#### Claim-evidence traceability readiness audit")
        st.caption("Evidence-link documentation only. The workflow reads no result values and does not verify claim truth.")
        with st.expander("Claim-evidence traceability readiness workflow"):
            st.download_button("Download claim-traceability template", create_claim_traceability_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_claim_traceability_template.csv", "text/csv", key="inclusive_claim_traceability_template_download")
            traceability_upload = st.file_uploader("Upload claim-traceability CSV", type=["csv"], key="inclusive_claim_traceability_upload")
            if traceability_upload is not None:
                try:
                    traceability_data = load_claim_traceability_csv(traceability_upload)
                except ValueError as error:
                    st.error(f"Claim-traceability validation failed: {error}")
                else:
                    traceability_versions = traceability_data["instrument_version"].drop_duplicates().tolist()
                    selected_traceability_version = st.selectbox("Version for claim-traceability audit", traceability_versions, key="inclusive_claim_traceability_version")
                    traceability_audit = audit_claim_traceability(traceability_data, selected_traceability_version)
                    st.warning(str(traceability_audit["interpretation"]))
                    for title, key in (("Traceability summary", "claim_traceability_summary"), ("Traceability prompts", "claim_traceability_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(traceability_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download claim-traceability summary", "claim_traceability_summary", "inclusive_claim_traceability_summary.csv"), ("Download claim-traceability prompts", "claim_traceability_prompts", "inclusive_claim_traceability_prompts.csv"), ("Download traceability research questions", "research_question_candidates", "inclusive_claim_traceability_questions.csv")):
                        st.download_button(label, traceability_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_claim_traceability_{key}_download")
        st.markdown("#### Release package readiness audit")
        st.caption("Pre-release documentation only. The workflow does not inspect, approve, upload, or publish files.")
        with st.expander("Release package readiness workflow"):
            st.download_button("Download release-readiness template", create_release_readiness_template().to_csv(index=False).encode("utf-8-sig"), "inclusive_release_readiness_template.csv", "text/csv", key="inclusive_release_readiness_template_download")
            release_upload = st.file_uploader("Upload release-readiness CSV", type=["csv"], key="inclusive_release_readiness_upload")
            if release_upload is not None:
                try:
                    release_data = load_release_readiness_csv(release_upload)
                except ValueError as error:
                    st.error(f"Release-readiness validation failed: {error}")
                else:
                    release_versions = release_data["instrument_version"].drop_duplicates().tolist()
                    selected_release_version = st.selectbox("Version for release-readiness audit", release_versions, key="inclusive_release_readiness_version")
                    release_audit = audit_release_readiness(release_data, selected_release_version)
                    st.warning(str(release_audit["interpretation"]))
                    for title, key in (("Release summary", "release_readiness_summary"), ("Release prompts", "release_readiness_prompts"), ("Research question candidates", "research_question_candidates")):
                        st.markdown(f"**{title}**")
                        st.dataframe(release_audit[key], width="stretch", hide_index=True)
                    for label, key, filename in (("Download release-readiness summary", "release_readiness_summary", "inclusive_release_readiness_summary.csv"), ("Download release-readiness prompts", "release_readiness_prompts", "inclusive_release_readiness_prompts.csv"), ("Download release research questions", "research_question_candidates", "inclusive_release_readiness_questions.csv")):
                        st.download_button(label, release_audit[key].to_csv(index=False).encode("utf-8-sig"), filename, "text/csv", key=f"inclusive_release_readiness_{key}_download")
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
