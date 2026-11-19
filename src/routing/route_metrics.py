"""Metrics from exact selected road edges."""

from dataclasses import dataclass

import networkx as nx


@dataclass(frozen=True)
class RouteMetrics:
    total_distance_m: float
    total_distance_km: float
    total_travel_time_s: float
    total_travel_time_min: float
    hop_count: int
    optimized_cost: float


def calculate(graph: nx.MultiDiGraph, edge_path: tuple, objective: str) -> RouteMetrics:
    """Sum stored weights from keyed directed edges only."""
    length = sum(graph.edges[u, v, k]["length_m"] for u, v, k in edge_path)
    duration = sum(graph.edges[u, v, k]["travel_time_s"] for u, v, k in edge_path)
    return RouteMetrics(
        length,
        length / 1000,
        duration,
        duration / 60,
        len(edge_path),
        length if objective == "distance" else duration,
    )
