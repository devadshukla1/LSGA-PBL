import copy

import networkx as nx
import pytest

from src.analytics.centrality import centrality
from src.analytics.connectivity import connectivity_summary
from src.analytics.critical_nodes import critical_nodes
from src.analytics.failure_scenarios import failure_scenario
from src.analytics.mst import minimum_spanning_forest, undirected_projection
from src.analytics.resilience import failure_impact, resilience_experiment
from src.graph.dataset_service import load


def test_sample_reference_and_immutability():
    graph = load().graph
    before = copy.deepcopy(graph)
    metrics = {m: centrality(graph, m) for m in ("degree", "betweenness", "closeness", "pagerank")}
    assert metrics["degree"].scores == dict(graph.degree())
    assert metrics["betweenness"].scores == nx.betweenness_centrality(graph, weight="length_m")
    assert metrics["closeness"].scores == nx.closeness_centrality(graph, distance="length_m")
    assert sum(metrics["pagerank"].scores.values()) == pytest.approx(1)
    ranked = critical_nodes(graph, metrics)
    assert len(ranked) == 10
    summary = connectivity_summary(graph)
    assert (summary.weak_component_count, summary.strong_component_count) == (2, 6)
    forest = minimum_spanning_forest(graph)
    assert forest.forest_edge_count == len(graph) - forest.component_count
    assert forest.total_weight == sum(
        d["weight"]
        for _, _, d in nx.minimum_spanning_tree(undirected_projection(graph)).edges(data=True)
    )
    scores = metrics["degree"].scores
    assert resilience_experiment(graph, scores, repetitions=3) == resilience_experiment(
        graph, scores, repetitions=3
    )
    assert nx.utils.graphs_equal(graph, before)


def test_directed_orientation_degrees_and_sampling():
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, length_m=2, travel_time_s=3)
    graph.add_edge(0, 1, length_m=3, travel_time_s=4)
    graph.add_edge(1, 1, length_m=1, travel_time_s=1)
    graph.add_node(2)
    assert centrality(graph, "in_degree").scores[1] == 3
    assert centrality(graph, "out_degree").scores[0] == 2
    assert centrality(graph, "closeness", direction="incoming").scores[0] == 0
    assert centrality(graph, "closeness", direction="outgoing").scores[0] > 0
    a = centrality(graph, "betweenness", approximate=True, sample_size=2)
    b = centrality(graph, "betweenness", approximate=True, sample_size=2)
    assert a.approximate and a.scores == b.scores
    graph.edges[0, 1, 0]["length_m"] = 0
    with pytest.raises(ValueError):
        centrality(graph, "betweenness")


def test_failures_empty_and_denominators():
    graph = nx.MultiDiGraph([(0, 1), (1, 2)])
    zero = failure_impact(graph, failure_scenario(graph, 0), exact_threshold=10)
    assert zero["reachable_pair_fraction"] == 0.5
    removed = failure_scenario(graph, 1, "degree", dict(graph.degree()))
    impact = failure_impact(graph, removed)
    assert impact["largest_weak_component_fraction"] == 0.5
    assert impact["original_largest_weak_fraction"] == pytest.approx(1 / 3)
    assert impact["fragmentation_score"] == 0.5
    sampled = failure_impact(graph, failure_scenario(graph, 0), exact_threshold=1)
    assert sampled["reachability_approximate"]
    assert sampled == failure_impact(graph, failure_scenario(graph, 0), exact_threshold=1)
    empty = nx.MultiDiGraph()
    assert connectivity_summary(empty).node_count == 0
    assert minimum_spanning_forest(empty).forest_edge_count == 0
    assert failure_impact(empty, failure_scenario(empty, 0))["fragmentation_score"] == 1
    for invalid in (-1, 4, True):
        with pytest.raises(ValueError):
            failure_scenario(graph, invalid)
    with pytest.raises(ValueError):
        resilience_experiment(graph, dict(graph.degree()), repetitions=1)


def test_projection_exact_key_and_isolate():
    graph = nx.MultiDiGraph()
    graph.add_edge(0, 1, key=8, length_m=8)
    graph.add_edge(1, 0, key=9, length_m=2)
    graph.add_edge(0, 0, length_m=0)
    graph.add_node(2)
    forest = minimum_spanning_forest(graph)
    assert forest.forest_edges == ((1, 0, 9),)
    assert forest.total_weight == 2 and forest.component_count == 2


def test_critical_missing_metrics_and_pagerank_limits():
    graph = load().graph
    degree = centrality(graph, "degree")
    ranked = critical_nodes(graph, {"degree": degree}, top_k=3)
    assert ranked[0]["node_id"] == degree.top_nodes[0]
    assert ranked[0]["pagerank_score"] is None
    assert ranked[0]["available_metrics"] == ("degree",)
    with pytest.raises(ValueError, match="converge"):
        centrality(graph, "pagerank", max_iter=1, tol=1e-30)
    with pytest.raises(ValueError, match="override"):
        centrality(graph, "betweenness", exact_threshold=1, approximate=False)


def test_singleton_and_connected_tree():
    graph = nx.MultiDiGraph()
    graph.add_node(1)
    assert centrality(graph, "degree").scores == {1: 0}
    assert centrality(graph, "closeness").scores == {1: 0}
    assert centrality(graph, "pagerank").scores == {1: 1}
    assert minimum_spanning_forest(graph).is_connected
    for u, v, weight in [(1, 2, 3), (2, 3, 2), (1, 3, 9)]:
        graph.add_edge(u, v, length_m=weight)
    forest = minimum_spanning_forest(graph)
    assert forest.is_connected and forest.forest_edge_count == 2 and forest.total_weight == 5
