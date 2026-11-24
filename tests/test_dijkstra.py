"""Unit tests for manual Dijkstra shortest-path routing algorithm."""

import math

import networkx as nx
import pytest

from src.algorithms.dijkstra import DijkstraExecutionError, find_route_dijkstra
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph


@pytest.fixture
def sample_graph():
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    return build_metro_graph(stns, lines, conns, sl)


@pytest.fixture
def competing_paths_graph():
    """Graph with two competing paths:
    Path 1: A -> B -> D (2 stops, distance 10 km, time 15 min)
    Path 2: A -> C -> E -> D (3 stops, distance 4 km, time 6 min)
    """
    g = nx.MultiGraph()
    for n in ["A", "B", "C", "D", "E"]:
        g.add_node(n, station_name=n, lat=28.0, lon=77.0, lines={"L1"})

    # Path 1
    g.add_edge("A", "B", key="L1", line_id="L1", distance_km=5.0, estimated_time_min=7.5)
    g.add_edge("B", "D", key="L1", line_id="L1", distance_km=5.0, estimated_time_min=7.5)

    # Path 2
    g.add_edge("A", "C", key="L2", line_id="L2", distance_km=1.3, estimated_time_min=2.0)
    g.add_edge("C", "E", key="L2", line_id="L2", distance_km=1.3, estimated_time_min=2.0)
    g.add_edge("E", "D", key="L2", line_id="L2", distance_km=1.4, estimated_time_min=2.0)
    return g


def test_dijkstra_minimum_time_vs_distance(competing_paths_graph):
    """Verify Dijkstra selects Path 2 with lower travel time and distance despite more stops."""
    res_time = find_route_dijkstra(competing_paths_graph, "A", "D", objective="minimum_time")
    assert res_time.reachable is True
    assert res_time.station_path == ["A", "C", "E", "D"]
    assert res_time.total_stops == 3
    assert math.isclose(res_time.total_estimated_time_min, 6.0, abs_tol=1e-4)

    res_dist = find_route_dijkstra(competing_paths_graph, "A", "D", objective="minimum_distance")
    assert res_dist.reachable is True
    assert res_dist.station_path == ["A", "C", "E", "D"]
    assert math.isclose(res_dist.total_distance_km, 4.0, abs_tol=1e-4)


def test_dijkstra_identical_source_destination(competing_paths_graph):
    """Verify zero-cost route when source equals destination."""
    res = find_route_dijkstra(competing_paths_graph, "C", "C")
    assert res.reachable is True
    assert res.total_stops == 0
    assert res.total_estimated_time_min == 0.0
    assert res.total_distance_km == 0.0


def test_dijkstra_matches_networkx_oracle(sample_graph):
    """Verify Dijkstra optimal costs match NetworkX shortest path length oracle."""
    nodes = list(sample_graph.nodes())
    for i in range(min(5, len(nodes) - 1)):
        u, v = nodes[i], nodes[i + 1]
        res_time = find_route_dijkstra(sample_graph, u, v, objective="minimum_time")
        # NetworkX multi-graph oracle
        nx_cost_time = nx.shortest_path_length(sample_graph, u, v, weight="estimated_time_min")
        assert math.isclose(res_time.total_estimated_time_min, nx_cost_time, abs_tol=1e-3)

        res_dist = find_route_dijkstra(sample_graph, u, v, objective="minimum_distance")
        nx_cost_dist = nx.shortest_path_length(sample_graph, u, v, weight="distance_km")
        assert math.isclose(res_dist.total_distance_km, nx_cost_dist, abs_tol=1e-3)


def test_dijkstra_unsupported_objective(sample_graph):
    """Verify Dijkstra raises error for unsupported objective."""
    with pytest.raises(DijkstraExecutionError):
        find_route_dijkstra(sample_graph, "S01", "S02", objective="invalid_objective")
