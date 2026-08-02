"""Premium research-first Streamlit web platform for OpenPreEduLab.

Run from the repository root with:
``streamlit run app/streamlit_app.py``.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.allocation import (  # noqa: E402
    REQUIRED_COLUMNS,
    calculate_prai_score,
    evaluate_level,
    load_data,
    normalize_indicators,
    prepare_indicators,
)
from models.equity import generate_equity_report  # noqa: E402
from visualization.resource_allocation_plot import (  # noqa: E402
    calculate_dimension_scores,
    plot_dimension_radar,
    plot_resource_allocation_ranking,
    plot_score_heatmap,
    plot_trend_analysis,
)


SAMPLE_PATH = PROJECT_ROOT / "datasets" / "sample_preschool_data.csv"
NAV_ITEMS = [
    "Overview",
    "Data",
    "PRAI",
    "Equity",
    "Efficiency",
    "Forecast",
    "Simulation",
    "AI Interpretation",
    "Report",
    "Settings",
]


def _inject_design_system() -> None:
    """Apply the shared visual language for the landing page and platform."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600&display=swap');
        :root { --ink:#10233f; --muted:#667085; --line:#e8edf4; --paper:#fbfcfe; --blue:#1d4ed8; --softblue:#edf4ff; --green:#16a36a; }
        .stApp { background: var(--paper); color: var(--ink); font-family: 'Manrope', sans-serif; }
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { max-width: 1280px; padding: 1.4rem 3.4rem 4rem; }
        h1,h2,h3 { font-family: 'Manrope', sans-serif !important; letter-spacing:-.045em; color:var(--ink); }
        .landing-nav { position:sticky; top:0; z-index:10; display:flex; align-items:center; justify-content:space-between; background:rgba(251,252,254,.82); backdrop-filter:blur(18px); border:1px solid rgba(232,237,244,.85); border-radius:18px; padding:12px 16px; margin-bottom:28px; }
        .brand { font-weight:800; letter-spacing:-.05em; font-size:20px; color:var(--ink); } .brand-dot{color:var(--blue)}
        .nav-links { color:#667085; font-size:12px; letter-spacing:.01em; display:flex; gap:22px; }
        .eyebrow { color:var(--blue); font:500 11px 'DM Mono',monospace; text-transform:uppercase; letter-spacing:.12em; margin-bottom:18px; }
        .hero-kicker { display:inline-flex; border:1px solid #d9e5fb; background:#f2f6fd; color:#315ca8; border-radius:99px; padding:7px 11px; font:500 11px 'DM Mono',monospace; margin-bottom:28px; }
        .hero-title { font-size:clamp(46px,6vw,82px); line-height:.98; font-weight:800; letter-spacing:-.07em; margin:0 0 25px; max-width:720px; }
        .hero-title em { font-family:'Playfair Display',serif; font-weight:500; }
        .hero-copy { color:#59677b; font-size:18px; line-height:1.7; max-width:610px; margin-bottom:25px; }
        .hero-shell { min-height:690px; display:flex; flex-direction:column; justify-content:center; }
        .hero-art { min-height:520px; position:relative; overflow:hidden; border-radius:34px; background:linear-gradient(145deg,#dce7f7 0%,#f6f8fc 47%,#dce8fb 100%); border:1px solid #e2e8f2; box-shadow:0 28px 80px rgba(31,57,94,.12); }
        .hero-art:before { content:''; position:absolute; inset:-20%; background:radial-gradient(circle at 18% 30%,rgba(59,130,246,.38),transparent 24%),radial-gradient(circle at 76% 18%,rgba(15,49,91,.26),transparent 29%),radial-gradient(circle at 68% 78%,rgba(110,162,235,.34),transparent 30%); filter:blur(12px); }
        .art-window { position:absolute; width:68%; height:51%; top:10%; left:13%; border:1px solid rgba(255,255,255,.62); background:rgba(255,255,255,.22); backdrop-filter:blur(18px); border-radius:25px; transform:rotate(-7deg); }
        .policy-sheet { position:absolute; right:9%; top:20%; width:45%; height:56%; border-radius:14px; background:linear-gradient(150deg,rgba(255,255,255,.88),rgba(237,244,253,.48)); box-shadow:0 25px 40px rgba(24,54,94,.17); transform:rotate(8deg); padding:26px; }
        .policy-sheet:before,.policy-sheet:after { content:''; display:block; height:7px; border-radius:8px; background:#c8d7ea; margin-bottom:13px; } .policy-sheet:after{width:64%;}
        .data-orbit { position:absolute; width:240px; height:240px; left:8%; bottom:5%; border:1px solid rgba(29,78,216,.35); border-radius:50%; }
        .data-orbit:before,.data-orbit:after { content:''; position:absolute; width:13px; height:13px; background:#2360c5; border-radius:50%; box-shadow:66px -32px 0 #7da8e7,140px -78px 0 #1d4ed8,176px -11px 0 #8bb4eb; } .data-orbit:before{left:15px;bottom:58px}.data-orbit:after{left:45px;bottom:36px;background:#a0c0ef;}
        .chart-line { position:absolute; width:61%; height:35%; left:20%; bottom:13%; border-left:2px solid rgba(29,78,216,.36); border-bottom:2px solid rgba(29,78,216,.36); transform:rotate(-1deg); } .chart-line:after { content:''; position:absolute; width:92%; height:52%; left:4%; bottom:8%; border-top:3px solid #1d4ed8; border-radius:50% 50% 0 0; transform:skewY(-22deg); }
        .floating-label { position:absolute; bottom:8%; right:8%; border:1px solid rgba(255,255,255,.8); background:rgba(255,255,255,.62); backdrop-filter:blur(12px); border-radius:12px; padding:12px 14px; color:#31507b; font:500 10px 'DM Mono',monospace; }
        .section { padding:125px 0 18px; } .section-title { font-size:clamp(32px,4vw,54px); line-height:1.05; margin:0 0 16px; max-width:760px; } .section-copy { color:var(--muted); max-width:610px; line-height:1.75; }
        .glass-card { min-height:220px; border:1px solid rgba(223,230,240,.92); background:linear-gradient(145deg,rgba(255,255,255,.92),rgba(246,249,253,.76)); border-radius:22px; padding:25px; box-shadow:0 12px 30px rgba(16,35,63,.045); transition:transform .25s ease,box-shadow .25s ease; } .glass-card:hover { transform:translateY(-6px); box-shadow:0 22px 40px rgba(16,35,63,.1); } .card-icon { font-size:19px; color:var(--blue); margin-bottom:42px; } .glass-card h3{font-size:19px;margin:0 0 10px}.glass-card p{font-size:13px;color:var(--muted);line-height:1.65;margin:0}
        .comparison { border-radius:28px; padding:32px; background:#f2f6fb; border:1px solid #e4ebf5; } .flow-stack{font:500 12px 'DM Mono',monospace;color:#48627f;line-height:2.25}.flow-stack b{color:var(--ink)}
        .timeline { display:flex; align-items:center; gap:8px; overflow-x:auto; padding:25px 0; } .timeline-step { min-width:112px; text-align:center; color:#506078; font-size:11px; } .timeline-dot { width:38px;height:38px;display:grid;place-items:center;margin:0 auto 10px;border-radius:50%;background:#edf4ff;color:var(--blue);font:500 11px 'DM Mono',monospace;border:1px solid #d8e6ff; }.timeline-line{width:34px;height:1px;background:#cad6e6;flex:none}
        .quote-block { padding:130px 8% 120px; text-align:center; } .quote-block p{font:500 clamp(32px,4.5vw,64px)/1.12 'Playfair Display',serif;letter-spacing:-.045em;color:#1a3154;margin:0}.quote-block span{display:block;color:#6d7e94;font:500 11px 'DM Mono',monospace;letter-spacing:.12em;text-transform:uppercase;margin-top:26px}
        .launch-panel { margin:60px 0 90px; padding:78px 20px; border-radius:30px; text-align:center; background:linear-gradient(135deg,#102b55,#1d4ed8); color:white; box-shadow:0 30px 70px rgba(29,78,216,.21);}.launch-panel h2{color:white!important;font-size:44px;margin:0 0 14px}.launch-panel p{color:#d9e8ff;max-width:560px;margin:0 auto 22px;line-height:1.7}
        .stButton>button { border:0!important; border-radius:12px!important; font-family:'Manrope',sans-serif!important; font-weight:700!important; padding:.72rem 1.05rem!important; background:#1d4ed8!important; color:white!important; box-shadow:none!important; transition:transform .2s ease,background .2s ease!important; } .stButton>button:hover{transform:translateY(-2px);background:#1743bc!important}.secondary-button .stButton>button{background:#eef3fa!important;color:#193a69!important}
        [data-testid='stSidebar'] { background:#f7f9fc; border-right:1px solid #e8edf4; } [data-testid='stSidebar'] .block-container{padding:1.6rem 1rem;} [data-testid='stSidebar'] .stRadio label{font-size:13px;color:#5f6e82;padding:7px 3px;}
        .dashboard-top { padding:12px 0 28px; } .dashboard-top h1{font-size:42px;margin:0 0 6px}.dashboard-top p{color:#758197;margin:0}.prototype-pill{display:inline-block;color:#3560a8;background:#edf4ff;border:1px solid #d9e7ff;border-radius:99px;padding:6px 9px;font:500 10px 'DM Mono',monospace;margin-bottom:13px}
        .metric-card { padding:20px; border:1px solid #e8edf4; background:white; border-radius:18px; min-height:118px; }.metric-label{font:500 10px 'DM Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:#7d8999}.metric-value{font-size:29px;font-weight:800;letter-spacing:-.06em;color:#162e53;margin:10px 0 4px}.metric-note{font-size:11px;color:#7a8798}.status-ok{color:#159565}.status-muted{color:#8b96a6}
        .dashboard-pipeline{display:flex;align-items:center;gap:7px;overflow-x:auto;padding:22px 0 6px}.pipeline-node{min-width:94px;text-align:center;font-size:11px;color:#637086}.pipeline-icon{width:38px;height:38px;border-radius:50%;margin:0 auto 8px;display:grid;place-items:center;background:#edf8f3;border:1px solid #c9ead8;color:#16915f}.pipeline-off .pipeline-icon{background:#f2f4f7;border-color:#e2e6ec;color:#9aa5b4}.pipeline-arrow{color:#b7c1ce}
        .module-card{border:1px solid #e8edf4;background:white;border-radius:20px;padding:22px;min-height:175px}.module-card h3{font-size:18px;margin:16px 0 8px}.module-card p{font-size:12px;color:#748095;line-height:1.65}.module-tag{font:500 10px 'DM Mono',monospace;color:#4370b9}.quiet-note{border-left:3px solid #8db3ea;background:#f3f7fd;padding:14px 16px;color:#55708f;font-size:12px;border-radius:0 12px 12px 0}
        @media(max-width:760px){.block-container{padding:1rem 1.1rem 3rem}.nav-links{display:none}.hero-shell{min-height:auto}.hero-art{min-height:390px}.section{padding-top:78px}.quote-block{padding:85px 4%}.timeline{padding-bottom:12px}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _load_uploaded_csv(uploaded_file: object) -> pd.DataFrame:
    """Validate an uploaded CSV through the allocation engine."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temporary_file:
        path = Path(temporary_file.name)
        temporary_file.write(uploaded_file.getvalue())
    try:
        return load_data(path)
    finally:
        path.unlink(missing_ok=True)


@st.cache_data(show_spinner=False)
def _sample_data() -> pd.DataFrame:
    """Load the repository sample dataset once per app session."""
    return load_data(PROJECT_ROOT / "datasets" / "sample_preschool_data.csv")


def _metric(label: str, value: str, note: str, status: str = "") -> str:
    """Return a compact dashboard metric-card fragment."""
    return f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note {status}'>{note}</div></div>"


def _module_card(icon: str, title: str, description: str, tag: str) -> str:
    """Return a reusable research-module card."""
    return f"<div class='module-card'><div class='module-tag'>{icon} &nbsp; {tag}</div><h3>{title}</h3><p>{description}</p></div>"


def _switch_to_platform() -> None:
    """Persist the transition from landing page to research platform."""
    st.session_state["view"] = "platform"
    st.rerun()


def _landing_page() -> None:
    """Render the editorial, scroll-led product landing page."""
    st.markdown(
        """
        <div class='landing-nav'>
          <div class='brand'>OpenPreEdu<span class='brand-dot'>Lab</span></div>
          <div class='nav-links'><span>Research</span><span>Workflow</span><span>Modules</span><span>Documentation</span><span>GitHub</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    hero_left, hero_right = st.columns([1.04, 0.96], gap="large")
    with hero_left:
        st.markdown(
            """
            <div class='hero-shell'>
              <div class='hero-kicker'>OPEN-SOURCE · RESEARCH PROTOTYPE v0.1</div>
              <h1 class='hero-title'>Research infrastructure for <em>preschool</em> education.</h1>
              <p class='hero-copy'>Integrating educational policy, statistical modelling and AI-assisted interpretation into one reproducible research workflow.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        action_left, action_right = st.columns([0.46, 0.54])
        with action_left:
            st.button("Launch Platform", on_click=_switch_to_platform, use_container_width=True)
        with action_right:
            st.markdown("<div class='secondary-button'>", unsafe_allow_html=True)
            st.button("View Research Workflow", key="hero_workflow", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    with hero_right:
        st.markdown(
            """
            <div class='hero-art' aria-label='Education policy and research data visual'>
              <div class='art-window'></div><div class='policy-sheet'></div><div class='data-orbit'></div>
              <div class='chart-line'></div><div class='floating-label'>EDUCATION × POLICY × DATA<br>REPRODUCIBLE RESEARCH</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section'><div class='eyebrow'>01 — Research challenge</div><h2 class='section-title'>From isolated analysis to a reusable research workflow.</h2><p class='section-copy'>OpenPreEduLab treats statistical analysis as research infrastructure: transparent inputs, documented assumptions, modular models, and interpretable outputs.</p></div>", unsafe_allow_html=True)
    legacy, platform = st.columns(2, gap="large")
    with legacy:
        st.markdown("<div class='comparison'><div class='eyebrow'>Traditional workflow</div><div class='flow-stack'><b>Manual reading</b><br>↓<br>SPSS analysis<br>↓<br>Single paper<br>↓<br>End of workflow</div></div>", unsafe_allow_html=True)
    with platform:
        st.markdown("<div class='comparison'><div class='eyebrow'>OpenPreEduLab</div><div class='flow-stack'><b>Dataset</b><br>↓<br>Models · Simulation · Interpretation<br>↓<br><b>Reusable research output</b></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section'><div class='eyebrow'>02 — Core modules</div><h2 class='section-title'>A coherent research stack, not a collection of tools.</h2></div>", unsafe_allow_html=True)
    modules = [
        ("01", "Research Intelligence", "Structured support for literature, policy, variables, and research-gap evidence."),
        ("02", "Statistical Modelling", "PRAI, equity, efficiency, and forecast modules with explicit assumptions."),
        ("03", "Policy Simulation", "Transparent scenario comparison for demographic and fiscal conditions."),
        ("04", "LLM Interpretation", "Bounded research interpretation that does not replace statistical analysis."),
    ]
    cols = st.columns(4, gap="medium")
    for column, (number, title, copy) in zip(cols, modules):
        with column:
            st.markdown(f"<div class='glass-card'><div class='card-icon'>{number}</div><h3>{title}</h3><p>{copy}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='section'><div class='eyebrow'>03 — Research workflow</div><h2 class='section-title'>A traceable path from dataset to research report.</h2></div>", unsafe_allow_html=True)
    steps = ["Dataset", "Schema", "PRAI", "Equity", "Efficiency", "Forecast", "Simulation", "AI Interpretation", "Report"]
    timeline = "".join(f"<div class='timeline-step'><div class='timeline-dot'>{index + 1:02}</div>{step}</div>" + ("<div class='timeline-line'></div>" if index < len(steps) - 1 else "") for index, step in enumerate(steps))
    st.markdown(f"<div class='timeline'>{timeline}</div>", unsafe_allow_html=True)
    st.markdown("<div class='quote-block'><p>Research should not end with publication.<br>Every study should become reusable research infrastructure.</p><span>OpenPreEduLab research philosophy</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='launch-panel'><h2>Ready to enter the research workspace?</h2><p>Explore the documented prototype workflow with the repository sample dataset. Real data remain subject to provenance and definition review.</p></div>", unsafe_allow_html=True)
    launch_left, launch_middle, launch_right = st.columns([0.35, 0.3, 0.35])
    with launch_middle:
        st.button("Launch OpenPreEduLab", key="footer_launch", on_click=_switch_to_platform, use_container_width=True)


def _dashboard_header(data: pd.DataFrame) -> None:
    """Render the dashboard overview header and sample-data metrics."""
    st.markdown("<div class='dashboard-top'><div class='prototype-pill'>RESEARCH PROTOTYPE v0.1</div><h1>Welcome back.</h1><p>A calm workspace for reproducible preschool education research.</p></div>", unsafe_allow_html=True)
    years = int(data["year"].nunique())
    cities = int(data["city"].nunique())
    cards = st.columns(4, gap="medium")
    values = [
        ("Cities", str(cities), "sample research localities", ""),
        ("Years", str(years), "longitudinal coverage", ""),
        ("Observations", str(len(data)), "city-year records", ""),
        ("Schema", "Ready", "validated sample input", "status-ok"),
    ]
    for column, arguments in zip(cards, values):
        with column:
            st.markdown(_metric(*arguments), unsafe_allow_html=True)


def _workflow_strip() -> None:
    """Render the dashboard's horizontal pipeline state."""
    nodes = [("Data", True), ("Allocation", True), ("Equity", True), ("Efficiency", False), ("Forecast", False), ("Simulation", False), ("Report", False)]
    fragments = []
    for index, (label, complete) in enumerate(nodes):
        class_name = "" if complete else " pipeline-off"
        icon = "✓" if complete else "·"
        fragments.append(f"<div class='pipeline-node{class_name}'><div class='pipeline-icon'>{icon}</div>{label}</div>")
        if index < len(nodes) - 1:
            fragments.append("<div class='pipeline-arrow'>→</div>")
    st.markdown("<div class='eyebrow' style='margin-top:36px'>Research workflow</div><div class='dashboard-pipeline'>" + "".join(fragments) + "</div>", unsafe_allow_html=True)


def _data_page(data: pd.DataFrame, source: str) -> None:
    """Render data input, preview, and governance boundaries."""
    st.markdown("<div class='eyebrow'>Data layer</div><h2>Data with visible assumptions.</h2>", unsafe_allow_html=True)
    if source == "Sample dataset":
        st.markdown("<div class='quiet-note'>This is a synthetic sample dataset for software demonstration. Its results are not real-world findings or policy evaluation evidence.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='quiet-note'>Uploaded data are user-provided inputs. A valid schema does not establish source provenance, definition compatibility, or permission for substantive research claims.</div>", unsafe_allow_html=True)
    st.write("")
    present = len(set(REQUIRED_COLUMNS) & set(data.columns))
    left, right = st.columns([0.33, 0.67], gap="large")
    with left:
        st.markdown(_metric("Schema fields", f"{present}/{len(REQUIRED_COLUMNS)}", "existing engine requirements", "status-ok"), unsafe_allow_html=True)
        st.markdown("<div class='module-card'><div class='module-tag'>GOVERNANCE</div><h3>Research data gate</h3><p>Real data must progress from raw source to staging, independent review, and processed release. The interface will not impute, smooth, or silently remap variables.</p></div>", unsafe_allow_html=True)
    with right:
        with st.expander("Inspect input records", expanded=True):
            st.dataframe(data, use_container_width=True, hide_index=True)


def _prai_page(data: pd.DataFrame) -> pd.DataFrame:
    """Run the documented MVP PRAI and present a calm research result page."""
    st.markdown("<div class='eyebrow'>Statistical modelling</div><h2>Preschool Resource Allocation Index.</h2><p class='section-copy'>Equal dimension weights are the documented MVP default. Scores are comparable only within the jointly normalised input sample.</p>", unsafe_allow_html=True)
    results = calculate_prai_score(data, weight_method="equal")
    results["allocation_level"] = evaluate_level(results["resource_allocation_score"])
    year = st.selectbox("Reference year", sorted(results["year"].unique()), key="prai_year")
    slice_ = results.loc[results["year"] == year].sort_values("resource_allocation_score", ascending=False)
    summary = st.columns(3, gap="medium")
    for column, values in zip(summary, [("Highest score", f"{slice_.iloc[0]['resource_allocation_score']:.1f}", slice_.iloc[0]["city"], ""), ("Sample mean", f"{slice_['resource_allocation_score'].mean():.1f}", "selected cross-section", ""), ("Model status", "MVP", "equal-dimension weighting", "status-ok")]):
        with column: st.markdown(_metric(*values), unsafe_allow_html=True)
    figure, axis = plt.subplots(figsize=(10, 5))
    plot_resource_allocation_ranking(results, year=int(year), ax=axis)
    st.pyplot(figure, clear_figure=True)
    with st.expander("Inspect calculated PRAI results"):
        st.dataframe(results.sort_values(["year", "resource_allocation_score"], ascending=[True, False]), use_container_width=True, hide_index=True)
    st.download_button("Download PRAI results", results.to_csv(index=False).encode("utf-8"), "allocation_result.csv", "text/csv")
    return results


def _equity_page(results: pd.DataFrame) -> None:
    """Render bounded, descriptive equity indicators."""
    st.markdown("<div class='eyebrow'>Distribution analysis</div><h2>Educational equity evaluation.</h2><p class='section-copy'>These measures describe inequality in observed PRAI scores for a shared reference year. They do not establish causal mechanisms or policy effects.</p>", unsafe_allow_html=True)
    year = st.selectbox("Reference year", sorted(results["year"].unique()), key="equity_year")
    report = generate_equity_report(results, year=int(year))
    cards = st.columns(3, gap="medium")
    for column, (_, row) in zip(cards, report.iterrows()):
        with column:
            st.markdown(_metric(row["indicator"], f"{row['value']:.3f}", row["equity_level"], "status-ok" if row["equity_level"] == "Excellent Equity" else ""), unsafe_allow_html=True)
    st.write("")
    st.dataframe(report, use_container_width=True, hide_index=True)


def _visualisation_page(data: pd.DataFrame, results: pd.DataFrame) -> None:
    """Show the reusable research visualisation suite."""
    st.markdown("<div class='eyebrow'>Research visualisation</div><h2>Readable evidence, not decorative dashboards.</h2>", unsafe_allow_html=True)
    year = st.selectbox("Visualisation year", sorted(results["year"].unique()), key="visual_year")
    left, right = st.columns(2, gap="large")
    with left:
        figure, axis = plt.subplots(figsize=(8, 5))
        plot_resource_allocation_ranking(results, year=int(year), ax=axis)
        st.pyplot(figure, clear_figure=True)
    with right:
        figure, axis = plt.subplots(figsize=(8, 5))
        plot_score_heatmap(results, ax=axis)
        st.pyplot(figure, clear_figure=True)
    figure, axis = plt.subplots(figsize=(10, 5))
    plot_trend_analysis(results, ax=axis)
    st.pyplot(figure, clear_figure=True)
    dimensions = calculate_dimension_scores(normalize_indicators(prepare_indicators(data)))
    cities = st.multiselect("Cities for dimension profile", sorted(dimensions["city"].unique()), default=sorted(dimensions["city"].unique())[:3])
    if cities:
        figure, axis = plt.subplots(figsize=(7, 7), subplot_kw={"projection": "polar"})
        plot_dimension_radar(dimensions, year=int(year), cities=cities, ax=axis)
        st.pyplot(figure, clear_figure=True)


def _coming_soon_page(title: str, tag: str, detail: str) -> None:
    """Render an honest module-integration page without fictitious output."""
    st.markdown(f"<div class='eyebrow'>{tag}</div><h2>{title}</h2><p class='section-copy'>{detail}</p>", unsafe_allow_html=True)
    st.markdown("<div class='quiet-note'>The underlying research module is retained in the repository. Interactive controls will be enabled only after a definition-compatible processed dataset is available and the module-specific input assumptions are visible to the researcher.</div>", unsafe_allow_html=True)


def _report_page() -> None:
    """Render the bounded report-output page."""
    st.markdown("<div class='eyebrow'>Research output</div><h2>Research reports with traceable inputs.</h2><p class='section-copy'>The pipeline can generate structured outputs from the sample workflow. Real-world reports must retain source provenance, model assumptions, validation notes, and interpretation limits.</p>", unsafe_allow_html=True)
    st.markdown(_module_card("↗", "Report generation", "Use the existing pipeline for reproducible tables and a research summary. The platform will not represent generated text as an automatically validated paper.", "PIPELINE OUTPUT"), unsafe_allow_html=True)


def _settings_page() -> None:
    """Render project provenance and version information."""
    st.markdown("<div class='eyebrow'>Platform settings</div><h2>Prototype configuration.</h2>", unsafe_allow_html=True)
    st.markdown(_module_card("◌", "OpenPreEduLab v0.1", "Open-source AI research infrastructure prototype for preschool education research. Current interface uses sample data by default.", "RESEARCH PROTOTYPE"), unsafe_allow_html=True)
    st.caption("See docs/Data_Review_Protocol.md and docs/User_Interface_Guide.md for governance and usage boundaries.")


def _dashboard() -> None:
    """Render the authenticated-style research workspace."""
    with st.sidebar:
        st.markdown("<div class='brand' style='font-size:21px;margin:5px 6px 28px'>OpenPreEdu<span class='brand-dot'>Lab</span></div>", unsafe_allow_html=True)
        st.caption("RESEARCH WORKSPACE")
        page = st.radio("Workflow navigation", NAV_ITEMS, label_visibility="collapsed")
        st.divider()
        source = st.radio("Research input", ["Sample dataset", "Upload CSV"], label_visibility="collapsed")
        upload = st.file_uploader("Upload PRAI CSV", type=["csv"], label_visibility="collapsed") if source == "Upload CSV" else None
        st.caption("raw → staging → review → processed")
        if st.button("← Back to landing", use_container_width=True):
            st.session_state["view"] = "landing"
            st.rerun()

    try:
        if source == "Sample dataset":
            data = _sample_data()
        elif upload is None:
            st.info("Upload a PRAI-compatible CSV or switch to the sample dataset.")
            return
        else:
            data = _load_uploaded_csv(upload)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Input validation failed: {error}")
        return

    if page == "Overview":
        _dashboard_header(data)
        _workflow_strip()
        st.markdown("<div class='eyebrow' style='margin-top:42px'>Quick actions</div>", unsafe_allow_html=True)
        cards = st.columns(3, gap="medium")
        content = [
            ("⌁", "PRAI score", "Calculate documented MVP allocation scores with equal-dimension weights.", "ACTIVE"),
            ("≋", "Equity index", "Describe observed cross-sectional inequality with CV, Gini and Theil.", "ACTIVE"),
            ("◌", "Data gate", "Inspect schema while retaining the research data-governance boundary.", "REQUIRED"),
        ]
        for column, arguments in zip(cards, content):
            with column: st.markdown(_module_card(*arguments), unsafe_allow_html=True)
    elif page == "Data": _data_page(data, source)
    elif page == "PRAI": _prai_page(data)
    elif page == "Equity": _equity_page(calculate_prai_score(data))
    elif page == "Efficiency": _coming_soon_page("Efficiency evaluation.", "DEA MODULE", "DEA methods are implemented in the research codebase. Its interface awaits an approved processed input panel with documented input-output comparability.")
    elif page == "Forecast": _coming_soon_page("Forecast framework.", "FORECAST MODULE", "Population, teacher-demand, and fiscal-requirement forecasting remains a research prototype. It requires a documented historical series before interactive output is meaningful.")
    elif page == "Simulation": _coming_soon_page("Policy simulation.", "SCENARIO MODULE", "Scenario comparison is a transparent research prototype. It must not be used as a real-world policy forecast without calibrated parameters and validated inputs.")
    elif page == "AI Interpretation": _coming_soon_page("AI-assisted interpretation.", "INTERPRETATION LAYER", "LLM output is bounded to model-result interpretation. It does not replace statistical evidence, causal identification, or researcher judgment.")
    elif page == "Report": _report_page()
    else: _settings_page()


def main() -> None:
    """Run the OpenPreEduLab web platform."""
    st.set_page_config(page_title="OpenPreEduLab", page_icon="◌", layout="wide", initial_sidebar_state="expanded")
    _inject_design_system()
    if "view" not in st.session_state:
        st.session_state["view"] = "landing"
    if st.session_state["view"] == "landing":
        _landing_page()
    else:
        _dashboard()


if __name__ == "__main__":
    main()
