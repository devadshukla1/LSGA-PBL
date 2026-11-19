"""Shared validation and result construction for advanced routing."""

import math
from dataclasses import dataclass

import networkx as nx

from src.algorithms.routing_models import RouteResult, RoutingDiagnostics
from src.routing.route_metrics import calculate
from src.routing.route_validation import validate_route


def validate_request(graph, source, target, objective: str) -> str:
    if not isinstance(graph, nx.MultiDiGraph):
        raise ValueError("Expected MultiDiGraph")
    if source not in graph or target not in graph:
        raise ValueError("Unknown source or destination")
    if objective not in {"distance", "travel_time"}:
        raise ValueError("Unknown objective")
    for _, _, data in graph.edges(data=True):
        for field in ("length_m", "travel_time_s"):
            value = data.get(field)
            if not isinstance(value, int | float) or not math.isfinite(value) or value < 0:
                raise ValueError("Weights must be finite and nonnegative")
    return "length_m" if objective == "distance" else "travel_time_s"


def result_from_edges(graph, source, target, edges, algorithm, objective, expanded=0, examined=0):
    reachable = edges is not None
    nodes = (source,) + tuple(v for _, v, _ in edges) if reachable else ()
    metrics = calculate(graph, edges, objective) if reachable else None
    route = RouteResult(
        algorithm,
        objective,
        source,
        target,
        reachable,
        nodes,
        edges or (),
        metrics.total_distance_m if metrics else None,
        metrics.total_travel_time_s if metrics else None,
        metrics.optimized_cost if metrics else None,
        expanded,
        examined,
        "ok" if reachable else "unreachable",
        "Route found" if reachable else "Destination is unreachable",
        RoutingDiagnostics("zero", True, False, "valid"),
    )
    validate_route(graph, route)
    return route


@dataclass(frozen=True)
class AlternativeRoutesResult:
    source: object
    target: object
    objective: str
    requested_k: int
    returned_k: int
    routes: tuple[RouteResult, ...]
    status: str
    message: str


def find_alternative_routes(graph, source, target, k=3, objective="distance", max_k=5):
    from src.algorithms.yen_k_shortest import yen_k_shortest_paths

    routes = yen_k_shortest_paths(graph, source, target, k, objective, max_k)
    return AlternativeRoutesResult(
        source,
        target,
        objective,
        k,
        len(routes),
        tuple(routes),
        "ok" if routes else "unreachable",
        f"Found {len(routes)} loopless routes",
    )
