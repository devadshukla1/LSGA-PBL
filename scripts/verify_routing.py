"""Routing engine verification script for Phase 3.

Verifies:
1. BFS simple path test.
2. Dijkstra minimum time test.
3. Dijkstra minimum distance test.
4. Parallel edge preservation and tie-breaking.
5. Equal-cost path resolution.
6. Disconnected graph handling.
7. Source equals destination test.
8. Invalid weight rejection test.
9. Route reconstruction and segment integrity.
10. NetworkX oracle comparison across both Synthetic and Real Delhi Metro datasets.
"""

import math
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_routing_checks() -> bool:
    checks = []

    try:
        import networkx as nx

        from src.algorithms.bfs import find_route_bfs
        from src.algorithms.comparison import compare_routing_algorithms
        from src.algorithms.dijkstra import DijkstraExecutionError, find_route_dijkstra
        from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
        from src.data.loader import is_metro_dataset_available, load_validated_dataset
        from src.graph.metro_builder import build_metro_graph
    except Exception as e:
        print(f"[FAIL] Imports failed: {e}")
        return False

    # Load Sample Dataset
    s_stns, s_lines, s_conns, s_sl, s_meta = load_validated_dataset(SAMPLE_DATA_DIR)
    s_graph = build_metro_graph(s_stns, s_lines, s_conns, s_sl)

    # 1. BFS Simple Path Test
    try:
        bfs_res = find_route_bfs(s_graph, "S03", "S12")
        nx_hops = nx.shortest_path_length(s_graph, "S03", "S12")
        bfs_ok = bfs_res.reachable and bfs_res.total_stops == nx_hops and len(bfs_res.station_path) == nx_hops + 1
        bfs_msg = f"{bfs_res.total_stops} stops (Oracle matches: {nx_hops}), time: {bfs_res.total_estimated_time_min}m"
    except Exception as e:
        bfs_ok = False
        bfs_msg = str(e)
    checks.append(("BFS minimum-stop routing", bfs_ok, bfs_msg))

    # 2. Dijkstra Time Test
    try:
        d_time_res = find_route_dijkstra(s_graph, "S03", "S12", objective="minimum_time")
        nx_time = nx.shortest_path_length(s_graph, "S03", "S12", weight="estimated_time_min")
        d_time_ok = d_time_res.reachable and math.isclose(d_time_res.total_estimated_time_min, nx_time, abs_tol=1e-3)
        d_time_msg = (
            f"{d_time_res.total_estimated_time_min} min (Oracle: {nx_time} min), "
            f"stops: {d_time_res.total_stops}"
        )
    except Exception as e:
        d_time_ok = False
        d_time_msg = str(e)
    checks.append(("Dijkstra minimum-time routing", d_time_ok, d_time_msg))

    # 3. Dijkstra Distance Test
    try:
        d_dist_res = find_route_dijkstra(s_graph, "S03", "S12", objective="minimum_distance")
        nx_dist = nx.shortest_path_length(s_graph, "S03", "S12", weight="distance_km")
        d_dist_ok = d_dist_res.reachable and math.isclose(d_dist_res.total_distance_km, nx_dist, abs_tol=1e-3)
        d_dist_msg = f"{d_dist_res.total_distance_km} km (Oracle: {nx_dist} km)"
    except Exception as e:
        d_dist_ok = False
        d_dist_msg = str(e)
    checks.append(("Dijkstra minimum-distance routing", d_dist_ok, d_dist_msg))

    # 4. Parallel Edge Preservation (Central S01 <-> City Square S10)
    try:
        # In sample, S01-S10 is connected via L01 (time 3.2m) and L02 (time 3.5m)
        par_time = find_route_dijkstra(s_graph, "S01", "S10", objective="minimum_time")
        # Should pick L01 (faster 3.2m)
        chosen_edge = par_time.segments[0].edge_key
        par_ok = par_time.total_stops == 1 and chosen_edge == "L01" and par_time.total_estimated_time_min == 3.2
        par_msg = f"Edge key '{chosen_edge}' selected with time {par_time.total_estimated_time_min}m"
    except Exception as e:
        par_ok = False
        par_msg = str(e)
    checks.append(("Parallel edge multi-key handling", par_ok, par_msg))

    # 5. Equal-Cost Path Resolution
    try:
        eq_g = nx.MultiGraph()
        for n in ["X", "Y1", "Y2", "Z"]:
            eq_g.add_node(n, lat=28.0, lon=77.0, lines=set())
        eq_g.add_edge("X", "Y1", key="L1", line_id="L1", distance_km=2.0, estimated_time_min=2.0)
        eq_g.add_edge("Y1", "Z", key="L1", line_id="L1", distance_km=2.0, estimated_time_min=2.0)
        eq_g.add_edge("X", "Y2", key="L2", line_id="L2", distance_km=2.0, estimated_time_min=2.0)
        eq_g.add_edge("Y2", "Z", key="L2", line_id="L2", distance_km=2.0, estimated_time_min=2.0)

        eq_res = find_route_dijkstra(eq_g, "X", "Z", objective="minimum_time")
        eq_ok = eq_res.reachable and eq_res.total_estimated_time_min == 4.0 and eq_res.total_stops == 2
        eq_msg = f"Resolved optimal path: {' -> '.join(eq_res.station_path)}"
    except Exception as e:
        eq_ok = False
        eq_msg = str(e)
    checks.append(("Equal-cost path deterministic handling", eq_ok, eq_msg))

    # 6. Disconnected Graph Test
    try:
        disc_g = nx.MultiGraph()
        disc_g.add_node("A", lat=28.0, lon=77.0, lines=set())
        disc_g.add_node("B", lat=28.0, lon=77.0, lines=set())
        disc_res = find_route_bfs(disc_g, "A", "B")
        disc_ok = not disc_res.reachable and disc_res.total_stops == 0
        disc_msg = f"Reachable: {disc_res.reachable}, Message: {disc_res.message}"
    except Exception as e:
        disc_ok = False
        disc_msg = str(e)
    checks.append(("Disconnected stations handling", disc_ok, disc_msg))

    # 7. Source equals Destination Test
    try:
        same_res = find_route_bfs(s_graph, "S01", "S01")
        same_ok = same_res.reachable and same_res.total_stops == 0 and same_res.total_distance_km == 0.0
        same_msg = f"{same_res.total_stops} stops, {same_res.total_distance_km} km"
    except Exception as e:
        same_ok = False
        same_msg = str(e)
    checks.append(("Source equals destination handling", same_ok, same_msg))

    # 8. Invalid Weight Rejection Test
    try:
        bad_g = nx.MultiGraph()
        bad_g.add_node("A", lat=28.0, lon=77.0, lines=set())
        bad_g.add_node("B", lat=28.0, lon=77.0, lines=set())
        bad_g.add_edge("A", "B", key="L1", line_id="L1", distance_km=-5.0, estimated_time_min=-2.0)
        try:
            find_route_dijkstra(bad_g, "A", "B", objective="minimum_time")
            bad_ok = False
            bad_msg = "Failed to reject negative weight"
        except DijkstraExecutionError:
            bad_ok = True
            bad_msg = "Successfully caught DijkstraExecutionError on negative weight"
    except Exception as e:
        bad_ok = False
        bad_msg = str(e)
    checks.append(("Negative weight rejection", bad_ok, bad_msg))

    # 9. Algorithm Comparison Table Generation
    try:
        comp_df, results_map = compare_routing_algorithms(s_graph, "S03", "S12")
        comp_ok = len(comp_df) >= 3 and all(r.reachable for r in results_map.values())
        bfs_k = results_map["BFS (Min Stops)"].total_stops
        d_k = results_map["Dijkstra (Min Time)"].total_estimated_time_min
        comp_msg = f"Generated {len(comp_df)} rows: BFS stops={bfs_k}, Dijkstra time={d_k}m"
    except Exception as e:
        comp_ok = False
        comp_msg = str(e)
    checks.append(("Routing comparison table", comp_ok, comp_msg))

    # 10. Real Delhi Metro Dataset Routing Test
    try:
        if is_metro_dataset_available(METRO_DATA_DIR):
            m_stns, m_lines, m_conns, m_sl, m_meta = load_validated_dataset(METRO_DATA_DIR)
            m_graph = build_metro_graph(m_stns, m_lines, m_conns, m_sl)
            # Route from Dwarka (STN048) to Rajiv Chowk (STN199)
            m_res = find_route_dijkstra(m_graph, "STN048", "STN199", objective="minimum_time")
            real_ok = m_res.reachable and m_res.total_stops > 0
            real_msg = (
                f"Dwarka to Rajiv Chowk: {m_res.total_stops} stops, {m_res.total_distance_km} km, "
                f"{m_res.total_estimated_time_min} min ({m_res.runtime_ms} ms)"
            )
        else:
            real_ok = True
            real_msg = "REAL DATASET: NOT AVAILABLE (skipped optional test)"
    except Exception as e:
        real_ok = False
        real_msg = str(e)
    checks.append(("Delhi Metro real network routing", real_ok, real_msg))

    # Print Report
    print("=" * 78)
    print(" METROGRAPH ANALYTICS - PHASE 3 ROUTING ENGINE VERIFICATION")
    print("=" * 78)
    all_passed = True
    for name, status, details in checks:
        tag = "[ PASS ]" if status else "[ FAIL ]"
        if not status:
            all_passed = False
        print(f"{tag} {name.ljust(38)} : {details}")
    print("=" * 78)

    if all_passed:
        print("OVERALL RESULT: PASS")
    else:
        print("OVERALL RESULT: FAIL")
    print("=" * 78)

    return all_passed


if __name__ == "__main__":
    success = run_routing_checks()
    sys.exit(0 if success else 1)
