"""Unified Delhi Metro Map Visualization Engine.

Provides clean, publication-grade interactive network maps with:
1. True Two-Tier Metro Line Highlighting (selected line 6px full color, other lines 1.8px muted 15% opacity).
2. Proper geographic aspect ratio (scaleanchor='x', scaleratio=1.14 for Delhi's ~28.6°N latitude)
   preventing vertical stretching or horizontal squishing.
3. Clean compact horizontal legend without title overlap.
4. Route highlighting, centrality heatmaps, and station closure disruption views.
5. Strictly offline Plotly rendering (zero external map tiles or OSMnx).
"""

from typing import Any, List, Optional

import networkx as nx
import plotly.graph_objects as go

from src.algorithms.routing_models import RouteResult


def render_delhi_metro_map(
    graph: nx.MultiGraph,
    selected_line: Optional[str] = None,
    filter_interchanges_only: bool = False,
    highlight_stations: Optional[List[str]] = None,
    title: str = "Delhi Metro Network Map (Interactive Offline Visualization)",
    height: int = 720,
) -> go.Figure:
    """Renders a polished, publication-grade interactive map of the Delhi Metro network.

    Features:
    - Focus Highlighting:
      * When selected_line is chosen:
        - Highlighted line renders at width=6.0px with full opacity (1.0).
        - Non-selected lines fade into background at width=1.8px with opacity=0.15.
        - Stations on the selected line remain fully opaque and readable.
        - Non-selected stations are dimmed (opacity=0.20, size=4.5px).
      * When 'All Lines' is chosen:
        - All lines render at standard width=3.5px with their official color identity.
    - Geometry:
      * Preserves spatial Delhi NCR layout using validated station coordinates.
      * Locks latitude/longitude aspect ratio (scaleanchor='x', scaleratio=1.14).
    - Legend:
      * Horizontal, non-overlapping legend positioned above the canvas.
    """
    highlight_stations = highlight_stations or []
    is_line_selected = bool(selected_line and selected_line != "All Lines")
    sel_clean = selected_line.strip().lower() if selected_line else ""

    def is_match_line(lid: str, lname: str) -> bool:
        if not is_line_selected:
            return True
        return sel_clean in (str(lid).strip().lower(), str(lname).strip().lower())

    fig = go.Figure()

    # 1. Group track segments by line
    lines_edges: dict[str, dict] = {}

    for u, v, _key, data in graph.edges(keys=True, data=True):
        line_id = data.get("line_id", "Unknown")
        line_name = data.get("line_name", line_id)
        line_color = data.get("line_color", "#94A3B8")

        x0, y0 = graph.nodes[u]["lon"], graph.nodes[u]["lat"]
        x1, y1 = graph.nodes[v]["lon"], graph.nodes[v]["lat"]
        dist = data.get("distance_km", "N/A")
        time_min = data.get("estimated_time_min", "N/A")
        provenance = data.get("weight_provenance", "published")

        u_name = graph.nodes[u].get("station_name", u)
        v_name = graph.nodes[v].get("station_name", v)

        if line_id not in lines_edges:
            lines_edges[line_id] = {
                "name": line_name,
                "color": line_color,
                "x": [],
                "y": [],
                "hover": [],
            }

        lines_edges[line_id]["x"].extend([x0, x1, None])
        lines_edges[line_id]["y"].extend([y0, y1, None])
        hover_info = (
            f"<b>{line_name}</b><br>"
            f"{u_name} ↔ {v_name}<br>"
            f"Distance: {dist} km ({provenance})<br>"
            f"Est. Time: {time_min} min"
        )
        lines_edges[line_id]["hover"].extend([hover_info, hover_info, ""])

    # 1a. Background dimmed lines when a line filter is active
    if is_line_selected:
        dim_x: list = []
        dim_y: list = []
        dim_hover: list = []

        for line_id, data in lines_edges.items():
            if not is_match_line(line_id, data["name"]):
                dim_x.extend(data["x"])
                dim_y.extend(data["y"])
                dim_hover.extend(data["hover"])

        if dim_x:
            fig.add_trace(
                go.Scatter(
                    x=dim_x,
                    y=dim_y,
                    mode="lines",
                    line=dict(width=1.8, color="#334155"),
                    opacity=0.15,
                    hoverinfo="text",
                    hovertext=dim_hover,
                    name="Other Lines (Dimmed)",
                    showlegend=False,
                )
            )

    # 1b. Active / Selected lines
    for line_id, data in lines_edges.items():
        is_highlighted = is_match_line(line_id, data["name"])
        if is_line_selected and not is_highlighted:
            continue

        l_width = 6.0 if is_line_selected else 3.5

        fig.add_trace(
            go.Scatter(
                x=data["x"],
                y=data["y"],
                mode="lines",
                line=dict(width=l_width, color=data["color"]),
                opacity=1.0,
                hoverinfo="text",
                hovertext=data["hover"],
                name=data["name"],
                showlegend=True,
            )
        )

    # 2. Collect and Draw Stations
    hl_reg = {"x": [], "y": [], "text": [], "hover": []}
    hl_inter = {"x": [], "y": [], "text": [], "hover": []}
    dim_nodes = {"x": [], "y": [], "hover": []}

    for node, data in graph.nodes(data=True):
        is_interchange = data.get("is_interchange", False)

        if filter_interchanges_only and not is_interchange:
            continue

        lines_list = sorted(list(data.get("lines", [])))

        # Line membership check
        on_selected_line = True
        if is_line_selected:
            connected_lines = {str(d.get("line_name", "")).strip().lower() for _, _, d in graph.edges(node, data=True)}
            connected_ids = {str(d.get("line_id", "")).strip().lower() for _, _, d in graph.edges(node, data=True)}
            station_lines_lower = {str(l_item).strip().lower() for l_item in lines_list}
            on_selected_line = (
                sel_clean in station_lines_lower
                or sel_clean in connected_lines
                or sel_clean in connected_ids
            )

        lon = data.get("lon", 0.0)
        lat = data.get("lat", 0.0)
        name = data.get("station_name", data.get("name", node))
        lines_served = ", ".join(lines_list) if lines_list else "Single Line"

        hover_info = (
            f"<b>{name}</b> ({node})<br>"
            f"Lines: {lines_served}<br>"
            f"Degree: {graph.degree(node)}<br>"
            f"Type: {'Interchange Hub' if is_interchange else 'Standard Station'}"
        )

        if is_line_selected and not on_selected_line:
            dim_nodes["x"].append(lon)
            dim_nodes["y"].append(lat)
            dim_nodes["hover"].append(hover_info)
        else:
            if is_interchange:
                hl_inter["x"].append(lon)
                hl_inter["y"].append(lat)
                hl_inter["text"].append(name)
                hl_inter["hover"].append(hover_info)
            else:
                hl_reg["x"].append(lon)
                hl_reg["y"].append(lat)
                hl_reg["text"].append(name)
                hl_reg["hover"].append(hover_info)

    # 2a. Dimmed Stations Trace
    if dim_nodes["x"]:
        fig.add_trace(
            go.Scatter(
                x=dim_nodes["x"],
                y=dim_nodes["y"],
                mode="markers",
                marker=dict(
                    size=4.5,
                    color="#475569",
                    opacity=0.20,
                ),
                hoverinfo="text",
                hovertext=dim_nodes["hover"],
                name="Non-Selected Stations",
                showlegend=False,
            )
        )

    # 2b. Regular Stations Trace
    if hl_reg["x"]:
        fig.add_trace(
            go.Scatter(
                x=hl_reg["x"],
                y=hl_reg["y"],
                mode="markers",
                marker=dict(
                    size=8,
                    color="#0EA5E9" if is_line_selected else "#1E293B",
                    line=dict(width=1.5, color="#F8FAFC"),
                ),
                text=hl_reg["text"],
                hoverinfo="text",
                hovertext=hl_reg["hover"],
                name="Regular Station",
                showlegend=not is_line_selected,
            )
        )

    # 2c. Interchange Hubs Trace
    if hl_inter["x"]:
        fig.add_trace(
            go.Scatter(
                x=hl_inter["x"],
                y=hl_inter["y"],
                mode="markers",
                marker=dict(
                    size=13,
                    symbol="diamond",
                    color="#F59E0B" if is_line_selected else "#38BDF8",
                    line=dict(width=2, color="#FFFFFF"),
                ),
                text=hl_inter["text"],
                hoverinfo="text",
                hovertext=hl_inter["hover"],
                name="Interchange Hub",
                showlegend=True,
            )
        )

    # 2d. Explicit Highlighted Stations (e.g. query/selection)
    if highlight_stations:
        spec_x = []
        spec_y = []
        spec_hover = []
        spec_text = []
        for sid in highlight_stations:
            if sid in graph.nodes:
                d = graph.nodes[sid]
                spec_x.append(d["lon"])
                spec_y.append(d["lat"])
                sname = d.get("station_name", sid)
                spec_text.append(sname)
                spec_hover.append(f"<b>TARGET STATION: {sname}</b> ({sid})")

        if spec_x:
            fig.add_trace(
                go.Scatter(
                    x=spec_x,
                    y=spec_y,
                    mode="markers+text",
                    marker=dict(
                        size=16,
                        symbol="star",
                        color="#22C55E",
                        line=dict(width=2, color="#FFFFFF"),
                    ),
                    text=spec_text,
                    textposition="top center",
                    textfont=dict(color="#22C55E", size=11, family="sans-serif"),
                    hoverinfo="text",
                    hovertext=spec_hover,
                    name="Target Station",
                    showlegend=True,
                )
            )

    # Layout styling
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(color="#F8FAFC", size=15),
            x=0.02,
            y=0.98,
        ),
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111827",
        hovermode="closest",
        legend=dict(
            font=dict(color="#F8FAFC", size=10),
            bgcolor="rgba(17, 24, 39, 0.85)",
            bordercolor="#374151",
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            zeroline=False,
            showticklabels=False,
            title="Longitude (East ➔)",
            titlefont=dict(color="#64748B", size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            zeroline=False,
            showticklabels=False,
            title="Latitude (North ➔)",
            titlefont=dict(color="#64748B", size=10),
            scaleanchor="x",
            scaleratio=1.14,
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
    )

    return fig


# Backward-compatible alias for existing imports
create_metro_network_plot = render_delhi_metro_map


def plot_metro_route(
    graph: nx.MultiGraph,
    route_result: RouteResult,
    title: Optional[str] = None,
    height: int = 700,
) -> go.Figure:
    """Renders the entire network dimmed with the optimal route highlighted prominently."""
    default_title = (
        f"Optimal Route: {route_result.source_station_id} ➔ {route_result.destination_station_id} "
        f"({route_result.algorithm} • {route_result.total_stops} stops • {route_result.total_distance_km} km • "
        f"{route_result.total_estimated_time_min} min)"
    )
    chart_title = title or default_title

    fig = go.Figure()

    # 1. Base Network (Background Muted Lines)
    bg_x = []
    bg_y = []
    for u, v, _key in graph.edges(keys=True):
        x0, y0 = graph.nodes[u]["lon"], graph.nodes[u]["lat"]
        x1, y1 = graph.nodes[v]["lon"], graph.nodes[v]["lat"]
        bg_x.extend([x0, x1, None])
        bg_y.extend([y0, y1, None])

    fig.add_trace(
        go.Scatter(
            x=bg_x,
            y=bg_y,
            mode="lines",
            line=dict(width=1.5, color="#1F2937"),
            hoverinfo="skip",
            name="Network Track",
            showlegend=False,
        )
    )

    # 2. All Stations (Muted Background Dots)
    all_x = [d["lon"] for _, d in graph.nodes(data=True)]
    all_y = [d["lat"] for _, d in graph.nodes(data=True)]
    fig.add_trace(
        go.Scatter(
            x=all_x,
            y=all_y,
            mode="markers",
            marker=dict(size=4, color="#374151"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    # If unreachable or no path, return base plot with title
    if not route_result.reachable or not route_result.station_path:
        fig.update_layout(
            title=dict(text=f"<b>{chart_title}</b>", font=dict(color="#EF4444", size=14)),
            paper_bgcolor="#0B1120",
            plot_bgcolor="#111827",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            margin=dict(l=20, r=20, t=50, b=20),
            height=height,
        )
        return fig

    # 3. Route Segments (Drawn with line-specific colors & bold width)
    for seg in route_result.segments:
        x0 = graph.nodes[seg.source_station_id]["lon"]
        y0 = graph.nodes[seg.source_station_id]["lat"]
        x1 = graph.nodes[seg.destination_station_id]["lon"]
        y1 = graph.nodes[seg.destination_station_id]["lat"]

        u_name = graph.nodes[seg.source_station_id].get("station_name", seg.source_station_id)
        v_name = graph.nodes[seg.destination_station_id].get("station_name", seg.destination_station_id)

        hover_text = (
            f"<b>{seg.line_name}</b><br>"
            f"{u_name} ➔ {v_name}<br>"
            f"Distance: {seg.distance_km} km<br>"
            f"Time: {seg.estimated_time_min} min"
        )

        fig.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=6.5, color=seg.line_color),
                hoverinfo="text",
                hovertext=hover_text,
                name=seg.line_name,
                showlegend=False,
            )
        )

    # 4. Intermediate Station Nodes on Route
    inter_x = []
    inter_y = []
    inter_hover = []
    inter_names = []

    transfer_stations_set = set(route_result.transfer_stations)

    for sid in route_result.station_path[1:-1]:
        if sid in transfer_stations_set:
            continue
        d = graph.nodes[sid]
        inter_x.append(d["lon"])
        inter_y.append(d["lat"])
        name = d.get("station_name", sid)
        inter_names.append(name)
        inter_hover.append(f"Station: <b>{name}</b> ({sid})<br>Lines: {', '.join(sorted(list(d.get('lines', []))))}")

    if inter_x:
        fig.add_trace(
            go.Scatter(
                x=inter_x,
                y=inter_y,
                mode="markers+text",
                marker=dict(size=11, color="#38BDF8", line=dict(width=2, color="#F8FAFC")),
                text=inter_names,
                textposition="top center",
                textfont=dict(color="#F8FAFC", size=9),
                hoverinfo="text",
                hovertext=inter_hover,
                name="Intermediate Stations",
            )
        )

    # 4b. Transfer Interchange Stations along Route (Gold/Orange Rings)
    if route_result.transfer_stations:
        tr_x = []
        tr_y = []
        tr_hover = []
        tr_names = []

        for sid in route_result.transfer_stations:
            if sid in graph.nodes:
                d = graph.nodes[sid]
                tr_x.append(d["lon"])
                tr_y.append(d["lat"])
                name = d.get("station_name", sid)
                tr_names.append(f"⇄ {name}")
                tr_hover.append(
                    f"<b>TRANSFER INTERCHANGE</b><br>Station: <b>{name}</b> ({sid})<br>"
                    f"Lines: {', '.join(sorted(list(d.get('lines', []))))}"
                )

        if tr_x:
            fig.add_trace(
                go.Scatter(
                    x=tr_x,
                    y=tr_y,
                    mode="markers+text",
                    marker=dict(
                        size=17,
                        symbol="circle-dot",
                        color="#F59E0B",
                        line=dict(width=3, color="#FEF08A"),
                    ),
                    text=tr_names,
                    textposition="bottom center",
                    textfont=dict(color="#FDE047", size=10, family="sans-serif"),
                    hoverinfo="text",
                    hovertext=tr_hover,
                    name="Transfer Stations",
                )
            )

    # 5. Origin Station Marker (Green Star)
    src_id = route_result.source_station_id
    src_data = graph.nodes[src_id]
    src_name = src_data.get("station_name", src_id)
    fig.add_trace(
        go.Scatter(
            x=[src_data["lon"]],
            y=[src_data["lat"]],
            mode="markers+text",
            marker=dict(size=18, symbol="star", color="#22C55E", line=dict(width=2.5, color="#FFFFFF")),
            text=[f"START: {src_name}"],
            textposition="bottom center",
            textfont=dict(color="#22C55E", size=12, family="sans-serif"),
            hoverinfo="text",
            hovertext=[f"<b>Origin Station</b><br>{src_name} ({src_id})"],
            name="Origin",
        )
    )

    # 6. Destination Station Marker (Red Diamond)
    dest_id = route_result.destination_station_id
    dest_data = graph.nodes[dest_id]
    dest_name = dest_data.get("station_name", dest_id)
    fig.add_trace(
        go.Scatter(
            x=[dest_data["lon"]],
            y=[dest_data["lat"]],
            mode="markers+text",
            marker=dict(size=18, symbol="diamond-wide", color="#EF4444", line=dict(width=2.5, color="#FFFFFF")),
            text=[f"END: {dest_name}"],
            textposition="top center",
            textfont=dict(color="#EF4444", size=12, family="sans-serif"),
            hoverinfo="text",
            hovertext=[f"<b>Destination Station</b><br>{dest_name} ({dest_id})"],
            name="Destination",
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>{chart_title}</b>",
            font=dict(color="#F8FAFC", size=15),
            x=0.02,
            y=0.98,
        ),
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111827",
        hovermode="closest",
        legend=dict(
            font=dict(color="#F8FAFC", size=10),
            bgcolor="rgba(17, 24, 39, 0.8)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(showgrid=True, gridcolor="#1F2937", zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            zeroline=False,
            showticklabels=False,
            scaleanchor="x",
            scaleratio=1.14,
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
    )

    return fig


def plot_centrality_network(
    graph: nx.MultiGraph,
    station_results: List[Any],
    metric: str = "betweenness_centrality",
    selected_line: Optional[str] = None,
    highlight_interchanges: bool = True,
    highlight_articulation_points: bool = True,
    title: Optional[str] = None,
    height: int = 700,
) -> go.Figure:
    """Renders an interactive network heatmap showing structural centrality values."""
    res_map = {r.station_id: r for r in station_results}
    fig = go.Figure()

    # 1. Background edges grouped by line
    edge_segments_by_line: dict[str, dict] = {}
    for u, v, _key, data in graph.edges(keys=True, data=True):
        line_id = data.get("line_id", "Unknown")
        line_name = data.get("line_name", line_id)
        line_color = data.get("line_color", "#94A3B8")

        if selected_line and selected_line != "All Lines" and line_name != selected_line and line_id != selected_line:
            continue

        if line_id not in edge_segments_by_line:
            edge_segments_by_line[line_id] = {
                "name": line_name,
                "color": line_color,
                "x": [],
                "y": [],
            }

        x0, y0 = graph.nodes[u]["lon"], graph.nodes[u]["lat"]
        x1, y1 = graph.nodes[v]["lon"], graph.nodes[v]["lat"]
        edge_segments_by_line[line_id]["x"].extend([x0, x1, None])
        edge_segments_by_line[line_id]["y"].extend([y0, y1, None])

    for line_id, segment in edge_segments_by_line.items():
        fig.add_trace(
            go.Scatter(
                x=segment["x"],
                y=segment["y"],
                mode="lines",
                line=dict(width=2.5, color=segment["color"]),
                hoverinfo="none",
                name=segment["name"],
                showlegend=False,
                opacity=0.35,
            )
        )

    # 2. Collect node data
    node_x = []
    node_y = []
    node_color = []
    node_size = []
    node_hover = []
    node_text = []

    ap_x = []
    ap_y = []
    ap_hover = []

    inter_x = []
    inter_y = []
    inter_hover = []

    vals = [
        getattr(r, metric, 0.0) if metric in ("betweenness_centrality", "degree_centrality") else r.degree
        for r in station_results
    ]
    max_val = max(vals) if vals and max(vals) > 0 else 1.0

    metric_label = "Betweenness Centrality" if metric == "betweenness_centrality" else "Degree Centrality"

    for node, data in graph.nodes(data=True):
        sid = str(node)
        r = res_map.get(sid)
        if not r:
            continue

        lines_list = sorted(list(data.get("lines", [])))
        if selected_line and selected_line != "All Lines":
            if not any(selected_line in (lid, data.get("station_name")) for lid in lines_list):
                continue

        val = getattr(r, metric, 0.0) if metric in ("betweenness_centrality", "degree_centrality") else r.degree
        scaled_size = 8 + int(24 * (val / max_val))

        x, y = data["lon"], data["lat"]
        name = data.get("station_name", sid)

        node_x.append(x)
        node_y.append(y)
        node_color.append(val)
        node_size.append(scaled_size)

        lines_str = ", ".join(r.line_names) or "None"
        hover_info = (
            f"<b>{name}</b> ({sid})<br>"
            f"<b>{metric_label}:</b> {val:.5f}<br>"
            f"Degree: {r.degree} | Lines: {r.line_count} ({lines_str})<br>"
            f"Interchange: {'Yes' if r.is_interchange else 'No'}<br>"
            f"Articulation Point: {'Yes (Cut-Vertex)' if r.is_articulation_point else 'No'}"
        )
        node_hover.append(hover_info)

        if val >= 0.7 * max_val:
            node_text.append(name)
        else:
            node_text.append("")

        if highlight_articulation_points and r.is_articulation_point:
            ap_x.append(x)
            ap_y.append(y)
            ap_hover.append(f"<b>CRITICAL CUT-VERTEX</b><br>{name} ({sid})")

        if highlight_interchanges and r.is_interchange:
            inter_x.append(x)
            inter_y.append(y)
            inter_hover.append(f"<b>INTERCHANGE HUB</b><br>{name} ({sid})")

    # Add Main Node Scatter with continuous colorscale
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(
                size=node_size,
                color=node_color,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(
                    title=dict(text=metric_label, font=dict(color="#F8FAFC", size=11)),
                    tickfont=dict(color="#F8FAFC", size=9),
                    x=1.02,
                ),
                line=dict(width=1.5, color="#FFFFFF"),
            ),
            text=node_text,
            textposition="top center",
            textfont=dict(color="#FDE047", size=9),
            hoverinfo="text",
            hovertext=node_hover,
            name="Stations",
            showlegend=False,
        )
    )

    # Highlight Interchanges with outer cyan rings
    if inter_x:
        fig.add_trace(
            go.Scatter(
                x=inter_x,
                y=inter_y,
                mode="markers",
                marker=dict(
                    size=16,
                    symbol="circle-open",
                    line=dict(width=2.5, color="#38BDF8"),
                ),
                hoverinfo="text",
                hovertext=inter_hover,
                name="Interchange Station",
                showlegend=True,
            )
        )

    # Highlight Articulation Points with red diamonds
    if ap_x:
        fig.add_trace(
            go.Scatter(
                x=ap_x,
                y=ap_y,
                mode="markers",
                marker=dict(
                    size=18,
                    symbol="diamond-open",
                    line=dict(width=2.5, color="#EF4444"),
                ),
                hoverinfo="text",
                hovertext=ap_hover,
                name="Articulation Point (Cut-Vertex)",
                showlegend=True,
            )
        )

    chart_title = title or f"<b>Station Centrality Heatmap: {metric_label}</b>"

    fig.update_layout(
        title=dict(text=chart_title, font=dict(color="#F8FAFC", size=15), x=0.02, y=0.98),
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111827",
        hovermode="closest",
        legend=dict(
            font=dict(color="#F8FAFC", size=10),
            bgcolor="rgba(17, 24, 39, 0.8)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(showgrid=True, gridcolor="#1F2937", zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            zeroline=False,
            showticklabels=False,
            scaleanchor="x",
            scaleratio=1.14,
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
    )

    return fig


def plot_top_stations(
    station_results: List[Any],
    metric: str = "betweenness_centrality",
    top_n: int = 10,
    title: Optional[str] = None,
) -> go.Figure:
    """Renders a clean horizontal bar chart showing top N stations by a centrality metric."""
    metric_label = "Betweenness Centrality" if metric == "betweenness_centrality" else "Degree Centrality"

    sorted_res = sorted(
        station_results,
        key=lambda r: getattr(r, metric, 0.0),
        reverse=True,
    )[:top_n]
    sorted_res.reverse()

    station_names = [f"{r.station_name} ({r.station_id})" for r in sorted_res]
    vals = [getattr(r, metric, 0.0) for r in sorted_res]
    colors = [
        "#EF4444" if r.is_articulation_point else ("#38BDF8" if r.is_interchange else "#94A3B8")
        for r in sorted_res
    ]

    hover_texts = [
        (
            f"<b>{r.station_name}</b><br>{metric_label}: {v:.5f}<br>"
            f"Lines: {r.line_count}<br>Interchange: {r.is_interchange}"
        )
        for r, v in zip(sorted_res, vals)
    ]

    fig = go.Figure(
        go.Bar(
            x=vals,
            y=station_names,
            orientation="h",
            marker=dict(color=colors),
            hoverinfo="text",
            hovertext=hover_texts,
            text=[f"{v:.4f}" for v in vals],
            textposition="auto",
        )
    )

    fig_title = title or f"<b>Top {top_n} Stations by {metric_label}</b>"

    fig.update_layout(
        title=dict(text=fig_title, font=dict(color="#F8FAFC", size=14), x=0.02, y=0.98),
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111827",
        font=dict(color="#F8FAFC"),
        xaxis=dict(title=metric_label, showgrid=True, gridcolor="#1F2937"),
        yaxis=dict(showgrid=False),
        margin=dict(l=20, r=20, t=50, b=40),
        height=max(360, top_n * 30),
    )

    return fig


def plot_closure_comparison(
    original_graph: nx.MultiGraph,
    simulated_graph: nx.MultiGraph,
    closed_station_ids: List[str],
    original_route_stations: Optional[List[str]] = None,
    new_route_stations: Optional[List[str]] = None,
    color_by_component: bool = False,
    title: Optional[str] = None,
    height: int = 700,
) -> go.Figure:
    """Renders side-by-side or layered offline visualization highlighting network disruption."""
    fig = go.Figure()

    closed_set = {str(sid) for sid in closed_station_ids}

    comp_map = {}
    if color_by_component:
        import plotly.colors as pcolors
        colors_pool = pcolors.qualitative.Plotly + pcolors.qualitative.Dark24
        components = sorted(list(nx.connected_components(simulated_graph)), key=len, reverse=True)
        for c_idx, c_nodes in enumerate(components):
            c_color = colors_pool[c_idx % len(colors_pool)]
            for node in c_nodes:
                comp_map[str(node)] = (c_idx + 1, c_color)

    # 1. Background Tracks (Remaining vs Severed)
    active_edge_x = []
    active_edge_y = []
    severed_edge_x = []
    severed_edge_y = []

    for u, v, _key, data in original_graph.edges(keys=True, data=True):
        u_str = str(u)
        v_str = str(v)
        x0, y0 = original_graph.nodes[u]["lon"], original_graph.nodes[u]["lat"]
        x1, y1 = original_graph.nodes[v]["lon"], original_graph.nodes[v]["lat"]

        if u_str in closed_set or v_str in closed_set:
            severed_edge_x.extend([x0, x1, None])
            severed_edge_y.extend([y0, y1, None])
        else:
            active_edge_x.extend([x0, x1, None])
            active_edge_y.extend([y0, y1, None])

    if severed_edge_x:
        fig.add_trace(
            go.Scatter(
                x=severed_edge_x,
                y=severed_edge_y,
                mode="lines",
                line=dict(width=2.0, color="#EF4444", dash="dot"),
                hoverinfo="none",
                name="Severed Track Connections",
                opacity=0.45,
            )
        )

    if active_edge_x:
        fig.add_trace(
            go.Scatter(
                x=active_edge_x,
                y=active_edge_y,
                mode="lines",
                line=dict(width=2.5, color="#475569"),
                hoverinfo="none",
                name="Active Surviving Tracks",
                opacity=0.4,
            )
        )

    # 2. Original vs New Route Overlays
    if original_route_stations and len(original_route_stations) > 1:
        orig_rx = []
        orig_ry = []
        for sid in original_route_stations:
            if sid in original_graph.nodes:
                orig_rx.append(original_graph.nodes[sid]["lon"])
                orig_ry.append(original_graph.nodes[sid]["lat"])
        if orig_rx:
            fig.add_trace(
                go.Scatter(
                    x=orig_rx,
                    y=orig_ry,
                    mode="lines",
                    line=dict(width=4.0, color="#64748B", dash="dash"),
                    hoverinfo="none",
                    name="Original Baseline Route",
                )
            )

    if new_route_stations and len(new_route_stations) > 1:
        new_rx = []
        new_ry = []
        for sid in new_route_stations:
            if sid in simulated_graph.nodes:
                new_rx.append(simulated_graph.nodes[sid]["lon"])
                new_ry.append(simulated_graph.nodes[sid]["lat"])
        if new_rx:
            fig.add_trace(
                go.Scatter(
                    x=new_rx,
                    y=new_ry,
                    mode="lines",
                    line=dict(width=5.0, color="#22C55E"),
                    hoverinfo="none",
                    name="Active Detour Route",
                )
            )

    # 3. Active Surviving Stations
    active_x = []
    active_y = []
    active_names = []
    active_hovers = []
    active_colors = []

    for node, data in simulated_graph.nodes(data=True):
        sid = str(node)
        active_x.append(data["lon"])
        active_y.append(data["lat"])
        sname = data.get("station_name", sid)
        active_names.append(sname)

        if color_by_component and sid in comp_map:
            c_id, c_col = comp_map[sid]
            active_colors.append(c_col)
            comp_info = f"<br>Component: <b>Group {c_id}</b>"
        else:
            active_colors.append("#38BDF8")
            comp_info = ""

        deg = simulated_graph.degree[node]
        active_hovers.append(
            f"<b>{sname}</b> ({sid})<br>Surviving Degree: {deg}{comp_info}"
        )

    if active_x:
        fig.add_trace(
            go.Scatter(
                x=active_x,
                y=active_y,
                mode="markers",
                marker=dict(size=8, color=active_colors, line=dict(width=1, color="#F8FAFC")),
                hoverinfo="text",
                hovertext=active_hovers,
                name="Operational Stations",
                showlegend=True,
            )
        )

    # 4. Closed Stations (Red 'X' Markers)
    closed_x = []
    closed_y = []
    closed_hovers = []
    closed_texts = []

    for sid in closed_station_ids:
        if sid in original_graph.nodes:
            d = original_graph.nodes[sid]
            closed_x.append(d["lon"])
            closed_y.append(d["lat"])
            sname = d.get("station_name", sid)
            closed_texts.append(f"✕ {sname}")
            closed_hovers.append(
                f"<b>CLOSED STATION</b><br>{sname} ({sid})<br>Status: Disrupted / Out of Service"
            )

    if closed_x:
        fig.add_trace(
            go.Scatter(
                x=closed_x,
                y=closed_y,
                mode="markers+text",
                marker=dict(size=16, symbol="x", color="#EF4444", line=dict(width=3, color="#FFFFFF")),
                text=closed_texts,
                textposition="bottom center",
                textfont=dict(color="#EF4444", size=11, family="sans-serif"),
                hoverinfo="text",
                hovertext=closed_hovers,
                name="Closed Stations",
                showlegend=True,
            )
        )

    chart_title = title or "<b>Metro Network Disruption & Closure Impact View</b>"

    fig.update_layout(
        title=dict(text=chart_title, font=dict(color="#F8FAFC", size=15), x=0.02, y=0.98),
        paper_bgcolor="#0B1120",
        plot_bgcolor="#111827",
        hovermode="closest",
        legend=dict(
            font=dict(color="#F8FAFC", size=10),
            bgcolor="rgba(17, 24, 39, 0.8)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(showgrid=True, gridcolor="#1F2937", zeroline=False, showticklabels=False),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            zeroline=False,
            showticklabels=False,
            scaleanchor="x",
            scaleratio=1.14,
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=height,
    )

    return fig
