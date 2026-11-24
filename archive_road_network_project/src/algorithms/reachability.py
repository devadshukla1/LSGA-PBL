"""Directed hop-minimal paths from BFS parent links."""

from collections.abc import Mapping

from src.algorithms.bfs import bfs
from src.algorithms.traversal_models import Node, ReachabilityResult, TraversalResult


def reconstruct_path(source: Node, target: Node, parent: Mapping) -> tuple:
    if target not in parent:
        return ()
    path = []
    seen = set()
    node = target
    while node != source:
        if node in seen or node not in parent:
            raise ValueError("Incomplete or cyclic parent chain")
        seen.add(node)
        path.append(node)
        node = parent[node]
    if source not in parent:
        raise ValueError("Missing source in parent chain")
    return (source, *reversed(path))


def from_bfs(traversal: TraversalResult, target: Node) -> ReachabilityResult:
    if traversal.algorithm != "BFS":
        raise ValueError("Hop-minimal paths require a BFS tree")
    path = reconstruct_path(traversal.start_node, target, traversal.parent)
    return ReachabilityResult(
        traversal.start_node,
        target,
        bool(path),
        path,
        len(path) - 1 if path else None,
        traversal.nodes_visited,
    )


def find_unweighted_path(graph, source: Node, target: Node) -> ReachabilityResult:
    if target not in graph:
        raise ValueError("Unknown target node")
    return from_bfs(bfs(graph, source), target)


def is_reachable(graph, source: Node, target: Node) -> bool:
    return find_unweighted_path(graph, source, target).is_reachable


def find_reachable_nodes(graph, source: Node) -> frozenset:
    return bfs(graph, source).visited_nodes


def count_reachable_nodes(graph, source: Node) -> int:
    return bfs(graph, source).reachable_count
