"""Iterative depth-first traversal with explicit child iterators."""

from src.algorithms.traversal_models import Node, TraversalResult, prepare, result


def dfs(graph_or_adjacency, start_node: Node) -> TraversalResult:
    """Record discovery and true finish order for the reachable DFS tree."""
    if start_node not in graph_or_adjacency:
        raise ValueError("Unknown start node")
    roads = prepare(graph_or_adjacency)
    stack = [(start_node, iter(roads[start_node]))]
    parents = {start_node: None}
    depth = {start_node: 0}
    finish = []
    edges = []
    examined = 0
    while stack:
        u, children = stack[-1]
        for v, key in children:
            examined += 1
            if v not in parents:
                parents[v] = u
                depth[v] = depth[u] + 1
                edges.append((u, v, key))
                stack.append((v, iter(roads[v])))
                break
        else:
            finish.append(u)
            stack.pop()
    return result("DFS", start_node, parents, depth, finish, edges, examined)
