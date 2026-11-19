"""Tests verifying spatial index nearest-node queries against brute-force reference."""

import math

import networkx as nx
import pytest

from src.indexing.nearest_node import brute_force_nearest_node, brute_force_nearest_nodes
from src.indexing.spatial_index import build_spatial_index


def _build_test_network() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(25):
        r, c = divmod(i, 5)
        g.add_node(i, x=77.200 + c * 0.005, y=28.600 + r * 0.005)
    return g


def test_nearest_node_equivalence_against_brute_force():
    g = _build_test_network()
    index = build_spatial_index(g)

    query_points = [
        (28.600, 77.200),  # Exact node 0
        (28.612, 77.213),  # Interior point
        (28.590, 77.190),  # Southwest exterior point
        (28.635, 77.235),  # Northeast exterior point
        (28.618, 77.204),  # Near row 3, col 1
    ]

    for q_lat, q_lon in query_points:
        res_idx = index.nearest_node(q_lat, q_lon)
        res_bf = brute_force_nearest_node(g, q_lat, q_lon)

        assert res_idx.node_id == res_bf.node_id, f"Mismatch at ({q_lat}, {q_lon})"
        assert math.isclose(res_idx.distance_m, res_bf.distance_m, abs_tol=0.01)
        assert math.isclose(res_idx.latitude, res_bf.latitude, abs_tol=1e-6)
        assert math.isclose(res_idx.longitude, res_bf.longitude, abs_tol=1e-6)


def test_nearest_node_equidistant_tie_breaking():
    """Verify deterministic tie breaking when multiple nodes are equidistant."""
    g = nx.MultiDiGraph(crs="EPSG:4326")
    # Place node 10 at (-0.01, 0) and node 20 at (+0.01, 0) relative to (28.60, 77.20)
    g.add_node("node_A", x=77.19, y=28.60)
    g.add_node("node_B", x=77.21, y=28.60)

    index = build_spatial_index(g)

    # Query exactly at midpoint (28.60, 77.20)
    res_idx = index.nearest_node(28.60, 77.20)
    res_bf = brute_force_nearest_node(g, 28.60, 77.20)

    # Both must resolve to the identical node using canonical string ID tie-breaking
    assert res_idx.node_id == res_bf.node_id
    assert math.isclose(res_idx.distance_m, res_bf.distance_m, abs_tol=0.01)


def test_nearest_node_duplicate_coordinates():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node("dup_1", x=77.21, y=28.63)
    g.add_node("dup_2", x=77.21, y=28.63)

    index = build_spatial_index(g)
    res_idx = index.nearest_node(28.63, 77.21)
    res_bf = brute_force_nearest_node(g, 28.63, 77.21)

    assert res_idx.node_id == res_bf.node_id
    assert res_idx.distance_m == 0.0


def test_brute_force_batch_queries():
    g = _build_test_network()
    queries = [(28.600, 77.200), (28.610, 77.210)]
    results = brute_force_nearest_nodes(g, queries)
    assert len(results) == 2
    assert results[0].node_id == 0


def test_brute_force_empty_graph():
    empty_g = nx.MultiDiGraph(crs="EPSG:4326")
    with pytest.raises(ValueError, match="empty graph"):
        brute_force_nearest_node(empty_g, 28.60, 77.20)
