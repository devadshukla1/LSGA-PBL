"""Shared manual priority-queue relaxation used by Dijkstra and A*."""

import heapq
import math
from collections.abc import Mapping
from itertools import count

import networkx as nx

from src.algorithms.heuristics import safe_heuristic
from src.algorithms.path_reconstruction import reconstruct_route
from src.algorithms.routing_models import RouteResult, RoutingDiagnostics
from src.algorithms.routing_tiebreak import signature
from src.graph.representation import build_adjacency


def search(graph_or_adjacency, source, target, objective: str, algorithm: str) -> RouteResult:
    """Run directed edge relaxation and retain each winning predecessor key."""
    if objective not in {"distance", "travel_time"}:
        raise ValueError("Unknown routing objective")
    if source not in graph_or_adjacency or target not in graph_or_adjacency:
        raise ValueError("Unknown source or destination")
    if isinstance(graph_or_adjacency, nx.MultiDiGraph):
        graph = graph_or_adjacency
        adjacency = build_adjacency(graph)
    elif isinstance(graph_or_adjacency, Mapping):
        graph = None
        adjacency = graph_or_adjacency
    else:
        raise TypeError("Expected a MultiDiGraph or adjacency mapping")
    field = "length_m" if objective == "distance" else "travel_time_s"
    for edges in adjacency.values():
        for edge in edges:
            for value in (edge.length_m, edge.travel_time_s):
                if not isinstance(value, int | float) or not math.isfinite(value) or value < 0:
                    raise ValueError("Routing weights must be finite and nonnegative")
    if algorithm == "astar" and graph is not None:
        heuristic, kind, fallback = safe_heuristic(graph, target, objective)
    else:
        heuristic, kind, fallback = lambda node: 0.0, "zero", algorithm == "astar"
    serial = count()
    heap = [(heuristic(source), 0.0, next(serial), source)]
    best = {source: 0.0}
    predecessors = {}
    expanded = examined = 0
    while heap:
        _, cost, _, u = heapq.heappop(heap)
        if cost > best[u]:
            continue
        expanded += 1
        if u == target:
            break
        for edge in sorted(
            adjacency[u],
            key=lambda edge: signature(((edge.source_node, edge.target_node, edge.edge_key),)),
        ):
            examined += 1
            v = edge.target_node
            candidate = cost + getattr(edge, field)
            if not math.isfinite(candidate):
                raise ValueError("Accumulated route cost is nonfinite")
            if candidate < best.get(v, math.inf):
                best[v] = candidate
                predecessors[v] = (u, edge.edge_key)
                heapq.heappush(heap, (candidate + heuristic(v), candidate, next(serial), v))
    nodes, edges = reconstruct_route(source, target, predecessors)
    reachable = bool(nodes)
    if reachable:
        lookup = {
            (edge.source_node, edge.target_node, edge.edge_key): edge
            for outgoing in adjacency.values()
            for edge in outgoing
        }
        distance = sum(lookup[edge].length_m for edge in edges)
        duration = sum(lookup[edge].travel_time_s for edge in edges)
        total = distance if objective == "distance" else duration
    else:
        distance = duration = total = None
    return RouteResult(
        algorithm,
        objective,
        source,
        target,
        reachable,
        nodes,
        edges,
        distance,
        duration,
        total,
        expanded,
        examined,
        "ok" if reachable else "unreachable",
        "Route found" if reachable else "Destination is unreachable",
        RoutingDiagnostics(kind, True, fallback, "pending"),
    )
