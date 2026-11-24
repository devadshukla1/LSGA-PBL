"""Check path orientation, edge keys, and reported costs."""

import math

import networkx as nx

from src.algorithms.routing_models import RouteResult
from src.routing.route_metrics import calculate


def validate_route(graph: nx.MultiDiGraph, result: RouteResult) -> None:
    """Raise ValueError when any reported route field disagrees with the graph."""
    if result.source not in graph or result.target not in graph:
        raise ValueError("Missing route endpoint")
    if not result.is_reachable:
        if result.node_path or result.edge_path or result.optimized_cost is not None:
            raise ValueError("Malformed unreachable route")
        return
    if (
        not result.node_path
        or result.node_path[0] != result.source
        or result.node_path[-1] != result.target
    ):
        raise ValueError("Invalid route endpoints")
    if len(result.edge_path) != len(result.node_path) - 1:
        raise ValueError("Node and edge path lengths disagree")
    for (u, v, k), start, end in zip(
        result.edge_path, result.node_path[:-1], result.node_path[1:], strict=True
    ):
        if u != start or v != end or not graph.has_edge(u, v, k):
            raise ValueError("Invalid directed road edge or key")
    metrics = calculate(graph, result.edge_path, result.objective)
    for actual, expected in [
        (result.total_distance_m, metrics.total_distance_m),
        (result.total_travel_time_s, metrics.total_travel_time_s),
        (result.optimized_cost, metrics.optimized_cost),
    ]:
        if (
            actual is None
            or not math.isfinite(actual)
            or not math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-8)
        ):
            raise ValueError("Reported route cost differs from keyed road weights")
