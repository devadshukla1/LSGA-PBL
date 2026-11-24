"""Tests for the analytical graph projection utility."""

import networkx as nx

from src.analytics.graph_projection import build_analysis_graph


def test_projection_preserves_nodes_and_attributes():
    mg = nx.MultiGraph()
    mg.add_node("A", station_name="Alpha", lat=28.5, lon=77.2, lines={"L1"}, is_interchange=False)
    mg.add_node("B", station_name="Beta", lat=28.6, lon=77.3, lines={"L1"}, is_interchange=False)
    mg.add_edge("A", "B", key="k1", line_id="L1", distance_km=2.0, estimated_time_min=3.0)

    sg = build_analysis_graph(mg)

    assert isinstance(sg, nx.Graph)
    assert not isinstance(sg, nx.MultiGraph)
    assert sg.number_of_nodes() == 2
    assert sg.number_of_edges() == 1
    assert sg.nodes["A"]["station_name"] == "Alpha"
    assert sg.nodes["B"]["lat"] == 28.6


def test_projection_collapses_parallel_edges():
    """Two parallel lines between A and B should collapse to a single edge in the analysis graph."""
    mg = nx.MultiGraph()
    mg.add_node("A", station_name="A", lat=28.0, lon=77.0)
    mg.add_node("B", station_name="B", lat=28.1, lon=77.1)

    # Parallel edge 1: slower
    mg.add_edge("A", "B", key="e1", line_id="L1", distance_km=5.0, estimated_time_min=8.0)
    # Parallel edge 2: faster
    mg.add_edge("A", "B", key="e2", line_id="L2", distance_km=4.5, estimated_time_min=6.0)

    sg = build_analysis_graph(mg)

    assert sg.number_of_nodes() == 2
    assert sg.number_of_edges() == 1
    edge_data = sg["A"]["B"]
    assert edge_data["parallel_service_count"] == 2
    assert edge_data["lines"] == {"L1", "L2"}
    # Minimum valid weights retained
    assert edge_data["distance_km"] == 4.5
    assert edge_data["estimated_time_min"] == 6.0


def test_projection_does_not_mutate_original_multigraph():
    mg = nx.MultiGraph()
    mg.add_node("A")
    mg.add_node("B")
    mg.add_edge("A", "B", key="1")
    mg.add_edge("A", "B", key="2")

    orig_edge_count = mg.number_of_edges()
    sg = build_analysis_graph(mg)

    assert mg.number_of_edges() == orig_edge_count == 2
    assert sg.number_of_edges() == 1


def test_empty_graph_projection():
    mg = nx.MultiGraph()
    sg = build_analysis_graph(mg)
    assert sg.number_of_nodes() == 0
    assert sg.number_of_edges() == 0
