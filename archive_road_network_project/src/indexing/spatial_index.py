"""Spatial indexing using a 3D Earth-centered Cartesian KD-tree."""

import math
import time
from collections.abc import Hashable, Sequence

import networkx as nx
import numpy as np
from pyproj import CRS, Transformer
from pyproj.exceptions import CRSError
from scipy.spatial import cKDTree

from src.indexing.index_models import NearestNodeResult, SpatialIndexMetadata

EARTH_RADIUS_M = 6_371_008.8


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in meters between two (lat, lon) coordinates."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    term = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    clamped = min(1.0, max(0.0, term))
    return 2.0 * EARTH_RADIUS_M * math.asin(math.sqrt(clamped))


def lat_lon_to_cartesian_3d(
    lat: float, lon: float, radius: float = EARTH_RADIUS_M
) -> tuple[float, float, float]:
    """Convert spherical latitude and longitude (degrees) to 3D Cartesian coordinates (x, y, z)."""
    phi = math.radians(lat)
    lam = math.radians(lon)
    cos_phi = math.cos(phi)
    x = radius * cos_phi * math.cos(lam)
    y = radius * cos_phi * math.sin(lam)
    z = radius * math.sin(phi)
    return x, y, z


def chord_distance_to_great_circle_m(
    chord_distance: float, radius: float = EARTH_RADIUS_M
) -> float:
    """Convert 3D Cartesian chord distance to great-circle arc distance in meters."""
    ratio = min(1.0, max(0.0, chord_distance / (2.0 * radius)))
    return 2.0 * radius * math.asin(ratio)


def extract_node_coordinates(graph: nx.MultiDiGraph) -> dict[Hashable, tuple[float, float]]:
    """Extract and validate WGS84 (latitude, longitude) coordinates for every node.

    Raises:
        ValueError: If graph has no nodes or node coordinates are invalid or missing.
    """
    if len(graph) == 0:
        return {}

    crs_val = graph.graph.get("crs", "EPSG:4326")
    try:
        crs = CRS.from_user_input(crs_val)
        transformer = Transformer.from_crs(crs, 4326, always_xy=True)
    except (CRSError, ValueError, TypeError) as err:
        raise ValueError(f"Unrecognized or invalid coordinate reference system: {crs_val}") from err

    coords: dict[Hashable, tuple[float, float]] = {}
    for node, data in graph.nodes(data=True):
        if "x" not in data or "y" not in data:
            raise ValueError(f"Node {node} is missing 'x' or 'y' coordinate attribute")
        try:
            raw_x, raw_y = float(data["x"]), float(data["y"])
            if not (math.isfinite(raw_x) and math.isfinite(raw_y)):
                raise ValueError
        except (ValueError, TypeError) as err:
            raise ValueError(f"Node {node} contains non-numeric or non-finite coordinates") from err

        lon, lat = transformer.transform(raw_x, raw_y)
        if not (math.isfinite(lat) and math.isfinite(lon)):
            raise ValueError(f"Node {node} transformed coordinates are not finite")
        if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
            raise ValueError(
                f"Node {node} coordinate ({lat}, {lon}) falls outside valid geographic range"
            )
        coords[node] = (lat, lon)

    return coords


class SpatialIndex:
    """Reusable 3D KD-tree index for fast nearest-node geographic queries."""

    def __init__(
        self,
        node_ids: Sequence[Hashable],
        node_coords: dict[Hashable, tuple[float, float]],
        build_time: float,
        crs_str: str,
    ) -> None:
        self._node_ids: list[Hashable] = list(node_ids)
        self._node_coords: dict[Hashable, tuple[float, float]] = node_coords
        self._metadata = SpatialIndexMetadata(
            node_count=len(self._node_ids),
            build_time_seconds=build_time,
            coordinate_reference_system=crs_str,
            distance_metric="great_circle_meters",
        )

        # Convert to 3D Cartesian coordinates
        coords_3d = np.empty((len(self._node_ids), 3), dtype=np.float64)
        for i, nid in enumerate(self._node_ids):
            lat, lon = self._node_coords[nid]
            coords_3d[i] = lat_lon_to_cartesian_3d(lat, lon)

        self._tree = cKDTree(coords_3d)

    @property
    def metadata(self) -> SpatialIndexMetadata:
        return self._metadata

    @property
    def node_count(self) -> int:
        return len(self._node_ids)

    def nearest_node(self, latitude: float, longitude: float) -> NearestNodeResult:
        """Find the nearest road network node to the given geographic coordinates.

        Uses 3D spherical chord distance in cKDTree, resolving ties deterministically
        by exact Haversine distance and canonical string node ID ordering.
        """
        if not (math.isfinite(latitude) and math.isfinite(longitude)):
            raise ValueError("Query coordinates must be finite numbers")
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            raise ValueError(
                "Query coordinates out of bounds: latitude [-90, 90], longitude [-180, 180]"
            )

        qx, qy, qz = lat_lon_to_cartesian_3d(latitude, longitude)
        query_point = np.array([qx, qy, qz], dtype=np.float64)

        # Find initial nearest distance
        d_min, best_idx = self._tree.query(query_point, k=1)

        # To guarantee deterministic tie-breaking matching brute force:
        # Check all candidate nodes within a tiny radius around d_min
        epsilon_radius = d_min * (1.0 + 1e-9) + 1e-4
        candidate_indices = self._tree.query_ball_point(query_point, r=epsilon_radius)

        if len(candidate_indices) > 1:
            best_idx = min(
                candidate_indices,
                key=lambda idx: (
                    haversine_m(
                        latitude,
                        longitude,
                        self._node_coords[self._node_ids[idx]][0],
                        self._node_coords[self._node_ids[idx]][1],
                    ),
                    str(self._node_ids[idx]),
                ),
            )

        chosen_id = self._node_ids[best_idx]
        node_lat, node_lon = self._node_coords[chosen_id]
        exact_distance = haversine_m(latitude, longitude, node_lat, node_lon)

        return NearestNodeResult(
            node_id=chosen_id,
            distance_m=round(exact_distance, 4),
            latitude=node_lat,
            longitude=node_lon,
            query_latitude=latitude,
            query_longitude=longitude,
        )

    def nearest_nodes(self, coordinates: Sequence[tuple[float, float]]) -> list[NearestNodeResult]:
        """Perform batch nearest-node queries."""
        return [self.nearest_node(lat, lon) for lat, lon in coordinates]


def build_spatial_index(graph: nx.MultiDiGraph) -> SpatialIndex:
    """Build a SpatialIndex for the given graph."""
    if len(graph) == 0:
        raise ValueError("Cannot build spatial index for an empty graph")

    start_time = time.perf_counter()
    coords = extract_node_coordinates(graph)
    # Canonical ordering of node IDs
    node_ids = sorted(coords.keys(), key=lambda n: str(n))
    crs_str = str(graph.graph.get("crs", "EPSG:4326"))
    index = SpatialIndex(
        node_ids=node_ids,
        node_coords=coords,
        build_time=time.perf_counter() - start_time,
        crs_str=crs_str,
    )
    return index


# Dataset-level spatial index cache
_SPATIAL_INDEX_CACHE: dict[str, tuple[int, SpatialIndex]] = {}


def get_spatial_index(
    graph: nx.MultiDiGraph,
    dataset_id: str | None = None,
    force_rebuild: bool = False,
) -> SpatialIndex:
    """Retrieve or build a cached spatial index for a road network dataset.

    Invalidates cache if graph node count/identity has changed.
    """
    key = dataset_id or f"graph_{id(graph)}"
    graph_signature = len(graph) + graph.number_of_edges()

    if not force_rebuild and key in _SPATIAL_INDEX_CACHE:
        cached_sig, cached_index = _SPATIAL_INDEX_CACHE[key]
        if cached_sig == graph_signature and cached_index.node_count == len(graph):
            return cached_index

    index = build_spatial_index(graph)
    _SPATIAL_INDEX_CACHE[key] = (graph_signature, index)
    return index


def clear_spatial_index_cache() -> None:
    """Clear all cached spatial index structures."""
    _SPATIAL_INDEX_CACHE.clear()
