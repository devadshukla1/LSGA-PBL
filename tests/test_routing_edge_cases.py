"""Unit tests for routing edge cases: negative weights, missing attributes, mixed node IDs."""

import networkx as nx
import pytest

from src.algorithms.bfs import find_route_bfs
from src.algorithms.dijkstra import DijkstraExecutionError, find_route_dijkstra


def test_dijkstra_rejects_negative_weight():
    """Verify Dijkstra rejects corrupt negative weights."""
    g = nx.MultiGraph()
    g.add_node("A", lat=28.0, lon=77.0, lines=set())
    g.add_node("B", lat=28.0, lon=77.0, lines=set())
    g.add_edge("A", "B", key="L1", line_id="L1", distance_km=5.0, estimated_time_min=-2.5)

    with pytest.raises(DijkstraExecutionError):
        find_route_dijkstra(g, "A", "B", objective="minimum_time")


def test_dijkstra_rejects_nan_weight():
    """Verify Dijkstra rejects NaN weights."""
    g = nx.MultiGraph()
    g.add_node("A", lat=28.0, lon=77.0, lines=set())
    g.add_node("B", lat=28.0, lon=77.0, lines=set())
    g.add_edge("A", "B", key="L1", line_id="L1", distance_km=float("nan"), estimated_time_min=5.0)

    with pytest.raises(DijkstraExecutionError):
        find_route_dijkstra(g, "A", "B", objective="minimum_distance")


def test_dijkstra_missing_weight_attribute():
    """Verify Dijkstra rejects edges missing required weight attribute."""
    g = nx.MultiGraph()
    g.add_node("A", lat=28.0, lon=77.0, lines=set())
    g.add_node("B", lat=28.0, lon=77.0, lines=set())
    # Omit estimated_time_min
    g.add_edge("A", "B", key="L1", line_id="L1", distance_km=3.0)

    with pytest.raises(DijkstraExecutionError):
        find_route_dijkstra(g, "A", "B", objective="minimum_time")


def test_mixed_type_station_ids():
    """Verify Dijkstra heap tie-breaker is safe even when station IDs are mixed types (int and str)."""
    g = nx.MultiGraph()
    # Mixed int and string station IDs
    g.add_node(101, station_name="Station 101", lat=28.0, lon=77.0, lines=set())
    g.add_node("STN_B", station_name="Station B", lat=28.1, lon=77.1, lines=set())
    g.add_node(103, station_name="Station 103", lat=28.2, lon=77.2, lines=set())

    g.add_edge(101, "STN_B", key="L1", line_id="L1", distance_km=2.0, estimated_time_min=3.0)
    g.add_edge("STN_B", 103, key="L1", line_id="L1", distance_km=2.0, estimated_time_min=3.0)

    # String conversion in our API ensures safe lookup
    res_bfs = find_route_bfs(g, "101", "103")
    assert res_bfs.reachable is True
    assert res_bfs.total_stops == 2

    res_dijkstra = find_route_dijkstra(g, "101", "103", objective="minimum_time")
    assert res_dijkstra.reachable is True
    assert res_dijkstra.total_stops == 2
    assert res_dijkstra.total_estimated_time_min == 6.0


def test_equal_cost_alternative_routes():
    """Verify algorithm produces valid optimal route when multiple equal-cost paths exist."""
    g = nx.MultiGraph()
    for n in ["A", "B1", "B2", "C"]:
        g.add_node(n, lat=28.0, lon=77.0, lines=set())

    # Path 1: A -> B1 -> C (time 4.0)
    g.add_edge("A", "B1", key="L1", line_id="L1", distance_km=2.0, estimated_time_min=2.0)
    g.add_edge("B1", "C", key="L1", line_id="L1", distance_km=2.0, estimated_time_min=2.0)

    # Path 2: A -> B2 -> C (time 4.0)
    g.add_edge("A", "B2", key="L2", line_id="L2", distance_km=2.0, estimated_time_min=2.0)
    g.add_edge("B2", "C", key="L2", line_id="L2", distance_km=2.0, estimated_time_min=2.0)

    res = find_route_dijkstra(g, "A", "C", objective="minimum_time")
    assert res.reachable is True
    assert res.total_stops == 2
    assert res.total_estimated_time_min == 4.0
    # Must choose either Path 1 or Path 2 deterministically
    assert res.station_path in (["A", "B1", "C"], ["A", "B2", "C"])
