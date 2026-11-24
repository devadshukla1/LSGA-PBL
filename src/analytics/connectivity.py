"""Network connectivity analysis and connected components statistics."""

from typing import Dict, List

import networkx as nx


def analyze_network_connectivity(graph: nx.Graph) -> Dict[str, any]:
    """Computes global connectivity metrics and component decomposition.

    Metrics:
    - Number of connected components.
    - Component size distribution (largest, smallest).
    - Isolated stations (degree 0).
    - Component membership mapping per station.
    """
    n = graph.number_of_nodes()
    if n == 0:
        return {
            "connected_components_count": 0,
            "is_connected": True,
            "largest_component_size": 0,
            "smallest_component_size": 0,
            "isolated_stations": [],
            "isolated_count": 0,
            "station_to_component": {},
            "component_sizes": [],
        }

    components = list(nx.connected_components(graph))
    # Sort components by size descending
    components.sort(key=len, reverse=True)

    station_to_comp: Dict[str, int] = {}
    component_sizes: List[int] = []

    for comp_idx, comp_nodes in enumerate(components, start=1):
        component_sizes.append(len(comp_nodes))
        for node in comp_nodes:
            station_to_comp[str(node)] = comp_idx

    isolated_nodes = [str(node) for node, deg in graph.degree() if deg == 0]

    return {
        "connected_components_count": len(components),
        "is_connected": len(components) == 1,
        "largest_component_size": component_sizes[0] if component_sizes else 0,
        "smallest_component_size": component_sizes[-1] if component_sizes else 0,
        "isolated_stations": isolated_nodes,
        "isolated_count": len(isolated_nodes),
        "station_to_component": station_to_comp,
        "component_sizes": component_sizes,
    }
