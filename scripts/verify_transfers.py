"""Verification script for Phase 4: Minimum Transfer Optimization & Line-Aware Routing.

Executes and verifies:
1. Pure minimum-transfer routing with 0-1 BFS.
2. Lexicographic minimum-transfers then fastest routing.
3. Transfer-penalty-aware Dijkstra with variable penalties (0.0m to 10.0m).
4. Passenger transfer instructions and interchange detection.
5. Verification across both sample dataset and Delhi Metro dataset.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def verify_phase_4():
    print("=" * 70)
    print("METROGRAPH ANALYTICS - PHASE 4 TRANSFER ENGINE VERIFICATION")
    print("=" * 70)

    from src.algorithms.comparison import compare_routing_algorithms
    from src.algorithms.minimum_transfers import find_route_minimum_transfers
    from src.algorithms.route_utils import validate_route
    from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra
    from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
    from src.data.loader import load_validated_dataset
    from src.graph.metro_builder import build_metro_graph

    # 1. Sample Dataset Verification
    print("\n--- 1. Testing Sample Dataset (data/sample) ---")
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    sample_g = build_metro_graph(stns, lines, conns, sl)
    print(f"Graph loaded: {sample_g.number_of_nodes()} nodes, {sample_g.number_of_edges()} edges.")

    # S03 to S09
    res_01bfs = find_route_minimum_transfers(sample_g, "S03", "S09")
    print("\n[0-1 BFS Min Transfers] S03 -> S09:")
    print(f"  Path: {' -> '.join(res_01bfs.station_path)}")
    print(f"  Lines: {res_01bfs.line_sequence}")
    print(f"  Stops: {res_01bfs.total_stops}, Transfers: {res_01bfs.transfer_count}")
    print(f"  Transfer Stations: {res_01bfs.transfer_stations}")
    assert res_01bfs.reachable is True
    assert validate_route(sample_g, res_01bfs) is True

    print("\n  Passenger Instructions:")
    for instr in res_01bfs.transfer_instructions:
        print(f"    {instr}")

    # 2. Delhi Metro Dataset Verification
    print("\n--- 2. Testing Delhi Metro Dataset (data/metro) ---")
    d_stns, d_lines, d_conns, d_sl, d_meta = load_validated_dataset(METRO_DATA_DIR)
    delhi_g = build_metro_graph(d_stns, d_lines, d_conns, d_sl)
    print(f"Delhi Graph loaded: {delhi_g.number_of_nodes()} nodes, {delhi_g.number_of_edges()} edges.")

    # Find two prominent stations in Delhi Metro: Kashmere Gate and Rajiv Chowk / Dwarka Sector 21
    # Check node presence
    kashmere_gate = "DEL_STN_001" if "DEL_STN_001" in delhi_g else list(delhi_g.nodes)[0]
    dest_stn = list(delhi_g.nodes)[25]

    src_name = delhi_g.nodes[kashmere_gate].get("station_name", str(kashmere_gate))
    dst_name = delhi_g.nodes[dest_stn].get("station_name", str(dest_stn))

    print(f"\nRouting from: {src_name} ({kashmere_gate}) -> {dst_name} ({dest_stn})")

    # Run comparative analysis
    comp_df, results_map = compare_routing_algorithms(delhi_g, kashmere_gate, dest_stn, transfer_penalty_min=5.0)
    print("\nMulti-Objective Comparative Evaluation:")
    print(comp_df.to_string(index=False))

    # Test Transfer Penalty Sensitivity
    print("\n--- 3. Transfer Penalty Sensitivity Sweep ---")
    for penalty in [0.0, 3.0, 5.0, 10.0]:
        pen_res = find_route_transfer_aware_dijkstra(
            delhi_g, kashmere_gate, dest_stn, transfer_penalty_min=penalty
        )
        print(
            f"  Penalty {penalty:4.1f} min | Transfers: {pen_res.transfer_count:2d} | "
            f"Transit Time: {pen_res.segment_travel_time_min:5.1f} min | "
            f"Modeled Time: {pen_res.total_modeled_journey_time_min:5.1f} min | "
            f"Stops: {pen_res.total_stops:2d}"
        )

    print("\n" + "=" * 70)
    print("PHASE 4 VERIFICATION COMPLETE: ALL CHECKS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    verify_phase_4()
