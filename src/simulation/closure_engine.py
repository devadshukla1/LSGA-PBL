"""Station closure engine for isolated simulation graph construction."""

from typing import Any, List, Optional, Set

import networkx as nx

from src.core.exceptions import MetroGraphError
from src.simulation.connectivity_impact import compute_connectivity_metrics
from src.simulation.models import ClosureSimulationResult


class StationClosureError(MetroGraphError):
    """Raised when station closure simulation fails validation."""

    pass


def _resolve_station_id(graph: nx.MultiGraph, sid: Any) -> Any:
    """Resolves station ID to the exact key in the graph (str or int)."""
    if graph.has_node(sid):
        return sid
    if isinstance(sid, str) and sid.isdigit() and graph.has_node(int(sid)):
        return int(sid)
    if graph.has_node(str(sid)):
        return str(sid)
    return sid


def simulate_station_closure(
    original_graph: nx.MultiGraph,
    closed_station_ids: Optional[List[str]] = None,
    dataset_id: str = "metro_network",
) -> ClosureSimulationResult:
    """Simulates the closure of single or multiple stations on an isolated graph copy.

    Requirements & Invariants:
    1. The original_graph is NEVER mutated.
    2. Validates station IDs and raises StationClosureError on unknown IDs.
    3. Handles empty closed_station_ids as a valid baseline simulation.
    4. Normalizes duplicates in closed_station_ids.
    5. Creates an isolated copy of the MultiGraph and removes selected nodes and incident edges.
    6. Preserves all remaining parallel edges, edge attributes, and weights.
    7. Evaluates before-and-after connectivity and reachability metrics.

    Args:
        original_graph: The original transit NetworkX MultiGraph.
        closed_station_ids: List of station IDs to close (default empty).
        dataset_id: Label identifying the active dataset.

    Returns:
        ClosureSimulationResult with baseline, simulated graph, and impact delta metrics.
    """
    closed_list = closed_station_ids or []
    # Deduplicate while preserving order
    seen: Set[str] = set()
    unique_closed: List[str] = []
    for sid in closed_list:
        sid_str = str(sid).strip()
        if sid_str and sid_str not in seen:
            seen.add(sid_str)
            unique_closed.append(sid_str)

    # Validate that all requested stations exist in the graph
    resolved_closed = []
    closed_names = []
    warnings: List[str] = []

    for sid in unique_closed:
        res_node = _resolve_station_id(original_graph, sid)
        if not original_graph.has_node(res_node):
            raise StationClosureError(f"Cannot close unknown station '{sid}' (not in graph).")
        resolved_closed.append(res_node)
        sname = original_graph.nodes[res_node].get("station_name", str(sid))
        closed_names.append(sname)

    # 1. Baseline metrics on original graph
    baseline_metrics = compute_connectivity_metrics(original_graph)

    # 2. Create isolated deep copy of the MultiGraph
    # Memory documentation: A full copy of a 260-node, 273-edge MultiGraph consumes ~100 KB,
    # ensuring complete isolation and thread-safety without side-effects.
    sim_graph: nx.MultiGraph = original_graph.copy()

    # 3. Remove selected stations
    sim_graph.remove_nodes_from(resolved_closed)

    # 4. Post-closure metrics on simulation graph
    post_metrics = compute_connectivity_metrics(sim_graph)

    # 5. Compute deltas
    removed_stations = baseline_metrics.station_count - post_metrics.station_count
    removed_edges = baseline_metrics.edge_count - post_metrics.edge_count
    comp_change = post_metrics.connected_components - baseline_metrics.connected_components
    largest_reduction = baseline_metrics.largest_component_size - post_metrics.largest_component_size
    pair_loss = baseline_metrics.reachable_station_pairs - post_metrics.reachable_station_pairs
    ratio_change = round(post_metrics.reachability_ratio - baseline_metrics.reachability_ratio, 5)

    if comp_change > 0:
        warnings.append(
            f"Network fragmented: {comp_change} additional disconnected component(s) created."
        )
    if post_metrics.isolated_stations_count > baseline_metrics.isolated_stations_count:
        iso_diff = post_metrics.isolated_stations_count - baseline_metrics.isolated_stations_count
        warnings.append(f"{iso_diff} station(s) became completely isolated (degree 0).")

    return ClosureSimulationResult(
        dataset_id=dataset_id,
        closed_station_ids=unique_closed,
        closed_station_names=closed_names,
        baseline_metrics=baseline_metrics,
        post_closure_metrics=post_metrics,
        removed_stations_count=removed_stations,
        removed_edges_count=removed_edges,
        component_count_change=comp_change,
        largest_component_reduction=largest_reduction,
        reachable_pairs_loss=pair_loss,
        reachability_ratio_change=ratio_change,
        simulation_graph=sim_graph,
        warnings=warnings,
    )
