"""Route optimizer over local weighted road datasets with multi-algorithm routing."""

import streamlit as st
from streamlit_folium import st_folium

from src.graph.dataset_service import list_datasets, load
from src.routing.route_alternatives import find_alternative_routes
from src.routing.route_comparison import compare_routes
from src.routing.routing_service import find_route
from src.ui.formatting import format_distance, format_time
from src.ui.sidebar import render_app_sidebar
from src.ui.state import set_active_dataset_id
from src.ui.theme import inject_custom_theme
from src.visualization.alternative_route_maps import alternative_route_maps
from src.visualization.route_maps import route_map


def optimizer() -> None:
    """Render the Route Optimizer page with single and multi-path routing."""
    inject_custom_theme()

    st.title("Route Optimizer")
    st.caption(
        "Travel time is estimated from road lengths and speed assumptions. "
        "It is not live traffic data."
    )

    with st.form("route"):
        dataset = st.selectbox("Local dataset", list_datasets())
        source = st.text_input("Source junction ID", value="0")
        target = st.text_input("Destination junction ID", value="1")
        algorithm = st.radio(
            "Algorithm", ["Dijkstra", "A*", "Bidirectional Dijkstra"], horizontal=True
        )
        alternatives = st.checkbox("Enable alternative routes")
        k = st.number_input("Number of routes", min_value=1, max_value=5, value=3)
        objective = st.radio(
            "Objective", ["Shortest Distance", "Shortest Estimated Travel Time"], horizontal=True
        )
        run = st.form_submit_button("Run Route Optimization")

    try:
        active_info = load(dataset)
        set_active_dataset_id(dataset)
        render_app_sidebar(active_info.graph, active_info.metadata.dataset_name, active_info.origin)
    except Exception:
        render_app_sidebar()

    if run:
        st.session_state.pop("route_output", None)
        st.session_state.pop("alternatives_output", None)
        try:
            info = load(dataset)
            route = find_route(
                info.graph,
                int(source),
                int(target),
                {
                    "Dijkstra": "dijkstra",
                    "A*": "astar",
                    "Bidirectional Dijkstra": "bidirectional_dijkstra",
                }[algorithm],
                "distance" if objective == "Shortest Distance" else "travel_time",
            )
            if alternatives:
                result = find_alternative_routes(
                    info.graph, int(source), int(target), int(k), route.objective
                )
                st.session_state["alternatives_output"] = (
                    result.routes,
                    alternative_route_maps(info.graph, result.routes),
                )
            st.session_state["route_output"] = (
                info.origin,
                route,
                route_map(info.graph, route) if route.is_reachable else None,
            )
        except (OSError, ValueError, TypeError, KeyError) as error:
            st.error(f"Routing failed: {error}")

    if "route_output" not in st.session_state:
        return

    origin, route, view = st.session_state["route_output"]
    st.caption(origin)

    if not route.is_reachable:
        st.warning("Destination is unreachable")
        return

    st.success("Route validated")

    # Responsive Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Distance", format_distance(route.total_distance_m))
    c2.metric("Estimated Time", format_time(route.total_travel_time_s))
    c3.metric("Nodes Expanded", f"{route.nodes_expanded:,}")
    c4.metric("Edges Examined", f"{route.edges_examined:,}")

    st.write(
        {
            "Algorithm": route.algorithm,
            "Objective": route.objective,
            "Distance (km)": route.total_distance_m / 1000,
            "Estimated time (min)": route.total_travel_time_s / 60,
            "Road edges": len(route.edge_path),
            "Nodes expanded": route.nodes_expanded,
            "Edges examined": route.edges_examined,
            "Status": route.status,
        }
    )
    st.caption(f"Heuristic: {route.diagnostics.heuristic_type}")

    tab_map, tab_details = st.tabs(["Route Map", "Turn-by-Turn Waypoints & Diagnostics"])

    with tab_map:
        st_folium(view, returned_objects=[], height=430)

    with tab_details:
        st.subheader("Route Waypoints")
        st.write("Node sequence:", route.node_path)
        st.write("Directed road edge sequence (u, v, key):", route.edge_path)

    if "alternatives_output" in st.session_state:
        st.divider()
        st.subheader("Alternative Routes (Yen's K-Shortest Paths)")
        routes, maps = st.session_state["alternatives_output"]
        st.dataframe(compare_routes(routes), use_container_width=True)
        if routes:
            selected = st.selectbox(
                "Displayed alternative", range(len(routes)), format_func=lambda i: f"Route {i + 1}"
            )
            st_folium(
                maps[selected], returned_objects=[], height=430, key=f"alternative-{selected}"
            )


if __name__ == "__main__":
    optimizer()
