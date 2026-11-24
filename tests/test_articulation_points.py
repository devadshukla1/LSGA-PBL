"""Tests for articulation point (cut-vertex) detection."""

import networkx as nx

from src.analytics.articulation_points import analyze_articulation_points, find_articulation_points


def test_chain_articulation_points():
    """A - B - C - D: removing B disconnects A; removing C disconnects D."""
    g = nx.path_graph(["A", "B", "C", "D"])
    aps = find_articulation_points(g)
    nx_aps = set(nx.articulation_points(g))

    assert aps == nx_aps
    assert aps == {"B", "C"}
    assert "A" not in aps
    assert "D" not in aps


def test_star_articulation_point():
    """Center node in a star is the single articulation point."""
    g = nx.star_graph(5)
    g_str = nx.relabel_nodes(g, {i: f"N{i}" for i in range(6)})
    aps = find_articulation_points(g_str)

    assert aps == {"N0"}


def test_cycle_has_no_articulation_points():
    """In a simple cycle (biconnected), removing any single node leaves the rest connected."""
    g = nx.cycle_graph(["A", "B", "C", "D"])
    aps = find_articulation_points(g)
    assert len(aps) == 0


def test_two_triangles_sharing_vertex():
    """Triangle 1 (A, B, C) and Triangle 2 (C, D, E) connected at pivot C."""
    g = nx.Graph()
    g.add_edges_from([("A", "B"), ("B", "C"), ("C", "A")])
    g.add_edges_from([("C", "D"), ("D", "E"), ("E", "C")])

    aps = find_articulation_points(g)
    assert aps == {"C"}


def test_analyze_articulation_points_details():
    g = nx.path_graph(["A", "B", "C"])
    bc_map = {"A": 0.0, "B": 1.0, "C": 0.0}

    res = analyze_articulation_points(g, betweenness_dict=bc_map)
    assert res["articulation_point_count"] == 1
    assert "B" in res["articulation_points"]
    assert res["details"][0]["station_id"] == "B"
    assert res["details"][0]["betweenness_centrality"] == 1.0
