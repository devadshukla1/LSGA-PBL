"""Route recalculation and disruption comparison engine."""

from typing import List

import networkx as nx

from src.algorithms.bfs import find_route_bfs
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.minimum_transfers import (
    find_route_min_transfers_then_fastest,
    find_route_minimum_transfers,
)
from src.algorithms.routing_models import RouteResult
from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra
from src.simulation.closure_engine import _resolve_station_id
from src.simulation.models import RouteRerouteResult


def calculate_route_with_objective(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
    objective: str = "minimum_time",
    transfer_penalty_min: float = 5.0,
) -> RouteResult:
    """Dispatches route query to the appropriate Phase 3 / Phase 4 routing engine."""
    obj_clean = objective.lower().replace("-", "_").replace(" ", "_")

    if "stop" in obj_clean or "bfs" in obj_clean:
        return find_route_bfs(graph, source, destination)
    elif "lexicographic" in obj_clean or "transfers_then_fastest" in obj_clean:
        return find_route_min_transfers_then_fastest(graph, source, destination)
    elif "min_transfer" in obj_clean or "minimum_transfer" in obj_clean:
        return find_route_minimum_transfers(graph, source, destination)
    elif "penalty" in obj_clean or "transfer_aware" in obj_clean:
        return find_route_transfer_aware_dijkstra(
            graph, source, destination, transfer_penalty_min=transfer_penalty_min
        )
    elif "distance" in obj_clean:
        return find_route_dijkstra(graph, source, destination, objective="minimum_distance")
    else:
        # Default minimum time
        return find_route_dijkstra(graph, source, destination, objective="minimum_time")


def compare_routes_across_closure(
    original_graph: nx.MultiGraph,
    simulated_graph: nx.MultiGraph,
    source: str,
    destination: str,
    closed_station_ids: List[str],
    objective: str = "minimum_time",
    transfer_penalty_min: float = 5.0,
) -> RouteRerouteResult:
    """Calculates baseline and post-closure routes, categorizing disruption outcome.

    Disruption Categories:
    - ENDPOINT_CLOSED: Source or destination station itself is closed.
    - ALREADY_UNREACHABLE: No baseline route existed even before closures.
    - UNREACHABLE: Baseline route existed, but closures severed all remaining paths.
    - UNCHANGED: The exact station and edge sequence is still valid and optimal.
    - REROUTED: A detour route was successfully found with different station hops or lines.
    """
    closed_set = {str(s) for s in closed_station_ids}
    src_str = str(source)
    dst_str = str(destination)

    # 1. Endpoint closed check
    if src_str in closed_set or dst_str in closed_set:
        closed_endpoints = []
        if src_str in closed_set:
            closed_endpoints.append(f"Origin '{src_str}'")
        if dst_str in closed_set:
            closed_endpoints.append(f"Destination '{dst_str}'")
        msg = f"Cannot route: {', '.join(closed_endpoints)} is closed in this simulation."
        return RouteRerouteResult(
            source_station_id=src_str,
            destination_station_id=dst_str,
            objective=objective,
            disruption_status="ENDPOINT_CLOSED",
            original_reachable=False,
            new_reachable=False,
            message=msg,
        )

    # Check endpoints exist in original graph
    src_node = _resolve_station_id(original_graph, src_str)
    dst_node = _resolve_station_id(original_graph, dst_str)

    if not original_graph.has_node(src_node) or not original_graph.has_node(dst_node):
        return RouteRerouteResult(
            source_station_id=src_str,
            destination_station_id=dst_str,
            objective=objective,
            disruption_status="ALREADY_UNREACHABLE",
            original_reachable=False,
            new_reachable=False,
            message="Source or destination does not exist in graph.",
        )

    # 2. Baseline route calculation
    orig_res = calculate_route_with_objective(
        original_graph,
        src_str,
        dst_str,
        objective=objective,
        transfer_penalty_min=transfer_penalty_min,
    )

    if not orig_res.reachable:
        return RouteRerouteResult(
            source_station_id=src_str,
            destination_station_id=dst_str,
            objective=objective,
            disruption_status="ALREADY_UNREACHABLE",
            original_reachable=False,
            new_reachable=False,
            message="No baseline route existed between these stations prior to closure.",
        )

    # 3. Post-closure route calculation
    # Endpoints might have been removed from simulated_graph
    if not simulated_graph.has_node(src_node) or not simulated_graph.has_node(dst_node):
        return RouteRerouteResult(
            source_station_id=src_str,
            destination_station_id=dst_str,
            objective=objective,
            disruption_status="ENDPOINT_CLOSED",
            original_reachable=True,
            new_reachable=False,
            original_stops=orig_res.total_stops,
            original_transfers=orig_res.transfer_count,
            original_estimated_time_min=orig_res.total_estimated_time_min,
            original_distance_km=orig_res.total_distance_km,
            original_station_path=orig_res.station_path,
            message="Route unavailable because origin or destination station was removed.",
        )

    post_res = calculate_route_with_objective(
        simulated_graph,
        src_str,
        dst_str,
        objective=objective,
        transfer_penalty_min=transfer_penalty_min,
    )

    if not post_res.reachable:
        return RouteRerouteResult(
            source_station_id=src_str,
            destination_station_id=dst_str,
            objective=objective,
            disruption_status="UNREACHABLE",
            original_reachable=True,
            new_reachable=False,
            original_stops=orig_res.total_stops,
            original_transfers=orig_res.transfer_count,
            original_estimated_time_min=orig_res.total_estimated_time_min,
            original_distance_km=orig_res.total_distance_km,
            original_station_path=orig_res.station_path,
            message="Route severed: destination is unreachable after selected closures.",
        )

    # 4. Determine if route was UNCHANGED or REROUTED
    # Check exact station sequence and edge path
    is_identical = (
        orig_res.station_path == post_res.station_path
        and orig_res.edge_path == post_res.edge_path
    )

    disruption_status = "UNCHANGED" if is_identical else "REROUTED"
    msg = (
        "Baseline route remains unaffected by closures."
        if is_identical
        else "Detour route successfully computed around closed stations."
    )

    stops_diff = post_res.total_stops - orig_res.total_stops
    transfers_diff = post_res.transfer_count - orig_res.transfer_count
    time_diff = round(post_res.total_estimated_time_min - orig_res.total_estimated_time_min, 2)
    dist_diff = round(post_res.total_distance_km - orig_res.total_distance_km, 3)

    return RouteRerouteResult(
        source_station_id=src_str,
        destination_station_id=dst_str,
        objective=objective,
        disruption_status=disruption_status,
        original_reachable=True,
        new_reachable=True,
        original_stops=orig_res.total_stops,
        new_stops=post_res.total_stops,
        stops_diff=stops_diff,
        original_transfers=orig_res.transfer_count,
        new_transfers=post_res.transfer_count,
        transfers_diff=transfers_diff,
        original_estimated_time_min=orig_res.total_estimated_time_min,
        new_estimated_time_min=post_res.total_estimated_time_min,
        time_diff_min=time_diff,
        original_distance_km=orig_res.total_distance_km,
        new_distance_km=post_res.total_distance_km,
        distance_diff_km=dist_diff,
        original_station_path=orig_res.station_path,
        new_station_path=post_res.station_path,
        message=msg,
    )
