"""Interactive synthetic congestion, road closure, and emergency rerouting simulation."""

import json

import streamlit as st
from streamlit_folium import st_folium

from src.graph.dataset_service import list_datasets, load
from src.simulation.scenario_builder import create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.scenario_storage import list_scenarios, load_scenario, save_scenario
from src.simulation.simulation_engine import simulate
from src.ui.formatting import format_distance, format_time
from src.ui.sidebar import render_app_sidebar
from src.ui.state import set_active_dataset_id
from src.ui.theme import inject_custom_theme
from src.visualization.simulation_maps import simulation_map


def traffic() -> None:
    """Render the Traffic Simulator page with congestion and closure modeling."""
    inject_custom_theme()

    st.title("Traffic Simulator")
    st.warning("Congestion values are simulated assumptions, not live traffic measurements.")

    dataset = st.selectbox("Dataset", list_datasets(), key="sim_dataset")

    try:
        active_info = load(dataset)
        set_active_dataset_id(dataset)
        render_app_sidebar(active_info.graph, active_info.metadata.dataset_name, active_info.origin)
    except Exception:
        render_app_sidebar()

    saved = st.selectbox("Saved scenario", ["", *list_scenarios()])

    # Button 0
    if st.button("Load scenario") and saved:
        try:
            info = load(dataset)
            scenario = load_scenario(saved, info.graph, dataset)
            st.session_state["loaded_scenario"] = scenario
            st.session_state.pop("sim_output", None)
            st.session_state.update(
                sim_level=scenario.congestion_level,
                sim_seed=scenario.random_seed,
                sim_coverage=int(scenario.congestion_coverage * 100),
                sim_closed=json.dumps(scenario.closed_edges),
                sim_blocked=json.dumps(scenario.blocked_nodes),
            )
        except (ValueError, OSError) as error:
            st.error(str(error))

    # Button 1
    if st.button("Reset scenario"):
        st.session_state.update(
            sim_level="normal", sim_seed=42, sim_coverage=50, sim_closed="[]", sim_blocked="[]"
        )
        st.session_state.pop("sim_output", None)
        st.session_state.pop("loaded_scenario", None)

    # Form with Button 2
    with st.form("simulation"):
        source = st.text_input("Source ID", "0")
        target = st.text_input("Destination ID", "1")
        level = st.selectbox(
            "Congestion", ["normal", "light", "moderate", "heavy"], key="sim_level"
        )
        coverage = st.slider("Affected roads (%)", 0, 100, 50, key="sim_coverage")
        seed = st.number_input("Random seed", value=42, step=1, key="sim_seed")
        closed = st.text_area(
            "Closed directed edges as JSON [[source, destination, key]]", "[]", key="sim_closed"
        )
        blocked = st.text_area("Blocked junction IDs as JSON [node]", "[]", key="sim_blocked")
        algorithm = st.selectbox("Algorithm", ["dijkstra", "astar", "bidirectional_dijkstra"])
        mode = st.selectbox("Mode", ["Emergency simulated fastest route", "Shortest distance"])
        run = st.form_submit_button("Run Simulation")

    if run:
        st.session_state.pop("sim_output", None)
        try:
            with st.spinner("Calculating simulated routes"):
                info = load(dataset)
                loaded = st.session_state.get("loaded_scenario")
                scenario = create_scenario(
                    info.graph,
                    dataset,
                    level,
                    int(seed),
                    coverage / 100,
                    tuple(tuple(e) for e in json.loads(closed)),
                    tuple(json.loads(blocked)),
                    parameters=loaded.parameters
                    if loaded and loaded.congestion_level == level and loaded.dataset_id == dataset
                    else None,
                )
                request = SimulationRequest(
                    int(source),
                    int(target),
                    algorithm,
                    "travel_time" if mode.startswith("Emergency") else "distance",
                )
                result = simulate(info.graph, scenario, request, dataset)
                st.session_state["sim_output"] = (
                    info.graph,
                    scenario,
                    result,
                    simulation_map(info.graph, scenario, result),
                )
        except (ValueError, TypeError, OSError, KeyError) as error:
            st.error(f"Simulation failed: {error}")

    if "sim_output" in st.session_state:
        graph, scenario, result, view = st.session_state["sim_output"]
        st.success(f"Simulation complete · {result.status}")

        # Comparison metric cards
        comp = result.comparison
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Baseline Distance", format_distance(comp.get("baseline_distance_m", 0)))
        c2.metric("Baseline Time", format_time(comp.get("baseline_travel_time_s", 0)))

        sc_dist = (
            format_distance(comp["scenario_distance_m"])
            if comp.get("scenario_distance_m") is not None
            else "N/A"
        )
        dist_diff = comp.get("distance_difference_m")
        c3.metric(
            "Scenario Distance",
            sc_dist,
            delta=f"{dist_diff:+.1f} m" if dist_diff is not None else None,
        )

        sc_time = (
            format_time(comp["scenario_travel_time_s"])
            if comp.get("scenario_travel_time_s") is not None
            else "N/A"
        )
        time_diff = comp.get("travel_time_difference_s")
        c4.metric(
            "Scenario Time",
            sc_time,
            delta=f"{time_diff:+.1f} s" if time_diff is not None else None,
            delta_color="inverse",
        )

        st.write(result.comparison)
        st.write("Baseline keyed route", result.baseline.edge_path)
        st.write(
            "Scenario keyed route", result.scenario_route.edge_path if result.scenario_route else []
        )
        st.caption(
            "Cyan baseline · green scenario · amber congestion · red closures and blocked nodes. "
            "Context and disruption layers show up to 300 items each."
        )
        st_folium(view, returned_objects=[], height=430)

        # Button 3
        if st.button("Save scenario"):
            save_scenario(scenario, graph, scenario.dataset_id)
            st.success("Scenario saved")


if __name__ == "__main__":
    traffic()
