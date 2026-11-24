"""Global sidebar navigation and dataset status indicator for SmartRoute Analytics."""

import networkx as nx
import streamlit as st

from config import APP_NAME
from src.ui.formatting import format_percentage
from src.ui.state import get_active_dataset_id


def render_app_sidebar(
    graph: nx.MultiDiGraph | None = None,
    dataset_name: str | None = None,
    origin_info: str | None = None,
) -> None:
    """Render the standard global sidebar showing active dataset status and demo flow."""
    with st.sidebar:
        st.markdown(f"### 🚦 {APP_NAME}")
        st.caption("Large-Scale Graph Analysis · Final Academic Project")
        st.divider()

        # Active Dataset Summary
        active_id = get_active_dataset_id()
        st.markdown("**Active Road Network**")
        disp_name = dataset_name or active_id.replace("_", " ").title()
        st.markdown(f"📁 **{disp_name}**")
        if origin_info:
            st.caption(origin_info)

        if graph is not None:
            n_nodes = graph.number_of_nodes()
            n_edges = graph.number_of_edges()
            c1, c2 = st.columns(2)
            c1.metric("Junctions", f"{n_nodes:,}")
            c2.metric("Roads", f"{n_edges:,}")

            density = n_edges / (n_nodes * (n_nodes - 1)) if n_nodes > 1 else 0.0
            st.caption(f"Network density: {format_percentage(density, decimals=3)}")
        else:
            st.caption("Select a dataset in the active page to inspect network structure.")

        st.divider()

        # College Project Demonstration Sequence Guide
        with st.expander("📋 Demonstration Workflow", expanded=False):
            st.markdown(
                """
                **Suggested Review Order:**
                1. **Overview**: Network topologies & structure
                2. **Route Optimizer**: Shortest path vs time
                3. **Traffic Simulator**: Congestion & disruptions
                4. **Graph Analytics**: Centrality & resilience
                5. **Partitioning**: Geographic vs graph-aware
                6. **Algorithm Lab**: Runtime, scaling & optimality
                7. **Results & Export**: Historical runs & CSV exports
                """
            )
            st.caption("Reproducible offline execution supported.")
