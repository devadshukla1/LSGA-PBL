"""Data models for spatial nearest-node queries and index metadata."""

from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True)
class NearestNodeResult:
    """Result of a spatial nearest-node lookup."""

    node_id: Hashable
    distance_m: float
    latitude: float
    longitude: float
    query_latitude: float
    query_longitude: float


@dataclass(frozen=True)
class SpatialIndexMetadata:
    """Metadata describing a built spatial index."""

    node_count: int
    build_time_seconds: float
    coordinate_reference_system: str
    distance_metric: str = "great_circle_meters"
