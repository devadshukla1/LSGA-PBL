"""Betweenness centrality calculation and shortest-path load analytics."""

from typing import Dict, Optional

import networkx as nx


def compute_betweenness_centrality(
    graph: nx.Graph,
    weighted: bool = False,
    weight_attribute: str = "estimated_time_min",
    normalized: bool = True,
) -> Dict[str, float]:
    """Computes betweenness centrality for all nodes in the simple analysis graph.

    Definition:
        C_B(v) = sum_{s != v != t} (sigma_{st}(v) / sigma_{st})
    where sigma_{st} is the total number of shortest paths between s and t,
    and sigma_{st}(v) is the number of those shortest paths passing through v.

    Normalization:
        For undirected graphs, normalized by 2 / ((N - 1)(N - 2)) for N > 2.
        For N <= 2, betweenness centrality is 0.0.

    Modes:
        - Unweighted (default): Shortest hop distance between stations.
        - Weighted: Shortest estimated travel time along minimum-weight projected edges.

    Args:
        graph: Simple undirected NetworkX Graph.
        weighted: Whether to weight shortest paths by an edge weight.
        weight_attribute: Edge attribute for weighted betweenness.
        normalized: Whether to normalize centrality values.

    Returns:
        Dictionary mapping station_id -> betweenness centrality float.
    """
    n = graph.number_of_nodes()
    if n <= 2:
        return {str(node): 0.0 for node in graph.nodes}

    weight_key: Optional[str] = weight_attribute if weighted else None

    # NetworkX Brandes algorithm implementation
    bc_dict = nx.betweenness_centrality(
        graph,
        weight=weight_key,
        normalized=normalized,
        endpoints=False,
    )

    return {str(node): round(float(val), 6) for node, val in bc_dict.items()}
