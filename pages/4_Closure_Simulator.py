"""Page 4: Station Closure & Network Resilience Simulator."""

import json
from datetime import datetime, timezone

import streamlit as st

from src.core.settings import APP_ICON
from src.simulation.closure_engine import simulate_station_closure
from src.simulation.critical_station_impact import compute_all_stations_impact_ranking
from src.simulation.impact_comparison import build_impact_comparison_table
from src.simulation.route_rerouting import compare_routes_across_closure
from src.ui.components import (
    render_metric_card,
    render_page_header,
    render_section_header,
)
from src.ui.session_state import get_current_dataset_and_graph, init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme_css
from src.visualization.delhi_metro_map import plot_closure_comparison

st.set_page_config(page_title="Closure Simulator - MetroGraph", page_icon=APP_ICON, layout="wide")
st.markdown(apply_theme_css(), unsafe_allow_html=True)
init_session_state()
render_sidebar()

stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation = (
    get_current_dataset_and_graph()
)

render_page_header(
    title="Station Closure & Resilience Simulator",
    subtitle=(
        "Simulate single or multi-station outages, evaluate topological network fragmentation, "
        f"and compute automated commuter detours for {metadata.get('dataset_name', '')}."
    ),
    badge="PAGE 4",
)

# Station Mappings
station_options = dict(zip(stations_df["station_id"], stations_df["station_name"]))
station_display_list = sorted([f"{name} ({sid})" for sid, name in station_options.items()])

# SECTION 1: Closure Configuration Controls
render_section_header("1. Outage Scenario Configuration", icon="🛠️")
st.caption(
    "Select one or more stations to hypothetically close. The simulation creates an isolated graph "
    "copy and severs all incident links. The baseline network remains untouched."
)

cfg_c1, cfg_c2 = st.columns([0.7, 0.3])
with cfg_c1:
    selected_displays = st.multiselect(
        "Select Stations to Close",
        station_display_list,
        default=[],
        help="Select any number of stations. Closed stations and their track connections are removed.",
    )
with cfg_c2:
    closure_scenario = st.selectbox(
        "Closure Scenario Note (Optional)",
        [
            "Emergency Maintenance Outage",
            "Severe Waterlogging / Flooding",
            "Signaling & Electrical Grid Failure",
            "Structural Integrity Inspection",
            "Custom User Simulation",
        ],
        index=0,
    )

selected_station_ids = [d.split("(")[-1].rstrip(")") for d in selected_displays]
st.session_state["closed_stations"] = selected_station_ids

btn_c1, btn_c2 = st.columns([0.25, 0.75])
with btn_c1:
    run_sim_btn = st.button("🚀 Run Simulation", type="primary", use_container_width=True)
with btn_c2:
    if st.button("🔄 Reset Simulation"):
        st.session_state["closed_stations"] = []
        st.session_state["closure_result"] = None
        st.session_state["reroute_result"] = None
        st.rerun()

if run_sim_btn:
    with st.spinner("Executing isolated network disruption analysis..."):
        st.session_state["closure_result"] = simulate_station_closure(
            original_graph=metro_graph,
            closed_station_ids=selected_station_ids,
            dataset_id=metadata.get("dataset_name", "Metro Network"),
        )
        st.session_state["reroute_result"] = None

# Default baseline zero-closure if none run yet
if st.session_state.get("closure_result") is None:
    st.session_state["closure_result"] = simulate_station_closure(
        original_graph=metro_graph,
        closed_station_ids=[],
        dataset_id=metadata.get("dataset_name", "Metro Network"),
    )

sim_res = st.session_state["closure_result"]
sim_graph = sim_res.simulation_graph

if sim_res.warnings:
    for w in sim_res.warnings:
        st.warning(f"⚠️ {w}")

st.divider()

# SECTION 2: Network Impact Metrics
render_section_header("2. Topological Impact & Pairwise Reachability", icon="📊")
m_c1, m_c2, m_c3, m_c4, m_c5, m_c6 = st.columns(6)

b_m = sim_res.baseline_metrics
p_m = sim_res.post_closure_metrics

with m_c1:
    render_metric_card("Closed Stations", sim_res.removed_stations_count)
with m_c2:
    render_metric_card("Active Stations", p_m.station_count)
with m_c3:
    comp_delta = f"+{sim_res.component_count_change}" if sim_res.component_count_change > 0 else "Stable"
    render_metric_card(
        "Components",
        p_m.connected_components,
        delta=comp_delta,
    )
with m_c4:
    render_metric_card("Largest Component", p_m.largest_component_size)
with m_c5:
    render_metric_card("Isolated Stations", p_m.isolated_stations_count)
with m_c6:
    ratio_pct = f"{p_m.reachability_ratio * 100:.1f}%"
    delta_ratio = f"{sim_res.reachability_ratio_change * 100:.1f}%"
    render_metric_card(
        "Reachability Ratio",
        ratio_pct,
        delta=delta_ratio,
    )

comp_table = build_impact_comparison_table(sim_res)
st.dataframe(comp_table, use_container_width=True, hide_index=True)

st.divider()

# SECTION 3: Route Recalculation & Commuter Detours
render_section_header("3. Dynamic Journey Recalculation & Detour Analysis", icon="🧭")
st.caption(
    "Test whether origin-destination journeys can be maintained around the closed stations, "
    "or whether network severance causes travel delays or journey cancellation."
)

rc1, rc2, rc3 = st.columns(3)
with rc1:
    route_src_display = st.selectbox("Origin Station", station_display_list, index=0, key="sim_src")
with rc2:
    default_dst_idx = min(8, len(station_display_list) - 1)
    route_dst_display = st.selectbox("Destination Station", station_display_list, index=default_dst_idx, key="sim_dst")
with rc3:
    reroute_obj = st.selectbox(
        "Rerouting Objective",
        [
            "Minimum Travel Time (Dijkstra)",
            "Minimum Stops (BFS)",
            "Minimum Distance (Dijkstra)",
            "Minimum Transfers (0-1 BFS)",
            "Minimum Transfers, Then Fastest (Lexicographic)",
            "Fastest with Transfer Penalty (Dijkstra)",
        ],
        index=0,
        key="sim_obj",
    )

route_src_id = route_src_display.split("(")[-1].rstrip(")")
route_dst_id = route_dst_display.split("(")[-1].rstrip(")")

if st.button("🔍 Check Route Availability & Detour", type="secondary"):
    st.session_state["reroute_result"] = compare_routes_across_closure(
        original_graph=metro_graph,
        simulated_graph=sim_graph,
        source=route_src_id,
        destination=route_dst_id,
        closed_station_ids=sim_res.closed_station_ids,
        objective=reroute_obj,
    )

reroute_res = st.session_state.get("reroute_result")
if reroute_res is not None:
    st.markdown(f"#### Rerouting Outcome: **{reroute_res.disruption_status}**")
    if reroute_res.disruption_status in ["ENDPOINT_CLOSED", "UNREACHABLE"]:
        st.error(f"❌ {reroute_res.message}")
    elif reroute_res.disruption_status == "ALREADY_UNREACHABLE":
        st.warning(f"⚠️ {reroute_res.message}")
    else:
        if reroute_res.disruption_status == "UNCHANGED":
            st.success(f"✅ {reroute_res.message}")
        else:
            st.info(f"🔄 {reroute_res.message}")

        rm1, rm2, rm3, rm4 = st.columns(4)
        with rm1:
            diff_str = f"+{reroute_res.stops_diff}" if reroute_res.stops_diff > 0 else str(reroute_res.stops_diff)
            render_metric_card(
                "Stops (Before ➔ After)",
                f"{reroute_res.original_stops} ➔ {reroute_res.new_stops}",
                delta=f"Diff: {diff_str}",
            )
        with rm2:
            tr_diff = reroute_res.transfers_diff
            tr_diff_str = f"+{tr_diff}" if tr_diff > 0 else str(tr_diff)
            render_metric_card(
                "Transfers",
                f"{reroute_res.original_transfers} ➔ {reroute_res.new_transfers}",
                delta=f"Diff: {tr_diff_str}",
            )
        with rm3:
            t_diff = reroute_res.time_diff_min
            t_diff_str = f"+{t_diff:.1f}m" if t_diff > 0 else f"{t_diff:.1f}m"
            orig_t = f"{reroute_res.original_estimated_time_min:.1f}m"
            new_t = f"{reroute_res.new_estimated_time_min:.1f}m"
            render_metric_card(
                "Travel Time",
                f"{orig_t} ➔ {new_t}",
                delta=f"Diff: {t_diff_str}",
            )
        with rm4:
            d_diff = reroute_res.distance_diff_km
            d_diff_str = f"+{d_diff:.2f}km" if d_diff > 0 else f"{d_diff:.2f}km"
            orig_d = f"{reroute_res.original_distance_km:.2f}km"
            new_d = f"{reroute_res.new_distance_km:.2f}km"
            render_metric_card(
                "Distance",
                f"{orig_d} ➔ {new_d}",
                delta=f"Diff: {d_diff_str}",
            )

st.divider()

# SECTION 4: Interactive Disruption Map Visualization
render_section_header("4. Disruption Map & Component Isolation View", icon="🗺️")
st.caption(
    "Closed stations are marked with red 'X' crosses; severed track links are dotted red. "
    "Active surviving stations and detour routes are displayed clearly."
)

vc1, vc2 = st.columns([0.7, 0.3])
with vc2:
    color_comps = st.checkbox("Colorize Disjoint Components", value=False)

orig_path = reroute_res.original_station_path if (reroute_res and reroute_res.original_reachable) else None
new_path = reroute_res.new_station_path if (reroute_res and reroute_res.new_reachable) else None

fig_disruption = plot_closure_comparison(
    original_graph=metro_graph,
    simulated_graph=sim_graph,
    closed_station_ids=sim_res.closed_station_ids,
    original_route_stations=orig_path,
    new_route_stations=new_path,
    color_by_component=color_comps,
    title=f"Disruption Schematic: {len(sim_res.closed_station_ids)} Closed Station(s)",
)
st.plotly_chart(fig_disruption, use_container_width=True)

st.divider()

# SECTION 5: Critical Station Vulnerability Ranking
render_section_header("5. Critical Station Vulnerability Rankings", icon="⚠️")
st.caption(
    "Simulates the isolated removal of each station to measure its individual topological impact. "
    "Stations whose removal increases disconnected components are structural cut-vertices (articulation points)."
)

if st.button("📊 Evaluate All-Station Vulnerability Rankings", type="secondary"):
    with st.spinner("Simulating individual station removals across entire network..."):
        impact_ranking_df = compute_all_stations_impact_ranking(metro_graph)
        st.dataframe(impact_ranking_df.head(20), use_container_width=True, hide_index=True)
        st.caption("Top 20 most vulnerable stations sorted by component increase and pair loss.")

st.divider()

# SECTION 6: Export Results (CSV & JSON)
render_section_header("6. Export Simulation Artifacts", icon="📥")
st.caption("Export full topological metrics and route impact diagnostics in standard tabular and JSON formats.")

exp_c1, exp_c2 = st.columns(2)
with exp_c1:
    csv_data = comp_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Export Metrics Table (CSV)",
        data=csv_data,
        file_name="metrograph_closure_simulation_metrics.csv",
        mime="text/csv",
        use_container_width=True,
    )

with exp_c2:
    json_payload = {
        "dataset_id": sim_res.dataset_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "closure_scenario": closure_scenario,
        "closed_stations": [
            {"station_id": sid, "station_name": sname}
            for sid, sname in zip(sim_res.closed_station_ids, sim_res.closed_station_names)
        ],
        "summary_metrics": {
            "baseline_stations": b_m.station_count,
            "remaining_stations": p_m.station_count,
            "removed_stations": sim_res.removed_stations_count,
            "baseline_edges": b_m.edge_count,
            "remaining_edges": p_m.edge_count,
            "removed_edges": sim_res.removed_edges_count,
            "baseline_components": b_m.connected_components,
            "remaining_components": p_m.connected_components,
            "component_change": sim_res.component_count_change,
            "baseline_reachable_pairs": b_m.reachable_station_pairs,
            "remaining_reachable_pairs": p_m.reachable_station_pairs,
            "reachable_pairs_lost": sim_res.reachable_pairs_loss,
            "baseline_reachability_ratio": b_m.reachability_ratio,
            "remaining_reachability_ratio": p_m.reachability_ratio,
        },
        "disruption_warnings": sim_res.warnings,
    }
    if reroute_res:
        json_payload["route_rerouting"] = {
            "origin": reroute_res.source_station_id,
            "destination": reroute_res.destination_station_id,
            "objective": reroute_res.objective,
            "status": reroute_res.disruption_status,
            "original_stops": reroute_res.original_stops,
            "new_stops": reroute_res.new_stops,
            "original_time_min": reroute_res.original_estimated_time_min,
            "new_time_min": reroute_res.new_estimated_time_min,
            "time_diff_min": reroute_res.time_diff_min,
        }

    st.download_button(
        label="📦 Export Full Simulation Payload (JSON)",
        data=json.dumps(json_payload, indent=2).encode("utf-8"),
        file_name="metrograph_closure_simulation_payload.json",
        mime="application/json",
        use_container_width=True,
    )
