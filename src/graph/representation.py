"""Read-only representations of directed keyed roads."""

from collections.abc import Hashable, Sequence

import networkx as nx
import numpy as np

from src.graph.models import RoadEdge


def build_adjacency(graph: nx.MultiDiGraph) -> dict:
    adjacency = {n: [] for n in graph}
    for u, v, k, d in graph.edges(keys=True, data=True):
        adjacency[u].append(
            RoadEdge(
                u,
                v,
                k,
                d["length_m"],
                d["speed_kph"],
                d["travel_time_s"],
                d.get("highway", "unknown"),
                d.get("oneway"),
                d.get("geometry"),
            )
        )
    return adjacency


def outgoing(adjacency: dict, node: Hashable) -> list:
    return adjacency[node]


def incoming(adjacency: dict, node: Hashable) -> list:
    return [edge for edges in adjacency.values() for edge in edges if edge.target_node == node]


def entry_count(adjacency: dict) -> int:
    return sum(map(len, adjacency.values()))


def consistent(graph: nx.MultiDiGraph, adjacency: dict) -> bool:
    return adjacency == build_adjacency(graph)


def adjacency_matrix(
    graph: nx.MultiDiGraph, nodes: Sequence, objective: str = "length_m", limit: int = 100
) -> np.ndarray:
    """Minimum parallel-edge cost in explicit node order, zero diagonal."""
    if len(nodes) > limit or len(set(nodes)) != len(nodes) or not all(n in graph for n in nodes):
        raise ValueError(f"Select unique existing nodes, at most {limit}")
    if objective not in {"length_m", "travel_time_s"}:
        raise ValueError("Unknown weight objective")
    matrix = np.full((len(nodes), len(nodes)), np.inf)
    np.fill_diagonal(matrix, 0)
    indices = {n: i for i, n in enumerate(nodes)}
    for u, v, d in graph.subgraph(nodes).edges(data=True):
        i, j = indices[u], indices[v]
        matrix[i, j] = min(matrix[i, j], d[objective])
    return matrix
