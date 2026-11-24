"""Tests for degree centrality calculation."""

import math

import networkx as nx

from src.analytics.degree_centrality import compute_degree_centrality, compute_station_degrees


def test_degree_centrality_matches_networkx_star():
    """Star graph with center node C and 4 leaves: L1, L2, L3, L4."""
    g = nx.star_graph(4)  # 0 is center, 1..4 leaves (total 5 nodes)
    # Convert node keys to string
    g_str = nx.relabel_nodes(g, {i: f"N{i}" for i in range(5)})

    dc = compute_degree_centrality(g_str)
    nx_dc = nx.degree_centrality(g_str)

    for n in g_str.nodes:
        assert math.isclose(dc[n], nx_dc[n], abs_tol=1e-5)

    assert dc["N0"] == 1.0  # 4 / 4
    assert dc["N1"] == 0.25  # 1 / 4


def test_degree_centrality_linear_chain():
    """Chain: A - B - C - D (N=4, N-1=3)."""
    g = nx.path_graph(["A", "B", "C", "D"])
    dc = compute_degree_centrality(g)

    assert math.isclose(dc["A"], 1 / 3, abs_tol=1e-5)
    assert math.isclose(dc["B"], 2 / 3, abs_tol=1e-5)
    assert math.isclose(dc["C"], 2 / 3, abs_tol=1e-5)
    assert math.isclose(dc["D"], 1 / 3, abs_tol=1e-5)


def test_degree_centrality_single_node_and_empty():
    g1 = nx.Graph()
    g1.add_node("SOLO")
    dc1 = compute_degree_centrality(g1)
    assert dc1["SOLO"] == 0.0

    g0 = nx.Graph()
    dc0 = compute_degree_centrality(g0)
    assert dc0 == {}


def test_compute_station_degrees():
    g = nx.Graph()
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    g.add_edge("B", "D")

    degrees = compute_station_degrees(g)
    assert degrees["B"] == 3
    assert degrees["A"] == 1
