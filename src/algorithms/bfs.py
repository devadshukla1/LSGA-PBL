"""FIFO traversal over directed roads."""

from collections import deque

from src.algorithms.traversal_models import Node, TraversalResult, prepare, result


def bfs(graph_or_adjacency, start_node: Node) -> TraversalResult:
    """Visit every reachable node and record its minimum hop distance."""
    if start_node not in graph_or_adjacency:
        raise ValueError("Unknown start node")
    roads = prepare(graph_or_adjacency)
    queue = deque([start_node])
    parents = {start_node: None}
    depth = {start_node: 0}
    edges = []
    examined = 0
    while queue:
        u = queue.popleft()
        for v, key in roads[u]:
            examined += 1
            if v not in parents:
                parents[v] = u
                depth[v] = depth[u] + 1
                edges.append((u, v, key))
                queue.append(v)
    return result("BFS", start_node, parents, depth, (), edges, examined)
