"""Tests verifying deterministic reproducibility across graph generators, simulations, and seeds."""

from scripts.generate_sample_graph import build_sample
from src.analytics.centrality import centrality
from src.analytics.resilience import resilience_experiment
from src.benchmarks.query_generator import generate_benchmark_queries
from src.partitioning.geographic import geographic_partition
from src.partitioning.graph_aware import graph_aware_partition
from src.simulation.scenario_builder import create_scenario


def test_sample_graph_generation_reproducibility() -> None:
    """Verify build_sample produces topologically identical graphs."""
    g1 = build_sample()
    g2 = build_sample()

    assert set(g1.nodes()) == set(g2.nodes())
    assert set(g1.edges(keys=True)) == set(g2.edges(keys=True))
    for u, v, k in g1.edges(keys=True):
        assert g1.edges[u, v, k]["length_m"] == g2.edges[u, v, k]["length_m"]
        assert g1.edges[u, v, k]["travel_time_s"] == g2.edges[u, v, k]["travel_time_s"]


def test_scenario_creation_reproducibility() -> None:
    """Verify create_scenario produces identical closed edges and parameters with same seed."""
    g = build_sample()
    sc1 = create_scenario(g, "sample", "moderate", 42, 0.5)
    sc2 = create_scenario(g, "sample", "moderate", 42, 0.5)

    assert sc1.congestion_level == sc2.congestion_level
    assert sc1.random_seed == sc2.random_seed
    assert sc1.closed_edges == sc2.closed_edges
    assert sc1.blocked_nodes == sc2.blocked_nodes
    assert sc1.parameters == sc2.parameters


def test_resilience_experiment_reproducibility() -> None:
    """Verify percolation experiments produce identical retention tables with same seed."""
    g = build_sample()
    deg = centrality(g, metric="degree")
    t1 = resilience_experiment(g, deg.scores, "degree", (0.0, 0.2), seed=42, repetitions=5)
    t2 = resilience_experiment(g, deg.scores, "degree", (0.0, 0.2), seed=42, repetitions=5)

    assert t1 == t2


def test_partitioning_methods_reproducibility() -> None:
    """Verify geographic and graph-aware partitionings are deterministic."""
    g = build_sample()
    geo1 = geographic_partition(g, k=4)
    geo2 = geographic_partition(g, k=4)
    assert geo1.node_to_partition == geo2.node_to_partition

    aware1 = graph_aware_partition(g, k=4, seed=123)
    aware2 = graph_aware_partition(g, k=4, seed=123)
    assert aware1.node_to_partition == aware2.node_to_partition


def test_query_generator_reproducibility_check() -> None:
    """Verify query generator determinism."""
    g = build_sample()
    q1 = generate_benchmark_queries(g, count=8, seed=999)
    q2 = generate_benchmark_queries(g, count=8, seed=999)
    assert q1 == q2
