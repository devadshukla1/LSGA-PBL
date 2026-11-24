"""Minimum Transfer routing algorithms for metro networks using line-aware state expansion.

Includes:
1. 0-1 BFS for pure Minimum Transfers (optionally tie-broken by fewest hops).
2. Lexicographic Dijkstra for Minimum Transfers, then Minimum Travel Time.
"""

import heapq
import math
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

from src.algorithms.routing_models import RouteResult, RouteSegment
from src.algorithms.transfer_utils import build_transfer_instructions, count_transfers
from src.core.exceptions import MetroGraphError


class TransferRoutingError(MetroGraphError):
    """Raised when transfer-aware routing fails due to invalid parameters or graph state."""

    pass


def _resolve_node(graph: nx.MultiGraph, n: Any) -> Any:
    """Resolves station identifier to existing graph node format (str or int)."""
    if graph.has_node(n):
        return n
    if isinstance(n, str) and n.isdigit() and graph.has_node(int(n)):
        return int(n)
    if graph.has_node(str(n)):
        return str(n)
    return n


def _reconstruct_expanded_path(
    graph: nx.MultiGraph,
    source_node: Any,
    dest_node: Any,
    predecessors: Dict[Tuple[Any, Optional[str]], Tuple[Tuple[Any, Optional[str]], Any]],
    best_dest_state: Tuple[Any, Optional[str]],
    algorithm: str,
    objective: str,
    explored_nodes: int,
    examined_edges: int,
    runtime_ms: float,
    transfer_penalty_min: float = 0.0,
) -> RouteResult:
    """Reconstructs the full route from the expanded state predecessor map.

    Each predecessor map entry maps:
        curr_state (node, line_id) -> (prev_state (prev_node, prev_line_id), edge_key)
    """
    if source_node == dest_node:
        return RouteResult(
            source_station_id=str(source_node),
            destination_station_id=str(dest_node),
            algorithm=algorithm,
            objective=objective,
            station_path=[str(source_node)],
            edge_path=[],
            segments=[],
            total_stops=0,
            total_distance_km=0.0,
            total_estimated_time_min=0.0,
            explored_nodes=explored_nodes,
            examined_edges=examined_edges,
            runtime_ms=runtime_ms,
            reachable=True,
            message="Source and destination are identical.",
            transfer_count=0,
            transfer_stations=[],
            line_sequence=[],
            transfer_penalty_min=transfer_penalty_min,
            segment_travel_time_min=0.0,
            total_transfer_penalty_min=0.0,
            total_modeled_journey_time_min=0.0,
            optimization_objective=objective,
            transfer_instructions=[
                f"Origin and destination are the same station: {source_node}. No travel needed."
            ],
        )

    if best_dest_state not in predecessors and best_dest_state[0] != source_node:
        return RouteResult(
            source_station_id=str(source_node),
            destination_station_id=str(dest_node),
            algorithm=algorithm,
            objective=objective,
            station_path=[],
            edge_path=[],
            segments=[],
            total_stops=0,
            total_distance_km=0.0,
            total_estimated_time_min=0.0,
            explored_nodes=explored_nodes,
            examined_edges=examined_edges,
            runtime_ms=runtime_ms,
            reachable=False,
            message=f"No route exists between station '{source_node}' and '{dest_node}'.",
            transfer_count=0,
            transfer_stations=[],
            line_sequence=[],
            transfer_penalty_min=transfer_penalty_min,
            segment_travel_time_min=0.0,
            total_transfer_penalty_min=0.0,
            total_modeled_journey_time_min=0.0,
            optimization_objective=objective,
            transfer_instructions=["No route available."],
        )

    # Backtrack transitions
    curr_state = best_dest_state
    backtracked_steps: List[Tuple[Tuple[Any, Optional[str]], Tuple[Any, Optional[str]], Any]] = []

    while curr_state in predecessors:
        prev_state, edge_key = predecessors[curr_state]
        backtracked_steps.append((prev_state, curr_state, edge_key))
        curr_state = prev_state

    backtracked_steps.reverse()

    station_path: List[str] = [str(source_node)]
    edge_path: List[Tuple[str, str, str]] = []
    segments: List[RouteSegment] = []
    line_sequence: List[str] = []
    total_dist = 0.0
    total_time = 0.0

    for prev_state, to_state, edge_key in backtracked_steps:
        u_raw = prev_state[0]
        v_raw = to_state[0]
        edge_data = graph.get_edge_data(u_raw, v_raw, edge_key)
        if edge_data is None:
            edge_data = graph.get_edge_data(v_raw, u_raw, edge_key) or {}

        u_str = str(u_raw)
        v_str = str(v_raw)
        dist = float(edge_data.get("distance_km", 0.0))
        time_min = float(edge_data.get("estimated_time_min", 0.0))
        lid = str(edge_data.get("line_id", to_state[1] or "Unknown"))
        lname = str(edge_data.get("line_name", lid))
        lcolor = str(edge_data.get("line_color", "#94A3B8"))
        prov = str(edge_data.get("weight_provenance", "published"))

        total_dist += dist
        total_time += time_min

        seg = RouteSegment(
            source_station_id=u_str,
            destination_station_id=v_str,
            edge_key=str(edge_key),
            line_id=lid,
            line_name=lname,
            line_color=lcolor,
            distance_km=round(dist, 3),
            estimated_time_min=round(time_min, 2),
            weight_provenance=prov,
        )
        segments.append(seg)
        edge_path.append((u_str, v_str, str(edge_key)))
        line_sequence.append(lid)
        station_path.append(v_str)

    transfers = count_transfers(line_sequence)
    transfer_stations: List[str] = []
    for i in range(1, len(segments)):
        if segments[i].line_id != segments[i - 1].line_id:
            transfer_stations.append(segments[i].source_station_id)

    total_penalty = round(transfers * transfer_penalty_min, 2)
    modeled_journey_time = round(total_time + total_penalty, 2)

    station_names = {
        str(n): graph.nodes[n].get("station_name", str(n))
        for n in graph.nodes
    }
    instructions = build_transfer_instructions(station_path, segments, station_names)

    return RouteResult(
        source_station_id=str(source_node),
        destination_station_id=str(dest_node),
        algorithm=algorithm,
        objective=objective,
        station_path=station_path,
        edge_path=edge_path,
        segments=segments,
        total_stops=len(segments),
        total_distance_km=round(total_dist, 3),
        total_estimated_time_min=round(total_time, 2),
        explored_nodes=explored_nodes,
        examined_edges=examined_edges,
        runtime_ms=round(runtime_ms, 3),
        reachable=True,
        message="Route successfully computed.",
        transfer_count=transfers,
        transfer_stations=transfer_stations,
        line_sequence=line_sequence,
        transfer_penalty_min=transfer_penalty_min,
        segment_travel_time_min=round(total_time, 2),
        total_transfer_penalty_min=total_penalty,
        total_modeled_journey_time_min=modeled_journey_time,
        optimization_objective=objective,
        transfer_instructions=instructions,
    )


def find_route_minimum_transfers(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
) -> RouteResult:
    """Computes the route with the fewest metro line transfers using 0-1 BFS.

    State:
        (station_id, current_line_id)
        Initial state: (source, None). The first board has 0 transfer cost.

    Transitions:
        From (u, line_u) to (v, line_v) along multi-edge (u, v, key):
        - If line_u is None or line_u == line_v:
            transfer_cost = 0  -> appendleft in 0-1 BFS deque
        - If line_u is not None and line_u != line_v:
            transfer_cost = 1  -> append in 0-1 BFS deque

    Tie-breaking:
        Tracks (min_transfers, hops) so among equal transfer paths, the one with
        the fewest stops is preferred deterministically.

    Time Complexity:
        O(L * (|V| + |E|)) where L is maximum lines per station.
    """
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
            algorithm="0-1 BFS",
            objective="minimum_transfers",
            explored_nodes=1,
            examined_edges=0,
            runtime_ms=runtime_ms,
        )

    # Deque stores: (transfers, hops, (station, current_line))
    # We use 0-1 BFS pattern where cost 0 pushes left, cost 1 pushes right.
    # Distances map: state -> (transfers, hops)
    initial_state = (source_node, None)
    best_cost: Dict[Tuple[Any, Optional[str]], Tuple[int, int]] = {initial_state: (0, 0)}
    predecessors: Dict[Tuple[Any, Optional[str]], Tuple[Tuple[Any, Optional[str]], Any]] = {}

    queue = deque([initial_state])
    explored_states = 0
    examined_edges = 0
    best_dest_state: Optional[Tuple[Any, Optional[str]]] = None
    min_dest_transfers = float("inf")
    min_dest_hops = float("inf")

    while queue:
        curr_state = queue.popleft()
        curr_station, curr_line = curr_state
        curr_transfers, curr_hops = best_cost[curr_state]
        explored_states += 1

        if curr_station == dest_node:
            if (curr_transfers < min_dest_transfers) or (
                curr_transfers == min_dest_transfers and curr_hops < min_dest_hops
            ):
                min_dest_transfers = curr_transfers
                min_dest_hops = curr_hops
                best_dest_state = curr_state

        # Prune if already worse than best known arrival at destination
        if curr_transfers > min_dest_transfers:
            continue

        # Explore outgoing edges
        for neighbor in sorted(graph.adj[curr_station].keys(), key=lambda x: str(x)):
            edge_dict = graph.adj[curr_station][neighbor]
            # Stable sort edges by line_id, edge_key
            for edge_key in sorted(edge_dict.keys(), key=lambda k: (str(edge_dict[k].get("line_id", "")), str(k))):
                examined_edges += 1
                edge_data = edge_dict[edge_key]
                line_id = edge_data.get("line_id")
                line_id_str = str(line_id) if line_id is not None else "Unknown"

                # Cost evaluation
                if curr_line is None:
                    # Initial boarding: 0 transfers
                    is_transfer = False
                    add_transfers = 0
                elif curr_line == line_id_str:
                    is_transfer = False
                    add_transfers = 0
                else:
                    is_transfer = True
                    add_transfers = 1

                next_state = (neighbor, line_id_str)
                new_transfers = curr_transfers + add_transfers
                new_hops = curr_hops + 1
                new_cost = (new_transfers, new_hops)

                if next_state not in best_cost or new_cost < best_cost[next_state]:
                    best_cost[next_state] = new_cost
                    predecessors[next_state] = (curr_state, edge_key)

                    if not is_transfer:
                        queue.appendleft(next_state)
                    else:
                        queue.append(next_state)

    runtime_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

    return _reconstruct_expanded_path(
        graph=graph,
        source_node=source_node,
        dest_node=dest_node,
        predecessors=predecessors,
        best_dest_state=best_dest_state or (dest_node, None),
        algorithm="0-1 BFS",
        objective="minimum_transfers",
        explored_nodes=explored_states,
        examined_edges=examined_edges,
        runtime_ms=runtime_ms,
    )


def find_route_min_transfers_then_fastest(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
) -> RouteResult:
    """Computes the route minimizing transfers first, then minimizing travel time.

    Objective:
        Lexicographic tuple: (transfers: int, total_travel_time_min: float)
        1. Fewest transfers
        2. Lowest estimated travel time

    Algorithm:
        Dijkstra on the expanded state (station_id, current_line_id) with priority:
        (transfers, total_time, hops, entry_id)

    Time Complexity:
        O(L * (|V| + |E|) log(L * |V|))
    """
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
            algorithm="Lexicographic Dijkstra",
            objective="min_transfers_then_fastest",
            explored_nodes=1,
            examined_edges=0,
            runtime_ms=runtime_ms,
        )

    initial_state = (source_node, None)
    best_dist: Dict[Tuple[Any, Optional[str]], Tuple[int, float, int]] = {initial_state: (0, 0.0, 0)}
    predecessors: Dict[Tuple[Any, Optional[str]], Tuple[Tuple[Any, Optional[str]], Any]] = {}

    entry_counter = 0
    # Heap stores: ((transfers, total_time, hops), entry_id, state)
    heap: List[Tuple[Tuple[int, float, int], int, Tuple[Any, Optional[str]]]] = []
    heapq.heappush(heap, ((0, 0.0, 0), entry_counter, initial_state))

    settled_states = set()
    explored_states = 0
    examined_edges = 0
    best_dest_state: Optional[Tuple[Any, Optional[str]]] = None

    while heap:
        (curr_transfers, curr_time, curr_hops), _, curr_state = heapq.heappop(heap)
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
                    add_transfers = 0
                elif curr_line == line_id_str:
                    add_transfers = 0
                else:
                    add_transfers = 1

                next_state = (neighbor, line_id_str)
                new_transfers = curr_transfers + add_transfers
                new_time = round(curr_time + float(time_val), 4)
                new_hops = curr_hops + 1
                new_cost = (new_transfers, new_time, new_hops)

                if next_state not in best_dist or new_cost < best_dist[next_state]:
                    best_dist[next_state] = new_cost
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
        algorithm="Lexicographic Dijkstra",
        objective="min_transfers_then_fastest",
        explored_nodes=explored_states,
        examined_edges=examined_edges,
        runtime_ms=runtime_ms,
    )
