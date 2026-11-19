import math
import random

import networkx as nx
import pytest

from src.algorithms.astar import astar
from src.algorithms.dijkstra import dijkstra
from src.routing.routing_service import find_route


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize(
    "objective,field", [("distance", "length_m"), ("travel_time", "travel_time_s")]
)
def test_oracle(seed, objective, field):
    rng = random.Random(seed)
    graph = nx.MultiDiGraph(crs="EPSG:4326")
    for n in range(12):
        graph.add_node(n, x=77 + n * 0.001, y=28 + n * 0.001)
    for u in range(12):
        for v in range(12):
            if rng.random() < 0.13:
                for key in range(2 if rng.random() < 0.2 else 1):
                    distance = rng.randint(1, 100)
                    graph.add_edge(
                        u,
                        v,
                        key=key,
                        length_m=distance,
                        travel_time_s=distance / rng.randint(1, 5),
                        speed_kph=25,
                    )
    for u in graph:
        for v in graph:
            for solver in (dijkstra, astar):
                route = solver(graph, u, v, objective)
                if nx.has_path(graph, u, v):
                    expected = nx.shortest_path_length(graph, u, v, weight=field)
                    assert route.is_reachable and math.isclose(
                        route.optimized_cost, expected, rel_tol=1e-9
                    )
                    find_route(graph, u, v, route.algorithm, objective)
                else:
                    assert not route.is_reachable
