"""Explicit minimum-edge undirected projection and spanning forest."""

import math

import networkx as nx

from src.algorithms.routing_tiebreak import signature
from src.analytics.analytics_models import MSTResult


def undirected_projection(graph, weight="length_m"):
    if weight not in ("length_m", "travel_time_s"):
        raise ValueError("Invalid forest weight")
    projected = nx.Graph()
    projected.add_nodes_from(graph.nodes(data=True))
    for u, v, k, data in sorted(
        graph.edges(keys=True, data=True), key=lambda e: signature((e[:3],))
    ):
        value = data.get(weight)
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError("Forest weights must be finite and nonnegative")
        if u != v and (not projected.has_edge(u, v) or value < projected.edges[u, v]["weight"]):
            projected.add_edge(u, v, weight=value, original_edge=(u, v, k))
    return projected


def minimum_spanning_forest(graph, weight="length_m") -> MSTResult:
    projection = undirected_projection(graph, weight)
    forest = nx.minimum_spanning_tree(projection, weight="weight")
    components = nx.number_connected_components(projection)
    edges = tuple(data["original_edge"] for _, _, data in forest.edges(data=True))
    return MSTResult(
        "minimum directed edge per unordered pair; ignores one-way restrictions",
        weight,
        len(graph),
        projection.number_of_edges(),
        components,
        len(edges),
        sum(d["weight"] for _, _, d in forest.edges(data=True)),
        components == 1,
        edges,
    )
