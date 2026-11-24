"""Before-and-after connectivity impact comparison table."""

import pandas as pd

from src.simulation.models import ClosureSimulationResult


def build_impact_comparison_table(result: ClosureSimulationResult) -> pd.DataFrame:
    """Builds an informative before-and-after metric comparison DataFrame.

    Metrics compared:
    - Station Count (Active Vertices)
    - Multi-Edge Count (Active Physical Track Connections)
    - Connected Components
    - Largest Component Size
    - Smallest Component Size
    - Isolated Stations (Degree 0)
    - Reachable Station Pairs
    - Reachability Ratio
    """
    b = result.baseline_metrics
    p = result.post_closure_metrics

    if not b or not p:
        return pd.DataFrame()

    def fmt_delta(curr, base, higher_is_better=True, is_ratio=False):
        diff = curr - base
        if is_ratio:
            sign = "+" if diff > 0 else ""
            return f"{sign}{diff:.4f}"
        sign = "+" if diff > 0 else ""
        return f"{sign}{diff}"

    rows = [
        {
            "Metric": "Station Count (Active Vertices)",
            "Before Closure": str(b.station_count),
            "After Closure": str(p.station_count),
            "Change (Delta)": fmt_delta(p.station_count, b.station_count),
            "Interpretation": "Remaining operational stations in network.",
        },
        {
            "Metric": "Track Connections (Multi-Edges)",
            "Before Closure": str(b.edge_count),
            "After Closure": str(p.edge_count),
            "Change (Delta)": fmt_delta(p.edge_count, b.edge_count),
            "Interpretation": "Incident edges removed with closed stations.",
        },
        {
            "Metric": "Connected Components",
            "Before Closure": str(b.connected_components),
            "After Closure": str(p.connected_components),
            "Change (Delta)": fmt_delta(p.connected_components, b.connected_components),
            "Interpretation": "Count of disconnected sub-networks (higher indicates fragmentation).",
        },
        {
            "Metric": "Largest Component Size",
            "Before Closure": str(b.largest_component_size),
            "After Closure": str(p.largest_component_size),
            "Change (Delta)": fmt_delta(p.largest_component_size, b.largest_component_size),
            "Interpretation": "Size of main contiguous transit core.",
        },
        {
            "Metric": "Isolated Stations (Degree 0)",
            "Before Closure": str(b.isolated_stations_count),
            "After Closure": str(p.isolated_stations_count),
            "Change (Delta)": fmt_delta(p.isolated_stations_count, b.isolated_stations_count),
            "Interpretation": "Stations with 0 surviving connections.",
        },
        {
            "Metric": "Reachable Station Pairs",
            "Before Closure": f"{b.reachable_station_pairs:,}",
            "After Closure": f"{p.reachable_station_pairs:,}",
            "Change (Delta)": f"{p.reachable_station_pairs - b.reachable_station_pairs:,}",
            "Interpretation": "Sum of n_i*(n_i - 1)/2 across components.",
        },
        {
            "Metric": "Reachability Ratio",
            "Before Closure": f"{b.reachability_ratio:.4f}",
            "After Closure": f"{p.reachability_ratio:.4f}",
            "Change (Delta)": fmt_delta(p.reachability_ratio, b.reachability_ratio, is_ratio=True),
            "Interpretation": "Reachable pairs / Possible pairs in remaining graph.",
        },
    ]

    return pd.DataFrame(rows)
