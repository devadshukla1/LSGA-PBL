"""Page 3: Station Importance & Critical Interchange Analysis."""

import streamlit as st

from src.analytics.station_comparison import compare_two_stations
from src.analytics.station_ranking import compute_station_analytics, get_ranked_stations_dataframe
from src.core.settings import APP_ICON
from src.ui.components import (
    render_info_box,
    render_metric_card,
    render_page_header,
    render_section_header,
)
from src.ui.session_state import get_current_dataset_and_graph, init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme_css
from src.visualization.delhi_metro_map import (
    plot_centrality_network,
    plot_top_stations,
)

st.set_page_config(page_title="Station Importance - MetroGraph", page_icon=APP_ICON, layout="wide")
st.markdown(apply_theme_css(), unsafe_allow_html=True)
init_session_state()
render_sidebar()

stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation = (
    get_current_dataset_and_graph()
)

# --- Cached Analytics Pipeline ---
@st.cache_data(show_spinner="Evaluating network centralities and topological cut-vertices...")
def get_cached_station_analytics(dataset_fp: str, _metro_graph, _station_lines_df, _lines_df):
    results, summary, analysis_g = compute_station_analytics(_metro_graph, _station_lines_df, _lines_df)
    return results, summary

station_results, summary = get_cached_station_analytics(
    metadata.get("fingerprint", "default_fp"), metro_graph, station_lines_df, lines_df
)

render_page_header(
    title="Station Importance & Critical Interchange Analysis",
    subtitle=(
        "Structural centrality, articulation cut-vertices, and multi-line convergence analysis "
        f"for {metadata.get('dataset_name', '')}."
    ),
    badge="PAGE 3",
)

# --- Top-Level Summary Metrics ---
render_section_header("Topological Centrality & Connectivity Invariants", icon="🏆")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Total Stations |V|", summary.total_stations)
with c2:
    render_metric_card("Interchange Hubs", summary.total_interchanges)
with c3:
    render_metric_card(
        "Articulation Points",
        summary.total_articulation_points,
        delta="Vulnerable Cut-Vertices" if summary.total_articulation_points > 0 else "None",
    )
with c4:
    conn_text = f"{summary.connected_components} Component(s)"
    conn_delta = "Fully Connected" if summary.connected_components == 1 else "Partitioned"
    render_metric_card("Network Topology", conn_text, delta=conn_delta)

st.divider()

# --- Tabbed Analytical Views ---
tab_rankings, tab_viz, tab_interchanges, tab_articulation, tab_comparison = st.tabs([
    "Centrality Rankings",
    "Network Centrality Map",
    "Critical Interchanges",
    "Articulation Points",
    "Station Comparison",
])

# TAB 1: Centrality Rankings
with tab_rankings:
    st.markdown("### 🏆 Station Importance Rankings")
    st.caption(
        "Important Note on Transit Centrality: Degree centrality reflects immediate adjacent physical connectivity. "
        "Betweenness centrality reflects participation in topological shortest-hop paths across the network. "
        "Neither metric should be conflated directly with passenger ridership or station platform overcrowding."
    )

    rc1, rc2 = st.columns([0.6, 0.4])
    with rc1:
        sort_choice = st.selectbox(
            "Primary Ranking Metric",
            [
                "Betweenness Centrality",
                "Degree Centrality",
                "Degree (Adjacent Stations)",
                "Line Count",
            ],
            index=0,
        )
    with rc2:
        top_n_val = st.selectbox("Display Top N Stations", [10, 20, 50, 100, "All"], index=1)

    metric_key_map = {
        "Betweenness Centrality": "betweenness_centrality",
        "Degree Centrality": "degree_centrality",
        "Degree (Adjacent Stations)": "degree",
        "Line Count": "line_count",
    }
    top_limit = None if top_n_val == "All" else int(top_n_val)
    ranked_df = get_ranked_stations_dataframe(
        station_results, sort_by=metric_key_map[sort_choice], top_n=top_limit
    )

    st.dataframe(ranked_df, use_container_width=True, hide_index=True)

    csv_bytes = ranked_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Rankings as CSV",
        data=csv_bytes,
        file_name=f"metrograph_station_rankings_{metric_key_map[sort_choice]}.csv",
        mime="text/csv",
    )

    st.markdown("#### 📊 Top Stations Distribution")
    chart_metric = (
        "betweenness_centrality" if sort_choice == "Betweenness Centrality" else "degree_centrality"
    )
    bar_chart_n = 15 if top_limit is None or top_limit > 15 else top_limit
    fig_bar = plot_top_stations(station_results, metric=chart_metric, top_n=bar_chart_n)
    st.plotly_chart(fig_bar, use_container_width=True)

# TAB 2: Network Centrality Map
with tab_viz:
    st.markdown("### 🗺️ Schematic Centrality Heatmap")
    st.caption(
        "Node marker size and continuous color scaling indicate relative centrality. "
        "Outer blue circles denote interchange hubs; red diamonds highlight articulation points. "
        "Centrality scores are calculated globally on the complete network."
    )

    vc1, vc2, vc3 = st.columns(3)
    with vc1:
        viz_metric_choice = st.selectbox(
            "Visual Centrality Metric",
            ["Betweenness Centrality", "Degree Centrality"],
            index=0,
            key="viz_metric",
        )
    with vc2:
        line_filter_options = ["All Lines"] + sorted(lines_df["line_name"].unique().tolist())
        viz_line_filter = st.selectbox(
            "Filter Visual Line (Display Only)",
            line_filter_options,
            index=0,
            key="viz_line",
        )
    with vc3:
        highlight_aps = st.checkbox("Highlight Cut-Vertices (Articulation Points)", value=True)

    viz_metric_key = (
        "betweenness_centrality"
        if viz_metric_choice == "Betweenness Centrality"
        else "degree_centrality"
    )
    fig_net = plot_centrality_network(
        metro_graph,
        station_results,
        metric=viz_metric_key,
        selected_line=viz_line_filter,
        highlight_articulation_points=highlight_aps,
    )
    st.plotly_chart(fig_net, use_container_width=True)

# TAB 3: Critical Interchanges
with tab_interchanges:
    st.markdown("### 🔄 Multi-Line Interchange Hubs")
    st.caption(
        "Interchange stations serve 2 or more distinct lines. Notice that while many interchanges "
        "exhibit elevated betweenness, non-interchange bottleneck stations can also exhibit high betweenness."
    )

    interchange_results = [r for r in station_results if r.is_interchange]
    interchange_df = get_ranked_stations_dataframe(
        interchange_results, sort_by="betweenness_centrality", top_n=None
    )

    if not interchange_df.empty:
        st.dataframe(interchange_df, use_container_width=True, hide_index=True)
        msg = f"Detected **{len(interchange_results)}** structural interchange hubs across {summary.total_lines} lines."
        st.info(msg)
    else:
        st.warning("No multi-line interchange stations detected in active dataset.")

# TAB 4: Articulation Points
with tab_articulation:
    st.markdown("### ⚠️ Articulation Points (Topological Cut-Vertices)")
    render_info_box(
        title="Structural Vulnerability Definition",
        message=(
            "An articulation point is a station whose removal strictly increases the number of disconnected "
            "components in the network. A disruption at an articulation station immediately segments portions "
            "of the transit network from one another."
        ),
        level="warning" if summary.total_articulation_points > 0 else "success",
    )

    ap_results = [r for r in station_results if r.is_articulation_point]
    ap_df = get_ranked_stations_dataframe(
        ap_results, sort_by="betweenness_centrality", top_n=None
    )

    if not ap_df.empty:
        st.dataframe(ap_df, use_container_width=True, hide_index=True)
        st.caption(
            f"Total {len(ap_results)} articulation station(s) identified via Tarjan's DFS cut-vertex algorithm."
        )
    else:
        st.success("The network topology has zero articulation points (2-connected biconnected network).")

# TAB 5: Station Comparison
with tab_comparison:
    st.markdown("### ⚖️ Pairwise Station Comparison")
    st.caption(
        "Compare two stations side-by-side across all topological, centrality, and connectivity metrics."
    )

    station_names_list = sorted([f"{r.station_name} ({r.station_id})" for r in station_results])

    cmp_c1, cmp_c2 = st.columns(2)
    with cmp_c1:
        stn_a_display = st.selectbox("Select Station A", station_names_list, index=0)
    with cmp_c2:
        default_b_idx = min(1, len(station_names_list) - 1)
        stn_b_display = st.selectbox("Select Station B", station_names_list, index=default_b_idx)

    stn_a_id = stn_a_display.split("(")[-1].rstrip(")")
    stn_b_id = stn_b_display.split("(")[-1].rstrip(")")

    if stn_a_id == stn_b_id:
        st.info("ℹ️ Both selections are identical. Select distinct stations for comparative contrast.")

    comparison_df = compare_two_stations(stn_a_id, stn_b_id, station_results)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

st.divider()
st.info(
    "👉 Navigate to **4. Closure Simulator** in the sidebar to simulate single or multi-station closures, "
    "measure reachable pair destruction, and recalculate alternative routes."
)
