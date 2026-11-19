"""Tests for 3D KD-Tree spatial nearest-node indexing and brute-force equivalence."""

import pytest

from scripts.generate_sample_graph import build_sample
from src.indexing.nearest_node import brute_force_nearest_node
from src.indexing.spatial_index import build_spatial_index, get_spatial_index


def test_spatial_index_matches_brute_force_baseline() -> None:
    """Verify KD-Tree nearest node matches brute-force nearest node across test points."""
    graph = build_sample()
    index = build_spatial_index(graph)

    test_coords = [
        (28.630, 77.215),
        (28.635, 77.220),
        (28.625, 77.210),
        (28.640, 77.225),
    ]

    for lat, lon in test_coords:
        indexed_res = index.nearest_node(lat, lon)
        bf_res = brute_force_nearest_node(graph, lat, lon)

        assert indexed_res.node_id == bf_res.node_id
        assert pytest.approx(indexed_res.distance_m, abs=1e-3) == bf_res.distance_m


def test_spatial_index_cache_safety() -> None:
    """Verify get_spatial_index handles caching cleanly without cross-dataset collision."""
    graph = build_sample()
    idx1 = get_spatial_index(graph, dataset_id="ds_alpha")
    idx2 = get_spatial_index(graph, dataset_id="ds_alpha")

    # Reused for same dataset
    assert idx1 is idx2

    # Fresh index for new dataset
    idx3 = get_spatial_index(graph, dataset_id="ds_beta")
    assert idx3 is not idx1


def test_invalid_coordinates_raise_error() -> None:
    """Verify out-of-range latitude/longitude coordinates raise ValueError."""
    graph = build_sample()
    index = build_spatial_index(graph)

    with pytest.raises(ValueError):
        index.nearest_node(95.0, 77.0)  # Latitude > 90

    with pytest.raises(ValueError):
        index.nearest_node(28.0, 190.0)  # Longitude > 180
