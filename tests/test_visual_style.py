"""Tests for the shared high-clarity chart rendering configuration."""

import matplotlib as mpl

from visualization.style import EXPORT_DPI, SCREEN_DPI, configure_matplotlib


def test_chart_style_uses_high_density_screen_and_export_rendering() -> None:
    """Charts should remain sharp both in Streamlit and downloaded files."""
    configure_matplotlib()

    assert mpl.rcParams["figure.dpi"] == SCREEN_DPI
    assert mpl.rcParams["savefig.dpi"] == EXPORT_DPI
    assert mpl.get_backend().lower() == "agg"
    assert mpl.rcParams["lines.antialiased"] is True
    assert mpl.rcParams["figure.facecolor"] == "white"
