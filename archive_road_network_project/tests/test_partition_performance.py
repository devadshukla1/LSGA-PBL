"""Tests for partition and indexing benchmark metrics."""

import networkx as nx
import pytest

from src.benchmarks.partition_benchmarks import run_partition_benchmarks


def _build_benchmark_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(16):
        r, c = divmod(i, 4)
        g.add_node(i, x=77.20 + c * 0.002, y=28.60 + r * 0.002)

    for i in range(16):
        r, c = divmod(i, 4)
        if c + 1 < 4:
            g.add_edge(i, i + 1, length_m=100.0, speed_kph=40.0, travel_time_s=9.0)
        if r + 1 < 4:
            g.add_edge(i, i + 4, length_m=100.0, speed_kph=40.0, travel_time_s=9.0)
    return g


def test_partition_benchmarks_execution():
    g = _build_benchmark_graph()
    report = run_partition_benchmarks(g, k=2, repetitions=3, seed=42)

    assert report.correctness_verified is True
    assert report.k == 2
    assert report.node_count == 16
    assert report.edge_count == g.number_of_edges()

    # Timing fields are non-negative and valid
    for stats in (
        report.geographic_time,
        report.graph_aware_time,
        report.index_build_time,
        report.brute_force_query_time,
        report.indexed_query_time,
    ):
        assert stats.repetitions == 3
        assert stats.mean_s >= 0.0
        assert stats.median_s >= 0.0
        assert stats.min_s >= 0.0
        assert stats.max_s >= stats.min_s
        assert stats.std_s >= 0.0

    assert report.query_speedup > 0.0


def test_partition_benchmarks_empty_graph():
    empty_g = nx.MultiDiGraph(crs="EPSG:4326")
    with pytest.raises(ValueError, match="Cannot benchmark an empty graph"):
        run_partition_benchmarks(empty_g, k=2)
