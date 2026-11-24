"""Page 5: Algorithm Lab."""

import math

import pandas as pd
import plotly.express as px
import streamlit as st

from src.algorithms.comparison import compare_routing_algorithms
from src.core.settings import APP_ICON
from src.ui.components import (
    render_metric_card,
    render_page_header,
    render_section_header,
)
from src.ui.session_state import get_current_dataset_and_graph, init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.theme import THEME_COLORS, apply_theme_css

st.set_page_config(page_title="Algorithm Lab - MetroGraph", page_icon=APP_ICON, layout="wide")
st.markdown(apply_theme_css(), unsafe_allow_html=True)
init_session_state()
render_sidebar()

stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation = (
    get_current_dataset_and_graph()
)

render_page_header(
    title="Algorithm Benchmarking Lab",
    subtitle=(
        "Theoretical complexity, comparative runtime evaluation, and empirical profiling "
        f"for {metadata.get('dataset_name', '')}."
    ),
    badge="PAGE 5",
)

render_section_header("1. Active Graph Scale & Algorithmic Bounds", icon="📐")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Vertices |V|", metro_graph.number_of_nodes())
with c2:
    render_metric_card("Edges |E|", metro_graph.number_of_edges())
with c3:
    v = metro_graph.number_of_nodes()
    e = metro_graph.number_of_edges()
    render_metric_card("BFS Bound |V| + |E|", v + e)
with c4:
    dijkstra_bound = int((v + e) * math.log2(max(v, 2)))
    render_metric_card("Dijkstra Bound", f"{dijkstra_bound:,} ops")

st.markdown("<br/>", unsafe_allow_html=True)

render_section_header("2. Theoretical Complexity Framework", icon="🔬")
comparison_data = [
    {
        "Algorithm": "Breadth-First Search (BFS)",
        "Optimization Objective": "Minimum Station Stops",
        "Cost Structure": "Unweighted / Unit (w = 1)",
        "State Space": "Station Nodes V",
        "Time Complexity": "O(V + E)",
        "Phase": "Phase 3",
    },
    {
        "Algorithm": "Dijkstra (Priority Queue)",
        "Optimization Objective": "Shortest Travel Time / Distance",
        "Cost Structure": "Additive Edge Weights",
        "State Space": "Station Nodes V",
        "Time Complexity": "O((V + E) log V)",
        "Phase": "Phase 3",
    },
    {
        "Algorithm": "0-1 BFS",
        "Optimization Objective": "Minimum Transfers",
        "Cost Structure": "0 for same line, 1 for line switch",
        "State Space": "Expanded State (V x L)",
        "Time Complexity": "O(L * (V + E))",
        "Phase": "Phase 4",
    },
    {
        "Algorithm": "Lexicographic Dijkstra",
        "Optimization Objective": "Min Transfers then Shortest Time",
        "Cost Structure": "Tuple: (Transfers, Travel Time)",
        "State Space": "Expanded State (V x L)",
        "Time Complexity": "O(L * (V + E) log(L * V))",
        "Phase": "Phase 4",
    },
    {
        "Algorithm": "Transfer-Aware Dijkstra",
        "Optimization Objective": "Fastest with Transfer Friction Penalty",
        "Cost Structure": "Travel Time + Transfer Penalty",
        "State Space": "Expanded State (V x L)",
        "Time Complexity": "O(L * (V + E) log(L * V))",
        "Phase": "Phase 4",
    },
    {
        "Algorithm": "Degree Centrality",
        "Optimization Objective": "Local Station Neighborhood Connectivity",
        "Cost Structure": "Degree / (N - 1)",
        "State Space": "Analytical Simple Graph V",
        "Time Complexity": "O(V + E)",
        "Phase": "Phase 5",
    },
    {
        "Algorithm": "Betweenness Centrality (Brandes)",
        "Optimization Objective": "Shortest-Hop Path Load & Bridge Vitality",
        "Cost Structure": "Path-counting fractions",
        "State Space": "Analytical Simple Graph V",
        "Time Complexity": "O(V * E)",
        "Phase": "Phase 5",
    },
    {
        "Algorithm": "Cut-Vertex Detection (Tarjan DFS)",
        "Optimization Objective": "Network Segmentation & Articulation Points",
        "Cost Structure": "DFS Low-link Discovery",
        "State Space": "Analytical Simple Graph V",
        "Time Complexity": "O(V + E)",
        "Phase": "Phase 5",
    },
]
st.dataframe(comparison_data, use_container_width=True, hide_index=True)

st.divider()

render_section_header("3. Live Multi-Algorithm Route Comparison & Metrics", icon="🧪")
station_id_to_name = dict(zip(stations_df["station_id"], stations_df["station_name"]))
station_display_list = sorted([f"{name} ({sid})" for sid, name in station_id_to_name.items()])

qc1, qc2, qc3 = st.columns(3)
with qc1:
    bench_src = st.selectbox("Origin", station_display_list, index=0, key="lab_src")
with qc2:
    default_lab_dest = min(10, len(station_display_list) - 1)
    bench_dst = st.selectbox(
        "Destination",
        station_display_list,
        index=default_lab_dest,
        key="lab_dst",
    )
with qc3:
    penalty_param = st.slider("Transfer Wait Penalty (min)", 0.0, 15.0, 5.0, 0.5, key="lab_pen")

bench_src_id = bench_src.split("(")[-1].rstrip(")")
bench_dst_id = bench_dst.split("(")[-1].rstrip(")")

if st.button("⚡ Run Comparative Analysis", type="primary"):
    with st.spinner("Executing all 6 routing algorithms..."):
        comp_df, _ = compare_routing_algorithms(
            metro_graph, bench_src_id, bench_dst_id, transfer_penalty_min=penalty_param
        )
        st.session_state["lab_comp_df"] = comp_df

if st.session_state.get("lab_comp_df") is not None:
    comp_df = st.session_state["lab_comp_df"]
    if isinstance(comp_df, pd.DataFrame) and not comp_df.empty:
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        # Plotly comparison charts
        ch_col1, ch_col2 = st.columns(2)
        with ch_col1:
            time_col = (
                "Modeled Journey Time (min)"
                if "Modeled Journey Time (min)" in comp_df.columns
                else comp_df.columns[0]
            )
            color_col = "Transfers" if "Transfers" in comp_df.columns else None
            fig_time = px.bar(
                comp_df,
                x="Algorithm",
                y=time_col,
                color=color_col,
                title="Modeled Travel Time & Line Transfers",
                color_continuous_scale="Viridis",
            )
            fig_time.update_layout(
                paper_bgcolor=THEME_COLORS["card_bg"],
                plot_bgcolor=THEME_COLORS["card_bg"],
                font_color=THEME_COLORS["text_main"],
                margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig_time, use_container_width=True)

        with ch_col2:
            runtime_col = (
                "Runtime (ms)"
                if "Runtime (ms)" in comp_df.columns
                else ("Execution Time (ms)" if "Execution Time (ms)" in comp_df.columns else comp_df.columns[0])
            )
            fig_lat = px.bar(
                comp_df,
                x="Algorithm",
                y=runtime_col,
                title="Algorithm Execution Latency (ms)",
                color_discrete_sequence=[THEME_COLORS["primary"]],
            )
            fig_lat.update_layout(
                paper_bgcolor=THEME_COLORS["card_bg"],
                plot_bgcolor=THEME_COLORS["card_bg"],
                font_color=THEME_COLORS["text_main"],
                margin=dict(l=40, r=20, t=40, b=40),
            )
            st.plotly_chart(fig_lat, use_container_width=True)
    else:
        st.info("No comparative route calculations available. Select a station pair and click 'Run Benchmark'.")

st.divider()

render_section_header("4. Structural Centrality & Resilience Profiler", icon="🔬")
prof_c1, prof_c2 = st.columns(2)

with prof_c1:
    if st.button("📊 Profile Centrality Algorithms (Degree, Betweenness, Articulation)", key="btn_prof_centrality"):
        import time

        from src.analytics.articulation_points import find_articulation_points
        from src.analytics.betweenness_centrality import compute_betweenness_centrality
        from src.analytics.degree_centrality import compute_degree_centrality
        from src.analytics.graph_projection import build_analysis_graph

        with st.spinner("Measuring execution times of structural centrality algorithms..."):
            t0 = time.perf_counter_ns()
            analysis_g = build_analysis_graph(metro_graph)
            t_proj = (time.perf_counter_ns() - t0) / 1_000_000.0

            t0 = time.perf_counter_ns()
            dc_res = compute_degree_centrality(analysis_g)
            t_dc = (time.perf_counter_ns() - t0) / 1_000_000.0

            t0 = time.perf_counter_ns()
            bc_res = compute_betweenness_centrality(analysis_g)
            t_bc = (time.perf_counter_ns() - t0) / 1_000_000.0

            t0 = time.perf_counter_ns()
            ap_res = find_articulation_points(analysis_g)
            t_ap = (time.perf_counter_ns() - t0) / 1_000_000.0

            v_cnt = analysis_g.number_of_nodes()
            e_cnt = analysis_g.number_of_edges()

            centrality_profile = [
                {
                    "Algorithm": "Analytical Graph Projection",
                    "Target": "MultiGraph -> Simple Graph",
                    "Nodes": v_cnt,
                    "Edges": e_cnt,
                    "Runtime (ms)": f"{t_proj:.3f}",
                    "Result Summary": f"Collapsed {metro_graph.number_of_edges()} edges into {e_cnt} simple edges",
                },
                {
                    "Algorithm": "Degree Centrality",
                    "Target": "Simple Analysis Graph",
                    "Nodes": v_cnt,
                    "Edges": e_cnt,
                    "Runtime (ms)": f"{t_dc:.3f}",
                    "Result Summary": f"Computed {len(dc_res)} scores; max: {max(dc_res.values()):.4f}",
                },
                {
                    "Algorithm": "Betweenness Centrality",
                    "Target": "Simple Analysis Graph",
                    "Nodes": v_cnt,
                    "Edges": e_cnt,
                    "Runtime (ms)": f"{t_bc:.3f}",
                    "Result Summary": f"Computed {len(bc_res)} scores; max: {max(bc_res.values()):.4f}",
                },
                {
                    "Algorithm": "Cut-Vertices (Tarjan DFS)",
                    "Target": "Simple Analysis Graph",
                    "Nodes": v_cnt,
                    "Edges": e_cnt,
                    "Runtime (ms)": f"{t_ap:.3f}",
                    "Result Summary": f"Identified {len(ap_res)} structural articulation points",
                },
            ]
            st.dataframe(pd.DataFrame(centrality_profile), use_container_width=True, hide_index=True)

with prof_c2:
    sim_bench_station = st.selectbox(
        "Target Station for Single-Station Removal Profiling",
        station_display_list,
        index=0,
        key="prof_sim_target",
    )
    sim_target_id = sim_bench_station.split("(")[-1].rstrip(")")

    if st.button("⏱️ Profile Single-Station Closure & Connectivity Recalculation", key="btn_prof_closure"):
        import time

        from src.simulation.closure_engine import simulate_station_closure
        from src.simulation.connectivity_impact import compute_connectivity_metrics

        with st.spinner(f"Measuring graph isolation and connectivity metrics for {sim_bench_station}..."):
            t0 = time.perf_counter_ns()
            baseline_metrics = compute_connectivity_metrics(metro_graph)
            t_baseline = (time.perf_counter_ns() - t0) / 1_000_000.0

            t0 = time.perf_counter_ns()
            sim_res = simulate_station_closure(metro_graph, closed_station_ids=[sim_target_id])
            t_sim = (time.perf_counter_ns() - t0) / 1_000_000.0

            p_m = sim_res.post_closure_metrics
            resilience_profile = [
                {
                    "Operation": "Baseline Connectivity & Reachability",
                    "Target": "Original MultiGraph",
                    "Active Nodes": baseline_metrics.station_count,
                    "Active Edges": baseline_metrics.edge_count,
                    "Runtime (ms)": f"{t_baseline:.3f}",
                    "Components": baseline_metrics.connected_components,
                    "Reachability Ratio": f"{baseline_metrics.reachability_ratio:.4f}",
                },
                {
                    "Operation": f"Single Removal ({sim_target_id}) + Reroute Graph Copy",
                    "Target": "Isolated Simulated MultiGraph",
                    "Active Nodes": p_m.station_count,
                    "Active Edges": p_m.edge_count,
                    "Runtime (ms)": f"{t_sim:.3f}",
                    "Components": p_m.connected_components,
                    "Reachability Ratio": f"{p_m.reachability_ratio:.4f}",
                },
            ]
            st.dataframe(pd.DataFrame(resilience_profile), use_container_width=True, hide_index=True)

st.caption("Notice: Runtime depends on CPU hardware, background OS load, and input network size.")
