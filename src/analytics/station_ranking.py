"""Station importance ranking pipeline and comprehensive analytics engine."""

from typing import Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd

from src.analytics.articulation_points import find_articulation_points
from src.analytics.betweenness_centrality import compute_betweenness_centrality
from src.analytics.connectivity import analyze_network_connectivity
from src.analytics.degree_centrality import compute_degree_centrality
from src.analytics.graph_projection import build_analysis_graph
from src.analytics.models import NetworkAnalyticsSummary, StationAnalyticsResult


def compute_station_analytics(
    multi_graph: nx.MultiGraph,
    station_lines_df: pd.DataFrame,
    lines_df: Optional[pd.DataFrame] = None,
    weighted_betweenness: bool = False,
) -> Tuple[List[StationAnalyticsResult], NetworkAnalyticsSummary, nx.Graph]:
    """Computes comprehensive structural analytics across all stations.

    Process:
    1. Projects MultiGraph into simple analysis Graph without mutating original.
    2. Computes unweighted degree centrality.
    3. Computes unweighted (and optional weighted) betweenness centrality.
    4. Detects articulation points using Tarjan's DFS cut-vertex algorithm.
    5. Computes connected component membership and isolation status.
    6. Compiles structured StationAnalyticsResult for each station and a NetworkAnalyticsSummary.

    Returns:
        (station_results_list, network_summary, analysis_graph)
    """
    analysis_g = build_analysis_graph(multi_graph)
    dc_map = compute_degree_centrality(analysis_g)
    bc_map = compute_betweenness_centrality(analysis_g, weighted=False)
    weighted_bc_map = (
        compute_betweenness_centrality(analysis_g, weighted=True) if weighted_betweenness else None
    )
    ap_set = find_articulation_points(analysis_g)
    conn_data = analyze_network_connectivity(analysis_g)

    line_name_map = {}
    if lines_df is not None and not lines_df.empty:
        line_name_map = dict(zip(lines_df["line_id"], lines_df["line_name"]))

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

    station_results: List[StationAnalyticsResult] = []

    for node in sorted(analysis_g.nodes, key=lambda x: str(x)):
        sid = str(node)
        s_data = analysis_g.nodes[node]
        name = s_data.get("station_name", sid)
        deg = analysis_g.degree[node]
        dc = dc_map.get(sid, 0.0)
        bc = bc_map.get(sid, 0.0)
        w_bc = weighted_bc_map.get(sid) if weighted_bc_map else None
        l_list = station_to_lines.get(sid, list(s_data.get("lines", [])))
        l_names = station_to_line_names.get(sid, l_list)
        is_inter = len(l_list) >= 2 or s_data.get("is_interchange", False)
        is_ap = sid in ap_set
        comp_id = conn_data["station_to_component"].get(sid, 1)

        station_results.append(
            StationAnalyticsResult(
                station_id=sid,
                station_name=name,
                degree=deg,
                degree_centrality=dc,
                betweenness_centrality=bc,
                line_count=len(l_list),
                line_names=l_names,
                is_interchange=is_inter,
                is_articulation_point=is_ap,
                component_id=comp_id,
                weighted_betweenness_centrality=w_bc,
            )
        )

    # Calculate summary metrics
    total_nodes = analysis_g.number_of_nodes()
    total_edges = analysis_g.number_of_edges()
    degrees = dict(analysis_g.degree())
    max_d = max(degrees.values()) if degrees else 0
    avg_d = round(sum(degrees.values()) / total_nodes, 2) if total_nodes > 0 else 0.0

    # Highest degree & betweenness stations
    highest_deg_node = max(degrees, key=degrees.get) if degrees else ""
    highest_deg_name = (
        analysis_g.nodes[highest_deg_node].get("station_name", str(highest_deg_node))
        if highest_deg_node
        else "N/A"
    )

    highest_bc_node = max(bc_map, key=bc_map.get) if bc_map else ""
    highest_bc_name = (
        analysis_g.nodes[highest_bc_node].get("station_name", str(highest_bc_node))
        if highest_bc_node
        else "N/A"
    )

    interchange_count = sum(1 for r in station_results if r.is_interchange)

    summary = NetworkAnalyticsSummary(
        total_stations=total_nodes,
        total_connections=total_edges,
        total_multigraph_edges=multi_graph.number_of_edges(),
        total_lines=len(lines_df) if lines_df is not None else 0,
        total_interchanges=interchange_count,
        total_articulation_points=len(ap_set),
        connected_components=conn_data["connected_components_count"],
        largest_component_size=conn_data["largest_component_size"],
        smallest_component_size=conn_data["smallest_component_size"],
        isolated_stations_count=conn_data["isolated_count"],
        average_degree=avg_d,
        max_degree=max_d,
        highest_degree_station=f"{highest_deg_name} ({highest_deg_node})",
        highest_betweenness_station=f"{highest_bc_name} ({highest_bc_node})",
    )

    return station_results, summary, analysis_g


def get_ranked_stations_dataframe(
    station_results: List[StationAnalyticsResult],
    sort_by: str = "betweenness_centrality",
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    """Returns a formatted pandas DataFrame of station importance metrics.

    Args:
        station_results: List of StationAnalyticsResult objects.
        sort_by: Metric to rank by: 'betweenness_centrality', 'degree_centrality', 'degree', or 'line_count'.
        top_n: Optional limit to top N stations.
    """
    rows = []
    for r in station_results:
        rows.append({
            "Station ID": r.station_id,
            "Station Name": r.station_name,
            "Degree": r.degree,
            "Degree Centrality": round(r.degree_centrality, 5),
            "Betweenness Centrality": round(r.betweenness_centrality, 5),
            "Line Count": r.line_count,
            "Lines Served": ", ".join(r.line_names),
            "Interchange?": "Yes" if r.is_interchange else "No",
            "Articulation Point?": "Yes" if r.is_articulation_point else "No",
            "Component ID": r.component_id,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        col_map = {
            "betweenness_centrality": "Betweenness Centrality",
            "degree_centrality": "Degree Centrality",
            "degree": "Degree",
            "line_count": "Line Count",
        }
        sort_col = col_map.get(sort_by, "Betweenness Centrality")
        df = df.sort_values(by=[sort_col, "Station Name"], ascending=[False, True])
        df["Rank"] = range(1, len(df) + 1)
        # Reorder columns with Rank first
        cols = ["Rank"] + [c for c in df.columns if c != "Rank"]
        df = df[cols]

    if top_n is not None and top_n > 0:
        df = df.head(top_n)

    return df
