"""Interactive Graph Partitioning and Spatial Indexing Dashboard."""

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from config import DEFAULT_PARTITION_COUNT, DEFAULT_RANDOM_SEED
from src.graph.dataset_service import list_datasets, load
from src.indexing.nearest_node import brute_force_nearest_node
from src.indexing.spatial_index import (
    extract_node_coordinates,
    get_spatial_index,
)
from src.partitioning.partition_service import (
    compare_partitioning_methods,
    partition_graph,
)
from src.ui.sidebar import render_app_sidebar
from src.ui.state import set_active_dataset_id
from src.ui.theme import inject_custom_theme
from src.visualization.partition_maps import partition_map


def partitioning_page() -> None:
    inject_custom_theme()
    st.title("Partitioning")
    st.caption("Phase 8 of 12 · Large-Scale Graph Analysis")
    st.info(
        "Geographic bisection produces spatially coherent clusters. "
        "Graph-aware region growing actively reduces cross-partition cut edges. "
        "A 3D spherical KD-tree accelerates nearest-node lookups."
    )

    # -------------------------------------------------------------
    # SECTION A: Dataset Selection
    # -------------------------------------------------------------
    datasets = list_datasets()
    dataset = st.selectbox("Select Road Network Dataset", datasets, index=0)

    try:
        dataset_info = load(dataset)
        graph = dataset_info.graph
        set_active_dataset_id(dataset)
        render_app_sidebar(graph, dataset_info.metadata.dataset_name, dataset_info.origin)
    except Exception as err:
        render_app_sidebar()
        st.error(f"Failed to load dataset: {err}")
        return

    st.caption(
        f"{dataset_info.origin} · {len(graph)} junctions · {graph.number_of_edges()} directed roads"
    )

    # Compute default centroid for spatial indexing coordinates
    coords = extract_node_coordinates(graph)
    lats = [c[0] for c in coords.values()]
    lons = [c[1] for c in coords.values()]
    default_lat = round(sum(lats) / len(lats), 6) if lats else 28.63
    default_lon = round(sum(lons) / len(lons), 6) if lons else 77.21

    tab_partition, tab_comparison, tab_indexing = st.tabs(
        ["Partitioning & Map", "Method Comparison", "Spatial Indexing (KD-Tree)"]
    )

    # -------------------------------------------------------------
    # TAB 1: Partitioning & Map
    # -------------------------------------------------------------
    with tab_partition:
        st.subheader("Partition Configuration")
        col1, col2, col3 = st.columns(3)
        with col1:
            method = st.selectbox("Partition Method", ["Geographic", "Graph-Aware"], index=0)
        with col2:
            k = st.number_input(
                "Partitions (K)",
                min_value=1,
                max_value=max(1, len(graph)),
                value=min(DEFAULT_PARTITION_COUNT, len(graph)),
            )
        with col3:
            seed = st.number_input("Random Seed", value=DEFAULT_RANDOM_SEED)

        if st.button("Run Partitioning", key="btn_run_partition"):
            with st.spinner("Computing partitions..."):
                algo_key = "geographic" if method == "Geographic" else "graph_aware"
                res, quality = partition_graph(graph, method=algo_key, k=int(k), seed=int(seed))
                st.session_state["partition_active_result"] = (res, quality, algo_key, dataset)

        if "partition_active_result" in st.session_state:
            active_res, active_quality, active_algo, active_ds = st.session_state[
                "partition_active_result"
            ]
            if active_ds == dataset:
                st.success(
                    f"Partitioned into {active_res.actual_partition_count} regions in "
                    f"{active_res.runtime_seconds:.4f} s"
                )

                # Quality Metrics
                st.subheader("Partition Quality Metrics")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(
                    "Cut-Edge Count",
                    f"{active_quality.cut_edge_count} / {active_quality.total_edges}",
                )
                m2.metric("Cut-Edge Ratio", f"{active_quality.cut_edge_ratio * 100:.1f} %")
                m3.metric("Balance Ratio", f"{active_quality.partition_balance_ratio:.3f}")
                m4.metric("Size Std Dev", f"{active_quality.partition_size_std:.2f}")

                # Partition sizes breakdown table
                stats_rows = []
                for p, s in active_quality.partition_statistics.items():
                    stats_rows.append(
                        {
                            "Partition": f"P{p}",
                            "Nodes": s.node_count,
                            "Internal Edges": s.internal_edge_count,
                            "Outgoing Cuts": s.outgoing_cut_edges,
                            "Incoming Cuts": s.incoming_cut_edges,
                            "Internal Length (km)": round(s.total_road_length_m / 1000.0, 3),
                        }
                    )
                st.dataframe(pd.DataFrame(stats_rows), use_container_width=True)

                # Map Visualization
                st.subheader("Partition Map")
                st.caption(
                    "Colors indicate partitions. Distinct red dashed lines indicate cut edges "
                    "connecting different partitions."
                )
                map_obj = partition_map(graph, active_res)
                st_folium(
                    map_obj, height=450, returned_objects=[], key=f"part_map_{active_algo}_{k}"
                )

    # -------------------------------------------------------------
    # TAB 2: Method Comparison
    # -------------------------------------------------------------
    with tab_comparison:
        st.subheader("Geographic vs Graph-Aware Partitioning Comparison")
        comp_k = st.number_input(
            "Comparison Partitions (K)",
            min_value=1,
            max_value=max(1, len(graph)),
            value=min(DEFAULT_PARTITION_COUNT, len(graph)),
            key="comp_k",
        )

        if st.button("Run Comparison", key="btn_run_comparison"):
            with st.spinner("Evaluating both partitioning methods..."):
                comp_result = compare_partitioning_methods(graph, k=int(comp_k), seed=int(seed))
                st.session_state["partition_comparison"] = (comp_result, dataset)

        if "partition_comparison" in st.session_state:
            comp_res, comp_ds = st.session_state["partition_comparison"]
            if comp_ds == dataset:
                geo_q = comp_res.geographic_quality
                aware_q = comp_res.graph_aware_quality
                geo_r = comp_res.geographic_result
                aware_r = comp_res.graph_aware_result

                diff_cut_ratio = (geo_q.cut_edge_ratio - aware_q.cut_edge_ratio) * 100
                diff_balance = geo_q.partition_balance_ratio - aware_q.partition_balance_ratio
                diff_std = geo_q.partition_size_std - aware_q.partition_size_std
                diff_len = (
                    geo_q.cross_partition_road_length_m - aware_q.cross_partition_road_length_m
                ) / 1000.0
                diff_runtime = geo_r.runtime_seconds - aware_r.runtime_seconds

                comp_table = [
                    {
                        "Metric": "Cut Edges (Directed)",
                        "Geographic": geo_q.cut_edge_count,
                        "Graph-Aware": aware_q.cut_edge_count,
                        "Difference (Geo - Aware)": geo_q.cut_edge_count - aware_q.cut_edge_count,
                    },
                    {
                        "Metric": "Cut-Edge Ratio",
                        "Geographic": f"{geo_q.cut_edge_ratio * 100:.2f}%",
                        "Graph-Aware": f"{aware_q.cut_edge_ratio * 100:.2f}%",
                        "Difference (Geo - Aware)": f"{diff_cut_ratio:+.2f}%",
                    },
                    {
                        "Metric": "Partition Balance Ratio",
                        "Geographic": f"{geo_q.partition_balance_ratio:.4f}",
                        "Graph-Aware": f"{aware_q.partition_balance_ratio:.4f}",
                        "Difference (Geo - Aware)": f"{diff_balance:+.4f}",
                    },
                    {
                        "Metric": "Partition Size Std Dev",
                        "Geographic": f"{geo_q.partition_size_std:.2f}",
                        "Graph-Aware": f"{aware_q.partition_size_std:.2f}",
                        "Difference (Geo - Aware)": f"{diff_std:+.2f}",
                    },
                    {
                        "Metric": "Cross-Partition Length (km)",
                        "Geographic": round(geo_q.cross_partition_road_length_m / 1000.0, 3),
                        "Graph-Aware": round(aware_q.cross_partition_road_length_m / 1000.0, 3),
                        "Difference (Geo - Aware)": round(diff_len, 3),
                    },
                    {
                        "Metric": "Runtime (seconds)",
                        "Geographic": f"{geo_r.runtime_seconds:.4f} s",
                        "Graph-Aware": f"{aware_r.runtime_seconds:.4f} s",
                        "Difference (Geo - Aware)": f"{diff_runtime:+.4f} s",
                    },
                ]
                st.dataframe(pd.DataFrame(comp_table), use_container_width=True)

                st.caption(
                    "Tradeoff Analysis: Geographic bisection creates compact spatial polygons, "
                    "while Graph-Aware region growing explicitly reduces cut edges."
                )

                # Charts
                chart_df = pd.DataFrame(
                    {
                        "Partition": [
                            f"P{p}"
                            for p in range(comp_res.geographic_result.actual_partition_count)
                        ],
                        "Geographic": [
                            geo_q.partition_sizes.get(p, 0)
                            for p in range(comp_res.geographic_result.actual_partition_count)
                        ],
                        "Graph-Aware": [
                            aware_q.partition_sizes.get(p, 0)
                            for p in range(comp_res.graph_aware_result.actual_partition_count)
                        ],
                    }
                ).set_index("Partition")
                st.bar_chart(chart_df)

    # -------------------------------------------------------------
    # TAB 3: Spatial Indexing (KD-Tree)
    # -------------------------------------------------------------
    with tab_indexing:
        st.subheader("Spatial Nearest-Node Indexing (3D Spherical KD-Tree)")
        st.write(
            "Converts (lat, lon) to 3D Cartesian coordinates on a sphere. "
            "Enables logarithmic nearest-node queries without O(V) exhaustive scans."
        )

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            q_lat = st.number_input("Query Latitude", value=default_lat, format="%.6f")
        with col_q2:
            q_lon = st.number_input("Query Longitude", value=default_lon, format="%.6f")

        b_col1, b_col2 = st.columns(2)
        with b_col1:
            find_nearest = st.button("Query Nearest Node (KD-Tree)", key="btn_query_nearest")
        with b_col2:
            compare_index = st.button("Compare Index vs Brute-Force", key="btn_compare_index")

        if find_nearest or compare_index:
            try:
                # Retrieve index
                sp_index = get_spatial_index(graph, dataset_id=dataset)
                res_indexed = sp_index.nearest_node(float(q_lat), float(q_lon))

                res_bf = None
                if compare_index:
                    res_bf = brute_force_nearest_node(graph, float(q_lat), float(q_lon))

                st.session_state["spatial_query_result"] = (
                    res_indexed,
                    res_bf,
                    (float(q_lat), float(q_lon)),
                    sp_index.metadata,
                )
            except Exception as err:
                st.error(f"Spatial query failed: {err}")

        if "spatial_query_result" in st.session_state:
            res_idx, res_bf, q_point, meta = st.session_state["spatial_query_result"]
            dist_km = res_idx.distance_m / 1000.0
            st.success(
                f"Nearest Node: **{res_idx.node_id}** · "
                f"Distance: **{res_idx.distance_m:.2f} m** ({dist_km:.3f} km) · "
                f"Node Coords: ({res_idx.latitude:.6f}, {res_idx.longitude:.6f})"
            )

            if res_bf is not None:
                matches = (res_idx.node_id == res_bf.node_id) and (
                    abs(res_idx.distance_m - res_bf.distance_m) < 0.05
                )
                verif_text = "PASS (Equivalence Confirmed)" if matches else "FAIL"
                st.info(f"Correctness Verification: {verif_text}")
                st.write(
                    {
                        "KD-Tree Nearest Node": res_idx.node_id,
                        "Brute-Force Nearest Node": res_bf.node_id,
                        "KD-Tree Distance (m)": res_idx.distance_m,
                        "Brute-Force Distance (m)": res_bf.distance_m,
                        "Index Build Time (s)": round(meta.build_time_seconds, 6),
                    }
                )

            # Map view highlighting nearest node and query point
            if "partition_active_result" in st.session_state:
                active_res, _, _, _ = st.session_state["partition_active_result"]
                st.caption(
                    "Map showing query location (red marker) and nearest node (green highlight)"
                )
                highlight_map = partition_map(
                    graph,
                    active_res,
                    query_location=q_point,
                    nearest_node_id=res_idx.node_id,
                )
                st_folium(highlight_map, height=450, returned_objects=[], key="nearest_node_map")


if __name__ == "__main__":
    partitioning_page()
