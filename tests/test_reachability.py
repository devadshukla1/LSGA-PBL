import networkx as nx
import pytest

from src.algorithms.reachability import find_unweighted_path, reconstruct_path


def test_paths():
    g = nx.MultiDiGraph([(0, 1), (1, 2), (2, 1)])
    assert find_unweighted_path(g, 0, 2).path == (0, 1, 2)
    assert find_unweighted_path(g, 0, 0).hop_count == 0
    assert find_unweighted_path(g, 2, 0).hop_count is None
    with pytest.raises(ValueError):
        find_unweighted_path(g, 0, 5)
    for parents in ({0: None, 2: 1}, {0: None, 2: 1, 1: 2}):
        with pytest.raises(ValueError):
            reconstruct_path(0, 2, parents)
