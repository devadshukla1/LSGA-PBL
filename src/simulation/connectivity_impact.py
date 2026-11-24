"""Connectivity and pairwise reachability metrics evaluation."""

from typing import Dict, List

import networkx as nx

from src.simulation.models import ConnectivityMetrics


def compute_connectivity_metrics(graph: nx.MultiGraph) -> ConnectivityMetrics:
    """Computes comprehensive topological connectivity and pairwise reachability metrics.

    Reachability Metric Formula:
    For an undirected graph decomposed into disjoint connected components C_1, C_2, ..., C_k
    where component i has size n_i:
        Reachable Pairs = sum_{i=1}^k (n_i * (n_i - 1) / 2)

    Total Possible Pairs among remaining stations N:
        Possible Pairs = N * (N - 1) / 2

    Reachability Ratio = Reachable Pairs / Possible Pairs (or 1.0 for N <= 1).

    Time Complexity:
        O(V + E) using BFS/DFS component exploration via NetworkX.
        O(C) component aggregation for reachable pairs where C <= V.
    """
    station_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()

    if station_count == 0:
        return ConnectivityMetrics(
            station_count=0,
            edge_count=0,
            connected_components=0,
            is_connected=True,
            largest_component_size=0,
            smallest_component_size=0,
            isolated_stations_count=0,
            isolated_stations=[],
            component_sizes=[],
            station_to_component={},
            reachable_station_pairs=0,
            possible_station_pairs=0,
            reachability_ratio=0.0,
        )

    # Use NetworkX connected_components on the undirected graph
    components = list(nx.connected_components(graph))
    components.sort(key=len, reverse=True)

    station_to_comp: Dict[str, int] = {}
    component_sizes: List[int] = []
    reachable_pairs = 0

    for comp_idx, comp_nodes in enumerate(components, start=1):
        c_len = len(comp_nodes)
        component_sizes.append(c_len)
        reachable_pairs += (c_len * (c_len - 1)) // 2
        for node in comp_nodes:
            station_to_comp[str(node)] = comp_idx

    # Isolated stations have degree 0 in the remaining graph
    isolated_stations = [str(node) for node, deg in graph.degree() if deg == 0]

    possible_pairs = (station_count * (station_count - 1)) // 2
    if possible_pairs > 0:
        reachability_ratio = round(float(reachable_pairs) / float(possible_pairs), 5)
    else:
        reachability_ratio = 1.0 if station_count == 1 else 0.0

    return ConnectivityMetrics(
        station_count=station_count,
        edge_count=edge_count,
        connected_components=len(components),
        is_connected=len(components) == 1,
        largest_component_size=component_sizes[0] if component_sizes else 0,
        smallest_component_size=component_sizes[-1] if component_sizes else 0,
        isolated_stations_count=len(isolated_stations),
        isolated_stations=isolated_stations,
        component_sizes=component_sizes,
        station_to_component=station_to_comp,
        reachable_station_pairs=reachable_pairs,
        possible_station_pairs=possible_pairs,
        reachability_ratio=reachability_ratio,
    )
