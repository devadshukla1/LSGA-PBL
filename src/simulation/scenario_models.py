"""Immutable scenario configurations and simulation outcomes."""

from dataclasses import dataclass

from src.algorithms.routing_models import RouteResult


@dataclass(frozen=True)
class TrafficScenario:
    scenario_id: str
    scenario_name: str
    dataset_id: str
    dataset_fingerprint: str
    congestion_level: str
    random_seed: int
    congestion_coverage: float
    closed_edges: tuple
    blocked_nodes: tuple
    parameters: tuple[float, float]
    created_at: str
    schema_version: int = 1


@dataclass(frozen=True)
class SimulationRequest:
    source: int
    target: int
    algorithm: str = "dijkstra"
    objective: str = "travel_time"


@dataclass(frozen=True)
class SimulationResult:
    baseline: RouteResult
    scenario_route: RouteResult | None
    status: str
    comparison: dict
