"""Typed routing requests, edges, and results."""

from collections.abc import Hashable
from dataclasses import dataclass


@dataclass(frozen=True)
class RoutingRequest:
    source: Hashable
    target: Hashable
    algorithm: str
    objective: str


@dataclass(frozen=True)
class RouteEdge:
    source: Hashable
    target: Hashable
    edge_key: Hashable
    length_m: float
    travel_time_s: float


@dataclass(frozen=True)
class RoutingDiagnostics:
    heuristic_type: str
    heuristic_admissible: bool
    fallback_used: bool
    validation_status: str


@dataclass(frozen=True)
class RouteResult:
    algorithm: str
    objective: str
    source: Hashable
    target: Hashable
    is_reachable: bool
    node_path: tuple
    edge_path: tuple
    total_distance_m: float | None
    total_travel_time_s: float | None
    optimized_cost: float | None
    nodes_expanded: int
    edges_examined: int
    status: str
    message: str
    diagnostics: RoutingDiagnostics
