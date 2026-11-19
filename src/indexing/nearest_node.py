"""Brute-force nearest-node reference implementation."""

import math
from collections.abc import Sequence

import networkx as nx

from src.indexing.index_models import NearestNodeResult
from src.indexing.spatial_index import extract_node_coordinates, haversine_m


def brute_force_nearest_node(
    graph: nx.MultiDiGraph,
    latitude: float,
    longitude: float,
) -> NearestNodeResult:
    """Find the nearest graph node via exhaustive O(V) distance scan.

    Serves as the ground-truth correctness reference for spatial index verification.
    Uses the exact same spherical Earth Haversine metric and deterministic tie-breaking.
    """
    if len(graph) == 0:
        raise ValueError("Cannot query nearest node on an empty graph")
    if not (math.isfinite(latitude) and math.isfinite(longitude)):
        raise ValueError("Query coordinates must be finite numbers")
    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
        raise ValueError(
            "Query coordinates out of bounds: latitude [-90, 90], longitude [-180, 180]"
        )

    coords = extract_node_coordinates(graph)

    # Deterministic scan with canonical tie-breaking by (distance, str(node_id))
    best_node = None
    best_dist = math.inf
    best_lat = 0.0
    best_lon = 0.0

    # Sort nodes by string key to ensure deterministic traversal order
    for node in sorted(coords.keys(), key=lambda n: str(n)):
        n_lat, n_lon = coords[node]
        dist = haversine_m(latitude, longitude, n_lat, n_lon)
        if dist < best_dist:
            best_dist = dist
            best_node = node
            best_lat = n_lat
            best_lon = n_lon

    if best_node is None:
        raise ValueError("No valid nodes found in graph")

    return NearestNodeResult(
        node_id=best_node,
        distance_m=round(best_dist, 4),
        latitude=best_lat,
        longitude=best_lon,
        query_latitude=latitude,
        query_longitude=longitude,
    )


def brute_force_nearest_nodes(
    graph: nx.MultiDiGraph,
    coordinates: Sequence[tuple[float, float]],
) -> list[NearestNodeResult]:
    """Perform batch brute-force nearest-node lookups."""
    return [brute_force_nearest_node(graph, lat, lon) for lat, lon in coordinates]
