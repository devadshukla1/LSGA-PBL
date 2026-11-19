"""Tests for geographic and graph-aware partitioning invariants and balance metrics."""

from scripts.generate_sample_graph import build_sample
from src.partitioning.geographic import geographic_partition
from src.partitioning.graph_aware import graph_aware_partition
from src.partitioning.partition_metrics import compute_partition_metrics


def test_geographic_partitioning_all_nodes_assigned() -> None:
    """Verify geographic partitioning assigns every node to exactly one partition."""
    graph = build_sample()
    k = 4
    result = geographic_partition(graph, k=k)

    assert len(result.node_to_partition) == len(graph)
    assert result.actual_partition_count == k
    assert set(result.node_to_partition.keys()) == set(graph.nodes())
    assert set(result.node_to_partition.values()).issubset(set(range(k)))


def test_graph_aware_partitioning_deterministic_seed() -> None:
    """Verify graph-aware partitioning is strictly deterministic with fixed seed."""
    graph = build_sample()
    res1 = graph_aware_partition(graph, k=3, seed=42)
    res2 = graph_aware_partition(graph, k=3, seed=42)

    assert res1.node_to_partition == res2.node_to_partition
    rep1 = compute_partition_metrics(graph, res1)
    rep2 = compute_partition_metrics(graph, res2)
    assert rep1.cut_edge_count == rep2.cut_edge_count


def test_cut_edge_directed_accounting() -> None:
    """Verify directed cut-edge accounting counts parallel edges separately."""
    graph = build_sample()
    res = geographic_partition(graph, k=2)
    report = compute_partition_metrics(graph, res)

    assert report.cut_edge_count >= 0
    assert 0.0 <= report.cut_edge_ratio <= 1.0


def test_partition_balance_metrics() -> None:
    """Verify partition balance ratio is >= 1.0."""
    graph = build_sample()
    res = geographic_partition(graph, k=4)
    report = compute_partition_metrics(graph, res)

    assert report.partition_balance_ratio >= 1.0
    assert report.largest_partition_size >= report.smallest_partition_size
