"""Verification script for the end-to-end college demonstration workflow."""

import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.analytics.centrality import centrality
from src.analytics.critical_nodes import critical_nodes
from src.analytics.resilience import resilience_experiment
from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.report_export import export_benchmark_results
from src.graph.dataset_service import load
from src.graph.validation import validate
from src.indexing.spatial_index import build_spatial_index
from src.routing.route_alternatives import find_alternative_routes
from src.routing.routing_service import find_route
from src.simulation.scenario_builder import create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.simulation_engine import simulate


def run_demo_verification() -> bool:
    print("=" * 70)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("PHASE 11: End-to-End College Demonstration Workflow Verification")
    print("=" * 70)

    checklist = []

    # 1. Load graph & 2. Validate graph
    try:
        info = load("offline_sample")
        graph = info.graph
        rep = validate(graph, info.metadata)
        assert rep.valid
        checklist.append(
            (
                "1 & 2. Graph Loading and Validation",
                True,
                f"{len(graph)} nodes, {graph.number_of_edges()} edges",
            )
        )
    except Exception as err:
        import traceback

        traceback.print_exc()
        checklist.append(("1 & 2. Graph Loading and Validation", False, str(err)))
        return False

    # 3. Source/Target Selection, 4-7. Dijkstra, A*, Bidirectional Dijkstra
    try:
        source, target = 0, 10
        r_dijkstra = find_route(graph, source, target, "dijkstra", "travel_time")
        r_astar = find_route(graph, source, target, "astar", "travel_time")
        r_bidir = find_route(graph, source, target, "bidirectional_dijkstra", "travel_time")

        assert r_dijkstra.is_reachable and r_astar.is_reachable and r_bidir.is_reachable
        assert abs(r_dijkstra.optimized_cost - r_astar.optimized_cost) < 1e-4
        assert abs(r_dijkstra.optimized_cost - r_bidir.optimized_cost) < 1e-4
        checklist.append(
            (
                "3–7. Routing Equivalence (Dijkstra, A*, Bidirectional)",
                True,
                f"Identical optimal time: {r_dijkstra.optimized_cost:.2f} s",
            )
        )
    except Exception as err:
        checklist.append(
            ("3–7. Routing Equivalence (Dijkstra, A*, Bidirectional)", False, str(err))
        )

    # 8. Alternative routes
    try:
        alts = find_alternative_routes(graph, source, target, k=3, objective="travel_time")
        assert len(alts.routes) >= 2
        checklist.append(
            (
                "8. Yen's K-Shortest Detour Routes",
                True,
                f"Found {len(alts.routes)} alternative routes",
            )
        )
    except Exception as err:
        checklist.append(("8. Yen's K-Shortest Detour Routes", False, str(err)))

    # 9–12. Traffic Simulation & Rerouting
    try:
        baseline_edge = r_dijkstra.edge_path[0]
        scenario = create_scenario(
            graph,
            "offline_sample",
            level="heavy",
            seed=42,
            coverage=0.5,
            closed_edges=(baseline_edge,),
        )
        req = SimulationRequest(source, target, "dijkstra", "travel_time")
        sim_res = simulate(graph, scenario, req, "offline_sample")
        assert sim_res.status == "ok"
        assert baseline_edge not in sim_res.scenario_route.edge_path
        delay = sim_res.scenario_route.total_travel_time_s - sim_res.baseline.total_travel_time_s
        checklist.append(
            ("9–12. Traffic Congestion & Emergency Reroute", True, f"Delay delta: {delay:+.1f} s")
        )
    except Exception as err:
        checklist.append(("9–12. Traffic Congestion & Emergency Reroute", False, str(err)))

    # 13–15. Centrality, Critical Intersections, Resilience
    try:
        deg = centrality(graph, metric="degree")
        bet = centrality(graph, metric="betweenness")
        clo = centrality(graph, metric="closeness")
        pr = centrality(graph, metric="pagerank")
        metrics = {"degree": deg, "betweenness": bet, "closeness": clo, "pagerank": pr}
        crit = critical_nodes(graph, metrics, top_k=3)
        top_bottleneck = crit[0]["node_id"]

        resil = resilience_experiment(
            graph, deg.scores, "degree", (0.0, 0.2), seed=42, repetitions=3
        )
        assert len(resil) == 2
        checklist.append(
            (
                "13–15. Centrality, Bottlenecks, and Resilience",
                True,
                f"Top critical junction: {top_bottleneck}",
            )
        )
    except Exception as err:
        checklist.append(("13–15. Centrality, Bottlenecks, and Resilience", False, str(err)))

    # 16. Partitioning (Geographic vs Graph-Aware)
    try:
        from src.partitioning.partition_service import partition_graph

        res_geo, q_geo = partition_graph(graph, "geographic", k=4)
        res_aware, q_aware = partition_graph(graph, "graph_aware", k=4, seed=42)
        assert res_geo.actual_partition_count == 4 and res_aware.actual_partition_count == 4
        checklist.append(
            (
                "16. Graph Partitioning (Geographic & Graph-Aware)",
                True,
                f"K=4 (Geo cuts: {q_geo.cut_edge_count}, Aware cuts: {q_aware.cut_edge_count})",
            )
        )
    except Exception as err:
        checklist.append(("16. Graph Partitioning (Geographic & Graph-Aware)", False, str(err)))

    # 17–18. Spatial Indexing
    try:
        sp = build_spatial_index(graph)
        nearest = sp.nearest_node(28.63, 77.21)
        assert nearest.node_id in graph
        checklist.append(
            (
                "17–18. 3D KD-Tree Spatial Nearest-Node Lookup",
                True,
                f"Nearest: Node {nearest.node_id} ({nearest.distance_m:.1f} m)",
            )
        )
    except Exception as err:
        checklist.append(("17–18. 3D KD-Tree Spatial Nearest-Node Lookup", False, str(err)))

    # 19–20. Empirical Benchmark & Result Export
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            cfg = BenchmarkConfig(
                dataset_id="offline_sample",
                graph_sizes=[len(graph)],
                algorithms=["dijkstra", "astar", "bidirectional_dijkstra"],
                objectives=["distance"],
                query_count=3,
                repetitions=2,
                random_seed=42,
                memory_enabled=False,
                output_directory=Path(tmp_dir),
            )
            raw, summaries, comparisons, datasets_meta, manifest = run_benchmarks(graph, config=cfg)
            out = export_benchmark_results(
                raw, summaries, comparisons, datasets_meta, manifest, output_directory=Path(tmp_dir)
            )
            assert (out / "benchmark_summary.csv").is_file()
            checklist.append(
                (
                    "19–20. Benchmark Execution & Artifact Export",
                    True,
                    f"Saved {len(summaries)} summaries to {out.name}",
                )
            )
    except Exception as err:
        checklist.append(("19–20. Benchmark Execution & Artifact Export", False, str(err)))

    # Summary
    print("\nDEMONSTRATION CHECKLIST VERIFICATION:")
    print("-" * 70)
    all_ok = True
    for item, ok, detail in checklist:
        tag = "[PASS]" if ok else "[FAIL]"
        print(f"{tag} {item:<48} | {detail}")
        if not ok:
            all_ok = False
    print("-" * 70)

    if all_ok:
        print("DEMO VERIFICATION: PASS (Ready for College Examination)")
    else:
        print("DEMO VERIFICATION: FAIL")
    print("=" * 70)

    return all_ok


if __name__ == "__main__":
    success = run_demo_verification()
    sys.exit(0 if success else 1)
