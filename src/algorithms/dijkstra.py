"""Dijkstra shortest-path routing algorithm for weighted metro networks."""

import heapq
import math
import time
from typing import Any, Dict, Tuple

import networkx as nx

from src.algorithms.route_utils import reconstruct_route, validate_route
from src.algorithms.routing_models import RouteResult
from src.core.exceptions import MetroGraphError


class DijkstraExecutionError(MetroGraphError):
    """Raised when Dijkstra routing fails due to invalid parameters or graph state."""

    pass


def find_route_dijkstra(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
    objective: str = "minimum_time",
) -> RouteResult:
    """Computes the shortest path using Dijkstra's algorithm with a binary min-heap.

    Supports two optimization objectives:
    - 'minimum_time': Minimizes total cumulative `estimated_time_min`.
    - 'minimum_distance': Minimizes total cumulative `distance_km`.

    Algorithm Details:
    - Pure manual implementation using `heapq`.
    - Handles MultiGraph parallel edges natively without collapsing the graph.
    - Uses monotonically increasing entry counter in the heap to guarantee safe,
      deterministic tie-breaking across heterogeneous node types.
    - Rejects negative, NaN, or non-finite weights.
    - Tracks exact predecessor tuple: (predecessor_node, edge_key).
    - Early exit when destination node is popped (settled) from priority queue.

    Time Complexity:
        O((|V| + |E|) log |V|) where |E| counts all parallel multi-edges.
    Space Complexity:
        O(|V| + |E|) for distances, predecessors, and heap frontier.

    Raises:
        DijkstraExecutionError: If source/destination invalid or weights corrupt.
    """
    # Resolve station nodes: check direct match, integer conversion, or string conversion
    def resolve_node(n):
        if graph.has_node(n):
            return n
        if isinstance(n, str) and n.isdigit() and graph.has_node(int(n)):
            return int(n)
        if graph.has_node(str(n)):
            return str(n)
        return n

    source_node = resolve_node(source)
    dest_node = resolve_node(destination)

    if not graph.has_node(source_node):
        raise DijkstraExecutionError(f"Source station '{source}' does not exist in graph.")
    if not graph.has_node(dest_node):
        raise DijkstraExecutionError(f"Destination station '{dest_node}' does not exist in graph.")

    if objective not in ("minimum_time", "minimum_distance"):
        raise DijkstraExecutionError(
            f"Unsupported objective '{objective}'. Choose 'minimum_time' or 'minimum_distance'."
        )

    weight_attr = "estimated_time_min" if objective == "minimum_time" else "distance_km"

    start_time_ns = time.perf_counter_ns()

    # Fast-path for source == destination
    if source_node == dest_node:
        end_time_ns = time.perf_counter_ns()
        runtime_ms = (end_time_ns - start_time_ns) / 1_000_000.0
        return reconstruct_route(
            graph=graph,
            source=str(source_node),
            destination=str(dest_node),
            algorithm="Dijkstra",
            objective=objective,
            predecessors={},
            explored_nodes=1,
            examined_edges=0,
            runtime_ms=runtime_ms,
        )

    # Priority queue items: (distance, tie_breaker_counter, node_id)
    pq = []
    entry_counter = 0

    distances: Dict[Any, float] = {source_node: 0.0}
    # Predecessors map: node -> (parent_node, edge_key)
    predecessors: Dict[Any, Tuple[Any, str]] = {}
    settled = set()

    heapq.heappush(pq, (0.0, entry_counter, source_node))
    explored_nodes = 0
    examined_edges = 0

    while pq:
        curr_dist, _, u = heapq.heappop(pq)

        if u in settled:
            continue
        settled.add(u)
        explored_nodes += 1

        if u == dest_node:
            break

        # If current distance exceeds known optimal, skip
        if curr_dist > distances.get(u, float("inf")):
            continue

        # Sort neighbors for deterministic expansion
        neighbors = sorted(list(graph.adj[u].keys()), key=str)

        for v in neighbors:
            if v in settled:
                continue

            # Iterate through all multi-edges between u and v
            edges_between = graph.adj[u][v]
            examined_edges += len(edges_between)

            for key, attrs in edges_between.items():
                if weight_attr not in attrs:
                    raise DijkstraExecutionError(
                        f"Edge ({u}, {v}, key={key}) missing required weight attribute '{weight_attr}'."
                    )

                w = attrs[weight_attr]
                if w is None or not isinstance(w, (int, float)) or math.isnan(w) or w < 0:
                    raise DijkstraExecutionError(
                        f"Edge ({u}, {v}, key={key}) contains invalid non-positive or NaN weight: {w}."
                    )

                new_dist = curr_dist + float(w)

                if new_dist < distances.get(v, float("inf")):
                    distances[v] = new_dist
                    predecessors[v] = (u, str(key))
                    entry_counter += 1
                    heapq.heappush(pq, (new_dist, entry_counter, v))

    end_time_ns = time.perf_counter_ns()
    runtime_ms = (end_time_ns - start_time_ns) / 1_000_000.0

    result = reconstruct_route(
        graph=graph,
        source=str(source_node),
        destination=str(dest_node),
        algorithm="Dijkstra",
        objective=objective,
        predecessors=predecessors,
        explored_nodes=explored_nodes,
        examined_edges=examined_edges,
        runtime_ms=runtime_ms,
    )
    validate_route(graph, result)
    return result
