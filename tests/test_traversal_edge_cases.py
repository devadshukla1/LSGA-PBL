import copy

import networkx as nx
import pytest

from scripts.verify_traversal import main
from src.algorithms.bfs import bfs
from src.algorithms.connectivity import strong_components, weak_components
from src.algorithms.dfs import dfs
from src.graph.dataset_service import load


def test_empty_and_single():
    g = nx.MultiDiGraph()
    for f in (weak_components, strong_components):
        assert f(g).component_count == 0
    for f in (bfs, dfs):
        with pytest.raises(ValueError):
            f(g, "x")
    g.add_node("x")
    for f in (bfs, dfs):
        assert f(g, "x").visit_order == ("x",)
    for f in (weak_components, strong_components):
        assert f(g).components == (frozenset(["x"]),)


def test_sample_unchanged():
    g = load().graph
    original = copy.deepcopy(g)
    for f in (bfs, dfs):
        f(g, 0)
    weak_components(g)
    strong_components(g)
    assert nx.utils.graphs_equal(g, original)
    assert main() == 0
