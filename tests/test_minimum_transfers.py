"""Independent unit and oracle-checked tests for 0-1 BFS minimum-transfer routing."""

import networkx as nx
import pytest

from src.algorithms.minimum_transfers import (
    TransferRoutingError,
    find_route_minimum_transfers,
)
from src.algorithms.route_utils import validate_route
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph


@pytest.fixture
def sample_graph():
    """Loads the 12-station sample metro graph."""
    stations, lines, conns, st_lines, _ = load_validated_dataset("data/sample")
    return build_metro_graph(stations, lines, conns, st_lines)


@pytest.fixture
def simple_linear_graph():
    """A straight 3-station line on Line A: S1 - S2 - S3."""
    g = nx.MultiGraph()
    g.add_node("S1", station_name="Station 1", lat=28.0, lon=77.0, lines={"L1"}, is_interchange=False)
    g.add_node("S2", station_name="Station 2", lat=28.1, lon=77.1, lines={"L1"}, is_interchange=False)
    g.add_node("S3", station_name="Station 3", lat=28.2, lon=77.2, lines={"L1"}, is_interchange=False)
    g.add_edge("S1", "S2", key="e1", line_id="L1", line_name="Line 1", distance_km=2.0, estimated_time_min=3.0)
    g.add_edge("S2", "S3", key="e2", line_id="L1", line_name="Line 1", distance_km=2.0, estimated_time_min=3.0)
    return g


@pytest.fixture
def two_path_graph():
    """Graph with two routes between S1 and S4:

    Path A (Direct line L1): S1 - S2 - S3 - S4 (3 hops, 0 transfers)
    Path B (Short-cut via L2 and L3): S1 - X - S4 (2 hops, 1 transfer: L2 -> L3)
    """
    g = nx.MultiGraph()
    for s in ["S1", "S2", "S3", "S4", "X"]:
        g.add_node(s, station_name=s, lat=28.0, lon=77.0, lines=set(), is_interchange=False)

    # Path A: Line 1
    g.add_edge("S1", "S2", key="a1", line_id="L1", line_name="Line 1", distance_km=5.0, estimated_time_min=5.0)
    g.add_edge("S2", "S3", key="a2", line_id="L1", line_name="Line 1", distance_km=5.0, estimated_time_min=5.0)
    g.add_edge("S3", "S4", key="a3", line_id="L1", line_name="Line 1", distance_km=5.0, estimated_time_min=5.0)

    # Path B: Line 2 then Line 3
    g.add_edge("S1", "X", key="b1", line_id="L2", line_name="Line 2", distance_km=2.0, estimated_time_min=2.0)
    g.add_edge("X", "S4", key="b2", line_id="L3", line_name="Line 3", distance_km=2.0, estimated_time_min=2.0)
    return g


def test_zero_hop_route(sample_graph):
    """Origin == Destination should have 0 stops and 0 transfers."""
    res = find_route_minimum_transfers(sample_graph, "S01", "S01")
    assert res.reachable is True
    assert res.total_stops == 0
    assert res.transfer_count == 0
    assert res.station_path == ["S01"]
    assert res.segments == []


def test_single_line_zero_transfers(simple_linear_graph):
    """Linear route on same line must yield exactly 0 transfers."""
    res = find_route_minimum_transfers(simple_linear_graph, "S1", "S3")
    assert res.reachable is True
    assert res.total_stops == 2
    assert res.transfer_count == 0
    assert res.line_sequence == ["L1", "L1"]
    assert len(res.transfer_stations) == 0


def test_min_transfer_prefers_zero_transfers_over_fewer_stops(two_path_graph):
    """0-1 BFS must choose Path A (3 hops, 0 transfers) over Path B (2 hops, 1 transfer)."""
    res = find_route_minimum_transfers(two_path_graph, "S1", "S4")
    assert res.reachable is True
    assert res.transfer_count == 0
    assert res.station_path == ["S1", "S2", "S3", "S4"]
    assert res.line_sequence == ["L1", "L1", "L1"]


def test_sample_network_min_transfers(sample_graph):
    """Verify route computation on sample dataset between S03 and S09."""
    res = find_route_minimum_transfers(sample_graph, "S03", "S09")
    assert res.reachable is True
    assert validate_route(sample_graph, res) is True
    # S03 is on L01 only; S09 is on L03 only. Must transfer from L01 to L03 (at S04 or S10)
    assert res.transfer_count >= 1
    assert any(s in res.transfer_stations for s in ["S04", "S10"])


def test_invalid_station_raises_error(sample_graph):
    """Non-existent station should raise TransferRoutingError."""
    with pytest.raises(TransferRoutingError):
        find_route_minimum_transfers(sample_graph, "9999", "101")
