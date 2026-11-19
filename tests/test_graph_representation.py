import numpy as np
import pytest

from scripts.generate_sample_graph import build_sample
from src.graph.representation import adjacency_matrix, build_adjacency, consistent, entry_count


def test_parallel_matrix():
    g = build_sample()
    g.add_node(20)
    adj = build_adjacency(g)
    assert adj[20] == [] and consistent(g, adj) and entry_count(adj) == 34
    assert {e.edge_key for e in adj[0] if e.target_node == 1} == {0, 7}
    matrix = adjacency_matrix(g, [1, 0], "travel_time_s")
    assert matrix[1, 0] == pytest.approx(10.08) and np.isinf(matrix[0, 1])
    assert matrix[0, 0] == 0
    with pytest.raises(ValueError):
        adjacency_matrix(g, range(101))
