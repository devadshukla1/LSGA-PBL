"""Validation of route topology, edge keys, and cost optimality against NetworkX."""

import math
from collections.abc import Hashable

import networkx as nx

from src.algorithms.routing_models import RouteResult
from src.routing.route_metrics import calculate


def verify_route_correctness_and_optimality(
    graph: nx.MultiDiGraph,
    route: RouteResult,
    source: Hashable,
    target: Hashable,
    objective: str = "distance",
    expected_reachable: bool = True,
) -> tuple[bool, bool, float | None, float | None, float | None, list[str]]:
    """Validate route structure and compare optimal cost against NetworkX oracle.

    Returns:
        tuple of (
            route_valid,
            optimality_verified,
            reference_cost,
            absolute_error,
            relative_error,
            issues
        )
    """
    issues: list[str] = []
    weight_field = "length_m" if objective == "distance" else "travel_time_s"

    # Check endpoints
    if source not in graph or target not in graph:
        issues.append("Source or target junction missing from graph")
        return False, False, None, None, None, issues

    if route.source != source or route.target != target:
        issues.append(
            f"Route endpoints ({route.source}, {route.target}) "
            f"do not match query ({source}, {target})"
        )

    # Reachability checks
    if not expected_reachable:
        if route.is_reachable or route.node_path or route.edge_path:
            issues.append("Unreachable query returned reachable route path")
            return False, False, None, None, None, issues
        return True, True, None, 0.0, 0.0, issues

    if not route.is_reachable:
        issues.append("Expected reachable query, but algorithm returned unreachable")
        return False, False, None, None, None, issues

    # Validate node and edge sequence
    if not route.node_path or route.node_path[0] != source or route.node_path[-1] != target:
        issues.append("Route node path does not begin at source or end at target")

    if len(route.edge_path) != len(route.node_path) - 1:
        issues.append(
            f"Edge path count ({len(route.edge_path)}) does not match "
            f"node path steps ({len(route.node_path) - 1})"
        )

    # Check edge existence and directionality
    for (u, v, k), expected_u, expected_v in zip(
        route.edge_path, route.node_path[:-1], route.node_path[1:], strict=False
    ):
        if u != expected_u or v != expected_v:
            issues.append(
                f"Edge ({u}, {v}, {k}) disagrees with node step ({expected_u}, {expected_v})"
            )
        if not graph.has_edge(u, v, k):
            issues.append(f"Directed edge ({u}, {v}, {k}) missing from graph")

    # Verify reported cost against sum of edge weights
    metrics = calculate(graph, route.edge_path, objective)
    if route.optimized_cost is None or not math.isclose(
        route.optimized_cost, metrics.optimized_cost, rel_tol=1e-8, abs_tol=1e-6
    ):
        issues.append(
            f"Reported cost ({route.optimized_cost}) disagrees with "
            f"sum of edge weights ({metrics.optimized_cost})"
        )

    route_valid = len(issues) == 0

    # Query NetworkX oracle for optimal cost
    try:
        ref_cost = float(nx.shortest_path_length(graph, source, target, weight=weight_field))
    except (nx.NetworkXNoPath, nx.NodeNotFound) as err:
        issues.append(f"NetworkX oracle failed to find path: {err}")
        return route_valid, False, None, None, None, issues

    actual_cost = float(route.optimized_cost) if route.optimized_cost is not None else math.inf
    abs_error = abs(actual_cost - ref_cost)
    rel_error = (abs_error / ref_cost) if ref_cost > 0 else 0.0

    optimality_verified = math.isclose(actual_cost, ref_cost, rel_tol=1e-8, abs_tol=1e-6)
    if not optimality_verified:
        issues.append(
            f"Cost suboptimality: actual={actual_cost:.4f}, "
            f"reference={ref_cost:.4f}, diff={abs_error:.6f}"
        )

    return (
        route_valid,
        optimality_verified,
        round(ref_cost, 6),
        round(abs_error, 8),
        round(rel_error, 8),
        issues,
    )
