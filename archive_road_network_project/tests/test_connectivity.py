import networkx as nx
import pytest

from src.algorithms.bfs import bfs
from src.algorithms.connectivity import strong_components, weak_components


@pytest.mark.parametrize("seed", range(8))
def test_against_reference(seed):
    g = nx.MultiDiGraph(nx.gnp_random_graph(30, 0.08, seed=seed, directed=True))
    g.add_edges_from([(0, 0), (0, 1), (0, 1)])
    g.add_node(99)
    assert bfs(g, 0).depth == nx.single_source_shortest_path_length(g, 0)
    for function, oracle in [
        (weak_components, nx.weakly_connected_components),
        (strong_components, nx.strongly_connected_components),
    ]:
        r = function(g)
        assert set(r.components) == set(map(frozenset, oracle(g)))
        assert all(n in r.components[i] for n, i in r.node_to_component.items())
        assert r.component_count == len(r.components)
