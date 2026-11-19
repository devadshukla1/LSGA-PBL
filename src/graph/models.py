"""Road topology and dataset contracts."""

from collections.abc import Hashable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RoadEdge:
    source_node: Hashable
    target_node: Hashable
    edge_key: Hashable
    length_m: float
    speed_kph: float
    travel_time_s: float
    highway: str | list
    oneway: bool | list | None
    geometry: Any


@dataclass(frozen=True)
class GraphMetadata:
    dataset_id: str
    dataset_name: str
    source: str
    study_area: str
    created_at_utc: str
    node_count: int
    edge_count: int
    graph_type: str
    weighting_version: str
    osm_acquisition_parameters: dict
    is_offline_sample: bool


@dataclass(frozen=True)
class DatasetInfo:
    graph: Any
    metadata: GraphMetadata
    origin: str
    notice: str = ""


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str
    context: dict


@dataclass
class ValidationReport:
    issues: list[ValidationIssue] = field(default_factory=list)
    weak_components: int = 0
    strong_components: int = 0

    @property
    def valid(self) -> bool:
        return all(issue.severity != "ERROR" for issue in self.issues)


@dataclass(frozen=True)
class GraphStatistics:
    nodes: int
    directed_edges: int
    density: float
    average_in_degree: float
    average_out_degree: float
    maximum_degree: int
    minimum_degree: int
    weak_components: int
    strong_components: int
    largest_weak_component: int
    largest_strong_component: int
    parallel_edge_pairs: int
    self_loops: int
    total_length_m: float
    minimum_length_m: float
    maximum_length_m: float
    average_length_m: float
