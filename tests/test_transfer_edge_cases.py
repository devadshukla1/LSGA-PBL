"""Edge case tests for line-aware transfer routing."""

import networkx as nx
import pytest

from src.algorithms.minimum_transfers import (
    TransferRoutingError,
    find_route_min_transfers_then_fastest,
    find_route_minimum_transfers,
)
from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra


@pytest.fixture
def disconnected_graph():
    """Graph with two disconnected components."""
    g = nx.MultiGraph()
    g.add_node("C1_A", station_name="C1_A", lat=28.0, lon=77.0, lines={"L1"}, is_interchange=False)
    g.add_node("C1_B", station_name="C1_B", lat=28.1, lon=77.1, lines={"L1"}, is_interchange=False)
    g.add_edge("C1_A", "C1_B", key="e1", line_id="L1", line_name="Line 1", distance_km=1.0, estimated_time_min=2.0)

    g.add_node("C2_X", station_name="C2_X", lat=28.5, lon=77.5, lines={"L2"}, is_interchange=False)
    g.add_node("C2_Y", station_name="C2_Y", lat=28.6, lon=77.6, lines={"L2"}, is_interchange=False)
    g.add_edge("C2_X", "C2_Y", key="e2", line_id="L2", line_name="Line 2", distance_km=1.0, estimated_time_min=2.0)
    return g


@pytest.fixture
def parallel_line_graph():
    """Stations A and B directly connected by two distinct parallel lines."""
    g = nx.MultiGraph()
    g.add_node("A", station_name="A", lat=28.0, lon=77.0, lines={"L1", "L2"}, is_interchange=True)
    g.add_node("B", station_name="B", lat=28.1, lon=77.1, lines={"L1", "L2"}, is_interchange=True)
    g.add_node("C", station_name="C", lat=28.2, lon=77.2, lines={"L2"}, is_interchange=False)

    # A - B on L1 (slow)
    g.add_edge("A", "B", key="p1", line_id="L1", line_name="Line 1", distance_km=2.0, estimated_time_min=10.0)
    # A - B on L2 (fast)
    g.add_edge("A", "B", key="p2", line_id="L2", line_name="Line 2", distance_km=2.0, estimated_time_min=3.0)
    # B - C on L2
    g.add_edge("B", "C", key="p3", line_id="L2", line_name="Line 2", distance_km=2.0, estimated_time_min=3.0)
    return g


def test_disconnected_routes_return_unreachable(disconnected_graph):
    """Routing between disconnected components returns reachable=False with descriptive message."""
    res1 = find_route_minimum_transfers(disconnected_graph, "C1_A", "C2_X")
    assert res1.reachable is False
    assert "No route exists" in res1.message

    res2 = find_route_min_transfers_then_fastest(disconnected_graph, "C1_A", "C2_X")
    assert res2.reachable is False

    res3 = find_route_transfer_aware_dijkstra(disconnected_graph, "C1_A", "C2_X", transfer_penalty_min=5.0)
    assert res3.reachable is False


def test_parallel_edges_maintain_single_line_continuity(parallel_line_graph):
    """When going A -> B -> C, the algorithm should pick L2 for A-B to avoid an unnecessary transfer."""
    res = find_route_minimum_transfers(parallel_line_graph, "A", "C")
    assert res.reachable is True
    assert res.transfer_count == 0
    assert res.line_sequence == ["L2", "L2"]


def test_missing_nodes_raise_clean_error(parallel_line_graph):
    with pytest.raises(TransferRoutingError):
        find_route_minimum_transfers(parallel_line_graph, "NON_EXISTENT", "C")
