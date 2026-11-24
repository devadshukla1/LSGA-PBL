"""Interchange station structural analysis."""

from typing import Dict, List, Optional

import networkx as nx
import pandas as pd


def analyze_interchange_stations(
    graph: nx.Graph,
    station_lines_df: pd.DataFrame,
    lines_df: Optional[pd.DataFrame] = None,
) -> Dict[str, any]:
    """Analyzes stations serving two or more distinct metro lines.

    Distinguishes structural line convergence from graph degree:
    - An interchange station serves >= 2 distinct metro lines.
    - An interchange does NOT necessarily have high betweenness or high degree.
    """
    line_name_map = {}
    if lines_df is not None and not lines_df.empty:
        line_name_map = dict(zip(lines_df["line_id"], lines_df["line_name"]))

    # Aggregate lines per station
    station_to_lines: Dict[str, List[str]] = {}
    station_to_line_names: Dict[str, List[str]] = {}

    for _, row in station_lines_df.iterrows():
        sid = str(row["station_id"])
        lid = str(row["line_id"])
        lname = line_name_map.get(lid, lid)

        if sid not in station_to_lines:
            station_to_lines[sid] = []
            station_to_line_names[sid] = []

        if lid not in station_to_lines[sid]:
            station_to_lines[sid].append(lid)
            station_to_line_names[sid].append(lname)

    interchange_station_ids = {sid for sid, l_list in station_to_lines.items() if len(l_list) >= 2}

    records = []
    for sid in sorted(interchange_station_ids):
        s_data = graph.nodes[sid] if sid in graph.nodes else {}
        name = s_data.get("station_name", sid)
        deg = graph.degree[sid] if sid in graph.nodes else 0
        l_list = station_to_lines.get(sid, [])
        lnames = station_to_line_names.get(sid, [])

        records.append({
            "station_id": sid,
            "station_name": name,
            "line_count": len(l_list),
            "lines": l_list,
            "line_names": lnames,
            "degree": deg,
        })

    records_df = pd.DataFrame(records)
    if not records_df.empty:
        records_df = records_df.sort_values(by=["line_count", "degree"], ascending=[False, False])

    return {
        "interchange_count": len(interchange_station_ids),
        "interchange_station_ids": interchange_station_ids,
        "interchange_details": records_df,
    }
