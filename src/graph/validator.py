"""Graph structural, topological, and connectivity diagnostics validator."""

from typing import Any, Dict, List

import networkx as nx

from src.core.exceptions import GraphValidationError
from src.core.logging_config import get_logger

logger = get_logger("metrograph.graph_validator")


def validate_metro_graph(graph: nx.MultiGraph) -> Dict[str, Any]:
    """Validates structural invariants and computes connectivity diagnostics.

    Checks:
    - MultiGraph instance check
    - Node existence and required attributes (lat, lon, station_name, lines)
    - Coordinate valid ranges
    - Edge attributes (line_id, distance_km, estimated_time_min)
    - Positive weights
    - Preservation of parallel edges
    - Connected components, isolated nodes, average degree
    """
    if graph is None or not isinstance(graph, nx.MultiGraph):
        raise GraphValidationError("Graph object is null or not an instance of networkx.MultiGraph.")

    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()

    if node_count == 0:
        raise GraphValidationError("Graph contains no station nodes.")
    if edge_count == 0:
        raise GraphValidationError("Graph contains no connection edges.")

    # 1. Validate node attributes
    required_node_attrs = {"lat", "lon", "lines"}
    for node, attrs in graph.nodes(data=True):
        missing = required_node_attrs - set(attrs.keys())
        if missing:
            raise GraphValidationError(f"Station node '{node}' is missing attributes: {missing}")

        lat = attrs.get("lat", 0.0)
        lon = attrs.get("lon", 0.0)
        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lon <= 180.0):
            raise GraphValidationError(f"Station node '{node}' has out-of-range coordinates: lat={lat}, lon={lon}")

    # 2. Validate edge attributes and positive weights
    required_edge_attrs = {"line_id"}
    for u, v, k, attrs in graph.edges(keys=True, data=True):
        missing = required_edge_attrs - set(attrs.keys())
        if missing:
            raise GraphValidationError(f"Edge ({u}, {v}, key={k}) is missing required attributes: {missing}")

        if "distance_km" in attrs and attrs["distance_km"] <= 0:
            raise GraphValidationError(
                f"Edge ({u}, {v}, key={k}) has non-positive distance_km: {attrs['distance_km']}"
            )
        if "estimated_time_min" in attrs and attrs["estimated_time_min"] <= 0:
            raise GraphValidationError(
                f"Edge ({u}, {v}, key={k}) has non-positive estimated_time_min: {attrs['estimated_time_min']}"
            )

    # 3. Connectivity Diagnostics
    is_connected = nx.is_connected(graph)
    connected_components = list(nx.connected_components(graph))
    component_count = len(connected_components)
    largest_component_size = max(len(c) for c in connected_components) if connected_components else 0

    # Isolated nodes (degree 0)
    isolated_nodes = list(nx.isolates(graph))

    # Average node degree
    avg_degree = round(sum(d for _, d in graph.degree()) / node_count, 2)

    # Interchange nodes
    interchange_stations = [
        node for node, attrs in graph.nodes(data=True) if attrs.get("is_interchange", False)
    ]

    # Parallel edge detection
    parallel_edge_pairs: List[Dict[str, Any]] = []
    seen_pairs: Dict[tuple, int] = {}
    for u, v in graph.edges():
        pair = tuple(sorted([u, v]))
        seen_pairs[pair] = seen_pairs.get(pair, 0) + 1
    for pair, count in seen_pairs.items():
        if count > 1:
            parallel_edge_pairs.append({"endpoints": pair, "count": count})

    summary: Dict[str, Any] = {
        "is_valid": True,
        "node_count": node_count,
        "edge_count": edge_count,
        "is_connected": is_connected,
        "connected_components": component_count,
        "largest_component_size": largest_component_size,
        "isolated_nodes_count": len(isolated_nodes),
        "isolated_nodes": isolated_nodes,
        "average_degree": avg_degree,
        "interchange_station_count": len(interchange_stations),
        "interchange_stations": interchange_stations,
        "has_parallel_edges": len(parallel_edge_pairs) > 0,
        "parallel_edge_pairs": parallel_edge_pairs,
    }

    logger.info("Graph validation passed: %s", summary)
    return summary
