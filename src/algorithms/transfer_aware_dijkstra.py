"""Transfer-Penalty-Aware Dijkstra Routing Engine.

Optimizes:
    Total Modeled Journey Time = Sum(Segment Travel Time) + Sum(Transfer Penalty * Transfers)
Allows flexible configuration of transfer penalty (default 5.0 min, valid range 0.0 to 15.0 min).
"""

import heapq
import math
import time
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from src.algorithms.minimum_transfers import (
    TransferRoutingError,
    _reconstruct_expanded_path,
    _resolve_node,
)
from src.algorithms.routing_models import RouteResult


def find_route_transfer_aware_dijkstra(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
    transfer_penalty_min: float = 5.0,
) -> RouteResult:
    """Calculates fastest route penalizing line transfers by a configurable transfer wait penalty.

    Cost model:
        - Segment traversal along same line:
            cost = segment.estimated_time_min
        - Segment traversal switching to a different line:
            cost = segment.estimated_time_min + transfer_penalty_min
        - Initial boarding at origin:
            cost = segment.estimated_time_min (0 transfer penalty)

    Args:
        graph: NetworkX MultiGraph representing the metro network.
        source: Station ID of origin.
        destination: Station ID of destination.
        transfer_penalty_min: Additional time penalty per transfer in minutes (default 5.0 min).

    Returns:
        RouteResult populated with transfer count, segment travel times, transfer penalties,
        and total modeled journey time.
    """
    if transfer_penalty_min < 0:
        raise TransferRoutingError(
            f"Transfer penalty cannot be negative ({transfer_penalty_min} min provided)."
        )

    start_ns = time.perf_counter_ns()
    source_node = _resolve_node(graph, source)
    dest_node = _resolve_node(graph, destination)

    if not graph.has_node(source_node):
        raise TransferRoutingError(f"Source station '{source}' does not exist in graph.")
    if not graph.has_node(dest_node):
        raise TransferRoutingError(f"Destination station '{destination}' does not exist in graph.")

    if source_node == dest_node:
        runtime_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0
        return _reconstruct_expanded_path(
            graph=graph,
            source_node=source_node,
            dest_node=dest_node,
            predecessors={},
            best_dest_state=(dest_node, None),
            algorithm="Transfer-Aware Dijkstra",
            objective="transfer_aware_fastest",
            explored_nodes=1,
            examined_edges=0,
            runtime_ms=runtime_ms,
            transfer_penalty_min=transfer_penalty_min,
        )

    initial_state = (source_node, None)
    best_cost: Dict[Tuple[Any, Optional[str]], float] = {initial_state: 0.0}
    predecessors: Dict[Tuple[Any, Optional[str]], Tuple[Tuple[Any, Optional[str]], Any]] = {}

    entry_counter = 0
    # Heap stores: (total_modeled_cost, entry_counter, state)
    heap: List[Tuple[float, int, Tuple[Any, Optional[str]]]] = []
    heapq.heappush(heap, (0.0, entry_counter, initial_state))

    settled_states = set()
    explored_states = 0
    examined_edges = 0
    best_dest_state: Optional[Tuple[Any, Optional[str]]] = None

    while heap:
        curr_cost, _, curr_state = heapq.heappop(heap)
        if curr_state in settled_states:
            continue
        settled_states.add(curr_state)
        explored_states += 1

        curr_station, curr_line = curr_state

        if curr_station == dest_node:
            best_dest_state = curr_state
            break

        for neighbor in sorted(graph.adj[curr_station].keys(), key=lambda x: str(x)):
            edge_dict = graph.adj[curr_station][neighbor]
            for edge_key in sorted(edge_dict.keys(), key=lambda k: str(k)):
                examined_edges += 1
                edge_data = edge_dict[edge_key]
                line_id = edge_data.get("line_id")
                line_id_str = str(line_id) if line_id is not None else "Unknown"

                time_val = edge_data.get("estimated_time_min", float("inf"))
                if not isinstance(time_val, (int, float)) or math.isnan(time_val) or time_val <= 0:
                    continue

                if curr_line is None:
                    # Initial boarding: no transfer penalty
                    penalty = 0.0
                elif curr_line == line_id_str:
                    penalty = 0.0
                else:
                    penalty = transfer_penalty_min

                step_cost = float(time_val) + penalty
                new_cost = round(curr_cost + step_cost, 4)
                next_state = (neighbor, line_id_str)

                if next_state not in best_cost or new_cost < best_cost[next_state]:
                    best_cost[next_state] = new_cost
                    predecessors[next_state] = (curr_state, edge_key)
                    entry_counter += 1
                    heapq.heappush(heap, (new_cost, entry_counter, next_state))

    runtime_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

    return _reconstruct_expanded_path(
        graph=graph,
        source_node=source_node,
        dest_node=dest_node,
        predecessors=predecessors,
        best_dest_state=best_dest_state or (dest_node, None),
        algorithm="Transfer-Aware Dijkstra",
        objective="transfer_aware_fastest",
        explored_nodes=explored_states,
        examined_edges=examined_edges,
        runtime_ms=runtime_ms,
        transfer_penalty_min=transfer_penalty_min,
    )
