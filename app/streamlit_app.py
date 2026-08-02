"""Streamlit interface for the OpenPreEduLab research prototype.

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


def _load_uploaded_csv(uploaded_file: object) -> pd.DataFrame:
    """Validate an uploaded CSV through the existing allocation data loader."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temporary_file:
        temporary_path = Path(temporary_file.name)
        temporary_file.write(uploaded_file.getvalue())
    try:
        return load_data(temporary_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _data_status_message(source_label: str) -> None:
    """Display the data-governance status appropriate to the selected source."""
    if source_label == "Sample dataset":
        st.info(
            "This is synthetic sample data for software demonstration. Results are not "
            "real-world findings or policy evaluation evidence."
        )
    else:
        st.warning(
            "Uploaded data are treated as user-provided inputs. A successful calculation "
            "does not establish source provenance, definition compatibility, or eligibility "
            "for substantive policy claims. Follow the raw → staging → independent review "
            "→ processed workflow before reporting real-data results."
        )


def _render_data_overview(data: pd.DataFrame, source_label: str) -> None:
    """Render input preview and transparent schema checks."""
    st.subheader("Data input and eligibility")
    _data_status_message(source_label)
    st.caption(
        "Required PRAI schema fields are checked by the existing allocation engine. "
        "The interface does not impute missing values, remove outliers, or convert teacher "
        "headcounts into FTE values."
    )
    missing = sorted(set(REQUIRED_COLUMNS) - set(data.columns))
    if missing:
        st.error(f"Missing required fields: {', '.join(missing)}")
        return
    st.success(f"Schema check passed: {len(data):,} city-year observations.")
    st.dataframe(data.head(20), use_container_width=True)


def _render_allocation(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate and display PRAI scores using the documented MVP rule."""
    st.subheader("Preschool Resource Allocation Index (PRAI)")
    st.caption(
        "Default scoring uses the documented equal-dimension MVP weighting. "
        "Scores are comparable only within the jointly normalised input sample."
    )
    results = calculate_prai_score(data, weight_method="equal")
    results["allocation_level"] = evaluate_level(results["resource_allocation_score"])
    st.dataframe(results.sort_values(["year", "resource_allocation_score"], ascending=[True, False]), use_container_width=True)
    st.download_button(
        "Download PRAI results (CSV)",
        data=results.to_csv(index=False).encode("utf-8"),
        file_name="allocation_result.csv",
        mime="text/csv",
    )
    return results


def _render_equity(results: pd.DataFrame) -> None:
    """Render a descriptive, cross-sectional equity report for one selected year."""
    st.subheader("Educational equity evaluation")
    year = st.selectbox("Reference year", sorted(results["year"].unique()), key="equity_year")
    report = generate_equity_report(results, year=int(year))
    st.caption(
        "CV, Gini, and Theil describe inequality in observed PRAI scores for the selected "
        "year. They do not establish causes or policy effects."
    )
    st.dataframe(report, use_container_width=True)


def _render_visualisations(data: pd.DataFrame, results: pd.DataFrame) -> None:
    """Render reusable research visualisations from calculated sample results."""
    st.subheader("Research visualisations")
    available_years = sorted(results["year"].unique())
    selected_year = st.selectbox("Chart year", available_years, key="chart_year")

    left, right = st.columns(2)
    with left:
        figure, axis = plt.subplots(figsize=(8, 5))
        plot_resource_allocation_ranking(results, year=int(selected_year), ax=axis)
        st.pyplot(figure, clear_figure=True)
    with right:
        figure, axis = plt.subplots(figsize=(8, 5))
        plot_score_heatmap(results, ax=axis)
        st.pyplot(figure, clear_figure=True)

    figure, axis = plt.subplots(figsize=(9, 5))
    plot_trend_analysis(results, ax=axis)
    st.pyplot(figure, clear_figure=True)

    indicators = prepare_indicators(data)
    dimension_scores = calculate_dimension_scores(normalize_indicators(indicators))
    selected_cities = st.multiselect(
        "Cities for dimension profile",
        sorted(dimension_scores["city"].unique()),
        default=sorted(dimension_scores["city"].unique())[:3],
    )
    if selected_cities:
        figure, axis = plt.subplots(figsize=(7, 7), subplot_kw={"projection": "polar"})
        plot_dimension_radar(
            dimension_scores,
            year=int(selected_year),
            cities=selected_cities,
            ax=axis,
        )
        st.pyplot(figure, clear_figure=True)


def main() -> None:
    """Run the OpenPreEduLab interactive research-prototype interface."""
    st.set_page_config(page_title="OpenPreEduLab", page_icon="📘", layout="wide")
    st.title("OpenPreEduLab")
    st.caption("Open Preschool Education Research Platform · Research Prototype")
    st.warning(
        "Statistical models compute; researchers interpret. This interface is a "
        "reproducible research prototype, not a policy-decision system."
    )

    with st.sidebar:
        st.header("Data source")
        source = st.radio("Select input", ["Sample dataset", "Upload CSV"])
        uploaded_file = None
        if source == "Upload CSV":
            uploaded_file = st.file_uploader("Upload a PRAI-compatible CSV", type=["csv"])
        st.divider()
        st.markdown("**Data governance**")
        st.caption("Real data must pass raw → staging → independent review → processed.")

    try:
        if source == "Sample dataset":
            data = load_data(SAMPLE_PATH)
        elif uploaded_file is None:
            st.info("Upload a CSV to begin analysis, or select the sample dataset.")
            return
        else:
            data = _load_uploaded_csv(uploaded_file)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        st.error(f"Input validation failed: {error}")
        return

    input_tab, allocation_tab, equity_tab, visual_tab, methods_tab = st.tabs(
        ["Data", "PRAI", "Equity", "Visualisation", "Methods & limits"]
    )
    with input_tab:
        _render_data_overview(data, source)
    with allocation_tab:
        results = _render_allocation(data)
    with equity_tab:
        results = calculate_prai_score(data, weight_method="equal")
        _render_equity(results)
    with visual_tab:
        results = calculate_prai_score(data, weight_method="equal")
        _render_visualisations(data, results)
    with methods_tab:
        st.markdown(
            """
            ### Scope

            - Default PRAI scoring uses equal dimension weights in the MVP.
            - Equity indicators describe observed score distributions at one time point.
            - Sample and uploaded calculations are not causal inference or policy validation.
            - Uploaded real-world data require documented provenance, definition checks,
              independent review, and a processed-data release before research reporting.

            See `docs/Resource_Allocation_Index.md`, `docs/Data_Dictionary.md`, and
            `docs/Data_Review_Protocol.md` for the underlying research specification.
            """
        )


if __name__ == "__main__":
    main()
