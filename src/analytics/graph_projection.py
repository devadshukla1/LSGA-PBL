"""Analytical graph projection utility.

Transforms a physical multi-line transit MultiGraph into a simple undirected Graph
for unambiguous structural centrality, connectivity, and articulation point analysis.
"""

import networkx as nx


def build_analysis_graph(multi_graph: nx.MultiGraph) -> nx.Graph:
    """Projects a transit MultiGraph into a simple undirected Graph (V, E_simple).

    Why a simple Graph is required for structural centrality:
    1. In unweighted topological network analysis, degree centrality measures the number
       of distinct neighboring stations a station connects to directly. Counting parallel
       services as multiple neighbors artificially inflates a station's degree when two
       corridors share identical tracks.
    2. Betweenness centrality on a simple graph measures the fraction of shortest-hop
       paths passing through station v. Multiple parallel edges between the same two stations
       would generate redundant parallel shortest paths that distort betweenness values.
    3. Articulation point detection (Tarjan's DFS algorithm) operates on simple connected
       adjacencies. Parallel edges between the same pair of stations do not alter articulation
       properties.

    Projection Policy:
    - Node attributes (station_name, lat, lon, lines, is_interchange) are preserved.
    - Exactly one undirected edge (u, v) is created for each adjacent station pair.
    - Edge attributes:
      - 'distance_km': Minimum distance across parallel services.
      - 'estimated_time_min': Minimum estimated travel time across parallel services.
      - 'lines': Set of all line IDs connecting u and v.
      - 'parallel_service_count': Integer count of physical services between u and v.

    Args:
        multi_graph: The original transit NetworkX MultiGraph.

    Returns:
        A separate NetworkX Graph instance. Does NOT mutate the input MultiGraph.
    """
    g_simple = nx.Graph()

    # 1. Copy nodes with all attributes
    for node, data in multi_graph.nodes(data=True):
        g_simple.add_node(node, **data.copy())

    # 2. Collapse multi-edges into single undirected edges
    for u, v, _key, data in multi_graph.edges(keys=True, data=True):
        dist = float(data.get("distance_km", 0.0))
        time_min = float(data.get("estimated_time_min", 0.0))
        line_id = str(data.get("line_id", "Unknown"))

        if g_simple.has_edge(u, v):
            # Update existing edge with minimum valid weights and accumulate lines
            edge_data = g_simple[u][v]
            edge_data["parallel_service_count"] += 1
            edge_data["lines"].add(line_id)

            if dist > 0 and (edge_data["distance_km"] <= 0 or dist < edge_data["distance_km"]):
                edge_data["distance_km"] = dist
            if time_min > 0 and (edge_data["estimated_time_min"] <= 0 or time_min < edge_data["estimated_time_min"]):
                edge_data["estimated_time_min"] = time_min
        else:
            g_simple.add_edge(
                u,
                v,
                distance_km=dist,
                estimated_time_min=time_min,
                lines={line_id},
                parallel_service_count=1,
            )

    return g_simple
