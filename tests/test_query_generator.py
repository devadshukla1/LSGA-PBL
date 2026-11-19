"""Tests for reproducible query generation and reachability enforcement."""

import networkx as nx

from src.benchmarks.query_generator import (
    generate_benchmark_queries,
    generate_unreachable_queries,
)
from src.graph.dataset_service import load


def test_query_generator_reachability():
    info = load()
    graph = info.graph
    queries = generate_benchmark_queries(graph, count=15, seed=42)

    assert len(queries) > 0
    for q in queries:
        assert q.source != q.target
        assert q.source in graph
        assert q.target in graph
        assert q.is_reachable is True
        assert q.reference_cost is not None
        assert q.reference_cost > 0.0
        # Verify with NetworkX that path exists
        assert nx.has_path(graph, q.source, q.target)


def test_query_generator_deterministic_reproducibility():
    info = load()
    graph = info.graph
    q1 = generate_benchmark_queries(graph, count=10, seed=42)
    q2 = generate_benchmark_queries(graph, count=10, seed=42)

    assert len(q1) == len(q2)
    for a, b in zip(q1, q2, strict=True):
        assert a.source == b.source
        assert a.target == b.target
        assert a.reference_cost == b.reference_cost


def test_unreachable_query_generation():
    info = load()
    graph = info.graph
    unreachable = generate_unreachable_queries(graph, count=5, seed=42)
    for q in unreachable:
        assert q.is_reachable is False
        assert not nx.has_path(graph, q.source, q.target)


def test_query_generator_small_graph_bounds():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node(0, x=77.2, y=28.6)
    g.add_node(1, x=77.21, y=28.6)
    g.add_edge(0, 1, length_m=100.0, travel_time_s=10.0)

    # Only 1 unique reachable pair exists (0 -> 1)
    queries = generate_benchmark_queries(g, count=20, seed=42)
    assert len(queries) == 1
    assert queries[0].source == 0
    assert queries[0].target == 1
