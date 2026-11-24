"""Unit tests for route reconstruction and segment validity."""

import networkx as nx
import pytest

from src.algorithms.bfs import find_route_bfs
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.route_utils import (
    RouteValidationError,
    choose_best_parallel_edge,
    validate_route,
)


@pytest.fixture
def parallel_graph():
    """Graph with two parallel edges:
    S1 -- L01 (fast, 2.0 min) -- S2
    S1 -- L02 (slow, 5.0 min) -- S2
    """
    g = nx.MultiGraph()
    g.add_node("S1", station_name="Station 1", lat=28.0, lon=77.0, lines={"L01", "L02"})
    g.add_node("S2", station_name="Station 2", lat=28.1, lon=77.1, lines={"L01", "L02"})
    g.add_edge("S1", "S2", key="L01", line_id="L01", line_name="Red Line", distance_km=2.0, estimated_time_min=2.0)
    g.add_edge("S1", "S2", key="L02", line_id="L02", line_name="Blue Line", distance_km=2.0, estimated_time_min=5.0)
    return g


def test_choose_best_parallel_edge(parallel_graph):
    """Verify tie-breaker chooses the faster edge L01."""
    best_key, attrs = choose_best_parallel_edge(parallel_graph, "S1", "S2", preference="minimum_time")
    assert best_key == "L01"
    assert attrs["estimated_time_min"] == 2.0


def test_dijkstra_selects_faster_parallel_edge(parallel_graph):
    """Verify Dijkstra preserves exact edge key for faster parallel link."""
    res = find_route_dijkstra(parallel_graph, "S1", "S2", objective="minimum_time")
    assert res.total_stops == 1
    assert len(res.segments) == 1
    assert res.segments[0].edge_key == "L01"
    assert res.segments[0].line_id == "L01"
    assert res.total_estimated_time_min == 2.0


def test_bfs_selects_deterministic_parallel_edge(parallel_graph):
    """Verify BFS uses tie-breaking policy to choose L01."""
    res = find_route_bfs(parallel_graph, "S1", "S2")
    assert res.total_stops == 1
    assert len(res.segments) == 1
    assert res.segments[0].edge_key == "L01"
    assert res.segments[0].line_id == "L01"


def test_validate_route_detects_mismatch(parallel_graph):
    """Verify validate_route detects broken route invariants."""
    res = find_route_bfs(parallel_graph, "S1", "S2")
    # Mutate station path to introduce a mismatch
    res.station_path.append("S_GHOST")
    with pytest.raises(RouteValidationError):
        validate_route(parallel_graph, res)
