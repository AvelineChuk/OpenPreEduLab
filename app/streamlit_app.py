"""Premium research-first Streamlit web platform for OpenPreEduLab.

Run from the repository root with:
``streamlit run app/streamlit_app.py``.
"""

from __future__ import annotations

import sys
import tempfile
import base64
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
from models.efficiency import evaluate_panel_efficiency, prepare_efficiency_data  # noqa: E402
from models.forecast import (  # noqa: E402
    forecast_fiscal_requirement,
    forecast_population,
    forecast_teacher_demand,
)
from models.policy_simulation import simulate_policy_scenarios  # noqa: E402
from llm.deepseek import DeepSeekClient, DeepSeekRequestError, SUPPORTED_MODELS  # noqa: E402
from llm.interpreter import ResearchInterpretationAssistant, create_interpretation_request  # noqa: E402
from reporting.exports import report_to_docx, report_to_pdf  # noqa: E402
from visualization.resource_allocation_plot import (  # noqa: E402
    calculate_dimension_scores,
    plot_dimension_radar,
    plot_resource_allocation_ranking,
    plot_score_heatmap,
    plot_trend_analysis,
)


SAMPLE_PATH = PROJECT_ROOT / "datasets" / "sample_preschool_data.csv"
PRAI_TEMPLATE_PATH = PROJECT_ROOT / "datasets" / "templates" / "prai_input_template.csv"
HERO_IMAGE_PATH = PROJECT_ROOT / "assets" / "hero_children_learning.jpg"
NAV_ITEMS = [
    "Workflow",
    "Data",
    "PRAI",
    "Equity",
    "Visualisation",
    "Efficiency",
    "Forecast",
    "Simulation",
    "AI Interpretation",
    "Inclusive Support",
    "Teacher Development",
    "Reports",
    "Documentation",
    "Settings",
]


def _inject_design_system() -> None:
    """Apply the shared visual language for the landing page and platform."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@500;600&display=swap');
        :root { --ink:#1b2d35; --muted:#68767a; --line:#e8ebe9; --paper:#fdfdfb; --blue:#496b7c; --softblue:#eef4f3; --green:#3f7357; --wood:#b98f62; }
        .stApp { background:linear-gradient(180deg,#fdfcf9 0%,#f7f0e6 38%,#edf3ed 72%,#fbfaf7 100%); color: var(--ink); font-family: 'Manrope', sans-serif; }
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
        .impact-hero { min-height:680px; position:relative; overflow:hidden; display:flex; align-items:center; justify-content:center; text-align:center; border-radius:34px; background:radial-gradient(circle at 50% 35%,#faebd4 0,#eecba2 20%,transparent 45%),radial-gradient(circle at 85% 86%,#547c6c 0,transparent 31%),linear-gradient(135deg,#102c3c,#194458 56%,#476d63); box-shadow:0 32px 80px rgba(15,40,52,.22); }
        .impact-hero:before { content:''; position:absolute; width:110%; height:58%; left:-5%; bottom:-23%; background:#f8eddc; border-radius:50% 50% 0 0 / 58% 58% 0 0; transform:rotate(-4deg); opacity:.94; }
        .impact-hero:after { content:''; position:absolute; inset:0; background:linear-gradient(90deg,rgba(10,34,47,.35),transparent 40%,rgba(14,43,53,.22)); pointer-events:none; }
        .sun-disc { position:absolute; right:10%; top:11%; width:210px; height:210px; border-radius:50%; background:radial-gradient(circle at 34% 32%,#fff8e9,#e9c38d 62%,#c48e58); box-shadow:0 0 80px rgba(255,227,173,.42); z-index:1; opacity:.93; }
        .wood-arch { position:absolute; right:-5%; bottom:0; width:420px; height:350px; border:34px solid rgba(183,133,82,.68); border-bottom:0; border-radius:220px 220px 0 0; z-index:1; transform:rotate(-9deg); box-shadow:inset 0 0 0 1px rgba(255,236,205,.28); }
        .glass-research-card { position:absolute; left:7%; bottom:10%; width:215px; min-height:126px; z-index:4; padding:18px; text-align:left; border-radius:18px; background:rgba(244,249,244,.2); border:1px solid rgba(255,255,255,.35); backdrop-filter:blur(18px); box-shadow:0 18px 38px rgba(5,27,38,.17); color:#eef6ef; transform:rotate(-4deg); }
        .glass-research-card b{display:block;font:500 10px 'DM Mono',monospace;letter-spacing:.1em;color:#dcebdc;margin-bottom:15px}.glass-research-card span{display:block;font-size:13px;line-height:1.45}.mini-bars{display:flex;align-items:flex-end;gap:5px;height:25px;margin-top:12px}.mini-bars i{display:block;width:12px;background:#efcd94;border-radius:4px 4px 0 0}.mini-bars i:nth-child(1){height:9px}.mini-bars i:nth-child(2){height:22px}.mini-bars i:nth-child(3){height:15px}.mini-bars i:nth-child(4){height:25px}.mini-bars i:nth-child(5){height:18px}
        .hero-network { position:absolute; right:7%; bottom:12%; width:230px; height:130px; z-index:2; opacity:.75; }.hero-network:before,.hero-network:after{content:'';position:absolute;height:1px;background:#e5d5b7;transform-origin:left center}.hero-network:before{width:180px;left:18px;top:55px;transform:rotate(-20deg)}.hero-network:after{width:146px;left:35px;top:78px;transform:rotate(19deg)}.hero-network i{position:absolute;width:11px;height:11px;border-radius:50%;background:#f6e1b8;box-shadow:0 0 0 7px rgba(246,225,184,.12)}.hero-network i:nth-child(1){left:10px;top:51px}.hero-network i:nth-child(2){left:100px;top:18px}.hero-network i:nth-child(3){right:10px;top:83px}.hero-network i:nth-child(4){left:104px;bottom:6px;background:#a8d2b4}
        .hero-arc { position:absolute; top:6%; left:50%; width:540px; max-width:92%; transform:translateX(-50%); z-index:2; }
        .hero-center { position:relative; z-index:3; max-width:760px; padding:130px 20px 20px; color:white; }
        .hero-center h1 { color:white!important; font-family:'Playfair Display',serif!important; font-size:clamp(48px,7.2vw,104px); font-weight:600; white-space:nowrap; line-height:.9; margin:12px 0 20px; letter-spacing:-.075em; text-shadow:0 4px 20px rgba(7,28,38,.18); }
        .hero-center p { max-width:530px; margin:0 auto; font-size:17px; line-height:1.65; color:rgba(255,255,255,.82); }
        .hero-flag { display:inline-block; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.26); border-radius:99px; color:#f8eddc; padding:7px 12px; font:500 10px 'DM Mono',monospace; letter-spacing:.12em; }
        .hero-kid-scene { position:absolute; left:50%; bottom:3%; transform:translateX(-50%); width:min(830px,96%); z-index:2; opacity:.98; }
        .hero-side-note { position:absolute; z-index:4; right:5%; bottom:8%; text-align:left; color:#355649; font:500 10px 'DM Mono',monospace; letter-spacing:.06em; line-height:1.65; }
        .hero-orbit { position:absolute; left:7%; top:16%; height:105px; width:105px; border:1px solid rgba(255,255,255,.35); border-radius:50%; z-index:2; } .hero-orbit:after{content:'';position:absolute;width:12px;height:12px;border-radius:50%;background:#f2c784;right:4px;top:20px;box-shadow:-48px 58px 0 #8bb7a3;}
        .hero-actions { margin-top:-45px; position:relative; z-index:5; }
        .hero-art { min-height:520px; position:relative; overflow:hidden; border-radius:34px; background:linear-gradient(145deg,rgba(255,252,246,.78),rgba(229,239,231,.9)),linear-gradient(110deg,#e7d2b7 0%,#f8f1e7 42%,#d9eadc 100%); border:1px solid #e5e3dd; box-shadow:0 28px 80px rgba(61,73,63,.13); }
        .hero-art:before { content:''; position:absolute; inset:-20%; background:radial-gradient(circle at 18% 30%,rgba(184,138,88,.30),transparent 25%),radial-gradient(circle at 78% 22%,rgba(61,115,87,.24),transparent 29%),radial-gradient(circle at 68% 78%,rgba(255,255,255,.58),transparent 31%); filter:blur(14px); }
        .art-window { position:absolute; width:68%; height:51%; top:10%; left:13%; border:1px solid rgba(255,255,255,.62); background:rgba(255,255,255,.22); backdrop-filter:blur(18px); border-radius:25px; transform:rotate(-7deg); }
        .policy-sheet { position:absolute; right:9%; top:20%; width:45%; height:56%; border-radius:14px; background:linear-gradient(150deg,rgba(255,255,255,.88),rgba(245,241,232,.46)); box-shadow:0 25px 40px rgba(74,65,51,.14); transform:rotate(8deg); padding:26px; }
        .policy-sheet:before,.policy-sheet:after { content:''; display:block; height:7px; border-radius:8px; background:#cbd8ce; margin-bottom:13px; } .policy-sheet:after{width:64%;}
        .data-orbit { position:absolute; width:240px; height:240px; left:8%; bottom:5%; border:1px solid rgba(63,115,87,.35); border-radius:50%; }
        .data-orbit:before,.data-orbit:after { content:''; position:absolute; width:13px; height:13px; background:#3f7357; border-radius:50%; box-shadow:66px -32px 0 #9fb99e,140px -78px 0 #557b6a,176px -11px 0 #bed1bc; } .data-orbit:before{left:15px;bottom:58px}.data-orbit:after{left:45px;bottom:36px;background:#c9b08c;}
        .chart-line { position:absolute; width:61%; height:35%; left:20%; bottom:13%; border-left:2px solid rgba(63,115,87,.36); border-bottom:2px solid rgba(63,115,87,.36); transform:rotate(-1deg); } .chart-line:after { content:''; position:absolute; width:92%; height:52%; left:4%; bottom:8%; border-top:3px solid #3f7357; border-radius:50% 50% 0 0; transform:skewY(-22deg); }
        .floating-label { position:absolute; bottom:8%; right:8%; border:1px solid rgba(255,255,255,.8); background:rgba(255,255,255,.62); backdrop-filter:blur(12px); border-radius:12px; padding:12px 14px; color:#476957; font:500 10px 'DM Mono',monospace; }
        .section { padding:94px 7% 34px; margin:44px 0 22px; border:1px solid rgba(218,213,199,.65); border-radius:30px; background:linear-gradient(115deg,rgba(255,250,243,.88),rgba(238,244,237,.86)); box-shadow:0 18px 48px rgba(83,73,53,.05); } .section-title { font-size:clamp(32px,4vw,54px); line-height:1.05; margin:0 0 16px; max-width:760px; } .section-copy { color:var(--muted); max-width:610px; line-height:1.75; }
        .glass-card { min-height:220px; border:1px solid rgba(219,222,211,.92); background:linear-gradient(145deg,rgba(255,255,255,.88),rgba(247,240,229,.72)); border-radius:22px; padding:25px; box-shadow:0 12px 30px rgba(70,79,58,.06); transition:transform .25s ease,box-shadow .25s ease; } .glass-card:hover { transform:translateY(-6px); box-shadow:0 22px 40px rgba(63,91,72,.12); } .card-icon { font-size:19px; color:#3f7357; margin-bottom:42px; } .glass-card h3{font-size:19px;margin:0 0 10px}.glass-card p{font-size:13px;color:var(--muted);line-height:1.65;margin:0}
        .comparison { border-radius:28px; padding:32px; background:linear-gradient(145deg,#fffaf2,#e9f1e9); border:1px solid #e1e2d8; } .flow-stack{font:500 12px 'DM Mono',monospace;color:#547263;line-height:2.25}.flow-stack b{color:var(--ink)}
        .timeline { display:flex; align-items:center; gap:8px; overflow-x:auto; padding:25px 0; } .timeline-step { min-width:112px; text-align:center; color:#506078; font-size:11px; } .timeline-dot { width:38px;height:38px;display:grid;place-items:center;margin:0 auto 10px;border-radius:50%;background:#edf4ff;color:var(--blue);font:500 11px 'DM Mono',monospace;border:1px solid #d8e6ff; }.timeline-line{width:34px;height:1px;background:#cad6e6;flex:none}
        .quote-block { padding:130px 8% 120px; text-align:center; border-radius:34px; background:radial-gradient(circle at 50% 0%,#fff6e8,transparent 52%),linear-gradient(135deg,#edf4ee,#dcebdd); } .quote-block p{font:500 clamp(32px,4.5vw,64px)/1.12 'Playfair Display',serif;letter-spacing:-.045em;color:#244638;margin:0}.quote-block span{display:block;color:#62816e;font:500 11px 'DM Mono',monospace;letter-spacing:.12em;text-transform:uppercase;margin-top:26px}
        .launch-panel { margin:60px 0 90px; padding:78px 20px; border-radius:30px; text-align:center; background:linear-gradient(135deg,#1b3d46,#48755c); color:white; box-shadow:0 30px 70px rgba(39,82,60,.21);}.launch-panel h2{color:white!important;font-size:44px;margin:0 0 14px}.launch-panel p{color:#e4f1e6;max-width:560px;margin:0 auto 22px;line-height:1.7}
        .stButton>button { border:0!important; border-radius:12px!important; font-family:'Manrope',sans-serif!important; font-weight:700!important; padding:.72rem 1.05rem!important; background:#1d4ed8!important; color:white!important; box-shadow:none!important; transition:transform .2s ease,background .2s ease!important; } .stButton>button:hover{transform:translateY(-2px);background:#1743bc!important}.secondary-button .stButton>button{background:#eef3fa!important;color:#193a69!important}
        [data-testid='stSidebar'] { background:#f7f9fc; border-right:1px solid #e8edf4; } [data-testid='stSidebar'] .block-container{padding:1.6rem 1rem;} [data-testid='stSidebar'] .stRadio label{font-size:13px;color:#5f6e82;padding:7px 3px;}
        .dashboard-top { padding:12px 0 28px; } .dashboard-top h1{font-size:42px;margin:0 0 6px}.dashboard-top p{color:#758197;margin:0}.prototype-pill{display:inline-block;color:#3560a8;background:#edf4ff;border:1px solid #d9e7ff;border-radius:99px;padding:6px 9px;font:500 10px 'DM Mono',monospace;margin-bottom:13px}
        .metric-card { padding:20px; border:1px solid #e8edf4; background:white; border-radius:18px; min-height:118px; }.metric-label{font:500 10px 'DM Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:#7d8999}.metric-value{font-size:29px;font-weight:800;letter-spacing:-.06em;color:#162e53;margin:10px 0 4px}.metric-note{font-size:11px;color:#7a8798}.status-ok{color:#159565}.status-muted{color:#8b96a6}
        .dashboard-pipeline{display:flex;align-items:center;gap:7px;overflow-x:auto;padding:22px 0 6px}.pipeline-node{min-width:94px;text-align:center;font-size:11px;color:#637086}.pipeline-icon{width:38px;height:38px;border-radius:50%;margin:0 auto 8px;display:grid;place-items:center;background:#edf8f3;border:1px solid #c9ead8;color:#16915f}.pipeline-off .pipeline-icon{background:#f2f4f7;border-color:#e2e6ec;color:#9aa5b4}.pipeline-arrow{color:#b7c1ce}
        .module-card{border:1px solid #e8edf4;background:white;border-radius:20px;padding:22px;min-height:175px}.module-card h3{font-size:18px;margin:16px 0 8px}.module-card p{font-size:12px;color:#748095;line-height:1.65}.module-tag{font:500 10px 'DM Mono',monospace;color:#4370b9}.quiet-note{border-left:3px solid #8db3ea;background:#f3f7fd;padding:14px 16px;color:#55708f;font-size:12px;border-radius:0 12px 12px 0}
        @media(max-width:760px){.block-container{padding:1rem 1.1rem 3rem}.nav-links{display:none}.hero-shell{min-height:auto}.hero-art{min-height:390px}.section{padding-top:78px}.quote-block{padding:85px 4%}.timeline{padding-bottom:12px}}
        @media(max-width:760px){.impact-hero{min-height:590px}.hero-center{padding-top:100px}.hero-side-note{display:none}.hero-kid-scene{width:115%;bottom:6%}}
        </style>
        """,
        unsafe_allow_html=True,
    )
    if HERO_IMAGE_PATH.exists():
        encoded_image = base64.b64encode(HERO_IMAGE_PATH.read_bytes()).decode("ascii")
        st.markdown(
            f"<style>.impact-hero{{background-image:linear-gradient(90deg,rgba(11,33,43,.57),rgba(17,55,61,.16) 54%,rgba(28,66,51,.34)),url('data:image/jpeg;base64,{encoded_image}')!important;background-size:cover!important;background-position:center!important;}}.impact-hero:before{{background:linear-gradient(0deg,rgba(248,237,220,.42),transparent 50%)!important;filter:none!important;}}</style>",
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
    st.markdown(
        """
        <div class='impact-hero' aria-label='OpenPreEduLab visual introduction'>
          <div class='hero-orbit'></div>
          <div class='sun-disc'></div><div class='wood-arch'></div>
          <svg class='hero-arc' viewBox='0 0 600 150' aria-hidden='true'><path id='arcPath' d='M 60,128 A 245,245 0 0,1 540,128' fill='none'/><text fill='#f7ead7' font-family='DM Mono, monospace' font-size='15' letter-spacing='4'><textPath href='#arcPath' startOffset='50%' text-anchor='middle'>OPEN PRESCHOOL EDUCATION PLATFORM</textPath></text></svg>
          <div class='hero-center'><div class='hero-flag'>RESEARCH · PRACTICE · DEVELOPMENT</div><h1>OpenPreEduLab</h1><p>A comprehensive interactive platform for preschool education — connecting research, inclusive support, teacher development, policy, data and everyday learning.</p></div>
          <div class='hero-side-note'>INCLUSIVE SUPPORT<br>TEACHER DEVELOPMENT<br>POLICY · DATA · PRACTICE</div>
          <div class='glass-research-card'><b>OPEN RESEARCH SYSTEM</b><span>Evidence that connects learning, support, practice and policy.</span><div class='mini-bars'><i></i><i></i><i></i><i></i><i></i></div></div>
          <div class='hero-network'><i></i><i></i><i></i><i></i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    action_left, action_middle, action_right = st.columns([0.32, 0.18, 0.32])
    with action_left:
        st.button("Launch Platform", on_click=_switch_to_platform, width="stretch")
    with action_middle:
        st.markdown("<div class='secondary-button'>", unsafe_allow_html=True)
        st.button("Explore Research", key="hero_workflow", width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section'><div class='eyebrow'>01 — Research story</div><h2 class='section-title'>Research begins with children.</h2><p class='section-copy'>OpenPreEduLab treats data and policy as tools for understanding children's learning, development, and educational opportunities — never as an end in themselves.</p></div>", unsafe_allow_html=True)
    legacy, platform = st.columns(2, gap="large")
    with legacy:
        st.markdown("<div class='comparison'><div class='eyebrow'>Traditional workflow</div><div class='flow-stack'><b>Manual reading</b><br>↓<br>SPSS analysis<br>↓<br>Single paper<br>↓<br>End of workflow</div></div>", unsafe_allow_html=True)
    with platform:
        st.markdown("<div class='comparison'><div class='eyebrow'>OpenPreEduLab</div><div class='flow-stack'><b>Dataset</b><br>↓<br>Models · Simulation · Interpretation<br>↓<br><b>Reusable research output</b></div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section'><div class='eyebrow'>02 — Research challenges</div><h2 class='section-title'>The evidence we need is often fragmented.</h2></div>", unsafe_allow_html=True)
    modules = [
        ("01", "Fragmented Research Workflow", "Policy, data and analysis often remain isolated across individual studies."),
        ("02", "Limited Policy Simulation", "Many studies describe conditions without making assumptions visible in scenario testing."),
        ("03", "Low Reproducibility", "Definitions, transformations and model decisions are difficult to reuse or audit."),
        ("04", "Scattered Research Tools", "Researchers must bridge disconnected documents, datasets, software and reporting practices."),
    ]
    cols = st.columns(4, gap="medium")
    for column, (number, title, copy) in zip(cols, modules):
        with column:
            st.markdown(f"<div class='glass-card'><div class='card-icon'>{number}</div><h3>{title}</h3><p>{copy}</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='section'><div class='eyebrow'>03 — Research workflow</div><h2 class='section-title'>A traceable path from data to better questions.</h2></div>", unsafe_allow_html=True)
    steps = ["Dataset", "Schema", "PRAI", "Equity", "Efficiency", "Forecast", "Simulation", "AI Interpretation", "Report"]
    timeline = "".join(f"<div class='timeline-step'><div class='timeline-dot'>{index + 1:02}</div>{step}</div>" + ("<div class='timeline-line'></div>" if index < len(steps) - 1 else "") for index, step in enumerate(steps))
    st.markdown(f"<div class='timeline'>{timeline}</div>", unsafe_allow_html=True)
    st.markdown("<div class='quote-block'><p>Children are not data.<br>Data exists to better understand children's learning, development and educational opportunities.<br><br>Research should ultimately improve children's lives.</p><span>Children-centered research vision</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='launch-panel'><h2>Start your research.</h2><p>Explore the documented prototype workflow with the repository sample dataset. Real data remain subject to provenance and definition review.</p></div>", unsafe_allow_html=True)
    launch_left, launch_middle, launch_right = st.columns([0.35, 0.3, 0.35])
    with launch_middle:
        st.button("Launch OpenPreEduLab", key="footer_launch", on_click=_switch_to_platform, width="stretch")


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
    nodes = [("Data", True), ("Allocation", True), ("Equity", True), ("Efficiency", True), ("Forecast", True), ("Simulation", True), ("Report", True)]
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
        st.download_button("Download PRAI input template", PRAI_TEMPLATE_PATH.read_bytes(), "prai_input_template.csv", "text/csv", width="stretch")
        st.download_button("Download sample dataset", SAMPLE_PATH.read_bytes(), "sample_preschool_data.csv", "text/csv", width="stretch")
        st.caption("See docs/Data_Upload_Guide.md for the upload and research-use boundary.")
    with right:
        with st.expander("Inspect input records", expanded=True):
            st.dataframe(data, width="stretch", hide_index=True)


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
        st.dataframe(results.sort_values(["year", "resource_allocation_score"], ascending=[True, False]), width="stretch", hide_index=True)
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
    st.dataframe(report, width="stretch", hide_index=True)


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


def _efficiency_page(data: pd.DataFrame) -> pd.DataFrame:
    """Run the documented VRS/BCC DEA prototype on the current input."""
    st.markdown("<div class='eyebrow'>Efficiency evaluation</div><h2>Resource use and educational output.</h2><p class='section-copy'>Input-oriented VRS DEA compares city-year decision-making units within each observed year. Scores are relative to the selected sample, not absolute quality ratings.</p>", unsafe_allow_html=True)
    prepared = prepare_efficiency_data(data)
    results = evaluate_panel_efficiency(prepared, ["total_government_expenditure_yuan", "fte_teacher_count", "usable_indoor_area_sqm"], ["enrolled_children", "age_specific_enrolment_coverage_pct", "qualified_teacher_rate_pct"])
    year = st.selectbox("DEA reference year", sorted(results["year"].unique()), key="dea_year")
    subset = results.loc[results["year"] == year].sort_values("efficiency_score", ascending=False)
    cards = st.columns(3, gap="medium")
    values = [("Frontier DMUs", str(int((subset["efficiency_score"] >= .999).sum())), "relative score = 1.00", "status-ok"), ("Mean efficiency", f"{subset['efficiency_score'].mean():.3f}", "selected cross-section", ""), ("Returns to scale", "VRS", "input-oriented BCC model", "")]
    for column, item in zip(cards, values):
        with column: st.markdown(_metric(*item), unsafe_allow_html=True)
    st.dataframe(subset, width="stretch", hide_index=True)
    st.download_button("Download DEA efficiency results", results.to_csv(index=False).encode("utf-8"), "efficiency_result.csv", "text/csv")
    return results


def _forecast_page(data: pd.DataFrame) -> pd.DataFrame:
    """Run transparent population-linked planning forecasts."""
    st.markdown("<div class='eyebrow'>Forecast framework</div><h2>Planning assumptions made visible.</h2><p class='section-copy'>Population uses city-level linear time trends. Teacher and fiscal outputs translate projected child population through explicit planning assumptions; they are not factual forecasts.</p>", unsafe_allow_html=True)
    latest = int(data["year"].max())
    years = st.multiselect("Forecast years", list(range(latest + 1, latest + 6)), default=[latest + 1, latest + 2])
    ratio_default = float((data["fte_teacher_count"] / data["enrolled_children"]).mean())
    cost_default = float(data["government_expenditure_per_child_yuan"].mean())
    left, right = st.columns(2)
    with left: ratio = st.number_input("Planning FTE teachers per child", min_value=0.001, value=round(ratio_default, 4), step=0.001, format="%.4f")
    with right: cost = st.number_input("Planning cost per child (yuan)", min_value=1.0, value=float(round(cost_default, 2)), step=100.0)
    if not years:
        st.info("Select at least one future year to run a forecast.")
        return pd.DataFrame()
    population = forecast_population(data, years)
    teacher = forecast_teacher_demand(population, ratio)
    fiscal = forecast_fiscal_requirement(population, cost)
    results = population.merge(teacher, on=["city", "year", "future_child_population"]).merge(fiscal, on=["city", "year", "future_child_population"])
    st.dataframe(results, width="stretch", hide_index=True)
    st.download_button("Download forecast results", results.to_csv(index=False).encode("utf-8"), "forecast_result.csv", "text/csv")
    return results


def _simulation_page(data: pd.DataFrame) -> pd.DataFrame:
    """Run explicit prototype policy scenarios on the current input."""
    st.markdown("<div class='eyebrow'>Policy simulation</div><h2>Compare assumptions, not predictions.</h2><p class='section-copy'>Each control changes a documented prototype parameter. Scenario output is conditional on those assumptions and is not a validated policy forecast.</p>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a: subsidy = st.slider("Subsidy increase", 0.0, 0.30, 0.10, 0.01)
    with b: population = st.slider("Population change", -0.30, 0.10, -0.08, 0.01)
    with c: teacher_cost = st.slider("Teacher cost increase", 0.0, 0.30, 0.08, 0.01)
    d, e, f = st.columns(3)
    with d: base_cost = st.number_input("Baseline teacher cost (yuan)", min_value=1.0, value=80000.0, step=1000.0)
    with e: fiscal_growth = st.slider("Fiscal growth rate", -0.30, 0.20, -0.12, 0.01)
    with f: capacity = st.slider("Fiscal capacity multiplier", 0.50, 1.50, 1.10, 0.01)
    results = simulate_policy_scenarios(data, subsidy, population, teacher_cost, base_cost, fiscal_growth, capacity)
    latest = int(data["year"].max())
    summary = results.loc[results["year"] == latest].groupby("scenario", as_index=False)[["fiscal_requirement_yuan", "resource_allocation_score", "teacher_demand", "education_coverage_pct"]].mean(numeric_only=True)
    st.dataframe(summary, width="stretch", hide_index=True)
    st.download_button("Download scenario comparison", results.to_csv(index=False).encode("utf-8"), "simulation_result.csv", "text/csv")
    return results


def _ai_interpretation_page(data: pd.DataFrame) -> None:
    """Build a reviewable, evidence-bounded LLM interpretation request."""
    st.markdown("<div class='eyebrow'>AI-assisted interpretation</div><h2>Interpret results. Do not replace research judgement.</h2><p class='section-copy'>The platform constructs a bounded request from the current model outputs. No external call is made unless a researcher configures and approves an LLM client.</p>", unsafe_allow_html=True)
    latest = int(data["year"].max())
    allocation = calculate_prai_score(data)
    equity = generate_equity_report(allocation, year=latest)
    dea_data = prepare_efficiency_data(data)
    efficiency = evaluate_panel_efficiency(dea_data, ["total_government_expenditure_yuan", "fte_teacher_count", "usable_indoor_area_sqm"], ["enrolled_children", "age_specific_enrolment_coverage_pct", "qualified_teacher_rate_pct"])
    simulation = simulate_policy_scenarios(data, 0.10, -0.08, 0.08, 80000.0, -0.12, 1.10)
    context = st.text_area("Research context (optional)", placeholder="State the research question, study boundary, and any interpretation constraints.")
    results = {
        "resource_allocation": allocation.loc[allocation["year"] == latest],
        "equity": equity,
        "efficiency": efficiency.loc[efficiency["year"] == latest],
        "policy_simulation": simulation.loc[simulation["year"] == latest],
    }
    request = create_interpretation_request(results, context)
    st.markdown("<div class='quiet-note'>No model result has been transmitted to an external service. Review the prompt and data-governance boundary before configuring any provider or API credential.</div>", unsafe_allow_html=True)
    with st.expander("Preview interpretation request"):
        st.markdown("**System prompt**")
        st.code(request.system_prompt, language="text")
        st.markdown("**Evidence-bounded user prompt**")
        st.code(request.user_prompt, language="markdown")
    packet = f"# OpenPreEduLab AI Interpretation Request\n\n## System Prompt\n\n{request.system_prompt}\n\n## User Prompt\n\n{request.user_prompt}\n"
    st.download_button("Download reviewed interpretation request", packet.encode("utf-8"), "llm_interpretation_request.md", "text/markdown")
    st.caption("The downloadable request is the no-network option. Any generated response remains an assistive draft that requires researcher review.")

    st.divider()
    st.markdown("### Optional DeepSeek interpretation")
    st.markdown("<div class='quiet-note'>DeepSeek is an external service. Selecting Generate sends the reviewed system prompt, research context, and current model results to DeepSeek. OpenPreEduLab does not provide a shared or guaranteed free API quota. Use only a key and account you control; the key is used for this request only and is not written to this repository, downloaded reports, or platform files.</div>", unsafe_allow_html=True)
    with st.form("deepseek_interpretation_form", clear_on_submit=True):
        model = st.selectbox("DeepSeek model", SUPPORTED_MODELS, help="Model availability and billing are determined by your DeepSeek account.")
        api_key = st.text_input("Your DeepSeek API key", type="password", help="This field is cleared after submission and is never displayed in generated files.")
        consent = st.checkbox("I understand that the reviewed prompt and its model results will be sent to DeepSeek, an external provider.")
        submitted = st.form_submit_button("Generate interpretation with DeepSeek", width="stretch")

    if submitted:
        if not api_key.strip():
            st.error("Enter your own DeepSeek API key to generate an interpretation.")
        elif not consent:
            st.error("Confirm the external-data transmission notice before generating an interpretation.")
        else:
            try:
                with st.spinner("Generating an evidence-bounded interpretation…"):
                    assistant = ResearchInterpretationAssistant(DeepSeekClient(api_key, model=model))
                    response = assistant.interpret(results, context)
                st.session_state["deepseek_interpretation"] = response
                st.session_state["deepseek_model"] = model
                st.success("Interpretation generated. Review it against the displayed evidence and research design.")
            except (ValueError, DeepSeekRequestError) as error:
                st.error(str(error))

    response = st.session_state.get("deepseek_interpretation")
    if response:
        st.markdown("### Generated draft — researcher review required")
        st.markdown(response)
        record = f"# OpenPreEduLab AI-assisted Interpretation Record\n\nProvider: DeepSeek\nModel: {st.session_state.get('deepseek_model', 'unknown')}\n\n## System Prompt\n\n{request.system_prompt}\n\n## User Prompt\n\n{request.user_prompt}\n\n## Generated Draft\n\n{response}\n\n---\nThis draft is not a validated research finding, causal claim, or policy conclusion. It requires researcher review.\n"
        st.download_button("Download interpretation record", record.encode("utf-8"), "deepseek_interpretation_record.md", "text/markdown")
def _coming_soon_page(title: str, tag: str, detail: str) -> None:
    """Render an honest module-integration page without fictitious output."""
    st.markdown(f"<div class='eyebrow'>{tag}</div><h2>{title}</h2><p class='section-copy'>{detail}</p>", unsafe_allow_html=True)
    st.markdown("<div class='quiet-note'>The underlying research module is retained in the repository. Interactive controls will be enabled only after a definition-compatible processed dataset is available and the module-specific input assumptions are visible to the researcher.</div>", unsafe_allow_html=True)


def _report_page(data: pd.DataFrame) -> None:
    """Render the bounded report-output page."""
    st.markdown("<div class='eyebrow'>Research output</div><h2>Research reports with traceable inputs.</h2><p class='section-copy'>The pipeline can generate structured outputs from the sample workflow. Real-world reports must retain source provenance, model assumptions, validation notes, and interpretation limits.</p>", unsafe_allow_html=True)
    allocation = calculate_prai_score(data)
    latest = int(data["year"].max())
    latest_scores = allocation.loc[allocation["year"] == latest, "resource_allocation_score"]
    equity = generate_equity_report(allocation, year=latest)
    dea_data = prepare_efficiency_data(data)
    efficiency = evaluate_panel_efficiency(dea_data, ["total_government_expenditure_yuan", "fte_teacher_count", "usable_indoor_area_sqm"], ["enrolled_children", "age_specific_enrolment_coverage_pct", "qualified_teacher_rate_pct"])
    latest_efficiency = efficiency.loc[efficiency["year"] == latest, "efficiency_score"]
    forecast_years = [latest + 1, latest + 2]
    population = forecast_population(data, forecast_years)
    teacher_ratio = float((data["fte_teacher_count"] / data["enrolled_children"]).mean())
    cost_per_child = float(data["government_expenditure_per_child_yuan"].mean())
    forecast = forecast_population(data, forecast_years).merge(
        forecast_teacher_demand(population, teacher_ratio), on=["city", "year", "future_child_population"]
    ).merge(
        forecast_fiscal_requirement(population, cost_per_child), on=["city", "year", "future_child_population"]
    )
    simulation = simulate_policy_scenarios(data, 0.10, -0.08, 0.08, 80000.0, -0.12, 1.10)
    simulation_latest = simulation.loc[simulation["year"] == latest]
    equity_summary = "\n".join(
        f"- {row.indicator}: {row.value:.3f} ({row.equity_level})"
        for row in equity.itertuples(index=False)
    )
    report = f"""# OpenPreEduLab Research Run Summary

## Scope

- Input source: current platform dataset
- Observations: {len(data)} city-year records
- Latest observed year: {latest}
- PRAI scoring: equal-dimension MVP weighting

## Descriptive output

- Latest-year mean PRAI score: {latest_scores.mean():.2f}
- Latest-year score range: {latest_scores.min():.2f}–{latest_scores.max():.2f}

## Equity output

{equity_summary}

## Efficiency output

- Latest-year mean DEA efficiency: {latest_efficiency.mean():.3f}
- Latest-year relative-efficiency range: {latest_efficiency.min():.3f}–{latest_efficiency.max():.3f}
- Specification: input-oriented VRS/BCC DEA with documented prototype inputs and outputs.

## Forecast output

- Forecast years: {", ".join(map(str, forecast_years))}
- Planning FTE-teacher ratio: {teacher_ratio:.4f} teachers per child
- Planning cost per child: {cost_per_child:.2f} yuan
- Forecast records: {len(forecast)} city-year projections

## Scenario output

- Scenario records: {len(simulation)}
- Latest-year fiscal sustainability ratio range: {simulation_latest["fiscal_sustainability_ratio"].min():.3f}–{simulation_latest["fiscal_sustainability_ratio"].max():.3f}
- Parameters: subsidy +10%; population change -8%; teacher cost +8%; fiscal growth -12%; capacity multiplier 1.10.

## Research-use note

This summary records a computational run. It does not establish real-world findings, causal effects, or policy recommendations. Interpret results only with documented data provenance, model assumptions, and limitations.
"""
    st.markdown(_module_card("↗", "Research run summary", "Generate a transparent record across allocation, equity, efficiency, forecast and conditional scenario output. The platform does not present this text as an automatically validated research paper.", "PROTOTYPE OUTPUT"), unsafe_allow_html=True)
    output_format = st.selectbox(
        "Download format",
        ["Markdown (.md)", "Word document (.docx)", "PDF document (.pdf)"],
        help="All formats contain the same computational summary, assumptions, and research-use limitations.",
    )
    if output_format == "Markdown (.md)":
        payload, filename, mime_type = report.encode("utf-8"), "research_run_summary.md", "text/markdown"
    elif output_format == "Word document (.docx)":
        payload, filename, mime_type = (
            report_to_docx(report),
            "research_run_summary.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    else:
        payload, filename, mime_type = report_to_pdf(report), "research_run_summary.pdf", "application/pdf"
    st.download_button(f"Download research run summary ({output_format})", payload, filename, mime_type)
    with st.expander("Preview summary"):
        st.markdown(report)


def _documentation_page() -> None:
    """Render the research documentation entry point."""
    st.markdown("<div class='eyebrow'>Research documentation</div><h2>Methods remain visible.</h2><p class='section-copy'>OpenPreEduLab treats documentation as part of the research system: theory, variable definitions, data governance, validation and interpretation limits remain inspectable.</p>", unsafe_allow_html=True)
    cards = st.columns(3, gap="medium")
    items = [
        ("◫", "Research framework", "Vision, architecture and the research workflow.", "DOCS"),
        ("◌", "Model specifications", "PRAI, equity, efficiency, forecast and simulation assumptions.", "METHODS"),
        ("↗", "Data governance", "Source hierarchy, review protocol and processed-data boundary.", "DATA"),
    ]
    for column, item in zip(cards, items):
        with column:
            st.markdown(_module_card(*item), unsafe_allow_html=True)


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
        if st.button("← Back to landing", width="stretch"):
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
        st.info("To correct the file, use the PRAI input template and verify: required column names, one unique city-year record per row, numeric values in required fields, positive count denominators, and children-not-enrolled not exceeding children-seeking-a-place.")
        st.download_button(
            "Download PRAI input template",
            PRAI_TEMPLATE_PATH.read_bytes(),
            "prai_input_template.csv",
            "text/csv",
        )
        return

    if page == "Workflow":
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
    elif page == "Visualisation": _visualisation_page(data, calculate_prai_score(data))
    elif page == "Efficiency": _efficiency_page(data)
    elif page == "Forecast": _forecast_page(data)
    elif page == "Simulation": _simulation_page(data)
    elif page == "AI Interpretation": _ai_interpretation_page(data)
    elif page == "Inclusive Support": _coming_soon_page("Inclusive education support.", "FUTURE DEVELOPMENT", "A future platform area for organising evidence, practice resources and research workflows related to inclusive preschool education. Its design will follow accessibility, ethics and evidence requirements.")
    elif page == "Teacher Development": _coming_soon_page("Teacher professional development.", "FUTURE DEVELOPMENT", "A future platform area for teacher learning, professional-capability evidence and reflective practice. It will not infer teacher quality from incomplete administrative variables.")
    elif page == "Reports": _report_page(data)
    elif page == "Documentation": _documentation_page()
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
