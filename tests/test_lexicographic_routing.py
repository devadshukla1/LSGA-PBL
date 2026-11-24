"""Tests for Lexicographic routing: Minimum Transfers then Fastest."""

import networkx as nx
import pytest

from src.algorithms.minimum_transfers import find_route_min_transfers_then_fastest


@pytest.fixture
def multi_line_options_graph():
    """Graph with two 1-transfer routes:

    Route 1: S1 -[L1]-> T1 -[L2]-> D  (Time: 10 + 10 = 20 min)
    Route 2: S1 -[L3]-> T2 -[L4]-> D  (Time: 3 + 4 = 7 min)
    Both have 1 transfer. Route 2 is faster.
    """
    g = nx.MultiGraph()
    for s in ["S1", "T1", "T2", "D"]:
        g.add_node(s, station_name=s, lat=28.0, lon=77.0, lines=set(), is_interchange=True)

    g.add_edge("S1", "T1", key="e1", line_id="L1", line_name="Line 1", distance_km=5.0, estimated_time_min=10.0)
    g.add_edge("T1", "D", key="e2", line_id="L2", line_name="Line 2", distance_km=5.0, estimated_time_min=10.0)

    g.add_edge("S1", "T2", key="e3", line_id="L3", line_name="Line 3", distance_km=2.0, estimated_time_min=3.0)
    g.add_edge("T2", "D", key="e4", line_id="L4", line_name="Line 4", distance_km=3.0, estimated_time_min=4.0)
    return g


def test_lexicographic_tie_breaking(multi_line_options_graph):
    """Among routes with 1 transfer, lexicographic Dijkstra selects the fastest (7 min vs 20 min)."""
    res = find_route_min_transfers_then_fastest(multi_line_options_graph, "S1", "D")
    assert res.reachable is True
    assert res.transfer_count == 1
    assert res.total_estimated_time_min == 7.0
    assert res.station_path == ["S1", "T2", "D"]
    assert res.line_sequence == ["L3", "L4"]


def test_lexicographic_priority_transfers_over_speed():
    """A 0-transfer route taking 50 minutes must be chosen over a 1-transfer route taking 5 minutes."""
    g = nx.MultiGraph()
    for s in ["A", "B", "C", "D"]:
        g.add_node(s, station_name=s, lat=28.0, lon=77.0, lines=set(), is_interchange=False)

    # 0 transfer slow path
    g.add_edge("A", "D", key="slow", line_id="L_SLOW", line_name="Slow Line", distance_km=50.0, estimated_time_min=50.0)

    # 1 transfer fast path
    g.add_edge("A", "B", key="f1", line_id="L_FAST1", line_name="Fast 1", distance_km=1.0, estimated_time_min=2.0)
    g.add_edge("B", "D", key="f2", line_id="L_FAST2", line_name="Fast 2", distance_km=1.0, estimated_time_min=3.0)

    res = find_route_min_transfers_then_fastest(g, "A", "D")
    assert res.reachable is True
    assert res.transfer_count == 0
    assert res.station_path == ["A", "D"]
    assert res.total_estimated_time_min == 50.0
