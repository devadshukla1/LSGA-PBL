"""Tests for Plotly visualization generation across modules."""

from src.algorithms.bfs import find_route_bfs
from src.analytics.station_ranking import compute_station_analytics
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.visualization.metro_plot import (
    create_metro_network_plot,
    plot_closure_comparison,
    plot_metro_route,
    plot_top_stations,
)


def test_visualization_generators():
    """Verify all Plotly figure generators build figures without error."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    # 1. Network Plot
    fig1 = create_metro_network_plot(graph, title="Test Network")
    assert fig1 is not None

    # 2. Route Plot
    route_res = find_route_bfs(graph, "S01", "S06")
    fig2 = plot_metro_route(graph, route_res)
    assert fig2 is not None

    # 3. Closure Plot
    fig3 = plot_closure_comparison(graph, graph, closed_station_ids=["S02"])
    assert fig3 is not None

    # 4. Top Stations Plot
    station_results, _, _ = compute_station_analytics(graph, station_lines_df, lines_df)
    fig4 = plot_top_stations(station_results, metric="degree_centrality", top_n=5)
    assert fig4 is not None
