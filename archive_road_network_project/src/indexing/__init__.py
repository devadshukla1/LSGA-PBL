"""Spatial indexing and nearest-node query package."""

from src.indexing.index_models import NearestNodeResult, SpatialIndexMetadata
from src.indexing.nearest_node import brute_force_nearest_node, brute_force_nearest_nodes
from src.indexing.spatial_index import (
    SpatialIndex,
    build_spatial_index,
    clear_spatial_index_cache,
    extract_node_coordinates,
    get_spatial_index,
    haversine_m,
)

__all__ = [
    "NearestNodeResult",
    "SpatialIndex",
    "SpatialIndexMetadata",
    "brute_force_nearest_node",
    "brute_force_nearest_nodes",
    "build_spatial_index",
    "clear_spatial_index_cache",
    "extract_node_coordinates",
    "get_spatial_index",
    "haversine_m",
]
