"""Articulation point detection and topological cut-vertex analysis."""

from typing import Dict, Optional, Set

import networkx as nx


def find_articulation_points(graph: nx.Graph) -> Set[str]:
    """Detects articulation points (cut vertices) in the simple analytical graph.

    Definition:
        A vertex v is an articulation point if removing v and its incident edges
        strictly increases the number of connected components in the graph.

    Algorithm:
        Uses Tarjan's DFS-based articulation point algorithm via NetworkX.
        Time Complexity: O(V + E) on the simple analysis graph.

    Args:
        graph: Simple undirected NetworkX Graph.

    Returns:
        Set of station_id strings identifying articulation points.
    """
    if graph.number_of_nodes() <= 2:
        return set()

    ap_nodes = nx.articulation_points(graph)
    return {str(node) for node in ap_nodes}


def analyze_articulation_points(
    graph: nx.Graph,
    betweenness_dict: Optional[Dict[str, float]] = None,
) -> Dict[str, any]:
    """Analyzes all articulation points with structural attributes and betweenness.

    Distinguishes articulation points from high-betweenness stations:
    - An articulation point is structurally critical for graph connectivity.
    - A station can have high betweenness without being an articulation point
      (e.g. in dense mesh-like grid cycles).
    """
    ap_set = find_articulation_points(graph)
    betweenness_dict = betweenness_dict or {}

    records = []
    for sid in sorted(ap_set):
        s_data = graph.nodes[sid] if sid in graph.nodes else {}
        name = s_data.get("station_name", sid)
        deg = graph.degree[sid] if sid in graph.nodes else 0
        bc = betweenness_dict.get(sid, 0.0)
        is_inter = s_data.get("is_interchange", False)

        records.append({
            "station_id": sid,
            "station_name": name,
            "degree": deg,
            "betweenness_centrality": bc,
            "is_interchange": is_inter,
        })

    return {
        "articulation_point_count": len(ap_set),
        "articulation_points": ap_set,
        "details": records,
    }
