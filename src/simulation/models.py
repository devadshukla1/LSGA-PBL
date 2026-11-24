"""Data models for station closure and network resilience simulation."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import networkx as nx


@dataclass
class ConnectivityMetrics:
    """Encapsulates component decomposition and pairwise reachability metrics."""

    station_count: int
    edge_count: int
    connected_components: int
    is_connected: bool
    largest_component_size: int
    smallest_component_size: int
    isolated_stations_count: int
    isolated_stations: List[str] = field(default_factory=list)
    component_sizes: List[int] = field(default_factory=list)
    station_to_component: Dict[str, int] = field(default_factory=dict)
    reachable_station_pairs: int = 0
    possible_station_pairs: int = 0
    reachability_ratio: float = 0.0


@dataclass
class RouteRerouteResult:
    """Comparative outcome between a baseline route and a post-closure route."""

    source_station_id: str
    destination_station_id: str
    objective: str
    disruption_status: str  # "UNCHANGED", "REROUTED", "UNREACHABLE", "ENDPOINT_CLOSED", "ALREADY_UNREACHABLE"
    original_reachable: bool = False
    new_reachable: bool = False
    original_stops: int = 0
    new_stops: int = 0
    stops_diff: int = 0
    original_transfers: int = 0
    new_transfers: int = 0
    transfers_diff: int = 0
    original_estimated_time_min: float = 0.0
    new_estimated_time_min: float = 0.0
    time_diff_min: float = 0.0
    original_distance_km: float = 0.0
    new_distance_km: float = 0.0
    distance_diff_km: float = 0.0
    original_station_path: List[str] = field(default_factory=list)
    new_station_path: List[str] = field(default_factory=list)
    message: str = ""


@dataclass
class ClosureSimulationResult:
    """Encapsulates the complete outcome of a simulated station closure scenario."""

    dataset_id: str
    closed_station_ids: List[str] = field(default_factory=list)
    closed_station_names: List[str] = field(default_factory=list)
    baseline_metrics: Optional[ConnectivityMetrics] = None
    post_closure_metrics: Optional[ConnectivityMetrics] = None
    removed_stations_count: int = 0
    removed_edges_count: int = 0
    component_count_change: int = 0
    largest_component_reduction: int = 0
    reachable_pairs_loss: int = 0
    reachability_ratio_change: float = 0.0
    simulation_graph: Optional[nx.MultiGraph] = None
    warnings: List[str] = field(default_factory=list)
    reroute_results: Dict[str, RouteRerouteResult] = field(default_factory=dict)
