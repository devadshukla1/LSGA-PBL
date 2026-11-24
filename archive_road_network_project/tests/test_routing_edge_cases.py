from dataclasses import replace

import pytest

from scripts.generate_sample_graph import build_sample
from src.algorithms.astar import astar
from src.algorithms.dijkstra import dijkstra
from src.algorithms.heuristics import safe_heuristic
from src.algorithms.path_reconstruction import reconstruct_route
from src.routing.route_validation import validate_route
from src.routing.routing_service import find_route


def test_sample_objectives_and_keys():
    graph = build_sample()
    distance = find_route(graph, 0, 1, "dijkstra", "distance")
    time = find_route(graph, 0, 1, "astar", "travel_time")
    assert distance.edge_path == ((0, 1, 0),) and time.edge_path == ((0, 1, 7),)
    assert distance.optimized_cost == 100 and time.optimized_cost == 10.08
    assert not find_route(graph, 0, 15).is_reachable
    assert find_route(graph, 0, 0).node_path == (0,)
    with pytest.raises(ValueError):
        validate_route(graph, replace(distance, optimized_cost=1))
    with pytest.raises(ValueError):
        validate_route(graph, replace(distance, edge_path=((0, 1, 99),)))


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1])
def test_invalid_weights(bad):
    graph = build_sample()
    graph.edges[0, 1, 0]["length_m"] = bad
    for solver in (dijkstra, astar):
        with pytest.raises(ValueError):
            solver(graph, 0, 1)


def test_predecessor_and_fallback():
    assert reconstruct_route(0, 1, {1: (0, 7)}) == ((0, 1), ((0, 1, 7),))
    with pytest.raises(ValueError):
        reconstruct_route(0, 2, {2: (1, 0), 1: (2, 0)})
    graph = build_sample()
    graph.graph["crs"] = "invalid-crs"
    assert safe_heuristic(graph, 1, "distance")[1] == "zero"
