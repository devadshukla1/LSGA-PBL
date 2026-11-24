"""Tests for betweenness centrality calculation."""

import math

import networkx as nx

from src.analytics.betweenness_centrality import compute_betweenness_centrality


def test_betweenness_centrality_matches_networkx_chain():
    """Chain: A - B - C - D - E."""
    g = nx.path_graph(["A", "B", "C", "D", "E"])
    bc = compute_betweenness_centrality(g)
    nx_bc = nx.betweenness_centrality(g, normalized=True)

    for n in g.nodes:
        assert math.isclose(bc[n], nx_bc[n], abs_tol=1e-5)

    # In path of 5 nodes: Center C has highest betweenness:
    # Pairs (A,D), (A,E), (B,D), (B,E) pass through C (4 pairs out of (4*3)/2 = 6) -> 4/6 = 0.66667
    assert bc["C"] > bc["B"] > bc["A"]
    assert bc["A"] == 0.0
    assert bc["E"] == 0.0


def test_betweenness_centrality_star():
    """Star graph: center node must have betweenness = 1.0, leaves = 0.0."""
    g = nx.star_graph(4)
    g_str = nx.relabel_nodes(g, {i: f"N{i}" for i in range(5)})
    bc = compute_betweenness_centrality(g_str)

    assert math.isclose(bc["N0"], 1.0, abs_tol=1e-5)
    for leaf in ["N1", "N2", "N3", "N4"]:
        assert math.isclose(bc[leaf], 0.0, abs_tol=1e-5)


def test_betweenness_centrality_cycle():
    """In a symmetric 4-node cycle, all nodes must have identical betweenness."""
    g = nx.cycle_graph(["A", "B", "C", "D"])
    bc = compute_betweenness_centrality(g)

    assert math.isclose(bc["A"], bc["B"], abs_tol=1e-5)
    assert math.isclose(bc["B"], bc["C"], abs_tol=1e-5)
    assert math.isclose(bc["C"], bc["D"], abs_tol=1e-5)


def test_betweenness_centrality_small_graphs():
    # 1 node
    g1 = nx.Graph()
    g1.add_node("A")
    assert compute_betweenness_centrality(g1)["A"] == 0.0

    # 2 nodes
    g2 = nx.Graph()
    g2.add_edge("A", "B")
    bc2 = compute_betweenness_centrality(g2)
    assert bc2["A"] == 0.0 and bc2["B"] == 0.0
