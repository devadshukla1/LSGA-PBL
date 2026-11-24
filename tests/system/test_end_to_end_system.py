"""Full end-to-end system workflow test reproducing User Workflows A through F."""

from src.algorithms.bfs import find_route_bfs
from src.algorithms.comparison import compare_routing_algorithms
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.minimum_transfers import find_route_minimum_transfers
from src.analytics.station_comparison import compare_two_stations
from src.analytics.station_ranking import compute_station_analytics
from src.core.settings import SAMPLE_DATA_DIR
from src.data.loader import load_validated_dataset
from src.graph.interchanges import detect_interchange_stations
from src.graph.metro_builder import build_metro_graph
from src.simulation.closure_engine import simulate_station_closure
from src.simulation.impact_comparison import build_impact_comparison_table
from src.simulation.route_rerouting import compare_routes_across_closure


def test_full_system_workflows():
    # 1. Dataset Loading & Inspection (Workflow A)
    stations_df, lines_df, connections_df, station_lines_df, metadata = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stations_df, lines_df, connections_df, station_lines_df)
    assert graph.number_of_nodes() == 12
    interchange_res = detect_interchange_stations(station_lines_df, stations_df, lines_df)
    assert interchange_res["interchange_count"] == 4

    # 2. BFS and Dijkstra Route Planning (Workflow B)
    bfs_res = find_route_bfs(graph, "S01", "S06")
    assert bfs_res.reachable
    dijkstra_res = find_route_dijkstra(graph, "S01", "S06", objective="minimum_time")
    assert dijkstra_res.reachable

    # 3. Minimum Transfer & Multi-Objective Comparison (Workflow C)
    min_tr_res = find_route_minimum_transfers(graph, "S03", "S09")
    assert min_tr_res.reachable
    comp_df, results_map = compare_routing_algorithms(graph, "S03", "S09", transfer_penalty_min=5.0)
    assert len(comp_df) == 6

    # 4. Station Importance & Critical Interchanges (Workflow D)
    stn_results, summary, analysis_g = compute_station_analytics(graph, station_lines_df, lines_df)
    assert summary.total_stations == 12
    cmp_table = compare_two_stations("S01", "S04", stn_results)
    assert not cmp_table.empty

    # 5. Outage Simulation & Detour Rerouting (Workflow E)
    sim_res = simulate_station_closure(graph, ["S02"])
    assert sim_res.removed_stations_count == 1
    reroute_res = compare_routes_across_closure(
        original_graph=graph,
        simulated_graph=sim_res.simulation_graph,
        source="S01",
        destination="S03",
        closed_station_ids=sim_res.closed_station_ids,
        objective="Minimum Stops (BFS)",
    )
    assert reroute_res.disruption_status in ["UNCHANGED", "REROUTED", "UNREACHABLE"]

    # 6. Artifact & Table Generation (Workflow F)
    impact_table = build_impact_comparison_table(sim_res)
    assert len(impact_table) >= 7
