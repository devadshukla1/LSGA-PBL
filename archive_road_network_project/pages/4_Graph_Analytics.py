"""Interactive traversal, connectivity, and structural network analytics."""

import streamlit as st
from streamlit_folium import st_folium

from pages._analytics import structural_analytics
from src.algorithms.bfs import bfs
from src.algorithms.connectivity import strong_components, weak_components
from src.algorithms.dfs import dfs
from src.algorithms.reachability import from_bfs
from src.algorithms.traversal_models import prepare
from src.graph.dataset_service import list_datasets, load
from src.ui.sidebar import render_app_sidebar
from src.ui.state import set_active_dataset_id
from src.ui.theme import inject_custom_theme
from src.visualization.traversal_maps import traversal_map


def analytics() -> None:
    """Render the Graph Analytics page covering traversal, connectivity, and resilience."""
    inject_custom_theme()

    st.title("Graph Analytics")
    st.subheader("Graph Traversal & Connectivity")
    st.info(
        "BFS minimizes directed hops. DFS records exploration order. "
        "Neither optimizes distance or travel time."
    )

    with st.form("traversal"):
        dataset = st.selectbox("Local dataset", list_datasets())
        algorithm = st.radio("Algorithm", ["BFS", "DFS"])
        source = st.text_input("Start junction ID (blank uses first junction)")
        target = st.text_input("Target junction ID (optional)")
        run = st.form_submit_button("Run Traversal")

    try:
        active_info = load(dataset)
        set_active_dataset_id(dataset)
        render_app_sidebar(active_info.graph, active_info.metadata.dataset_name, active_info.origin)
    except Exception:
        render_app_sidebar()

    if run:
        st.session_state.pop("traversal_output", None)
        try:
            info = load(dataset)
            graph = info.graph
            roads = prepare(graph)
            start = int(source) if source.strip() else next(iter(roads))
            end = int(target) if target.strip() else None
            if end is not None and end not in roads:
                raise ValueError("Unknown target junction")
            tree = (bfs if algorithm == "BFS" else dfs)(roads, start)
            reach = None
            edges = []
            if end is not None:
                hops = tree if algorithm == "BFS" else bfs(roads, start)
                reach = from_bfs(hops, end)
                by_child = {v: (u, v, k) for u, v, k in hops.tree_edges}
                edges = [by_child[v] for v in reach.path[1:]]
            st.session_state["traversal_output"] = (
                info.origin,
                tree,
                reach,
                weak_components(roads),
                strong_components(roads),
                traversal_map(graph, tree, end, edges),
            )
        except (ValueError, OSError, TypeError) as error:
            st.error(str(error))

    if "traversal_output" not in st.session_state:
        structural_analytics()
        return

    origin, tree, reach, weak, strong, view = st.session_state["traversal_output"]
    st.caption(origin)

    # Metric summary cards
    c1, c2, c3 = st.columns(3)
    c1.metric("Start Node", str(tree.start_node))
    c2.metric("Nodes Visited", f"{tree.nodes_visited:,}")
    c3.metric("Edges Examined", f"{tree.edges_examined:,}")

    st.write(
        f"{tree.algorithm} from {tree.start_node} · {tree.nodes_visited} visited and reachable · "
        f"{tree.edges_examined} directed edges examined"
    )
    st.write(
        "First 100 visits and traversal-tree depths",
        [{"junction": n, "depth": tree.depth[n]} for n in tree.visit_order[:100]],
    )
    if tree.finish_order:
        st.write("First 100 DFS finishes", list(tree.finish_order[:100]))

    if reach:
        if reach.is_reachable:
            st.success(f"Reachable · directed hops: {reach.hop_count}")
            st.write("Hop-minimal path", list(reach.path))
        else:
            st.warning("Unreachable")

    for groups in (weak, strong):
        st.write(
            f"{groups.component_type.title()} components: {groups.component_count} · "
            f"largest: {groups.largest_component_size} · source component: "
            f"{groups.node_to_component[tree.start_node]}"
        )

    st.caption(
        "First 150 items per map layer. Green source, red target, violet visited nodes "
        "and tree edges, yellow hop-minimal path. Counts cover the full traversal."
    )
    st_folium(view, returned_objects=[], height=400)

    st.divider()
    structural_analytics()


if __name__ == "__main__":
    analytics()
