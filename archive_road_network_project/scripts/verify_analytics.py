"""Offline structural analytics verification."""

import copy
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analytics.centrality import centrality
from src.analytics.connectivity import connectivity_summary
from src.analytics.critical_nodes import critical_nodes
from src.analytics.mst import minimum_spanning_forest
from src.analytics.resilience import resilience_experiment
from src.graph.dataset_service import load
from src.graph.validation import validate


def main():
    info = load()
    graph = info.graph
    before = copy.deepcopy(graph)
    metrics = {m: centrality(graph, m) for m in ("degree", "betweenness", "closeness", "pagerank")}
    ranked = critical_nodes(graph, metrics)
    summary = connectivity_summary(graph)
    rows = resilience_experiment(graph, metrics["degree"].scores, levels=(0, 0.2), repetitions=10)
    forest = minimum_spanning_forest(graph)
    print("Top critical nodes", [(r["node_id"], round(r["combined_score"], 5)) for r in ranked[:3]])
    print(summary)
    print(rows[-1])
    print(forest)
    checks = {
        "Graph validation": validate(graph, info.metadata).valid,
        "Four centralities": all(len(r.scores) == len(graph) for r in metrics.values()),
        "Connectivity": summary.weak_component_count
        == nx.number_weakly_connected_components(graph),
        "Forest invariant": forest.forest_edge_count == len(graph) - forest.component_count,
        "Immutability": nx.utils.graphs_equal(graph, before),
    }
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
