"""Tests for cut-edge calculation and partition balance metrics."""

import math

import networkx as nx

from src.partitioning.partition_metrics import compute_partition_metrics
from src.partitioning.partition_models import PartitionResult


def test_cut_edge_directed_and_parallel():
    """Verify directed cut edges, parallel cut edges, and opposite road accounting."""
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node(0, x=77.20, y=28.60)
    g.add_node(1, x=77.21, y=28.60)
    g.add_node(2, x=77.22, y=28.60)

    # Edge from 0 to 1 (cut edge)
    g.add_edge(0, 1, key=0, length_m=100.0)
    # Parallel edge from 0 to 1 with key=1 (second cut edge)
    g.add_edge(0, 1, key=1, length_m=120.0)
    # Reverse edge from 1 to 0 (third cut edge)
    g.add_edge(1, 0, key=0, length_m=100.0)
    # Internal edge from 1 to 2
    g.add_edge(1, 2, key=0, length_m=50.0)

    # Partition assignment: node 0 in P0; nodes 1 and 2 in P1
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 1, 2: 1},
        partition_to_nodes={0: [0], 1: [1, 2]},
    )

    report = compute_partition_metrics(g, result)

    assert report.total_edges == 4
    # Cut edges: (0, 1, 0), (0, 1, 1), and (1, 0, 0)
    assert report.cut_edge_count == 3
    assert report.cut_edge_ratio == 0.75
    assert report.cross_partition_road_length_m == 320.0

    # Partition statistics
    p0_stats = report.partition_statistics[0]
    p1_stats = report.partition_statistics[1]

    # P0 has 2 outgoing cut edges to P1, and 1 incoming cut edge from P1
    assert p0_stats.outgoing_cut_edges == 2
    assert p0_stats.incoming_cut_edges == 1
    assert p0_stats.internal_edge_count == 0

    # P1 has 1 outgoing cut edge to P0, and 2 incoming cut edges from P0
    assert p1_stats.outgoing_cut_edges == 1
    assert p1_stats.incoming_cut_edges == 2
    assert p1_stats.internal_edge_count == 1
    assert p1_stats.total_road_length_m == 50.0


def test_cut_edge_zero_edge_graph():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node(0, x=77.20, y=28.60)
    g.add_node(1, x=77.21, y=28.60)

    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 1},
        partition_to_nodes={0: [0], 1: [1]},
    )

    report = compute_partition_metrics(g, result)
    assert report.total_edges == 0
    assert report.cut_edge_count == 0
    assert report.cut_edge_ratio == 0.0
    assert report.cross_partition_road_length_m == 0.0


def test_partition_balance_metrics_equal():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(8):
        g.add_node(i, x=77.20 + i * 0.001, y=28.60)

    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1},
        partition_to_nodes={0: [0, 1, 2, 3], 1: [4, 5, 6, 7]},
    )

    report = compute_partition_metrics(g, result)
    assert report.total_nodes == 8
    assert report.largest_partition_size == 4
    assert report.smallest_partition_size == 4
    assert report.partition_balance_ratio == 1.0
    assert report.partition_size_std == 0.0
    assert report.empty_partition_count == 0


def test_partition_balance_metrics_unequal():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(10):
        g.add_node(i, x=77.20 + i * 0.001, y=28.60)

    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1, 8: 1, 9: 1},
        partition_to_nodes={0: [0, 1, 2, 3, 4, 5, 6], 1: [7, 8, 9]},
    )

    report = compute_partition_metrics(g, result)
    assert report.largest_partition_size == 7
    assert report.smallest_partition_size == 3
    # Mean is 10/2 = 5. Balance ratio = 7 / 5 = 1.4
    assert math.isclose(report.partition_balance_ratio, 1.4, rel_tol=1e-5)
    # Sizes: [7, 3]. mean=5, diffs=[-2, 2], squared=[4, 4], mean=4, std=2.0
    assert math.isclose(report.partition_size_std, 2.0, rel_tol=1e-5)
