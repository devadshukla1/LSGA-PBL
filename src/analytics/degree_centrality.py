"""Degree centrality calculation and neighbor connectivity analysis."""

from typing import Dict

import networkx as nx


def compute_degree_centrality(graph: nx.Graph) -> Dict[str, float]:
    """Computes normalized degree centrality for all nodes in the simple analysis graph.

    Definition:
        C_D(v) = degree(v) / (N - 1)
    where:
        degree(v) = number of distinct adjacent stations connected to v.
        N = total stations in the graph.

    Edge Cases:
        - If N <= 1, degree centrality is defined as 0.0 for all nodes.

    Args:
        graph: Simple undirected NetworkX Graph.

    Returns:
        Dictionary mapping station_id -> normalized degree centrality float in [0.0, 1.0].
    """
    n = graph.number_of_nodes()
    if n <= 1:
        return {str(node): 0.0 for node in graph.nodes}

    # Use NetworkX degree_centrality as oracle
    raw_dc = nx.degree_centrality(graph)
    return {str(node): round(float(val), 6) for node, val in raw_dc.items()}


def compute_station_degrees(graph: nx.Graph) -> Dict[str, int]:
    """Returns the unnormalized integer degree (distinct neighbor count) for each station."""
    return {str(node): int(deg) for node, deg in graph.degree()}
