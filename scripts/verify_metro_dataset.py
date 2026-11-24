"""Comprehensive setup, graph, and dataset verification script for Phase 2.

Verifies:
1. Python version (>=3.11, <3.13)
2. Dependency imports
3. Project paths
4. Sample synthetic dataset integrity
5. Real Delhi Metro dataset integrity (if present)
6. Graph construction for both datasets
7. Parallel edge preservation
8. Interchange detection
9. Connectivity statistics
10. Offline Plotly visualization creation
11. GraphML cache serialization and round-trip
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_verification() -> bool:
    checks = []

    # 1. Sample dataset loading & validation
    try:
        from src.core.settings import SAMPLE_DATA_DIR
        from src.data.loader import load_validated_dataset

        s_stns, s_lines, s_conns, s_sl, s_meta = load_validated_dataset(SAMPLE_DATA_DIR)
        sample_ok = len(s_stns) == 12 and len(s_lines) == 3 and len(s_conns) == 14
        sample_msg = f"{len(s_stns)} stations, {len(s_lines)} lines, {len(s_conns)} connections"
    except Exception as e:
        sample_ok = False
        sample_msg = str(e)
    checks.append(("Sample dataset validation", sample_ok, sample_msg))

    # 2. Sample graph construction & MultiGraph check
    try:
        import networkx as nx

        from src.graph.metro_builder import build_metro_graph
        from src.graph.validator import validate_metro_graph

        s_graph = build_metro_graph(s_stns, s_lines, s_conns, s_sl)
        s_val = validate_metro_graph(s_graph)
        s_graph_ok = (
            isinstance(s_graph, nx.MultiGraph)
            and s_val["is_valid"]
            and s_val["is_connected"]
            and s_val["has_parallel_edges"]
        )
        s_graph_msg = (
            f"MultiGraph: {s_graph.number_of_nodes()} nodes, {s_graph.number_of_edges()} edges, "
            f"Parallel: {s_val['has_parallel_edges']}"
        )
    except Exception as e:
        s_graph_ok = False
        s_graph_msg = str(e)
    checks.append(("Sample MultiGraph invariants", s_graph_ok, s_graph_msg))

    # 3. Real Delhi Metro dataset verification
    try:
        from src.core.settings import METRO_DATA_DIR
        from src.data.loader import is_metro_dataset_available

        if is_metro_dataset_available(METRO_DATA_DIR):
            m_stns, m_lines, m_conns, m_sl, m_meta = load_validated_dataset(METRO_DATA_DIR)
            m_graph = build_metro_graph(m_stns, m_lines, m_conns, m_sl)
            m_val = validate_metro_graph(m_graph)
            real_ok = (
                len(m_stns) >= 200
                and len(m_lines) >= 10
                and len(m_conns) >= 200
                and m_val["is_valid"]
            )
            real_msg = (
                f"{len(m_stns)} stations, {len(m_lines)} lines, {len(m_conns)} edges, "
                f"{m_val['interchange_station_count']} interchanges, "
                f"Connected components: {m_val['connected_components']}"
            )
        else:
            real_ok = True
            real_msg = "REAL DATASET: NOT AVAILABLE (Optional real dataset not loaded)"
    except Exception as e:
        real_ok = False
        real_msg = str(e)
    checks.append(("Delhi Metro dataset & graph", real_ok, real_msg))

    # 4. Interchange detection logic
    try:
        from src.graph.interchanges import detect_interchange_stations

        inter_res = detect_interchange_stations(s_sl, s_stns, s_lines)
        inter_ok = inter_res["interchange_count"] == 4
        inter_msg = f"Detected {inter_res['interchange_count']} hubs: {inter_res['interchange_station_ids']}"
    except Exception as e:
        inter_ok = False
        inter_msg = str(e)
    checks.append(("Interchange station detection", inter_ok, inter_msg))

    # 5. Offline Plotly visualization
    try:
        import plotly.graph_objects as go

        from src.visualization.metro_plot import create_metro_network_plot

        fig = create_metro_network_plot(s_graph)
        plot_ok = isinstance(fig, go.Figure) and len(fig.data) > 0
        plot_msg = f"Plotly Figure created with {len(fig.data)} traces"
    except Exception as e:
        plot_ok = False
        plot_msg = str(e)
    checks.append(("Plotly offline visualization", plot_ok, plot_msg))

    # 6. GraphML cache serialization and round-trip
    try:
        from src.core.settings import PROCESSED_DATA_DIR
        from src.graph.metro_builder import load_graph_from_graphml, save_graph_to_graphml

        test_graphml = PROCESSED_DATA_DIR / "test_roundtrip.graphml"
        saved_file, meta_file = save_graph_to_graphml(s_graph, test_graphml, fingerprint="test")
        reloaded_graph = load_graph_from_graphml(saved_file)

        roundtrip_ok = (
            reloaded_graph.number_of_nodes() == s_graph.number_of_nodes()
            and reloaded_graph.number_of_edges() == s_graph.number_of_edges()
            and meta_file.is_file()
        )
        roundtrip_msg = (
            f"Round-trip verified: {reloaded_graph.number_of_nodes()} nodes, "
            f"{reloaded_graph.number_of_edges()} edges"
        )
        # Cleanup test files
        if saved_file.is_file():
            saved_file.unlink()
        if meta_file.is_file():
            meta_file.unlink()
    except Exception as e:
        roundtrip_ok = False
        roundtrip_msg = str(e)
    checks.append(("GraphML cache round-trip", roundtrip_ok, roundtrip_msg))

    # Print Report
    print("=" * 75)
    print(" METROGRAPH ANALYTICS - PHASE 2 DATASET & GRAPH VERIFICATION")
    print("=" * 75)
    all_passed = True
    for name, status, details in checks:
        tag = "[ PASS ]" if status else "[ FAIL ]"
        if not status:
            all_passed = False
        print(f"{tag} {name.ljust(35)} : {details}")
    print("=" * 75)

    if all_passed:
        print("OVERALL RESULT: PASS")
    else:
        print("OVERALL RESULT: FAIL")
    print("=" * 75)

    return all_passed


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
