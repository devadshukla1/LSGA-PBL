"""Tests for graph-aware balanced region growing partitioning."""

import copy

import networkx as nx
import pytest

from src.partitioning.graph_aware import graph_aware_partition
from src.partitioning.partition_validation import assert_valid_partition


def _build_directed_corridor() -> nx.MultiDiGraph:
    """Build a linear corridor graph with alternating one-way and two-way roads."""
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(12):
        g.add_node(i, x=77.20 + i * 0.002, y=28.60 + (i % 2) * 0.001)

    for i in range(11):
        # Forward edge
        g.add_edge(i, i + 1, length_m=80.0, speed_kph=40.0, travel_time_s=7.2)
        # Backward edge on even indices (some one-way roads)
        if i % 2 == 0:
            g.add_edge(i + 1, i, length_m=80.0, speed_kph=40.0, travel_time_s=7.2)
    return g


def test_graph_aware_k_1():
    g = _build_directed_corridor()
    res = graph_aware_partition(g, k=1)
    assert_valid_partition(g, res, expected_k=1)
    assert res.actual_partition_count == 1
    assert len(res.partition_to_nodes[0]) == 12


def test_graph_aware_balanced_k_3():
    g = _build_directed_corridor()
    res = graph_aware_partition(g, k=3)
    assert_valid_partition(g, res, expected_k=3)
    assert res.actual_partition_count == 3
    sizes = [len(nodes) for nodes in res.partition_to_nodes.values()]
    # 12 nodes divided by 3 should be 4, 4, 4 (or within tolerance)
    assert sum(sizes) == 12
    assert max(sizes) - min(sizes) <= 2


def test_graph_aware_disconnected_graph():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    # Island A (4 nodes)
    for i in range(4):
        g.add_node(i, x=77.20 + i * 0.001, y=28.60)
    g.add_edge(0, 1, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)
    g.add_edge(1, 2, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)
    g.add_edge(2, 3, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)

    # Island B (4 nodes)
    for i in range(4, 8):
        g.add_node(i, x=77.30 + (i - 4) * 0.001, y=28.70)
    g.add_edge(4, 5, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)
    g.add_edge(5, 6, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)
    g.add_edge(6, 7, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)

    res = graph_aware_partition(g, k=2)
    assert_valid_partition(g, res, expected_k=2)
    assert len(res.node_to_partition) == 8


def test_graph_aware_isolated_nodes():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(5):
        g.add_node(i, x=77.20 + i * 0.001, y=28.60)
    # Only connect 0-1 and 1-2; 3 and 4 are isolated
    g.add_edge(0, 1, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)
    g.add_edge(1, 2, length_m=50.0, speed_kph=30.0, travel_time_s=6.0)

    res = graph_aware_partition(g, k=2)
    assert_valid_partition(g, res, expected_k=2)
    assert len(res.node_to_partition) == 5
    assert set(res.node_to_partition.keys()) == {0, 1, 2, 3, 4}


def test_graph_aware_determinism():
    g = _build_directed_corridor()
    res1 = graph_aware_partition(g, k=3, seed=42)
    res2 = graph_aware_partition(g, k=3, seed=42)
    assert res1.node_to_partition == res2.node_to_partition


def test_graph_aware_boundary_refinement():
    g = _build_directed_corridor()
    res_no_refine = graph_aware_partition(g, k=3, max_refinement_passes=0)
    res_refined = graph_aware_partition(g, k=3, max_refinement_passes=3)
    assert_valid_partition(g, res_no_refine, expected_k=3)
    assert_valid_partition(g, res_refined, expected_k=3)


def test_graph_aware_immutability():
    g = _build_directed_corridor()
    nodes_before = copy.deepcopy(dict(g.nodes(data=True)))
    edges_before = copy.deepcopy(list(g.edges(keys=True, data=True)))

    graph_aware_partition(g, k=3)

    assert dict(g.nodes(data=True)) == nodes_before
    assert list(g.edges(keys=True, data=True)) == edges_before


def test_graph_aware_invalid_k():
    g = _build_directed_corridor()
    with pytest.raises(ValueError, match="K must be >= 1"):
        graph_aware_partition(g, k=0)
    with pytest.raises(ValueError, match="cannot exceed node count"):
        graph_aware_partition(g, k=100)
