"""Unit tests for comparative evaluation of routing algorithms."""

import pytest

from src.algorithms.comparison import compare_routing_algorithms
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph


@pytest.fixture
def sample_graph():
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    return build_metro_graph(stns, lines, conns, sl)


def test_compare_routing_algorithms(sample_graph):
    """Verify comparison table columns, row count, and results map."""
    comp_df, results_map = compare_routing_algorithms(sample_graph, "S03", "S12")

    assert len(comp_df) >= 3
    expected_cols = {
        "Algorithm",
        "Objective",
        "Reachable",
        "Stops",
        "Distance (km)",
        "Estimated Time (min)",
        "Explored Nodes",
        "Examined Edges",
        "Runtime (ms)",
    }
    assert expected_cols.issubset(set(comp_df.columns))

    assert "BFS (Min Stops)" in results_map
    assert "Dijkstra (Min Time)" in results_map
    assert "Dijkstra (Min Distance)" in results_map

    bfs_res = results_map["BFS (Min Stops)"]
    dijkstra_time_res = results_map["Dijkstra (Min Time)"]

    assert bfs_res.reachable is True
    assert dijkstra_time_res.reachable is True
    # BFS stops must be <= Dijkstra stops
    assert bfs_res.total_stops <= dijkstra_time_res.total_stops
