"""Inspect the active road dataset, topological statistics, and spatial visualization."""

from dataclasses import asdict
from itertools import islice

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from config import APP_DESCRIPTION, APP_NAME
from src.graph.dataset_service import acquire, list_datasets, load
from src.graph.representation import adjacency_matrix, build_adjacency
from src.graph.statistics import statistics
from src.graph.validation import validate
from src.ui.formatting import format_distance, format_percentage
from src.ui.sidebar import render_app_sidebar
from src.ui.state import set_active_dataset_id
from src.ui.theme import inject_custom_theme
from src.visualization.maps import road_map


def overview() -> None:
    """Render the Overview page with topological inspection and road network map."""
    inject_custom_theme()

    st.title(APP_NAME)
    st.caption("Smart City Traffic & Emergency Route Optimizer · Large-Scale Graph Analysis")
    st.write(APP_DESCRIPTION)
    st.info("Phase 10 of 12 · Full System Integration · (Foundation established in Phase 3 of 12)")

    if "next_dataset" in st.session_state:
        st.session_state["picker"] = st.session_state.pop("next_dataset")

    identifier = st.selectbox("Dataset", list_datasets(), key="picker")
    refresh = st.checkbox("Refresh cached OpenStreetMap data")
    fetch = st.button("Acquire Connaught Place road network")

    if fetch or st.session_state.get("selected") != identifier:
        try:
            with st.spinner("Validating road network…"):
                result = acquire(force_refresh=refresh) if fetch else load(identifier)
        except (ValueError, OSError, TypeError) as error:
            st.error(f"Invalid or unavailable dataset: {error}")
            return
        graph = result.graph
        st.session_state["selected"] = result.metadata.dataset_id
        set_active_dataset_id(result.metadata.dataset_id)
        st.session_state["dataset"] = result
        st.session_state["derived"] = (
            statistics(graph),
            validate(graph, result.metadata),
            build_adjacency(graph),
            road_map(graph),
        )
        if fetch and result.metadata.dataset_id != identifier:
            st.session_state["next_dataset"] = result.metadata.dataset_id
            st.rerun()

    result = st.session_state["dataset"]
    graph = result.graph
    stats, report, adj, map_view = st.session_state["derived"]

    render_app_sidebar(graph, result.metadata.dataset_name, result.origin)

    st.subheader(result.metadata.dataset_name)
    st.caption(f"{result.origin} · {result.metadata.graph_type} · {result.metadata.dataset_id}")
    if result.notice:
        st.warning(result.notice)

    # Validation banner
    if report.issues:
        st.warning("Valid with warnings")
    else:
        st.success("Valid")

    for issue in report.issues:
        st.caption(issue.message)

    # High-level responsive metric cards
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Junctions (|V|)", f"{stats.nodes:,}")
    m2.metric("Directed Roads (|E|)", f"{stats.directed_edges:,}")
    m3.metric("Total Length", format_distance(stats.total_length_m))
    m4.metric(
        "Strong Components",
        f"{stats.strong_components} (Weak: {stats.weak_components})",
    )

    tab_map, tab_stats, tab_inspect = st.tabs(
        ["Geographic Road Map", "Network Statistics", "Adjacency & Raw Structure"]
    )

    with tab_map:
        st.caption(
            "Map displays up to the first 500 junctions and 500 directed road segments. "
            "Road overlays can be viewed without background tiles."
        )
        st_folium(map_view, height=430, returned_objects=[], key=result.metadata.dataset_id)

    with tab_stats:
        st.subheader("Topological Summary Metrics")
        st.write(asdict(stats))

        st.caption(
            f"Average In-Degree: {stats.average_in_degree:.2f} · "
            f"Average Out-Degree: {stats.average_out_degree:.2f} · "
            f"Network Density: {format_percentage(stats.density, decimals=4)}"
        )

    with tab_inspect:
        st.subheader("Graph Inspection")
        c_left, c_right = st.columns(2)
        with c_left:
            st.caption("Sample Nodes (first 4):")
            st.json({str(n): d for n, d in islice(graph.nodes(data=True), 4)})
        with c_right:
            st.caption("Sample Edges (first 4):")
            st.json(
                [
                    {"edge": str((u, v, k)), **{a: str(b) for a, b in d.items()}}
                    for u, v, k, d in islice(graph.edges(keys=True, data=True), 4)
                ]
            )

        st.subheader("Adjacency List Inspection")
        node = st.selectbox("Outgoing roads from junction", list(graph))
        st.write([str(edge) for edge in adj[node][:10]])

        st.subheader("Adjacency Matrix (Sample Subgraph)")
        order = list(islice(graph, 8))
        objective = st.radio("Matrix weight", ["length_m", "travel_time_s"], horizontal=True)
        st.dataframe(
            pd.DataFrame(adjacency_matrix(graph, order, objective), index=order, columns=order)
        )


if __name__ == "__main__":
    overview()
