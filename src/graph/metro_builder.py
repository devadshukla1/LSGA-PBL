"""Metro graph builder utilizing NetworkX MultiGraph representation."""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import networkx as nx
import pandas as pd

from src.core.exceptions import GraphConstructionError
from src.core.logging_config import get_logger
from src.core.settings import PROCESSED_DATA_DIR
from src.graph.interchanges import detect_interchange_stations

logger = get_logger("metrograph.metro_builder")


def build_metro_graph(
    stations_df: pd.DataFrame,
    lines_df: pd.DataFrame,
    connections_df: pd.DataFrame,
    station_lines_df: Optional[pd.DataFrame] = None,
) -> nx.MultiGraph:
    """Builds a NetworkX MultiGraph from validated tabular metro data.

    Design Justification:
    - MultiGraph preserves parallel line services running along the same corridor.
    - Metro passenger trips are modeled as bidirectional for our topological base model.
    - Node attributes: station_name, lat, lon, lines, is_interchange, station_line_count.
    - Edge attributes: line_id, line_name, line_color, distance_km, estimated_time_min,
      weight_provenance.
    """
    try:
        graph = nx.MultiGraph()

        # Build lines lookup dict
        lines_info: Dict[str, Dict[str, str]] = {}
        for _, row in lines_df.iterrows():
            lid = str(row["line_id"])
            lines_info[lid] = {
                "name": str(row["line_name"]),
                "color": str(row["color"]),
            }

        # Calculate interchange memberships if station_lines_df provided
        station_line_map: Dict[str, set] = {}
        if station_lines_df is not None:
            interchange_res = detect_interchange_stations(station_lines_df, stations_df, lines_df)
            station_line_map = interchange_res["station_line_map"]

        # Add stations as nodes
        for _, row in stations_df.iterrows():
            sid = str(row["station_id"])
            lines_set = station_line_map.get(sid, set()).copy()
            graph.add_node(
                sid,
                station_name=str(row["station_name"]),
                name=str(row["station_name"]),  # Backwards compatibility alias
                lat=float(row["latitude"]),
                lon=float(row["longitude"]),
                lines=lines_set,
                station_line_count=len(lines_set),
                is_interchange=len(lines_set) >= 2,
            )

        # Add connections as multi-edges
        for _, row in connections_df.iterrows():
            u = str(row["source_station_id"])
            v = str(row["destination_station_id"])
            lid = str(row["line_id"])

            dist = float(row.get("distance_km", 1.0))
            time_min = float(row.get("estimated_time_min", 2.0))
            provenance = str(row.get("weight_provenance", "published"))

            line_meta = lines_info.get(lid, {"name": f"Line {lid}", "color": "#94A3B8"})

            # Track lines at both nodes if not already set by station_lines
            if u in graph.nodes:
                graph.nodes[u]["lines"].add(lid)
                graph.nodes[u]["station_line_count"] = len(graph.nodes[u]["lines"])
                graph.nodes[u]["is_interchange"] = len(graph.nodes[u]["lines"]) >= 2

            if v in graph.nodes:
                graph.nodes[v]["lines"].add(lid)
                graph.nodes[v]["station_line_count"] = len(graph.nodes[v]["lines"])
                graph.nodes[v]["is_interchange"] = len(graph.nodes[v]["lines"]) >= 2

            # Deterministic stable key: e.g. "L01"
            graph.add_edge(
                u,
                v,
                key=lid,
                line_id=lid,
                line_name=line_meta["name"],
                line_color=line_meta["color"],
                distance_km=dist,
                estimated_time_min=time_min,
                weight_provenance=provenance,
            )

        logger.info(
            "Constructed MultiGraph: %d nodes, %d edges, %d interchange hubs.",
            graph.number_of_nodes(),
            graph.number_of_edges(),
            sum(1 for _, d in graph.nodes(data=True) if d.get("is_interchange", False)),
        )
        return graph

    except Exception as e:
        err_msg = f"Failed to construct metro graph: {e}"
        logger.error(err_msg)
        raise GraphConstructionError(err_msg) from e


def save_graph_to_graphml(
    graph: nx.MultiGraph,
    output_path: Path | str = PROCESSED_DATA_DIR / "metro_network.graphml",
    fingerprint: str = "",
) -> Tuple[Path, Path]:
    """Serializes MultiGraph into GraphML format and saves metadata sidecar."""
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # GraphML does not natively serialize Python sets, convert node 'lines' to comma-string for export
    export_graph = graph.copy()
    for _, data in export_graph.nodes(data=True):
        if "lines" in data and isinstance(data["lines"], set):
            data["lines"] = ",".join(sorted(list(data["lines"])))

    nx.write_graphml(export_graph, str(out_path))

    # Sidecar JSON metadata
    meta = {
        "dataset_fingerprint": fingerprint,
        "schema_version": "2.0.0",
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "interchange_count": sum(1 for _, d in graph.nodes(data=True) if d.get("is_interchange", False)),
        "is_connected": nx.is_connected(graph),
        "connected_components": nx.number_connected_components(graph),
    }
    meta_path = out_path.with_suffix(".json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    logger.info("Saved GraphML cache to %s with metadata %s", out_path, meta_path)
    return out_path, meta_path


def load_graph_from_graphml(
    graphml_path: Path | str = PROCESSED_DATA_DIR / "metro_network.graphml",
) -> nx.MultiGraph:
    """Loads a MultiGraph from GraphML cache and restores node attribute types."""
    path = Path(graphml_path)
    if not path.is_file():
        raise FileNotFoundError(f"GraphML cache file not found: {path}")

    raw_graph = nx.read_graphml(str(path))
    # Convert to MultiGraph if needed
    graph = nx.MultiGraph(raw_graph)

    # Restore types
    for _, data in graph.nodes(data=True):
        if "lat" in data:
            data["lat"] = float(data["lat"])
        if "lon" in data:
            data["lon"] = float(data["lon"])
        if "lines" in data and isinstance(data["lines"], str):
            data["lines"] = set(data["lines"].split(",")) if data["lines"] else set()
        if "is_interchange" in data:
            data["is_interchange"] = (
                str(data["is_interchange"]).lower() == "true"
                if isinstance(data["is_interchange"], str)
                else bool(data["is_interchange"])
            )
        if "name" not in data and "station_name" in data:
            data["name"] = data["station_name"]

    for _, _, _, data in graph.edges(keys=True, data=True):
        if "distance_km" in data:
            data["distance_km"] = float(data["distance_km"])
        if "estimated_time_min" in data:
            data["estimated_time_min"] = float(data["estimated_time_min"])

    return graph
