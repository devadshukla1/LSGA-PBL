import copy

import networkx as nx
import pytest

from scripts.generate_sample_graph import build_sample
from src.algorithms.bidirectional_dijkstra import bidirectional_dijkstra
from src.algorithms.yen_k_shortest import yen_k_shortest_paths
from src.routing.route_comparison import compare_routes


@pytest.mark.parametrize("k", [True, 0, -1, 6, 1.5])
def test_invalid_k(k):
    with pytest.raises(ValueError):
        yen_k_shortest_paths(build_sample(), 0, 1, k)


def test_sample_and_overlap():
    graph = build_sample()
    snapshot = copy.deepcopy(graph)
    routes = yen_k_shortest_paths(graph, 0, 1, 5)
    assert routes[0].edge_path == ((0, 1, 0),)
    assert any(r.edge_path == ((0, 1, 7),) for r in routes)
    assert compare_routes(routes)[0]["Shared-Edge Ratio"] == 1
    assert nx.utils.graphs_equal(graph, snapshot)
    assert not bidirectional_dijkstra(graph, 0, 15).is_reachable
    zero = bidirectional_dijkstra(graph, 0, 0)
    assert zero.optimized_cost == 0
    assert compare_routes([zero])[0]["Cost Increase (%)"] is None
