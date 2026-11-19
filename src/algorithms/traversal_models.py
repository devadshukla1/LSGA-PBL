"""Shared ordered topology and traversal results."""

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

import networkx as nx

Node = Hashable
Edge = tuple[Node, Node, Hashable]


class OrderedRoads(dict):
    """Prepared outgoing (target, key) lists shared within one analysis."""


def canonical(value: Hashable) -> tuple:
    """Order scalar IDs naturally within type and tuple IDs recursively."""
    if isinstance(value, tuple):
        return ("tuple", tuple(map(canonical, value)))
    if type(value) in (int, str, bool, bytes, float):
        return (type(value).__name__, value)
    raise TypeError("Traversal identifiers must be scalar values or tuples of scalars")


def prepare(graph: nx.MultiDiGraph | Mapping) -> OrderedRoads:
    if isinstance(graph, OrderedRoads):
        return graph
    roads = OrderedRoads()
    for n in sorted(graph, key=canonical):
        if isinstance(graph, nx.MultiDiGraph):
            pairs = ((v, k) for _, v, k in graph.out_edges(n, keys=True))
        else:
            pairs = ((e.target_node, e.edge_key) for e in graph[n])
        roads[n] = tuple(sorted(pairs, key=lambda p: (canonical(p[0]), canonical(p[1]))))
    return roads


@dataclass(frozen=True)
class TraversalResult:
    algorithm: str
    start_node: Node
    visit_order: tuple
    visited_nodes: frozenset
    parent: Mapping
    depth: Mapping
    finish_order: tuple
    tree_edges: tuple[Edge, ...]
    edges_examined: int

    discovery_order = property(lambda self: self.visit_order)
    nodes_visited = property(lambda self: len(self.visit_order))
    reachable_count = property(lambda self: self.nodes_visited)


def result(name, start, parents, depth, finish, edges, count) -> TraversalResult:
    return TraversalResult(
        name,
        start,
        tuple(parents),
        frozenset(parents),
        MappingProxyType(parents),
        MappingProxyType(depth),
        tuple(finish),
        tuple(edges),
        count,
    )


@dataclass(frozen=True)
class ReachabilityResult:
    source: Node
    target: Node
    is_reachable: bool
    path: tuple
    hop_count: int | None
    explored_nodes: int


@dataclass(frozen=True)
class ConnectivityResult:
    component_type: str
    component_count: int
    components: tuple[frozenset, ...]
    node_to_component: Mapping
    largest_component_size: int
