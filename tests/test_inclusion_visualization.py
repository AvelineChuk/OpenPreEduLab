"""Rendering tests for inclusive education research charts."""

import matplotlib.pyplot as plt

from models.inclusion import calculate_inclusion_dimension_scores, load_inclusion_data
from models.support_gap import calculate_support_gaps
from visualization.inclusion_charts import (
    plot_dimension_heatmap,
    plot_five_dimension_radar,
    plot_institution_comparison,
    plot_support_gap_bars,
    plot_support_pathway,
)


def test_inclusion_visualization_suite_renders(sample_inclusive_dataset_path) -> None:
    """All five required chart types render from synthetic dimension scores."""
    data = load_inclusion_data(sample_inclusive_dataset_path)
    scores = calculate_inclusion_dimension_scores(data)
    gaps = calculate_support_gaps(scores)

    radar_figure, radar_axis = plt.subplots(subplot_kw={"projection": "polar"})
    assert plot_five_dimension_radar(scores, ax=radar_axis) is radar_axis
    pathway_figure, pathway_axis = plt.subplots()
    assert plot_support_pathway(scores, ax=pathway_axis) is pathway_axis
    gap_figure, gap_axis = plt.subplots()
    assert plot_support_gap_bars(gaps, ax=gap_axis) is gap_axis
    comparison_figure, comparison_axis = plt.subplots()
    assert plot_institution_comparison(scores, ["SYN-001", "SYN-002"], ax=comparison_axis) is comparison_axis
    heatmap_figure, heatmap_axis = plt.subplots()
    assert plot_dimension_heatmap(scores, ax=heatmap_axis) is heatmap_axis

    for figure in [radar_figure, pathway_figure, gap_figure, comparison_figure, heatmap_figure]:
        plt.close(figure)
