import random

import networkx as nx
import pytest

from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.routing_tiebreak import rank
from src.algorithms.yen_k_shortest import yen_k_shortest_paths
from src.routing.route_alternatives import result_from_edges
from src.routing.routing_service import find_route


def exhaustive(graph, source, target, objective):
    found = []

    def visit(node, nodes, edges):
        if node == target:
            found.append(result_from_edges(graph, source, target, edges, "oracle", objective))
            return
        for u, v, k in graph.out_edges(node, keys=True):
            if v not in nodes:
                visit(v, nodes | {v}, edges + ((u, v, k),))

    visit(source, {source}, ())
    return sorted(found, key=rank)


@pytest.mark.parametrize("seed", range(10))
@pytest.mark.parametrize(
    "objective,field", [("distance", "length_m"), ("travel_time", "travel_time_s")]
)
def test_oracles(seed, objective, field):
    rng = random.Random(seed)
    g = nx.MultiDiGraph()
    g.add_nodes_from(range(5))
    for u in g:
        for v in g:
            if rng.random() < 0.35:
                for key in range(2):
                    g.add_edge(
                        u,
                        v,
                        key=key,
                        length_m=rng.randint(0, 9),
                        travel_time_s=rng.randint(0, 9),
                        speed_kph=25,
                    )
    for source in g:
        for target in g:
            route = bidirectional_dijkstra(g, source, target, objective)
            expected = exhaustive(g, source, target, objective)
            assert route.is_reachable == bool(expected)
            if expected:
                cost = nx.shortest_path_length(g, source, target, weight=field)
                assert route.optimized_cost == cost
                assert find_route(g, source, target, "dijkstra", objective).optimized_cost == cost
            alternatives = yen_k_shortest_paths(g, source, target, 3, objective)
            assert [r.optimized_cost for r in alternatives] == [
                r.optimized_cost for r in expected[:3]
            ]
            assert len({r.edge_path for r in alternatives}) == len(alternatives)
            assert all(len(set(r.node_path)) == len(r.node_path) for r in alternatives)
            assert [r.edge_path for r in alternatives] == [
                r.edge_path for r in yen_k_shortest_paths(g, source, target, 3, objective)
            ]
