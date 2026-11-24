"""Unit tests for NetworkX MultiGraph construction and graph validator."""

import networkx as nx

from src.data.loader import load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.graph.validator import validate_metro_graph


def test_graph_type_is_multigraph():
    """Verify that graph representation is strictly networkx.MultiGraph."""
    stns, lines, conns, sl, meta = load_validated_dataset()
    graph = build_metro_graph(stns, lines, conns, sl)
    assert isinstance(graph, nx.MultiGraph)


def test_node_and_edge_counts_match_data():
    """Verify nodes and edges correspond accurately to input CSV rows."""
    stns, lines, conns, sl, meta = load_validated_dataset()
    graph = build_metro_graph(stns, lines, conns, sl)

    assert graph.number_of_nodes() == len(stns)
    assert graph.number_of_edges() == len(conns)


def test_line_attributes_and_interchanges():
    """Verify node attributes, interchange flags, and line metadata are preserved."""
    stns, lines, conns, sl, meta = load_validated_dataset()
    graph = build_metro_graph(stns, lines, conns, sl)

    for node, data in graph.nodes(data=True):
        assert "name" in data
        assert "lat" in data
        assert "lon" in data
        assert "lines" in data
        assert "is_interchange" in data
        if len(data["lines"]) >= 2:
            assert data["is_interchange"] is True

    # At least one station must serve multiple lines
    interchange_count = sum(1 for _, d in graph.nodes(data=True) if d["is_interchange"])
    assert interchange_count >= 2


def test_parallel_edges_preserved():
    """Verify parallel edges connecting the same pair of stations under different lines are retained."""
    stns, lines, conns, sl, meta = load_validated_dataset()
    graph = build_metro_graph(stns, lines, conns, sl)

    # In our dataset, S01 and S10 are connected on both L01 and L02
    edges_between = graph.get_edge_data("S01", "S10")
    assert edges_between is not None
    assert len(edges_between) >= 2

    # Check distinct lines on parallel edges
    lines_on_edges = {e["line_id"] for e in edges_between.values()}
    assert len(lines_on_edges) >= 2


def test_graph_connectivity():
    """Verify the sample metro network forms a single connected component."""
    stns, lines, conns, sl, meta = load_validated_dataset()
    graph = build_metro_graph(stns, lines, conns, sl)
    summary = validate_metro_graph(graph)

    assert summary["is_valid"] is True
    assert summary["is_connected"] is True
    assert summary["connected_components"] == 1
