"""Data models for structural station importance and network analytics."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class StationAnalyticsResult:
    """Encapsulates structural centrality, connectivity, and topological metrics for a station."""

    station_id: str
    station_name: str
    degree: int
    degree_centrality: float
    betweenness_centrality: float
    line_count: int
    line_names: List[str] = field(default_factory=list)
    is_interchange: bool = False
    is_articulation_point: bool = False
    component_id: int = 0
    weighted_betweenness_centrality: Optional[float] = None


@dataclass
class NetworkAnalyticsSummary:
    """Summarizes network-wide topological and structural vulnerability indicators."""

    total_stations: int
    total_connections: int  # Unweighted simple edges in the analytical projection
    total_multigraph_edges: int
    total_lines: int
    total_interchanges: int
    total_articulation_points: int
    connected_components: int
    largest_component_size: int
    smallest_component_size: int
    isolated_stations_count: int
    average_degree: float
    max_degree: int
    highest_degree_station: str
    highest_betweenness_station: str
