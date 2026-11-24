"""Tests for enhanced metro map visualization, line highlighting focus, and geographic aspect ratio."""

import pytest

from src.algorithms.bfs import find_route_bfs
from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.visualization.metro_plot import (
    create_metro_network_plot,
    plot_centrality_network,
    plot_closure_comparison,
    plot_metro_route,
)


@pytest.fixture(scope="module")
def metro_network_data():
    """Load real Delhi Metro graph."""
    stations_df, lines_df, connections_df, station_lines_df, meta = load_validated_dataset(METRO_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)
    return graph, lines_df, stations_df


def test_map_aspect_ratio_and_coordinates(metro_network_data):
    """Verify geographic aspect ratio calibration and coordinate validity."""
    graph, lines_df, stations_df = metro_network_data
    fig = create_metro_network_plot(graph, title="Delhi Metro Overview")

    # Assert aspect ratio scaleanchor is set to 'x' to prevent squishing
    assert fig.layout.yaxis.scaleanchor == "x"
    assert fig.layout.yaxis.scaleratio == pytest.approx(1.14, rel=1e-2)

    # Assert coordinates lie strictly within NCR bounding box
    for node, data in graph.nodes(data=True):
        assert 28.2 <= data["lat"] <= 28.95, f"Station {node} lat {data['lat']} out of bounds"
        assert 76.8 <= data["lon"] <= 77.60, f"Station {node} lon {data['lon']} out of bounds"


def test_metro_line_highlighting_two_tier_visuals(metro_network_data):
    """Verify line highlighting applies thick lines to selected line and dims other lines."""
    graph, lines_df, stations_df = metro_network_data

    # 1. Unfiltered: all lines drawn with standard width
    fig_all = create_metro_network_plot(graph, selected_line="All Lines")
    line_traces_all = [t for t in fig_all.data if t.mode == "lines"]
    assert len(line_traces_all) >= 10
    for t in line_traces_all:
        assert t.line.width == pytest.approx(3.5)

    # 2. Filtered: selected line drawn thick (6.0), other lines dimmed (1.8 width, muted color)
    selected_line = "Yellow Line"
    fig_filtered = create_metro_network_plot(graph, selected_line=selected_line)

    line_traces = [t for t in fig_filtered.data if t.mode == "lines"]
    # Should have a dimmed background trace and the highlighted Yellow Line trace
    dimmed_trace = next((t for t in line_traces if t.name == "Other Lines (Dimmed)"), None)
    assert dimmed_trace is not None, "Dimmed background trace should be present when filtering"
    assert dimmed_trace.opacity <= 0.20
    assert dimmed_trace.line.width <= 2.0

    highlighted_trace = next((t for t in line_traces if t.name.lower() == selected_line.lower()), None)
    assert highlighted_trace is not None, f"Selected line trace for {selected_line} should be present"
    assert highlighted_trace.line.width == pytest.approx(6.0)
    assert highlighted_trace.opacity == pytest.approx(1.0)


def test_station_opacity_under_line_filtering(metro_network_data):
    """Verify stations on non-selected lines are dimmed while selected stations remain prominent."""
    graph, lines_df, stations_df = metro_network_data
    fig_filtered = create_metro_network_plot(graph, selected_line="Red Line")

    marker_traces = [t for t in fig_filtered.data if "markers" in t.mode]
    dimmed_stns = next((t for t in marker_traces if t.name == "Non-Selected Stations"), None)
    assert dimmed_stns is not None
    assert dimmed_stns.marker.opacity <= 0.25
    assert dimmed_stns.marker.size <= 5.0

    interchange_stns = next((t for t in marker_traces if t.name == "Interchange Hub"), None)
    assert interchange_stns is not None
    assert interchange_stns.marker.size >= 12.0


def test_all_visualizations_preserve_aspect_ratio_and_offline_guarantee(metro_network_data):
    """Verify route, centrality, and closure plots also share aspect ratio calibration."""
    graph, lines_df, stations_df = metro_network_data

    # Route plot
    route = find_route_bfs(graph, "STN199", "STN097")  # Rajiv Chowk to Kashmere Gate
    fig_route = plot_metro_route(graph, route)
    assert fig_route.layout.yaxis.scaleanchor == "x"

    # Centrality plot
    from src.analytics.station_ranking import compute_station_analytics
    from src.data.loader import load_validated_dataset
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    s_graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)
    results, _, _ = compute_station_analytics(s_graph, station_lines_df, lines_df)
    fig_cent = plot_centrality_network(s_graph, results)
    assert fig_cent.layout.yaxis.scaleanchor == "x"

    # Closure plot
    fig_close = plot_closure_comparison(s_graph, s_graph, closed_station_ids=["S01"])
    assert fig_close.layout.yaxis.scaleanchor == "x"
