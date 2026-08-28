"""Shared screen and export styling for OpenPreEduLab charts.

The web application renders Matplotlib figures as raster images. A higher
screen DPI and explicit typography keep labels and thin lines legible on
high-density displays, while exports remain publication-ready at 300 DPI.
"""

from __future__ import annotations

import matplotlib as mpl


SCREEN_DPI = 160
EXPORT_DPI = 300


def configure_matplotlib() -> None:
    """Apply a restrained, high-clarity visual style to all platform charts."""
    mpl.use("Agg", force=True)
    mpl.rcParams.update(
        {
            "figure.dpi": SCREEN_DPI,
            "savefig.dpi": EXPORT_DPI,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#CBD5D1",
            "axes.labelcolor": "#344A50",
            "axes.titlecolor": "#1B2D35",
            "axes.titleweight": "semibold",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "font.size": 10,
            "text.color": "#1B2D35",
            "xtick.color": "#52666B",
            "ytick.color": "#52666B",
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "grid.color": "#D8E0DD",
            "grid.linewidth": 0.7,
            "grid.alpha": 0.65,
            "lines.antialiased": True,
            "patch.antialiased": True,
        }
    )
