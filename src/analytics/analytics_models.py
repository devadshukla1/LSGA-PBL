"""Typed analytics outputs with explicit graph interpretation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CentralityResult:
    metric_name: str
    scores: dict
    top_nodes: tuple
    graph_node_count: int
    graph_edge_count: int
    directed: bool
    weighted: bool
    approximate: bool
    parameters: dict
    runtime_seconds: float


@dataclass(frozen=True)
class ConnectivitySummary:
    node_count: int
    edge_count: int
    weak_component_count: int
    strong_component_count: int
    largest_weak_component_size: int
    largest_strong_component_size: int
    largest_weak_component_fraction: float
    largest_strong_component_fraction: float
    weak_sizes: tuple
    strong_sizes: tuple
    isolated_nodes: tuple


@dataclass(frozen=True)
class MSTResult:
    projection_method: str
    weight_attribute: str
    node_count: int
    edge_count: int
    component_count: int
    forest_edge_count: int
    total_weight: float
    is_connected: bool
    forest_edges: tuple


@dataclass(frozen=True)
class FailureScenario:
    failure_type: str
    removed_nodes: tuple
    seed: int | None = None
