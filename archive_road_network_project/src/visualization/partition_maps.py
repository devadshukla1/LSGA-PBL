"""Geographic Folium map visualization for partitioned road networks."""

from collections.abc import Hashable
from itertools import islice

import folium
import networkx as nx
from branca.element import Element
from pyproj import Transformer

from src.partitioning.partition_models import PartitionResult

PARTITION_PALETTE = [
    "#38BDF8",  # Sky blue
    "#34D399",  # Emerald green
    "#FBBF24",  # Amber
    "#A78BFA",  # Purple
    "#F472B6",  # Pink
    "#4ADE80",  # Green
    "#FB923C",  # Orange
    "#818CF8",  # Indigo
    "#2DD4BF",  # Teal
    "#E879F9",  # Fuchsia
]


def partition_map(
    graph: nx.MultiDiGraph,
    partition_result: PartitionResult,
    limit: int = 600,
    query_location: tuple[float, float] | None = None,
    nearest_node_id: Hashable | None = None,
) -> folium.Map:
    """Generate a Folium map rendering internal edges, cut edges, and partition clusters.

    Internal roads are color-coded by their partition ID.
    Cut edges connecting different partitions are styled as distinctive red dashed lines.
    For large networks, rendered visual elements are bounded by `limit` while the underlying
    partition calculations reflect the full graph.
    """
    crs_str = graph.graph.get("crs", "EPSG:4326")
    transform = Transformer.from_crs(crs_str, 4326, always_xy=True)

    def point(x: float, y: float) -> tuple[float, float]:
        lon, lat = transform.transform(x, y)
        return lat, lon

    positions = {n: point(d["x"], d["y"]) for n, d in graph.nodes(data=True)}
    node_to_part = partition_result.node_to_partition

    result = folium.Map(tiles=None)
    folium.TileLayer("OpenStreetMap").add_to(result)
    result.get_root().header.add_child(
        Element(
            "<style>.leaflet-tile-pane{filter:invert(1) hue-rotate(180deg) brightness(.76)}"
            ".leaflet-container{background:#111827}</style>"
        )
    )

    # Render edges (internal vs cut)
    for u, v, _k, d in islice(graph.edges(keys=True, data=True), limit):
        if u not in positions or v not in positions:
            continue
        geom = d.get("geometry")
        coords = (
            [point(x, y) for x, y in geom.coords]
            if geom is not None
            else [positions[u], positions[v]]
        )
        pu = node_to_part.get(u)
        pv = node_to_part.get(v)

        if pu is not None and pv is not None and pu != pv:
            # Cut edge: distinct red dashed line
            folium.PolyLine(
                coords,
                color="#EF4444",
                weight=3.5,
                dash_array="6, 6",
                tooltip=f"Cut Edge: P{pu} -> P{pv}",
            ).add_to(result)
        elif pu is not None:
            # Internal edge: partition color
            color = PARTITION_PALETTE[pu % len(PARTITION_PALETTE)]
            folium.PolyLine(
                coords,
                color=color,
                weight=2.5,
                opacity=0.8,
            ).add_to(result)

    # Render nodes
    for n in islice(graph.nodes, limit):
        if n not in positions:
            continue
        part = node_to_part.get(n, 0)
        color = PARTITION_PALETTE[part % len(PARTITION_PALETTE)]
        folium.CircleMarker(
            positions[n],
            radius=3.5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            tooltip=f"Node {n} (Partition {part})",
        ).add_to(result)

    # Render query location if provided
    if query_location is not None:
        folium.Marker(
            location=query_location,
            popup="Query Location",
            tooltip="Query Location",
            icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
        ).add_to(result)

    # Render nearest node highlight if provided
    if nearest_node_id is not None and nearest_node_id in positions:
        folium.CircleMarker(
            location=positions[nearest_node_id],
            radius=8,
            color="#22C55E",
            fill=True,
            fill_color="#22C55E",
            fill_opacity=1.0,
            tooltip=f"Nearest Node: {nearest_node_id}",
        ).add_to(result)

        if query_location is not None:
            folium.PolyLine(
                [query_location, positions[nearest_node_id]],
                color="#22C55E",
                weight=2,
                dash_array="4, 4",
                tooltip="Nearest Connection",
            ).add_to(result)

    if positions:
        lats, lons = zip(*positions.values(), strict=True)
        result.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

    return result
