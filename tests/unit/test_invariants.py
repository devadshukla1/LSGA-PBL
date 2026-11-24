"""Unit and property-based invariant tests for graph models and algorithms."""

import networkx as nx

from src.algorithms.bfs import find_route_bfs
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.minimum_transfers import find_route_minimum_transfers
from src.analytics.station_ranking import compute_station_analytics
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.simulation.closure_engine import simulate_station_closure


def test_invariant_route_continuity():
    """Property: Consecutive stations in a computed path must be connected in the graph."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    route_res = find_route_bfs(graph, "S01", "S06")
    assert route_res.reachable

    # Check each consecutive station pair
    for u, v in zip(route_res.station_path[:-1], route_res.station_path[1:]):
        assert graph.has_edge(u, v), f"Graph missing edge between {u} and {v}"


def test_invariant_bfs_segment_hop_count():
    """Property: Number of segments must equal total stops (station hops)."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    route_res = find_route_bfs(graph, "S03", "S08")
    assert route_res.reachable
    assert len(route_res.segments) == route_res.total_stops
    assert len(route_res.station_path) == route_res.total_stops + 1


def test_invariant_dijkstra_optimality():
    """Property: Dijkstra travel time must match NetworkX shortest path oracle."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    res = find_route_dijkstra(graph, "S01", "S06", objective="minimum_time")
    assert res.reachable

    # Compute oracle cost on projected simple graph
    oracle_cost = nx.dijkstra_path_length(graph, "S01", "S06", weight="estimated_time_min")
    assert abs(res.segment_travel_time_min - oracle_cost) < 1e-4


def test_invariant_transfer_count_logic():
    """Property: Reported transfer count must equal distinct line switches across segments."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    res = find_route_minimum_transfers(graph, "S03", "S09")
    assert res.reachable

    actual_switches = 0
    for i in range(1, len(res.segments)):
        if res.segments[i].line_id != res.segments[i - 1].line_id:
            actual_switches += 1
    assert res.transfer_count == actual_switches


def test_invariant_closure_graph_isolation():
    """Property: The original graph instance must remain strictly unchanged after closures."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    orig_nodes = set(graph.nodes())
    orig_edges = list(graph.edges(keys=True, data=True))

    _ = simulate_station_closure(graph, ["S01", "S02", "S04"])

    assert set(graph.nodes()) == orig_nodes
    assert list(graph.edges(keys=True, data=True)) == orig_edges


def test_invariant_component_size_sum():
    """Property: The sum of connected component sizes must equal total remaining nodes."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    sim_res = simulate_station_closure(graph, ["S02"])
    p_m = sim_res.post_closure_metrics

    assert sum(p_m.component_sizes) == p_m.station_count


def test_invariant_station_rankings_scope():
    """Property: All ranked station IDs must exist in the underlying dataset."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)

    results, _, _ = compute_station_analytics(graph, station_lines_df, lines_df)
    valid_ids = set(stations_df["station_id"])
    for r in results:
        assert r.station_id in valid_ids
