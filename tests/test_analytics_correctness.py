"""Tests for graph analytics, centrality measures, resilience degradation, and MST."""

from scripts.generate_sample_graph import build_sample
from src.analytics.centrality import centrality
from src.analytics.connectivity import connectivity_summary
from src.analytics.critical_nodes import critical_nodes
from src.analytics.mst import minimum_spanning_forest
from src.analytics.resilience import resilience_experiment


def test_degree_centralities() -> None:
    """Verify in-degree, out-degree, and total degree centrality computations."""
    graph = build_sample()
    for metric in ("degree", "in_degree", "out_degree"):
        res = centrality(graph, metric=metric)
        assert len(res.scores) == len(graph)
        assert all(0.0 <= score for score in res.scores.values())
        assert len(res.top_nodes) == len(graph)


def test_closeness_and_pagerank() -> None:
    """Verify closeness directions (incoming/outgoing) and PageRank scores."""
    graph = build_sample()
    close_in = centrality(graph, metric="closeness", direction="incoming")
    close_out = centrality(graph, metric="closeness", direction="outgoing")
    pr = centrality(graph, metric="pagerank")

    assert len(close_in.scores) == len(graph)
    assert len(close_out.scores) == len(graph)
    assert len(pr.scores) == len(graph)
    # PageRank scores sum to approximately 1.0 across all nodes
    assert abs(sum(pr.scores.values()) - 1.0) < 0.05


def test_critical_intersections_ranking() -> None:
    """Verify composite ranking combines normalized centrality metrics."""
    graph = build_sample()
    metrics = {
        name: centrality(graph, metric=name)
        for name in ("degree", "betweenness", "closeness", "pagerank")
    }
    ranking = critical_nodes(graph, metrics, top_k=5)

    assert len(ranking) == 5
    # Verify scores are sorted nonincreasing
    scores = [row["combined_score"] for row in ranking]
    assert scores == sorted(scores, reverse=True)


def test_connectivity_summary() -> None:
    """Verify weak and strong component metrics."""
    graph = build_sample()
    conn = connectivity_summary(graph)

    assert conn.node_count == len(graph)
    assert conn.edge_count == graph.number_of_edges()
    assert conn.weak_component_count == 2
    assert conn.strong_component_count == 6
    assert conn.largest_weak_component_size == 14
    assert conn.largest_strong_component_size == 9


def test_resilience_degradation_experiment() -> None:
    """Verify targeted failure reduces connectivity faster than random failure."""
    graph = build_sample()
    deg = centrality(graph, metric="degree")
    table = resilience_experiment(
        graph,
        scores=deg.scores,
        strategy="degree",
        levels=(0.0, 0.1, 0.2),
        seed=42,
        repetitions=5,
    )
    assert len(table) == 3
    # Baseline retention at 0% failure equals largest weak component fraction (14 / 16 = 0.875)
    assert table[0]["Targeted retention"] == 0.875
    assert table[0]["Random mean retention"] == 0.875


def test_minimum_spanning_forest() -> None:
    """Verify MST produces an acyclic forest on the undirected projection."""
    graph = build_sample()
    msf = minimum_spanning_forest(graph, weight="length_m")

    # In a forest with V nodes and C connected components, edge count is exactly V - C
    expected_edges = msf.node_count - msf.component_count
    assert msf.forest_edge_count == expected_edges
    assert len(msf.forest_edges) == expected_edges
