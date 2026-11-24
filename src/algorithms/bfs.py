"""Breadth-First Search (BFS) minimum-stop routing algorithm for metro networks."""

import time
from collections import deque
from typing import Any, Dict

import networkx as nx

from src.algorithms.route_utils import reconstruct_route, validate_route
from src.algorithms.routing_models import RouteResult
from src.core.exceptions import MetroGraphError


class BFSExecutionError(MetroGraphError):
    """Raised when BFS graph traversal cannot be completed."""

    pass


def find_route_bfs(
    graph: nx.MultiGraph,
    source: str,
    destination: str,
) -> RouteResult:
    """Computes the route minimizing total station-to-station stops (unweighted shortest path).

    Algorithm Details:
    - Pure manual implementation using `collections.deque`.
    - Explores graph level-by-level starting from the source station.
    - Guarantees minimum number of segments/stops: |station_path| - 1.
    - Stops exploration immediately once the destination node is settled.
    - Tie-breaks parallel multi-edges deterministically via `choose_best_parallel_edge`.
    - Measures runtime strictly using `time.perf_counter_ns()`.

    Time Complexity:
        O(|V| + |E|) where |E| counts all parallel multi-edges.
    Space Complexity:
        O(|V|) for queue, visited set, and predecessor lookup.

    Raises:
        BFSExecutionError: If source or destination nodes do not exist in graph.
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
        raise BFSExecutionError(f"Source station '{source}' does not exist in graph.")
    if not graph.has_node(dest_node):
        raise BFSExecutionError(f"Destination station '{dest_node}' does not exist in graph.")

    start_time_ns = time.perf_counter_ns()

    # Fast-path for source == destination
    if source_node == dest_node:
        end_time_ns = time.perf_counter_ns()
        runtime_ms = (end_time_ns - start_time_ns) / 1_000_000.0
        return reconstruct_route(
            graph=graph,
            source=str(source_node),
            destination=str(dest_node),
            algorithm="BFS",
            objective="minimum_stops",
            predecessors={},
            explored_nodes=1,
            examined_edges=0,
            runtime_ms=runtime_ms,
        )

    queue = deque([source_node])
    visited = {source_node}
    predecessors: Dict[Any, Any] = {}
    explored_nodes = 0
    examined_edges = 0
    destination_found = False

    while queue:
        curr = queue.popleft()
        explored_nodes += 1

        if curr == dest_node:
            destination_found = True
            break

        # Deterministic neighbor expansion
        # Sort neighbors for deterministic traversal ordering across platforms
        neighbors = sorted(list(graph.adj[curr].keys()), key=str)

        for neighbor in neighbors:
            # Count parallel edges examined
            edges_between = graph.adj[curr][neighbor]
            examined_edges += len(edges_between)

            if neighbor not in visited:
                visited.add(neighbor)
                predecessors[neighbor] = curr
                queue.append(neighbor)
                if neighbor == dest_node:
                    destination_found = True
                    break

        if destination_found:
            break

    end_time_ns = time.perf_counter_ns()
    runtime_ms = (end_time_ns - start_time_ns) / 1_000_000.0

    result = reconstruct_route(
        graph=graph,
        source=str(source_node),
        destination=str(dest_node),
        algorithm="BFS",
        objective="minimum_stops",
        predecessors=predecessors,
        explored_nodes=explored_nodes,
        examined_edges=examined_edges,
        runtime_ms=runtime_ms,
    )
    validate_route(graph, result)
    return result
