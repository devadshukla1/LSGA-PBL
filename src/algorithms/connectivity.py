"""Weak component floods and iterative two-pass Kosaraju."""

from types import MappingProxyType

from src.algorithms.traversal_models import ConnectivityResult, prepare


def _groups(neighbors, order, kind) -> ConnectivityResult:
    membership = {}
    components = []
    for root in order:
        if root in membership:
            continue
        index = len(components)
        stack = [root]
        membership[root] = index
        group = set()
        while stack:
            u = stack.pop()
            group.add(u)
            for v in neighbors[u]:
                if v not in membership:
                    membership[v] = index
                    stack.append(v)
        components.append(frozenset(group))
    return ConnectivityResult(
        kind,
        len(components),
        tuple(components),
        MappingProxyType(membership),
        max(map(len, components), default=0),
    )


def weak_components(graph) -> ConnectivityResult:
    roads = prepare(graph)
    neighbors = {n: [] for n in roads}
    for u, edges in roads.items():
        for v, _ in edges:
            neighbors[u].append(v)
            neighbors[v].append(u)
    return _groups(neighbors, roads, "weak")


def strong_components(graph) -> ConnectivityResult:
    roads = prepare(graph)
    reverse = {n: [] for n in roads}
    seen = set()
    finished = []
    for root in roads:
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, iter(roads[root]))]
        while stack:
            u, children = stack[-1]
            for v, _ in children:
                reverse[v].append(u)
                if v not in seen:
                    seen.add(v)
                    stack.append((v, iter(roads[v])))
                    break
            else:
                finished.append(u)
                stack.pop()
    return _groups(reverse, reversed(finished), "strong")
