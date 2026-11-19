"""Page labels and common Phase 1 presentation."""

import streamlit as st

from config import APP_DESCRIPTION, APP_NAME

PAGES = (
    (
        "1_Overview.py",
        "Overview",
        "Inspect the active road network, dataset metadata, and graph statistics.",
    ),
    (
        "2_Route_Optimizer.py",
        "Route Optimizer",
        "Compare shortest-distance and shortest-time routes for simulated emergency vehicles.",
    ),
    (
        "3_Traffic_Simulator.py",
        "Traffic Simulator",
        "Explore congestion, road closures, and emergency rerouting scenarios.",
    ),
    (
        "4_Graph_Analytics.py",
        "Graph Analytics",
        "Analyze centrality, connectivity, and road network resilience.",
    ),
    (
        "5_Partitioning.py",
        "Partitioning",
        "Compare geographic and graph-aware partitions of a road network.",
    ),
    (
        "6_Algorithm_Lab.py",
        "Algorithm Lab",
        "Benchmark algorithms and compare correctness, runtime, and memory use.",
    ),
    (
        "7_Results.py",
        "Results & Export",
        "Review experiment summaries and download measured results.",
    ),
)


def show_placeholder(filename: str) -> None:
    """Show a page's purpose and current implementation status."""
    title, description = next(
        (title, description) for name, title, description in PAGES if name == filename
    )
    if filename == "1_Overview.py":
        st.title(APP_NAME)
        st.caption("Smart City Traffic & Emergency Route Optimizer · Large-Scale Graph Analysis")
        st.write(APP_DESCRIPTION)
        st.info("Phase 1 of 12 · Project Foundation & Architecture")
        st.write("Graph algorithms and road datasets will be added in later phases.")
        st.subheader("Dashboard modules")
        st.markdown("\n".join(f"- **{label}** · {purpose}" for _, label, purpose in PAGES))
        st.caption("Select a page in the sidebar to read about its planned features.")
        st.subheader(title)
    else:
        st.title(title)
    st.write(description)
    st.info("Planned for a later development phase")
