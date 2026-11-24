"""Verification script for Phase 5: Station Importance & Critical Interchange Analysis.

Verifies:
1. Analytical graph projection from MultiGraph to simple Graph.
2. Degree centrality calculation against NetworkX oracle.
3. Betweenness centrality calculation against NetworkX oracle.
4. Articulation point detection against NetworkX oracle.
5. Interchange station detection.
6. Connected components analysis.
7. Station importance rankings dataframe generation.
8. Pairwise station comparison dataframe.
9. Visualization figure generation (Plotly network heatmap & bar chart).
10. Preservation of original MultiGraph without mutation.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_phase_5_verification() -> bool:
    print("=" * 70)
    print("METROGRAPH ANALYTICS - PHASE 5 STATION IMPORTANCE VERIFICATION")
    print("=" * 70)

    import networkx as nx

    from src.analytics.graph_projection import build_analysis_graph
    from src.analytics.station_comparison import compare_two_stations
    from src.analytics.station_ranking import compute_station_analytics, get_ranked_stations_dataframe
    from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
    from src.data.loader import load_validated_dataset
    from src.graph.metro_builder import build_metro_graph
    from src.visualization.metro_plot import plot_centrality_network, plot_top_stations

    checks = []

    # 1. Sample Dataset Verification
    print("\n--- 1. Testing Sample Dataset (data/sample) ---")
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    sample_mg = build_metro_graph(stns, lines, conns, sl)
    orig_nodes = sample_mg.number_of_nodes()
    orig_edges = sample_mg.number_of_edges()

    # Projection test
    sample_sg = build_analysis_graph(sample_mg)
    proj_ok = (
        isinstance(sample_sg, nx.Graph)
        and not isinstance(sample_sg, nx.MultiGraph)
        and sample_sg.number_of_nodes() == orig_nodes
        and sample_mg.number_of_edges() == orig_edges  # No mutation
    )
    details_msg = f"{sample_sg.number_of_nodes()} nodes, {sample_sg.number_of_edges()} edges"
    checks.append(("Analytical Graph Projection", proj_ok, details_msg))

    # Centrality and Invariants
    results, summary, sg = compute_station_analytics(sample_mg, sl, lines)
    nx_dc = nx.degree_centrality(sample_sg)
    nx_bc = nx.betweenness_centrality(sample_sg, normalized=True)
    nx_aps = set(nx.articulation_points(sample_sg))

    dc_matches = all(abs(r.degree_centrality - nx_dc[r.station_id]) < 1e-4 for r in results)
    checks.append(("Degree Centrality Oracle Match", dc_matches, f"Checked {len(results)} stations"))

    bc_matches = all(abs(r.betweenness_centrality - nx_bc[r.station_id]) < 1e-4 for r in results)
    checks.append(("Betweenness Centrality Oracle Match", bc_matches, f"Checked {len(results)} stations"))

    ap_set = {r.station_id for r in results if r.is_articulation_point}
    aps_match = ap_set == nx_aps
    checks.append(("Articulation Points Oracle Match", aps_match, f"Found {len(ap_set)}: {sorted(list(ap_set))}"))

    # Top rankings
    top_bc_df = get_ranked_stations_dataframe(results, sort_by="betweenness_centrality", top_n=5)
    rank_ok = len(top_bc_df) == 5 and "Betweenness Centrality" in top_bc_df.columns
    checks.append(("Station Rankings Pipeline", rank_ok, f"Top station: {top_bc_df.iloc[0]['Station Name']}"))

    # Pairwise comparison
    cmp_df = compare_two_stations("S01", "S04", results)
    cmp_ok = not cmp_df.empty and len(cmp_df) >= 8
    checks.append(("Station Pairwise Comparison", cmp_ok, f"Compared S01 and S04 ({len(cmp_df)} attributes)"))

    # Plotly figures
    fig_heat = plot_centrality_network(sample_mg, results, metric="betweenness_centrality")
    fig_bar = plot_top_stations(results, metric="betweenness_centrality", top_n=5)
    viz_ok = len(fig_heat.data) > 0 and len(fig_bar.data) > 0
    checks.append(("Offline Centrality Plotly Generation", viz_ok, "Heatmap & Bar chart rendered"))

    # 2. Delhi Metro Dataset Verification
    print("\n--- 2. Testing Delhi Metro Dataset (data/metro) ---")
    d_stns, d_lines, d_conns, d_sl, d_meta = load_validated_dataset(METRO_DATA_DIR)
    delhi_mg = build_metro_graph(d_stns, d_lines, d_conns, d_sl)
    d_results, d_summary, d_sg = compute_station_analytics(delhi_mg, d_sl, d_lines)

    delhi_ok = (
        d_summary.total_stations == 260
        and d_summary.total_interchanges == 25
        and d_summary.connected_components == 1
    )
    checks.append((
        "Delhi Metro Structural Analytics",
        delhi_ok,
        f"260 stations, 25 interchanges, {d_summary.total_articulation_points} articulation points, "
        f"Top Betweenness: {d_summary.highest_betweenness_station}, Top Degree: {d_summary.highest_degree_station}",
    ))

    # Print check outcomes
    all_passed = True
    print("\n" + "=" * 70)
    for name, passed, details in checks:
        status = "[ PASS ]" if passed else "[ FAIL ]"
        print(f"{status:8} {name:35} : {details}")
        if not passed:
            all_passed = False

    print("=" * 70)
    final_verdict = "PASS" if all_passed else "FAIL"
    print(f"OVERALL RESULT: {final_verdict}")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = run_phase_5_verification()
    sys.exit(0 if success else 1)
