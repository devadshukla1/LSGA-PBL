import networkx as nx

from src.algorithms.dfs import dfs


def test_frames_and_depth():
    g = nx.MultiDiGraph([(0, 2), (0, 1), (1, 2), (2, 1), (1, 1), (1, 2)])
    r = dfs(g, 0)
    assert r.discovery_order == (0, 1, 2) and r.finish_order == (2, 1, 0)
    assert r.depth[2] == 2 and r.parent[2] == 1 and r.edges_examined == 6


def test_deep_chain():
    g = nx.MultiDiGraph((i, i + 1) for i in range(3000))
    assert dfs(g, 0).finish_order == tuple(reversed(range(3001)))
