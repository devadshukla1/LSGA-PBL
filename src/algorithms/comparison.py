"""Multi-algorithm comparative evaluation runner with line and transfer metrics."""

from typing import Dict, List, Tuple

import networkx as nx
import pandas as pd

from src.algorithms.bfs import find_route_bfs
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.minimum_transfers import (
    find_route_min_transfers_then_fastest,
    find_route_minimum_transfers,
)
from src.algorithms.routing_models import RouteResult
from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra


def compare_routing_algorithms(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
    transfer_penalty_min: float = 5.0,
) -> Tuple[pd.DataFrame, Dict[str, RouteResult]]:
    """Runs all routing algorithms on the exact same query and compiles comparative metrics.

    Evaluates:
    1. BFS (Minimum Stops)
    2. Dijkstra (Minimum Travel Time)
    3. Dijkstra (Minimum Distance)
    4. 0-1 BFS (Minimum Transfers)
    5. Lexicographic Dijkstra (Min Transfers, then Fastest)
    6. Transfer-Aware Dijkstra (Fastest with Penalty)

    Returns:
        (comparison_df, results_map)
    """
    results: Dict[str, RouteResult] = {}

    # 1. BFS Minimum Stops
    try:
        results["BFS (Min Stops)"] = find_route_bfs(graph, source, destination)
    except Exception as e:
        results["BFS (Min Stops)"] = RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm="BFS",
            objective="minimum_stops",
            message=f"Failed: {e}",
        )

    # 2. Dijkstra Minimum Travel Time
    try:
        results["Dijkstra (Min Time)"] = find_route_dijkstra(
            graph, source, destination, objective="minimum_time"
        )
    except Exception as e:
        results["Dijkstra (Min Time)"] = RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm="Dijkstra",
            objective="minimum_time",
            message=f"Failed: {e}",
        )

    # 3. Dijkstra Minimum Modeled Distance
    try:
        results["Dijkstra (Min Distance)"] = find_route_dijkstra(
            graph, source, destination, objective="minimum_distance"
        )
    except Exception as e:
        results["Dijkstra (Min Distance)"] = RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm="Dijkstra",
            objective="minimum_distance",
            message=f"Failed: {e}",
        )

    # 4. 0-1 BFS Minimum Transfers
    try:
        results["0-1 BFS (Min Transfers)"] = find_route_minimum_transfers(
            graph, source, destination
        )
    except Exception as e:
        results["0-1 BFS (Min Transfers)"] = RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm="0-1 BFS",
            objective="minimum_transfers",
            message=f"Failed: {e}",
        )

    # 5. Lexicographic Dijkstra (Min Transfers, then Fastest)
    try:
        results["Lexicographic (Transfers then Fastest)"] = find_route_min_transfers_then_fastest(
            graph, source, destination
        )
    except Exception as e:
        results["Lexicographic (Transfers then Fastest)"] = RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm="Lexicographic Dijkstra",
            objective="min_transfers_then_fastest",
            message=f"Failed: {e}",
        )

    # 6. Transfer-Aware Dijkstra (Fastest with Configurable Penalty)
    try:
        results[f"Transfer-Aware ({transfer_penalty_min:.0f}m Penalty)"] = (
            find_route_transfer_aware_dijkstra(
                graph, source, destination, transfer_penalty_min=transfer_penalty_min
            )
        )
    except Exception as e:
        results[f"Transfer-Aware ({transfer_penalty_min:.0f}m Penalty)"] = RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm="Transfer-Aware Dijkstra",
            objective="transfer_aware_fastest",
            message=f"Failed: {e}",
        )

    rows: List[Dict[str, any]] = []
    for label, res in results.items():
        rows.append({
            "Label": label,
            "Algorithm": res.algorithm,
            "Objective": res.objective.replace("_", " ").title(),
            "Reachable": "Yes" if res.reachable else "No",
            "Stops": res.total_stops if res.reachable else "N/A",
            "Transfers": res.transfer_count if res.reachable else "N/A",
            "Distance (km)": f"{res.total_distance_km:.2f}" if res.reachable else "N/A",
            "Estimated Time (min)": f"{res.total_estimated_time_min:.1f}" if res.reachable else "N/A",
            "Travel Time (min)": f"{res.total_estimated_time_min:.1f}" if res.reachable else "N/A",
            "Modeled Journey Time (min)": (
                f"{res.total_modeled_journey_time_min:.1f}" if res.reachable else "N/A"
            ),
            "Explored Nodes": res.explored_nodes,
            "Examined Edges": res.examined_edges,
            "Runtime (ms)": f"{res.runtime_ms:.2f}",
        })

    comparison_df = pd.DataFrame(rows)
    return comparison_df, results
