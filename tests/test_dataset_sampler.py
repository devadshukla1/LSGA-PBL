"""Tests for deterministic graph-size sampling and dataset preparation."""

import copy

import networkx as nx
import pytest

from src.benchmarks.dataset_sampler import (
    _sample_connected_subgraph,
    prepare_benchmark_datasets,
)
from src.graph.dataset_service import load


def test_connected_subgraph_sampling_exact_size():
    info = load()
    graph = info.graph
    target = 10
    sub = _sample_connected_subgraph(graph, target_size=target, seed=42)

    assert len(sub) == target
    assert isinstance(sub, nx.MultiDiGraph)
    # Check that all sub nodes exist in parent graph
    assert all(n in graph.nodes for n in sub.nodes)
    # Verify edge keys and attributes are preserved
    for u, v, k, d in sub.edges(keys=True, data=True):
        assert graph.has_edge(u, v, k)
        assert "length_m" in d


def test_sampling_target_exceeds_graph_size():
    info = load()
    graph = info.graph
    with pytest.raises(ValueError, match="exceeds source graph size"):
        _sample_connected_subgraph(graph, target_size=100)


def test_sampling_nonpositive_size():
    info = load()
    graph = info.graph
    with pytest.raises(ValueError, match="must be positive"):
        _sample_connected_subgraph(graph, target_size=0)


def test_prepare_benchmark_datasets_handles_oversized_targets():
    info = load()
    graph = info.graph
    total = len(graph)
    # Request sizes smaller and larger than total
    target_sizes = [8, 12, 100, 500]
    datasets = prepare_benchmark_datasets(graph, "offline", target_sizes=target_sizes, seed=42)

    node_counts = [d.node_count for d in datasets]
    # Oversized targets (100, 500) skipped; valid ones (8, 12) and full (16) present
    assert 8 in node_counts
    assert 12 in node_counts
    assert total in node_counts
    assert 100 not in node_counts
    assert 500 not in node_counts


def test_sampler_preserves_original_graph():
    info = load()
    graph = info.graph
    nodes_before = copy.deepcopy(dict(graph.nodes(data=True)))
    edges_before = copy.deepcopy(list(graph.edges(keys=True, data=True)))

    prepare_benchmark_datasets(graph, "offline", target_sizes=[8, 12], seed=42)

    assert dict(graph.nodes(data=True)) == nodes_before
    assert list(graph.edges(keys=True, data=True)) == edges_before
