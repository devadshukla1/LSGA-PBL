"""Domain models and data structures for metro routing engine."""

from dataclasses import dataclass, field
from typing import Any, List


@dataclass(frozen=True)
class RouteSegment:
    """Represents a single station-to-station hop along a specific metro line edge.

    Preserves the exact multi-edge identity (u, v, edge_key).
    """

    source_station_id: str
    destination_station_id: str
    edge_key: str
    line_id: str
    line_name: str
    line_color: str
    distance_km: float
    estimated_time_min: float
    weight_provenance: str = "published"


@dataclass
class RouteResult:
    """Encapsulates the complete result of a routing query with diagnostics."""

    source_station_id: str
    destination_station_id: str
    algorithm: str  # "BFS", "Dijkstra", "0-1 BFS", "Lexicographic Dijkstra", "Transfer-Aware Dijkstra"
    objective: str  # "minimum_stops", "minimum_time", "minimum_distance", "minimum_transfers", etc.
    station_path: List[str] = field(default_factory=list)
    edge_path: List[Any] = field(default_factory=list)  # (u, v, key) tuples
    segments: List[RouteSegment] = field(default_factory=list)
    total_stops: int = 0
    total_distance_km: float = 0.0
    total_estimated_time_min: float = 0.0
    explored_nodes: int = 0
    examined_edges: int = 0
    runtime_ms: float = 0.0
    reachable: bool = False
    message: str = ""

    # Phase 4 Line-Aware and Transfer Fields (with backward-compatible defaults)
    transfer_count: int = 0
    transfer_stations: List[str] = field(default_factory=list)
    line_sequence: List[str] = field(default_factory=list)
    transfer_penalty_min: float = 0.0
    segment_travel_time_min: float = 0.0
    total_transfer_penalty_min: float = 0.0
    total_modeled_journey_time_min: float = 0.0
    optimization_objective: str = ""
    transfer_instructions: List[str] = field(default_factory=list)
