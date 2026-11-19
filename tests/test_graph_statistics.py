from scripts.generate_sample_graph import build_sample
from src.graph.statistics import statistics


def test_sample_statistics():
    g = build_sample()
    s = statistics(g)
    assert (s.nodes, s.directed_edges, s.parallel_edge_pairs, s.self_loops) == (16, 34, 1, 0)
    assert (s.weak_components, s.strong_components, s.largest_weak_component) == (2, 6, 14)
    assert (s.minimum_degree, s.maximum_degree, s.average_in_degree) == (1, 8, 2.125)
    assert s.total_length_m == 3907
    assert list(build_sample().edges(data=True, keys=True)) == list(g.edges(data=True, keys=True))
