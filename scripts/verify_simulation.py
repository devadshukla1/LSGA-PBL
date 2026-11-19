"""Offline scenario and routing verification."""

import copy
import math
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph.dataset_service import load
from src.graph.validation import validate
from src.simulation.scenario_builder import build_scenario_graph, create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.simulation_engine import simulate


def main():
    info = load()
    graph = info.graph
    original = copy.deepcopy(graph)
    checks = {"Base validation": validate(graph, info.metadata).valid}
    for level in ("normal", "light", "moderate", "heavy"):
        scenario = create_scenario(graph, "offline_sample", level)
        effective = build_scenario_graph(graph, scenario)
        checks[level + " reproducible"] = nx.utils.graphs_equal(
            effective, build_scenario_graph(graph, scenario)
        )
        for algorithm in ("dijkstra", "astar", "bidirectional_dijkstra"):
            result = simulate(graph, scenario, SimulationRequest(0, 1, algorithm))
            checks[level + " " + algorithm] = math.isclose(
                result.scenario_route.optimized_cost,
                nx.shortest_path_length(effective, 0, 1, weight="travel_time_s"),
            )
    closure = create_scenario(graph, "offline_sample", closed_edges=((0, 1, 7),))
    result = simulate(graph, closure, SimulationRequest(0, 1))
    print(result)
    checks["Closure reroute"] = result.scenario_route.edge_path == ((0, 1, 0),)
    blocked = create_scenario(graph, "offline_sample", blocked_nodes=(0,))
    checks["Blocked endpoint"] = (
        simulate(graph, blocked, SimulationRequest(0, 1)).status == "blocked_endpoint"
    )
    checks["Baseline unchanged"] = nx.utils.graphs_equal(graph, original)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
