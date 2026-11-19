import networkx as nx

from src.algorithms.bfs import bfs


def test_keyed_branch_and_minimum_depth():
    g = nx.MultiDiGraph()
    g.add_edges_from([(0, "b", 7), (0, "b", 2), (0, 1, 0), (1, "b", 0), ("b", 0, 0), (1, 1, 0)])
    g.add_node(9)
    r = bfs(g, 0)
    assert r.visit_order == (0, 1, "b") and r.parent == {0: None, 1: 0, "b": 0}
    assert r.tree_edges == ((0, 1, 0), (0, "b", 2)) and r.edges_examined == 6
    assert r.depth == {0: 0, 1: 1, "b": 1}
