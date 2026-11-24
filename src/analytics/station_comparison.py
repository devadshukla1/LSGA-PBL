"""Station pairwise comparison analytics."""

from typing import Dict, List

import pandas as pd

from src.analytics.models import StationAnalyticsResult


def compare_two_stations(
    station_a_id: str,
    station_b_id: str,
    station_results: List[StationAnalyticsResult],
) -> pd.DataFrame:
    """Produces a structured side-by-side comparative DataFrame between two stations.

    Handles identical station selections gracefully.
    """
    res_map: Dict[str, StationAnalyticsResult] = {r.station_id: r for r in station_results}

    res_a = res_map.get(station_a_id)
    res_b = res_map.get(station_b_id)

    if not res_a or not res_b:
        return pd.DataFrame()

    comparison_data = [
        {"Attribute": "Station ID", "Station A": res_a.station_id, "Station B": res_b.station_id},
        {"Attribute": "Station Name", "Station A": res_a.station_name, "Station B": res_b.station_name},
        {"Attribute": "Degree (Adjacent Stations)", "Station A": str(res_a.degree), "Station B": str(res_b.degree)},
        {
            "Attribute": "Degree Centrality",
            "Station A": f"{res_a.degree_centrality:.5f}",
            "Station B": f"{res_b.degree_centrality:.5f}",
        },
        {
            "Attribute": "Betweenness Centrality",
            "Station A": f"{res_a.betweenness_centrality:.5f}",
            "Station B": f"{res_b.betweenness_centrality:.5f}",
        },
        {"Attribute": "Metro Lines Count", "Station A": str(res_a.line_count), "Station B": str(res_b.line_count)},
        {
            "Attribute": "Lines Served",
            "Station A": ", ".join(res_a.line_names) or "None",
            "Station B": ", ".join(res_b.line_names) or "None",
        },
        {
            "Attribute": "Interchange Station?",
            "Station A": "Yes" if res_a.is_interchange else "No",
            "Station B": "Yes" if res_b.is_interchange else "No",
        },
        {
            "Attribute": "Articulation Point? (Cut-Vertex)",
            "Station A": "Yes" if res_a.is_articulation_point else "No",
            "Station B": "Yes" if res_b.is_articulation_point else "No",
        },
        {
            "Attribute": "Connected Component ID",
            "Station A": str(res_a.component_id),
            "Station B": str(res_b.component_id),
        },
    ]

    return pd.DataFrame(comparison_data)
