"""Tests for Transfer-Penalty-Aware Dijkstra routing."""

import networkx as nx
import pytest

from src.algorithms.minimum_transfers import TransferRoutingError
from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra


@pytest.fixture
def penalty_tradeoff_graph():
    """Graph exhibiting crossover behavior based on transfer penalty:

    Path 1 (Direct, 0 transfers): A -[L1]-> B (travel time: 10 min, 0 transfers)
    Path 2 (Transfer, 1 transfer): A -[L2]-> C -[L3]-> B (travel time: 3 + 3 = 6 min, 1 transfer)

    If penalty == 0.0 min:
        Path 1 cost = 10 min
        Path 2 cost = 6 min (Path 2 wins)

    If penalty == 5.0 min:
        Path 1 cost = 10 min
        Path 2 cost = 6 + 5 = 11 min (Path 1 wins)
    """
    g = nx.MultiGraph()
    for s in ["A", "B", "C"]:
        g.add_node(s, station_name=s, lat=28.0, lon=77.0, lines=set(), is_interchange=True)

    g.add_edge("A", "B", key="direct", line_id="L1", line_name="Line 1", distance_km=8.0, estimated_time_min=10.0)
    g.add_edge("A", "C", key="hop1", line_id="L2", line_name="Line 2", distance_km=2.0, estimated_time_min=3.0)
    g.add_edge("C", "B", key="hop2", line_id="L3", line_name="Line 3", distance_km=2.0, estimated_time_min=3.0)
    return g


def test_zero_penalty_prefers_fastest_transfer(penalty_tradeoff_graph):
    """With 0.0 penalty, the algorithm acts like pure Dijkstra travel time."""
    res = find_route_transfer_aware_dijkstra(penalty_tradeoff_graph, "A", "B", transfer_penalty_min=0.0)
    assert res.reachable is True
    assert res.station_path == ["A", "C", "B"]
    assert res.transfer_count == 1
    assert res.segment_travel_time_min == 6.0
    assert res.total_modeled_journey_time_min == 6.0


def test_high_penalty_prefers_direct_route(penalty_tradeoff_graph):
    """With 5.0 min penalty, the 10 min direct route beats 6 + 5 = 11 min route."""
    res = find_route_transfer_aware_dijkstra(penalty_tradeoff_graph, "A", "B", transfer_penalty_min=5.0)
    assert res.reachable is True
    assert res.station_path == ["A", "B"]
    assert res.transfer_count == 0
    assert res.segment_travel_time_min == 10.0
    assert res.total_modeled_journey_time_min == 10.0


def test_negative_penalty_rejected(penalty_tradeoff_graph):
    """Negative transfer penalties are physically invalid and must raise an error."""
    with pytest.raises(TransferRoutingError):
        find_route_transfer_aware_dijkstra(penalty_tradeoff_graph, "A", "B", transfer_penalty_min=-2.0)
