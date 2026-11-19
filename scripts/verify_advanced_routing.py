"""Offline advanced-route verification including an exhaustive tiny-graph oracle."""

import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.dijkstra import dijkstra
from src.algorithms.yen_k_shortest import yen_k_shortest_paths
from src.graph.dataset_service import load
from src.graph.validation import validate
from tests.test_advanced_routing_networkx import exhaustive


def main():
    info = load()
    graph = info.graph
    checks = {"Graph validation": validate(graph, info.metadata).valid}
    for objective, field in [("distance", "length_m"), ("travel_time", "travel_time_s")]:
        a = dijkstra(graph, 0, 1, objective)
        b = bidirectional_dijkstra(graph, 0, 1, objective)
        reference = nx.shortest_path_length(graph, 0, 1, weight=field)
        print(objective, a.optimized_cost, b.optimized_cost, reference)
        checks[objective] = a.optimized_cost == b.optimized_cost == reference
        routes = yen_k_shortest_paths(graph, 0, 1, 3, objective)
        oracle = exhaustive(graph.subgraph([0, 1, 2, 4, 5]), 0, 1, objective)
        tiny = yen_k_shortest_paths(graph.subgraph([0, 1, 2, 4, 5]), 0, 1, 3, objective)
        checks[objective + " oracle"] = [r.optimized_cost for r in tiny] == [
            r.optimized_cost for r in oracle[:3]
        ]
        checks[objective + " unique"] = len({r.edge_path for r in routes}) == len(routes)
        checks[objective + " deterministic"] = routes == yen_k_shortest_paths(
            graph, 0, 1, 3, objective
        )
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
