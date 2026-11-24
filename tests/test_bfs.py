"""Unit tests for manual BFS minimum-stop routing algorithm."""

import networkx as nx
import pytest

from src.algorithms.bfs import BFSExecutionError, find_route_bfs
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph


@pytest.fixture
def sample_graph():
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    return build_metro_graph(stns, lines, conns, sl)


@pytest.fixture
def chain_graph():
    """Simple linear chain: A - B - C - D."""
    g = nx.MultiGraph()
    for n in ["A", "B", "C", "D"]:
        g.add_node(n, station_name=n, lat=28.0, lon=77.0, lines={"L1"})
    g.add_edge("A", "B", key="L1", line_id="L1", line_name="Line 1", distance_km=2.0, estimated_time_min=3.0)
    g.add_edge("B", "C", key="L1", line_id="L1", line_name="Line 1", distance_km=2.0, estimated_time_min=3.0)
    g.add_edge("C", "D", key="L1", line_id="L1", line_name="Line 1", distance_km=2.0, estimated_time_min=3.0)
    return g


def test_bfs_simple_chain(chain_graph):
    """Verify BFS finds exact 3-segment route on linear chain."""
    res = find_route_bfs(chain_graph, "A", "D")
    assert res.reachable is True
    assert res.total_stops == 3
    assert res.station_path == ["A", "B", "C", "D"]
    assert res.total_distance_km == 6.0
    assert res.total_estimated_time_min == 9.0


def test_bfs_identical_source_destination(chain_graph):
    """Verify zero-hop route when source equals destination."""
    res = find_route_bfs(chain_graph, "B", "B")
    assert res.reachable is True
    assert res.total_stops == 0
    assert res.station_path == ["B"]
    assert res.total_distance_km == 0.0
    assert res.total_estimated_time_min == 0.0


def test_bfs_invalid_nodes(chain_graph):
    """Verify BFS raises execution error for nonexistent nodes."""
    with pytest.raises(BFSExecutionError):
        find_route_bfs(chain_graph, "A", "UNKNOWN")
    with pytest.raises(BFSExecutionError):
        find_route_bfs(chain_graph, "NONEXISTENT", "B")


def test_bfs_disconnected_graph():
    """Verify BFS correctly handles disconnected graph."""
    g = nx.MultiGraph()
    g.add_node("A", lat=28.0, lon=77.0, lines=set())
    g.add_node("B", lat=28.0, lon=77.0, lines=set())
    g.add_node("C", lat=28.0, lon=77.0, lines=set())
    g.add_edge("A", "B", key="L1", line_id="L1", distance_km=1.0, estimated_time_min=1.0)

    res = find_route_bfs(g, "A", "C")
    assert res.reachable is False
    assert res.total_stops == 0
    assert res.station_path == []


def test_bfs_matches_networkx_oracle(sample_graph):
    """Verify manual BFS stop count exactly matches NetworkX shortest path length."""
    nodes = list(sample_graph.nodes())
    for i in range(len(nodes) - 1):
        u, v = nodes[i], nodes[i + 1]
        res = find_route_bfs(sample_graph, u, v)
        expected_hops = nx.shortest_path_length(sample_graph, u, v)
        assert res.total_stops == expected_hops
        assert len(res.station_path) == expected_hops + 1
