"""Tests for geographic recursive bisection partitioning."""

import copy

import networkx as nx
import pytest

from src.partitioning.geographic import geographic_partition
from src.partitioning.partition_validation import assert_valid_partition


def _build_grid_graph(rows: int = 4, cols: int = 4) -> nx.MultiDiGraph:
    """Helper to build a small synthetic grid graph with geographic coordinates."""
    g = nx.MultiDiGraph(crs="EPSG:4326")
    node_id = 0
    for r in range(rows):
        for c in range(cols):
            g.add_node(node_id, x=77.20 + c * 0.01, y=28.60 + r * 0.01)
            node_id += 1

    # Connect adjacent grid nodes
    for r in range(rows):
        for c in range(cols):
            curr = r * cols + c
            if c + 1 < cols:
                right = r * cols + (c + 1)
                g.add_edge(curr, right, length_m=100.0, speed_kph=40.0, travel_time_s=9.0)
                g.add_edge(right, curr, length_m=100.0, speed_kph=40.0, travel_time_s=9.0)
            if r + 1 < rows:
                down = (r + 1) * cols + c
                g.add_edge(curr, down, length_m=100.0, speed_kph=40.0, travel_time_s=9.0)
                g.add_edge(down, curr, length_m=100.0, speed_kph=40.0, travel_time_s=9.0)
    return g


def test_geographic_k_1():
    g = _build_grid_graph(3, 3)
    res = geographic_partition(g, k=1)
    assert_valid_partition(g, res, expected_k=1)
    assert res.actual_partition_count == 1
    assert len(res.partition_to_nodes[0]) == 9
    assert all(p == 0 for p in res.node_to_partition.values())


def test_geographic_k_2():
    g = _build_grid_graph(4, 4)
    res = geographic_partition(g, k=2)
    assert_valid_partition(g, res, expected_k=2)
    assert res.actual_partition_count == 2
    assert len(res.partition_to_nodes[0]) == 8
    assert len(res.partition_to_nodes[1]) == 8


def test_geographic_k_3_non_power_of_two():
    g = _build_grid_graph(3, 4)  # 12 nodes
    res = geographic_partition(g, k=3)
    assert_valid_partition(g, res, expected_k=3)
    assert res.actual_partition_count == 3
    # 12 nodes divided by 3 should be 4, 4, 4
    sizes = [len(nodes) for nodes in res.partition_to_nodes.values()]
    assert sorted(sizes) == [4, 4, 4]


def test_geographic_k_5_odd_nodes():
    g = _build_grid_graph(3, 5)  # 15 nodes
    res = geographic_partition(g, k=5)
    assert_valid_partition(g, res, expected_k=5)
    assert res.actual_partition_count == 5
    sizes = [len(nodes) for nodes in res.partition_to_nodes.values()]
    assert sorted(sizes) == [3, 3, 3, 3, 3]


def test_geographic_k_equals_node_count():
    g = _build_grid_graph(2, 2)  # 4 nodes
    res = geographic_partition(g, k=4)
    assert_valid_partition(g, res, expected_k=4)
    assert res.actual_partition_count == 4
    for p in range(4):
        assert len(res.partition_to_nodes[p]) == 1


def test_geographic_invalid_k():
    g = _build_grid_graph(3, 3)
    with pytest.raises(ValueError, match="K must be >= 1"):
        geographic_partition(g, k=0)
    with pytest.raises(ValueError, match="K must be >= 1"):
        geographic_partition(g, k=-2)
    with pytest.raises(ValueError, match="cannot exceed node count"):
        geographic_partition(g, k=10)


def test_geographic_empty_graph():
    empty_g = nx.MultiDiGraph(crs="EPSG:4326")
    with pytest.raises(ValueError, match="Cannot partition an empty graph"):
        geographic_partition(empty_g, k=1)


def test_geographic_duplicate_and_equal_coordinates():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    # All nodes share the exact same coordinate
    for i in range(6):
        g.add_node(i, x=77.21, y=28.63)
    g.add_edge(0, 1, length_m=10.0, speed_kph=30.0, travel_time_s=1.2)

    res = geographic_partition(g, k=2)
    assert_valid_partition(g, res, expected_k=2)
    assert res.actual_partition_count == 2
    assert len(res.partition_to_nodes[0]) == 3
    assert len(res.partition_to_nodes[1]) == 3


def test_geographic_disconnected_graph():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    # Component 1
    g.add_node(0, x=77.10, y=28.50)
    g.add_node(1, x=77.11, y=28.51)
    g.add_edge(0, 1, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)
    # Component 2 (far away)
    g.add_node(2, x=77.50, y=28.90)
    g.add_node(3, x=77.51, y=28.91)
    g.add_edge(2, 3, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)

    res = geographic_partition(g, k=2)
    assert_valid_partition(g, res, expected_k=2)
    assert set(res.node_to_partition.keys()) == {0, 1, 2, 3}


def test_geographic_determinism():
    g = _build_grid_graph(4, 4)
    res1 = geographic_partition(g, k=4, seed=42)
    res2 = geographic_partition(g, k=4, seed=99)
    assert res1.node_to_partition == res2.node_to_partition


def test_geographic_immutability():
    g = _build_grid_graph(3, 3)
    nodes_before = copy.deepcopy(dict(g.nodes(data=True)))
    edges_before = copy.deepcopy(list(g.edges(keys=True, data=True)))

    geographic_partition(g, k=3)

    assert dict(g.nodes(data=True)) == nodes_before
    assert list(g.edges(keys=True, data=True)) == edges_before
