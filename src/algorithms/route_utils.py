"""Route reconstruction, path validation, and metric evaluation utilities."""

import math
from typing import Any, List, Tuple

import networkx as nx

from src.algorithms.routing_models import RouteResult, RouteSegment
from src.core.exceptions import MetroGraphError


class RouteValidationError(MetroGraphError):
    """Raised when an extracted path fails topological or invariant validation."""

    pass


def choose_best_parallel_edge(
    graph: nx.MultiGraph,
    u: str,
    v: str,
    preference: str = "minimum_time",
) -> Tuple[str, dict]:
    """Deterministically selects the best edge among parallel edges between stations u and v.

    Tie-breaking policy:
    1. If preference == 'minimum_time':
       - Smallest estimated_time_min (> 0)
       - Smallest distance_km (> 0)
       - Stable string sort on line_id and edge_key
    2. If preference == 'minimum_distance':
       - Smallest distance_km (> 0)
       - Smallest estimated_time_min (> 0)
       - Stable string sort on line_id and edge_key
    3. Default (BFS / minimum_stops):
       - Smallest estimated_time_min (> 0)
       - Smallest distance_km (> 0)
       - Stable string sort on line_id and edge_key
    """
    edges_dict = graph.get_edge_data(u, v)
    if not edges_dict:
        raise RouteValidationError(f"No edge exists in graph between '{u}' and '{v}'.")

    def sort_key(item: Tuple[Any, dict]):
        key, attrs = item
        t = attrs.get("estimated_time_min", float("inf"))
        d = attrs.get("distance_km", float("inf"))
        # Sanitize non-positive or NaN values
        t_clean = t if (isinstance(t, (int, float)) and t > 0 and not math.isnan(t)) else float("inf")
        d_clean = d if (isinstance(d, (int, float)) and d > 0 and not math.isnan(d)) else float("inf")
        line_id = str(attrs.get("line_id", ""))
        key_str = str(key)

        if preference == "minimum_distance":
            return (d_clean, t_clean, line_id, key_str)
        return (t_clean, d_clean, line_id, key_str)

    sorted_edges = sorted(edges_dict.items(), key=sort_key)
    best_key, best_attrs = sorted_edges[0]
    return str(best_key), best_attrs


def reconstruct_route(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
    algorithm: str,
    objective: str,
    predecessors: dict,
    explored_nodes: int,
    examined_edges: int,
    runtime_ms: float,
) -> RouteResult:
    """Reconstructs the full station path, exact multi-edge sequence, and segments.

    Predecessor format:
    - For BFS: predecessors[node] = parent_node
    - For Dijkstra: predecessors[node] = (parent_node, edge_key)
    """
    # 1. Zero-hop route (source == destination)
    if source == destination:
        return RouteResult(
            source_station_id=source,
            destination_station_id=destination,
            algorithm=algorithm,
            objective=objective,
            station_path=[source],
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
        )

    # 2. Check if destination was reached
    if destination in predecessors:
        dest_key = destination
    elif isinstance(destination, str) and destination.isdigit() and int(destination) in predecessors:
        dest_key = int(destination)
    else:
        dest_key = destination
    if dest_key not in predecessors:
        return RouteResult(
            source_station_id=str(source),
            destination_station_id=str(destination),
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
            message=f"No route exists between station '{source}' and '{destination}'.",
        )

    # 3. Backtrack station path and edge keys
    curr = dest_key
    station_path_rev = [str(curr)]
    edge_keys_rev = []

    src_key = source if source in graph.nodes else (
        int(source) if isinstance(source, str) and source.isdigit() and int(source) in graph.nodes else source
    )

    while curr != src_key:
        pred_entry = predecessors[curr]
        if isinstance(pred_entry, tuple):
            prev_node, edge_key = pred_entry
            station_path_rev.append(str(prev_node))
            edge_keys_rev.append(edge_key)
            curr = prev_node
        else:
            prev_node = pred_entry
            station_path_rev.append(str(prev_node))
            edge_keys_rev.append(None)  # BFS will choose deterministic edge
            curr = prev_node

    station_path = list(reversed(station_path_rev))
    edge_keys = list(reversed(edge_keys_rev))

    # Raw node sequence for edge lookup in graph
    raw_nodes = []
    curr_raw = dest_key
    raw_nodes.append(curr_raw)
    while curr_raw != src_key:
        p = predecessors[curr_raw]
        curr_raw = p[0] if isinstance(p, tuple) else p
        raw_nodes.append(curr_raw)
    raw_nodes = list(reversed(raw_nodes))

    # 4. Construct Segments & Validate Exact Multi-Edges
    segments: List[RouteSegment] = []
    edge_path: List[Tuple[str, str, str]] = []
    total_dist = 0.0
    total_time = 0.0

    for i in range(len(raw_nodes) - 1):
        u_raw = raw_nodes[i]
        v_raw = raw_nodes[i + 1]
        u_str = station_path[i]
        v_str = station_path[i + 1]
        explicit_key = edge_keys[i]

        if explicit_key is not None:
            # Dijkstra exact edge key
            edge_data = graph.get_edge_data(u_raw, v_raw, explicit_key)
            if edge_data is None:
                # Try symmetric lookup
                edge_data = graph.get_edge_data(v_raw, u_raw, explicit_key)
            chosen_key = str(explicit_key)
            attrs = edge_data if edge_data is not None else {}
        else:
            # BFS tie-breaking edge selection
            chosen_key, attrs = choose_best_parallel_edge(graph, u_raw, v_raw, preference=objective)

        dist = float(attrs.get("distance_km", 0.0))
        time_min = float(attrs.get("estimated_time_min", 0.0))
        lid = str(attrs.get("line_id", "Unknown"))
        lname = str(attrs.get("line_name", lid))
        lcolor = str(attrs.get("line_color", "#94A3B8"))
        prov = str(attrs.get("weight_provenance", "published"))

        total_dist += dist
        total_time += time_min

        seg = RouteSegment(
            source_station_id=u_str,
            destination_station_id=v_str,
            edge_key=chosen_key,
            line_id=lid,
            line_name=lname,
            line_color=lcolor,
            distance_km=round(dist, 3),
            estimated_time_min=round(time_min, 2),
            weight_provenance=prov,
        )
        segments.append(seg)
        edge_path.append((u_str, v_str, chosen_key))

    total_stops = len(station_path) - 1

    # Transfer calculations for BFS and standard Dijkstra
    line_seq = [s.line_id for s in segments]
    transfers = 0
    if len(line_seq) > 1:
        for k in range(1, len(line_seq)):
            if line_seq[k] != line_seq[k - 1]:
                transfers += 1

    transfer_stations = []
    for k in range(1, len(segments)):
        if segments[k].line_id != segments[k - 1].line_id:
            transfer_stations.append(segments[k].source_station_id)

    from src.algorithms.transfer_utils import build_transfer_instructions

    station_names = {str(n): graph.nodes[n].get("station_name", str(n)) for n in graph.nodes}
    instructions = build_transfer_instructions(station_path, segments, station_names)

    return RouteResult(
        source_station_id=str(source),
        destination_station_id=str(destination),
        algorithm=algorithm,
        objective=objective,
        station_path=station_path,
        edge_path=edge_path,
        segments=segments,
        total_stops=total_stops,
        total_distance_km=round(total_dist, 3),
        total_estimated_time_min=round(total_time, 2),
        explored_nodes=explored_nodes,
        examined_edges=examined_edges,
        runtime_ms=round(runtime_ms, 3),
        reachable=True,
        message="Route successfully computed.",
        transfer_count=transfers,
        transfer_stations=transfer_stations,
        line_sequence=line_seq,
        transfer_penalty_min=0.0,
        segment_travel_time_min=round(total_time, 2),
        total_transfer_penalty_min=0.0,
        total_modeled_journey_time_min=round(total_time, 2),
        optimization_objective=objective,
        transfer_instructions=instructions,
    )


def validate_route(graph: nx.MultiGraph, result: RouteResult) -> bool:
    """Validates structural and numeric integrity of a calculated RouteResult."""
    if not result.reachable:
        return True

    if result.total_stops == 0:
        return result.source_station_id == result.destination_station_id

    if len(result.station_path) != result.total_stops + 1:
        raise RouteValidationError(
            f"Station path length {len(result.station_path)} does not match stops + 1 ({result.total_stops + 1})."
        )

    if len(result.segments) != result.total_stops:
        raise RouteValidationError(
            f"Segment count {len(result.segments)} does not match stops ({result.total_stops})."
        )

    def graph_has(n):
        if graph.has_node(n):
            return True
        if isinstance(n, str) and n.isdigit() and graph.has_node(int(n)):
            return True
        if graph.has_node(str(n)):
            return True
        return False

    for seg in result.segments:
        if not graph_has(seg.source_station_id):
            raise RouteValidationError(f"Segment source station '{seg.source_station_id}' not in graph.")
        if not graph_has(seg.destination_station_id):
            raise RouteValidationError(f"Segment destination station '{seg.destination_station_id}' not in graph.")

        def resolve_raw(n):
            if graph.has_node(n):
                return n
            if isinstance(n, str) and n.isdigit() and graph.has_node(int(n)):
                return int(n)
            if graph.has_node(str(n)):
                return str(n)
            return n

        u_check = resolve_raw(seg.source_station_id)
        v_check = resolve_raw(seg.destination_station_id)

        edge_data = graph.get_edge_data(u_check, v_check, seg.edge_key)
        if edge_data is None:
            edge_data = graph.get_edge_data(v_check, u_check, seg.edge_key)
        if edge_data is None:
            raise RouteValidationError(
                f"Multi-edge ({seg.source_station_id}, {seg.destination_station_id}, key={seg.edge_key}) not in graph."
            )

    return True
