"""Interchange station structural detection and membership analysis."""

from typing import Any, Dict, List, Optional, Set

import pandas as pd


def detect_interchange_stations(
    station_lines_df: pd.DataFrame,
    stations_df: pd.DataFrame,
    lines_df: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """Analyzes station-line memberships to identify structural interchange stations.

    A station is defined structurally as an interchange if it is associated
    with two or more distinct metro lines.

    Returns:
        Dict containing:
        - interchange_count (int)
        - interchange_station_ids (List[str])
        - station_line_map (Dict[str, Set[str]])
        - interchange_details (pd.DataFrame with station_name, line_count, lines_served)
    """
    station_names = dict(zip(stations_df["station_id"], stations_df["station_name"]))
    line_names = (
        dict(zip(lines_df["line_id"], lines_df["line_name"]))
        if lines_df is not None
        else {}
    )

    # Group station_lines by station_id
    grouped = station_lines_df.groupby("station_id")["line_id"].unique()
    station_line_map: Dict[str, Set[str]] = {
        sid: set(lines) for sid, lines in grouped.items()
    }

    # Include stations that have no station_line rows (edge case)
    for sid in stations_df["station_id"]:
        if sid not in station_line_map:
            station_line_map[sid] = set()

    interchange_ids: List[str] = [
        sid for sid, lines in station_line_map.items() if len(lines) >= 2
    ]

    details_list = []
    for sid in interchange_ids:
        lines = sorted(list(station_line_map[sid]))
        named_lines = [line_names.get(lid, lid) for lid in lines]
        details_list.append({
            "station_id": sid,
            "station_name": station_names.get(sid, sid),
            "line_count": len(lines),
            "line_ids": ", ".join(lines),
            "lines_served": ", ".join(named_lines),
        })

    interchange_df = pd.DataFrame(details_list)
    if not interchange_df.empty:
        interchange_df = interchange_df.sort_values(
            by=["line_count", "station_name"], ascending=[False, True]
        ).reset_index(drop=True)

    return {
        "interchange_count": len(interchange_ids),
        "interchange_station_ids": interchange_ids,
        "station_line_map": station_line_map,
        "interchange_details": interchange_df,
    }
