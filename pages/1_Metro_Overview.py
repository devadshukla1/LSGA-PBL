"""Page 1: Metro Overview."""

import streamlit as st

from src.analytics.station_ranking import compute_station_analytics
from src.core.settings import APP_ICON
from src.simulation.connectivity_impact import compute_connectivity_metrics
from src.ui.components import (
    render_metric_card,
    render_page_header,
    render_section_header,
)
from src.ui.session_state import get_current_dataset_and_graph, init_session_state
from src.ui.sidebar import render_sidebar
from src.ui.theme import apply_theme_css
from src.visualization.delhi_metro_map import render_delhi_metro_map

st.set_page_config(page_title="Metro Overview - MetroGraph", page_icon=APP_ICON, layout="wide")
st.markdown(apply_theme_css(), unsafe_allow_html=True)
init_session_state()
render_sidebar()

stations_df, lines_df, connections_df, station_lines_df, metadata, metro_graph, validation = (
    get_current_dataset_and_graph()
)

# Compute lightweight summary analytics for overview cards
@st.cache_data
def get_overview_summary(fp: str, _metro_graph, _station_lines_df, _lines_df):
    _, summary, _ = compute_station_analytics(_metro_graph, _station_lines_df, _lines_df)
    baseline_conn = compute_connectivity_metrics(_metro_graph)
    return summary, baseline_conn

analytics_summary, baseline_conn = get_overview_summary(
    metadata.get("fingerprint", "default_fp"), metro_graph, station_lines_df, lines_df
)

render_page_header(
    title="Metro Overview",
    subtitle=f"Network topology and connectivity diagnostics for {metadata.get('dataset_name', '')}.",
    badge="PAGE 1",
)

# Summary metrics row
render_section_header("Topological Invariants & Structural Scope", icon="📊")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Total Stations", validation["node_count"])
with c2:
    render_metric_card("Total Lines", len(lines_df))
with c3:
    render_metric_card("Connections (Edges)", validation["edge_count"])
with c4:
    conn_status = f"{validation['connected_components']} Component(s)"
    delta_val = "Fully Connected" if validation["is_connected"] else "Segmented"
    render_metric_card("Network Topology", conn_status, delta=delta_val)

# Secondary row: Network Vulnerability & Resilience Baseline
sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    render_metric_card("Interchange Hubs", analytics_summary.total_interchanges)
with sc2:
    render_metric_card(
        "Cut-Vertices (APs)",
        analytics_summary.total_articulation_points,
        delta="Vulnerable Nodes" if analytics_summary.total_articulation_points > 0 else "None",
    )
with sc3:
    ratio_str = f"{baseline_conn.reachability_ratio * 100:.1f}%"
    render_metric_card(
        "Baseline Reachability",
        ratio_str,
        delta=f"{baseline_conn.reachable_station_pairs:,} Pairs",
    )
with sc4:
    render_metric_card(
        "Top Betweenness Station",
        analytics_summary.highest_betweenness_station.split("(")[0].strip(),
        delta="Max Bridge Vitality",
    )

st.divider()

# Interactive Filters & Delhi Metro Network Map
render_section_header("Delhi Metro Network Map & Line Corridor Filter", icon="🗺️")

st.markdown(
    """
    <div style="margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.88rem; color: #94A3B8;">
            Select any metro line corridor below. The selected line renders in full color (6px width),
            while non-selected lines fade to an ambient 15% opacity.
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)

f_col1, f_col2, f_col3 = st.columns([0.45, 0.28, 0.27])
with f_col1:
    line_choices = ["All Lines"] + sorted(lines_df["line_name"].unique().tolist())
    selected_line = st.selectbox("Filter by Metro Line", line_choices, index=0)
with f_col2:
    st.write("")
    st.write("")
    interchange_filter = st.checkbox("Show Interchange Hubs Only", value=False)
with f_col3:
    st.write("")
    st.link_button(
        "🌐 Open Delhi Metro Map",
        "https://delhimetrorail.com/map",
        help="Open the official Delhi Metro Rail Corporation (DMRC) interactive network map in a new tab.",
        use_container_width=True,
    )

fig = render_delhi_metro_map(
    metro_graph,
    selected_line=selected_line,
    filter_interchanges_only=interchange_filter,
    title=f"{metadata.get('dataset_name', 'Metro')} Spatial Topology",
    height=750,
)
st.plotly_chart(fig, use_container_width=True)

