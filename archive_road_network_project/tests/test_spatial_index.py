"""Tests for 3D Earth-centered Cartesian spatial KD-tree indexing."""

import math

import networkx as nx
import pytest

from src.indexing.spatial_index import (
    build_spatial_index,
    clear_spatial_index_cache,
    get_spatial_index,
    haversine_m,
)


def _build_geo_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node("A", x=77.210, y=28.630)
    g.add_node("B", x=77.211, y=28.630)
    g.add_node("C", x=77.210, y=28.631)
    g.add_node("D", x=77.215, y=28.635)
    g.add_edge("A", "B", length_m=100.0)
    return g


def test_spatial_index_exact_match():
    g = _build_geo_graph()
    index = build_spatial_index(g)

    # Query exact coordinates of node A
    res = index.nearest_node(latitude=28.630, longitude=77.210)
    assert res.node_id == "A"
    assert math.isclose(res.distance_m, 0.0, abs_tol=1e-3)
    assert res.latitude == 28.630
    assert res.longitude == 77.210


def test_spatial_index_nearest_resolution():
    g = _build_geo_graph()
    index = build_spatial_index(g)

    # Point very close to node D
    res = index.nearest_node(latitude=28.6349, longitude=77.2149)
    assert res.node_id == "D"
    expected_dist = haversine_m(28.6349, 77.2149, 28.635, 77.215)
    assert math.isclose(res.distance_m, expected_dist, abs_tol=0.05)


def test_spatial_index_batch_queries():
    g = _build_geo_graph()
    index = build_spatial_index(g)

    queries = [(28.630, 77.210), (28.635, 77.215)]
    results = index.nearest_nodes(queries)
    assert len(results) == 2
    assert results[0].node_id == "A"
    assert results[1].node_id == "D"


def test_spatial_index_single_node():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node("SOLO", x=77.20, y=28.60)
    index = build_spatial_index(g)
    res = index.nearest_node(latitude=28.65, longitude=77.25)
    assert res.node_id == "SOLO"
    assert res.distance_m > 0.0


def test_spatial_index_empty_graph():
    empty_g = nx.MultiDiGraph(crs="EPSG:4326")
    with pytest.raises(ValueError, match="Cannot build spatial index for an empty graph"):
        build_spatial_index(empty_g)


def test_spatial_index_invalid_coordinates():
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node("BAD", x=200.0, y=28.60)  # Longitude > 180!
    with pytest.raises(ValueError, match="outside valid geographic range"):
        build_spatial_index(g)

    g_nan = nx.MultiDiGraph(crs="EPSG:4326")
    g_nan.add_node("NAN", x=float("nan"), y=28.60)
    with pytest.raises(ValueError, match="non-finite"):
        build_spatial_index(g_nan)


def test_spatial_index_query_bounds():
    g = _build_geo_graph()
    index = build_spatial_index(g)
    with pytest.raises(ValueError, match="Query coordinates out of bounds"):
        index.nearest_node(latitude=95.0, longitude=77.0)
    with pytest.raises(ValueError, match="must be finite numbers"):
        index.nearest_node(latitude=float("inf"), longitude=77.0)


def test_spatial_index_caching():
    clear_spatial_index_cache()
    g = _build_geo_graph()

    idx1 = get_spatial_index(g, dataset_id="test_ds")
    idx2 = get_spatial_index(g, dataset_id="test_ds")
    assert idx1 is idx2  # Cached instance returned

    # Modify graph -> should invalidate / rebuild
    g.add_node("E", x=77.220, y=28.640)
    idx3 = get_spatial_index(g, dataset_id="test_ds")
    assert idx3 is not idx1
    assert idx3.node_count == 5
