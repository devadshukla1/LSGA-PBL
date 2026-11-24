"""Verify keyed optimal routes against NetworkX without network access."""

import math
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph.dataset_service import load
from src.graph.validation import validate
from src.routing.routing_service import find_route


def main() -> int:
    info = load()
    graph = info.graph
    checks = {"Dataset validation": validate(graph, info.metadata).valid}
    for objective, field in [("distance", "length_m"), ("travel_time", "travel_time_s")]:
        expected = nx.shortest_path_length(graph, 0, 1, weight=field)
        for algorithm in ("dijkstra", "astar"):
            route = find_route(graph, 0, 1, algorithm, objective)
            label = f"{algorithm} {objective}"
            passed = route.is_reachable and math.isclose(
                route.optimized_cost, expected, rel_tol=1e-9
            )
            checks[label] = passed
            print(label, route.optimized_cost, expected)
    checks["Unreachable"] = not find_route(graph, 0, 15).is_reachable
    checks["Same junction"] = find_route(graph, 0, 0).optimized_cost == 0
    for label, passed in checks.items():
        print("PASS" if passed else "FAIL", label)
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
