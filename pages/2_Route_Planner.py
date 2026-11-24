"""Page 2: Route Planner."""

import pandas as pd
import streamlit as st

from src.algorithms.bfs import find_route_bfs
from src.algorithms.comparison import compare_routing_algorithms
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.minimum_transfers import (
    find_route_min_transfers_then_fastest,
    find_route_minimum_transfers,
)
from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra
from src.core.settings import APP_ICON
from src.ui.components import (
    render_empty_state,
    render_metric_card,
    render_page_header,
    render_section_header,
)
from src.ui.session_state import get_current_dataset_and_graph, init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme_css
from src.visualization.delhi_metro_map import plot_metro_route

st.set_page_config(page_title="Route Planner - MetroGraph", page_icon=APP_ICON, layout="wide")
st.markdown(apply_theme_css(), unsafe_allow_html=True)
init_session_state()
render_sidebar()

stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation = (
    get_current_dataset_and_graph()
)

render_page_header(
    title="Smart Route Planner",
    subtitle=(
        "Multi-objective route optimization and line-aware itinerary planner "
        f"for {metadata.get('dataset_name', '')}."
    ),
    badge="PAGE 2",
)

# Station Name-to-ID lookups
station_id_to_name = dict(zip(stations_df["station_id"], stations_df["station_name"]))
station_display_list = sorted([f"{name} ({sid})" for sid, name in station_id_to_name.items()])

# Determine default indices safely from session state
src_idx = 0
if st.session_state.get("selected_source") in station_id_to_name:
    curr_src_id = st.session_state["selected_source"]
    curr_src_disp = f"{station_id_to_name[curr_src_id]} ({curr_src_id})"
    if curr_src_disp in station_display_list:
        src_idx = station_display_list.index(curr_src_disp)

dst_idx = min(8, len(station_display_list) - 1)
if st.session_state.get("selected_destination") in station_id_to_name:
    curr_dst_id = st.session_state["selected_destination"]
    curr_dst_disp = f"{station_id_to_name[curr_dst_id]} ({curr_dst_id})"
    if curr_dst_disp in station_display_list:
        dst_idx = station_display_list.index(curr_dst_disp)

render_section_header("1. Journey Origin, Destination & Optimization Objective", icon="🎯")
c1, c2, c3 = st.columns(3)
with c1:
    source_display = st.selectbox("Source Station", station_display_list, index=src_idx)
with c2:
    destination_display = st.selectbox("Destination Station", station_display_list, index=dst_idx)
with c3:
    obj_choices = [
        "Minimum Transfers (0-1 BFS)",
        "Minimum Transfers, Then Fastest (Lexicographic)",
        "Fastest with Transfer Penalty (Dijkstra)",
        "Minimum Stops (BFS)",
        "Minimum Travel Time (Dijkstra)",
        "Minimum Distance (Dijkstra)",
    ]
    curr_obj = st.session_state.get("routing_objective", obj_choices[0])
    obj_idx = obj_choices.index(curr_obj) if curr_obj in obj_choices else 0
    objective_label = st.selectbox("Routing Objective", obj_choices, index=obj_idx)

# Transfer Penalty slider
transfer_penalty_val = st.session_state.get("transfer_penalty_minutes", 5.0)
if "Transfer Penalty" in objective_label:
    transfer_penalty_val = st.slider(
        "Transfer Wait / Platform Friction Penalty (minutes)",
        min_value=0.0,
        max_value=15.0,
        value=transfer_penalty_val,
        step=0.5,
        help="Simulates walking and platform waiting friction added whenever a rider changes lines.",
    )
    st.session_state["transfer_penalty_minutes"] = transfer_penalty_val

source_id = source_display.split("(")[-1].rstrip(")")
dest_id = destination_display.split("(")[-1].rstrip(")")
st.session_state["selected_source"] = source_id
st.session_state["selected_destination"] = dest_id
st.session_state["routing_objective"] = objective_label

btn_c1, btn_c2, btn_c3 = st.columns([0.22, 0.28, 0.50])
with btn_c1:
    find_btn = st.button("🚀 Find Optimal Route", type="primary", use_container_width=True)
with btn_c2:
    compare_btn = st.button("⚖️ Compare All Algorithms", use_container_width=True)
with btn_c3:
    if st.button("🔄 Clear Results"):
        st.session_state["route_result"] = None
        st.session_state["comparison_df"] = None
        st.rerun()

# Execution Handlers
if find_btn:
    st.session_state["comparison_df"] = None
    with st.spinner("Computing optimal line-aware route..."):
        if "0-1 BFS" in objective_label:
            st.session_state["route_result"] = find_route_minimum_transfers(
                metro_graph, source_id, dest_id
            )
        elif "Lexicographic" in objective_label:
            st.session_state["route_result"] = find_route_min_transfers_then_fastest(
                metro_graph, source_id, dest_id
            )
        elif "Transfer Penalty" in objective_label:
            st.session_state["route_result"] = find_route_transfer_aware_dijkstra(
                metro_graph, source_id, dest_id, transfer_penalty_min=transfer_penalty_val
            )
        elif "Minimum Stops" in objective_label:
            st.session_state["route_result"] = find_route_bfs(metro_graph, source_id, dest_id)
        elif "Time" in objective_label:
            st.session_state["route_result"] = find_route_dijkstra(
                metro_graph, source_id, dest_id, objective="minimum_time"
            )
        else:
            st.session_state["route_result"] = find_route_dijkstra(
                metro_graph, source_id, dest_id, objective="minimum_distance"
            )

if compare_btn:
    with st.spinner("Executing multi-objective algorithm benchmark..."):
        comp_df, results_map = compare_routing_algorithms(
            metro_graph, source_id, dest_id, transfer_penalty_min=transfer_penalty_val
        )
        st.session_state["comparison_df"] = comp_df
        st.session_state["route_result"] = results_map.get("0-1 BFS (Min Transfers)")

# --- Display Comparison Table if Present ---
if st.session_state.get("comparison_df") is not None:
    render_section_header("2. Multi-Objective Algorithm Evaluation", icon="📊")
    st.dataframe(st.session_state["comparison_df"], use_container_width=True, hide_index=True)
    st.caption(
        "Notice: BFS guarantees minimum stops. Dijkstra guarantees minimum edge weights (travel time/distance). "
        "0-1 BFS minimizes transfers. Lexicographic Dijkstra minimizes transfers then time. "
        "Transfer-Aware Dijkstra optimizes combined segment time plus transfer friction."
    )
    st.divider()

# --- Display Route Results Panel ---
res = st.session_state.get("route_result")
if res is not None:
    if not res.reachable:
        st.error(f"❌ {res.message}")
    else:
        src_name = station_id_to_name.get(res.source_station_id, res.source_station_id)
        dst_name = station_id_to_name.get(res.destination_station_id, res.destination_station_id)

        render_section_header(f"Journey Summary: {src_name} ➔ {dst_name}", icon="📍")

        m1, m2, m3, m4, m5, m6 = st.columns(6)
        with m1:
            render_metric_card("Stops", res.total_stops)
        with m2:
            render_metric_card("Transfers", res.transfer_count)
        with m3:
            render_metric_card("In-Transit Time", f"{res.segment_travel_time_min:.1f} min")
        with m4:
            render_metric_card(
                "Modeled Time",
                f"{res.total_modeled_journey_time_min:.1f} min",
            )
        with m5:
            render_metric_card("Distance", f"{res.total_distance_km:.2f} km")
        with m6:
            render_metric_card("Latency", f"{res.runtime_ms:.2f} ms")

        # Step-by-step Passenger Transfer Instructions Box
        if res.transfer_instructions:
            with st.expander("🧭 Step-by-Step Passenger Directions", expanded=True):
                for step_txt in res.transfer_instructions:
                    st.markdown(f"- {step_txt}")

        # Route Visualizer
        render_section_header("Highlighted Metro Route Schematic", icon="🗺️")
        fig = plot_metro_route(metro_graph, res)
        st.plotly_chart(fig, use_container_width=True)

        # Tabbed Itinerary & Segment Breakdown
        itinerary_tab, segments_tab = st.tabs(["Station-by-Station Itinerary", "Segment Travel Details"])

        with itinerary_tab:
            st.markdown("#### 🚉 Stop Progression")
            if res.total_stops == 0:
                st.write(f"Origin and destination are identical: **{src_name}** (0 stops)")
            else:
                itinerary_items = []
                for idx, sid in enumerate(res.station_path):
                    sname = station_id_to_name.get(sid, sid)
                    is_transfer = sid in res.transfer_stations
                    badge = " 🔄 **[TRANSFER INTERCHANGE]**" if is_transfer else ""

                    if idx == 0:
                        itinerary_items.append(f"🟢 **Start:** {sname} (`{sid}`)")
                    elif idx == len(res.station_path) - 1:
                        itinerary_items.append(f"🔴 **Arrive:** {sname} (`{sid}`)")
                    else:
                        seg = res.segments[idx - 1]
                        line_info = f"&nbsp;&nbsp;&nbsp;&nbsp;↓ *[{seg.line_name}]*<br/>"
                        stop_info = f"⚪ **Stop {idx}:** {sname} (`{sid}`){badge}"
                        itinerary_items.append(f"{line_info}{stop_info}")

                st.markdown("<br/>".join(itinerary_items), unsafe_allow_html=True)

        with segments_tab:
            st.markdown("#### 📋 Segment Details")
            seg_rows = []
            for i, seg in enumerate(res.segments, start=1):
                u_name = station_id_to_name.get(seg.source_station_id, seg.source_station_id)
                v_name = station_id_to_name.get(seg.destination_station_id, seg.destination_station_id)
                is_transfer_hop = (i > 1) and (seg.line_id != res.segments[i - 2].line_id)

                seg_rows.append({
                    "Step": i,
                    "From Station": f"{u_name} ({seg.source_station_id})",
                    "To Station": f"{v_name} ({seg.destination_station_id})",
                    "Metro Line": seg.line_name,
                    "Transfer Here": "⇄ Yes" if is_transfer_hop else "No",
                    "Edge Key": seg.edge_key,
                    "Distance (km)": f"{seg.distance_km:.2f}",
                    "Est. Time (min)": f"{seg.estimated_time_min:.1f}",
                    "Provenance": seg.weight_provenance,
                })

            st.dataframe(pd.DataFrame(seg_rows), use_container_width=True, hide_index=True)
else:
    render_empty_state(
        title="No Route Calculated Yet",
        message="Select stations above and click 'Find Optimal Route' or 'Compare All Algorithms'.",
        icon="🚇",
    )
