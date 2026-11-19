"""Tests for graph structure invariants, edge keys, attributes, and fixtures."""

import networkx as nx
import pytest

from scripts.generate_sample_graph import build_sample
from src.graph.dataset_service import SAMPLE, metadata_for
from src.graph.storage import load_graph, save_graph
from src.graph.validation import validate


def test_sample_graph_is_multidigraph() -> None:
    """Verify road graph maintains MultiDiGraph semantics with parallel edges."""
    g = build_sample()
    assert isinstance(g, nx.MultiDiGraph)
    assert g.is_directed()
    assert g.number_of_nodes() > 0
    assert g.number_of_edges() > 0

    # Verify parallel edges between nodes 0 and 1
    edges_0_1 = g.get_edge_data(0, 1)
    assert edges_0_1 is not None
    assert len(edges_0_1) >= 2, "Sample graph must contain parallel edges with distinct keys"
    assert 0 in edges_0_1 and 7 in edges_0_1


def test_node_coordinates_and_attributes() -> None:
    """Verify all nodes possess numeric coordinates x and y."""
    g = build_sample()
    for node, data in g.nodes(data=True):
        assert "x" in data, f"Node {node} missing x coordinate"
        assert "y" in data, f"Node {node} missing y coordinate"
        assert isinstance(data["x"], int | float)
        assert isinstance(data["y"], int | float)


def test_edge_weight_invariants() -> None:
    """Verify directed edge attributes and positive weights."""
    g = build_sample()
    for u, v, k, data in g.edges(keys=True, data=True):
        assert "length_m" in data, f"Edge ({u}, {v}, {k}) missing length_m"
        assert "travel_time_s" in data, f"Edge ({u}, {v}, {k}) missing travel_time_s"
        assert data["length_m"] > 0, f"Edge ({u}, {v}, {k}) length must be positive"
        assert data["travel_time_s"] > 0, f"Edge ({u}, {v}, {k}) travel time must be positive"


def test_graphml_roundtrip_preserves_keys_and_attributes(tmp_path) -> None:
    """Verify GraphML serialization and deserialization preserves topology and attributes."""
    g = build_sample()
    meta = metadata_for(g, SAMPLE)
    out_file = tmp_path / "test_roundtrip.graphml"

    save_graph(g, out_file, meta)
    assert out_file.is_file()

    loaded = load_graph(out_file, meta)
    assert isinstance(loaded, nx.MultiDiGraph)
    assert loaded.number_of_nodes() == g.number_of_nodes()
    assert loaded.number_of_edges() == g.number_of_edges()

    # Verify edge keys and attributes match
    for u, v, k, data in g.edges(keys=True, data=True):
        loaded_data = loaded.get_edge_data(u, v, k)
        assert loaded_data is not None, f"Edge ({u}, {v}, {k}) lost during roundtrip"
        assert pytest.approx(loaded_data["length_m"]) == data["length_m"]
        assert pytest.approx(loaded_data["travel_time_s"]) == data["travel_time_s"]


def test_small_graph_fixtures_validation() -> None:
    """Verify behavior across standard small graph fixtures."""
    # Graph A: Empty graph
    empty_g = nx.MultiDiGraph()
    rep = validate(empty_g)
    assert not rep.valid

    # Graph B: Single node
    single_g = nx.MultiDiGraph()
    single_g.add_node(0, x=77.0, y=28.0)
    rep_single = validate(single_g)
    assert rep_single.weak_components == 1

    # Graph C: Two nodes with one directed edge
    two_nodes_g = nx.MultiDiGraph()
    two_nodes_g.add_node(0, x=77.0, y=28.0)
    two_nodes_g.add_node(1, x=77.01, y=28.01)
    two_nodes_g.add_edge(0, 1, key=0, length_m=100.0, speed_kph=50, travel_time_s=7.2)
    assert two_nodes_g.has_edge(0, 1, 0)
    assert not two_nodes_g.has_edge(1, 0)  # directed one-way

    # Graph D: Disconnected graph with isolated nodes
    disconn_g = two_nodes_g.copy()
    disconn_g.add_node(2, x=77.02, y=28.02)
    rep_disconn = validate(disconn_g)
    assert rep_disconn.weak_components == 2


def test_invalid_negative_weight_rejection() -> None:
    """Verify validation identifies invalid non-positive edge lengths."""
    bad_g = nx.MultiDiGraph()
    bad_g.add_node(0, x=77.0, y=28.0)
    bad_g.add_node(1, x=77.01, y=28.01)
    bad_g.add_edge(0, 1, key=0, length_m=-50.0, speed_kph=50, travel_time_s=7.2)

    rep = validate(bad_g)
    assert any(issue.code == "weight" for issue in rep.issues)
