"""Critical station structural impact analysis and vulnerability ranking."""

from typing import Dict, Optional

import networkx as nx
import pandas as pd

from src.simulation.closure_engine import simulate_station_closure


def evaluate_single_station_impact(
    graph: nx.MultiGraph,
    station_id: str,
) -> Dict[str, any]:
    """Evaluates the isolated structural impact of closing a single station."""
    res = simulate_station_closure(graph, closed_station_ids=[station_id])
    b = res.baseline_metrics
    p = res.post_closure_metrics

    sname = graph.nodes[station_id].get("station_name", station_id) if station_id in graph.nodes else station_id

    return {
        "station_id": station_id,
        "station_name": sname,
        "component_count_increase": res.component_count_change,
        "largest_component_reduction": res.largest_component_reduction,
        "reachable_pairs_loss": res.reachable_pairs_loss,
        "remaining_reachability_ratio": p.reachability_ratio if p else 0.0,
        "isolated_stations_created": (
            (p.isolated_stations_count - b.isolated_stations_count) if (p and b) else 0
        ),
        "is_articulation_point": res.component_count_change > 0,
    }


def compute_all_stations_impact_ranking(
    graph: nx.MultiGraph,
    max_stations: Optional[int] = None,
) -> pd.DataFrame:
    """Computes vulnerability impact rankings by simulating the removal of each station.

    Allows sorting by:
    - Component Count Increase (Topological Severing)
    - Reachable Pairs Loss (Connectivity Destruction)
    - Largest Component Reduction (Network Core Shrinkage)
    """
    station_nodes = list(graph.nodes)
    if max_stations and max_stations > 0:
        station_nodes = station_nodes[:max_stations]

    rows = []
    for sid in station_nodes:
        impact = evaluate_single_station_impact(graph, str(sid))
        rows.append({
            "Station ID": impact["station_id"],
            "Station Name": impact["station_name"],
            "Component Count Increase": impact["component_count_increase"],
            "Reachable Pairs Lost": impact["reachable_pairs_loss"],
            "Largest Component Reduction": impact["largest_component_reduction"],
            "Remaining Reachability Ratio": round(impact["remaining_reachability_ratio"], 4),
            "Cut-Vertex (AP)?": "Yes" if impact["is_articulation_point"] else "No",
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(
            by=["Component Count Increase", "Reachable Pairs Lost", "Largest Component Reduction"],
            ascending=[False, False, False],
        )
        df["Vulnerability Rank"] = range(1, len(df) + 1)
        cols = ["Vulnerability Rank"] + [c for c in df.columns if c != "Vulnerability Rank"]
        df = df[cols]

    return df
