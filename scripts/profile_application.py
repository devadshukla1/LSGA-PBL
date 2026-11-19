"""Application profiling tool for measuring execution runtime and identifying bottlenecks."""

import cProfile
import io
import pstats
import sys
import time
from pathlib import Path

import pandas as pd

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_sample_graph import build_sample
from src.analytics.centrality import centrality
from src.graph.validation import validate
from src.indexing.nearest_node import brute_force_nearest_node
from src.indexing.spatial_index import build_spatial_index
from src.partitioning.geographic import geographic_partition
from src.partitioning.graph_aware import graph_aware_partition
from src.routing.route_alternatives import find_alternative_routes
from src.routing.routing_service import find_route
from src.simulation.scenario_builder import create_scenario
from src.simulation.scenario_models import SimulationRequest
from src.simulation.simulation_engine import simulate


def profile_workload() -> list[dict]:
    """Execute and profile key application workloads."""
    records = []
    print("=" * 65)
    print("SMART CITY TRAFFIC & EMERGENCY ROUTE OPTIMIZER")
    print("PHASE 11: Application Performance Profiling")
    print("=" * 65)

    graph = build_sample()
    node_count = len(graph)
    edge_count = graph.number_of_edges()

    # 1. Graph Validation
    t0 = time.perf_counter()
    validate(graph)
    t_val = time.perf_counter() - t0
    records.append(
        {
            "operation": "graph_validation",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_val * 1000,
        }
    )

    # 2. Dijkstra (distance & travel_time)
    for obj in ("distance", "travel_time"):
        t0 = time.perf_counter()
        find_route(graph, 0, 10, "dijkstra", obj)
        t_dijk = time.perf_counter() - t0
        records.append(
            {
                "operation": f"routing_dijkstra_{obj}",
                "nodes": node_count,
                "edges": edge_count,
                "runtime_ms": t_dijk * 1000,
            }
        )

    # 3. A* (distance & travel_time)
    for obj in ("distance", "travel_time"):
        t0 = time.perf_counter()
        find_route(graph, 0, 10, "astar", obj)
        t_astar = time.perf_counter() - t0
        records.append(
            {
                "operation": f"routing_astar_{obj}",
                "nodes": node_count,
                "edges": edge_count,
                "runtime_ms": t_astar * 1000,
            }
        )

    # 4. Bidirectional Dijkstra
    for obj in ("distance", "travel_time"):
        t0 = time.perf_counter()
        find_route(graph, 0, 10, "bidirectional_dijkstra", obj)
        t_bidir = time.perf_counter() - t0
        records.append(
            {
                "operation": f"routing_bidirectional_{obj}",
                "nodes": node_count,
                "edges": edge_count,
                "runtime_ms": t_bidir * 1000,
            }
        )

    # 5. Yen's K-Shortest (K=3)
    t0 = time.perf_counter()
    find_alternative_routes(graph, 0, 10, k=3, objective="distance")
    t_yen = time.perf_counter() - t0
    records.append(
        {
            "operation": "routing_yen_k3",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_yen * 1000,
        }
    )

    # 6. Traffic Simulation
    sc = create_scenario(graph, "offline_sample", "heavy", 42, 0.5)
    req = SimulationRequest(0, 10, "dijkstra", "travel_time")
    t0 = time.perf_counter()
    simulate(graph, sc, req, "offline_sample")
    t_sim = time.perf_counter() - t0
    records.append(
        {
            "operation": "traffic_simulation",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_sim * 1000,
        }
    )

    # 7. Centrality Metrics
    for metric in ("degree", "betweenness", "closeness", "pagerank"):
        t0 = time.perf_counter()
        centrality(graph, metric=metric)
        t_cent = time.perf_counter() - t0
        records.append(
            {
                "operation": f"centrality_{metric}",
                "nodes": node_count,
                "edges": edge_count,
                "runtime_ms": t_cent * 1000,
            }
        )

    # 8. Partitioning
    t0 = time.perf_counter()
    geographic_partition(graph, k=4)
    t_geo = time.perf_counter() - t0
    records.append(
        {
            "operation": "partitioning_geographic",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_geo * 1000,
        }
    )

    t0 = time.perf_counter()
    graph_aware_partition(graph, k=4, seed=42)
    t_aware = time.perf_counter() - t0
    records.append(
        {
            "operation": "partitioning_graph_aware",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_aware * 1000,
        }
    )

    # 9. Spatial Indexing vs Brute-Force
    t0 = time.perf_counter()
    sp_index = build_spatial_index(graph)
    t_sp_build = time.perf_counter() - t0
    records.append(
        {
            "operation": "spatial_index_build",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_sp_build * 1000,
        }
    )

    t0 = time.perf_counter()
    sp_index.nearest_node(28.63, 77.21)
    t_sp_query = time.perf_counter() - t0
    records.append(
        {
            "operation": "spatial_index_query",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_sp_query * 1000,
        }
    )

    t0 = time.perf_counter()
    brute_force_nearest_node(graph, 28.63, 77.21)
    t_bf_query = time.perf_counter() - t0
    records.append(
        {
            "operation": "brute_force_query",
            "nodes": node_count,
            "edges": edge_count,
            "runtime_ms": t_bf_query * 1000,
        }
    )

    # Display profiling table
    df = pd.DataFrame(records)
    print("\nPROFILING SUMMARY TABLE:")
    print("-" * 65)
    for _, row in df.iterrows():
        print(f"  {row['operation']:<32} | {row['runtime_ms']:>8.3f} ms")
    print("-" * 65)

    # Save to CSV
    out_csv = ROOT / "results" / "qa" / "performance_profile.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"\n[INFO] Performance profile exported to: {out_csv}")

    return records


def run_cprofile():
    """Run cProfile on the overall application workload for deep function-level analysis."""
    print("\nExecuting cProfile for deep hotspot analysis...")
    profiler = cProfile.Profile()
    profiler.enable()

    # Representative pipeline
    graph = build_sample()
    find_route(graph, 0, 10, "astar", "travel_time")
    find_alternative_routes(graph, 0, 10, k=3, objective="travel_time")
    centrality(graph, metric="betweenness")
    geographic_partition(graph, k=4)
    build_spatial_index(graph)

    profiler.disable()
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
    ps.print_stats(15)
    print(s.getvalue())


if __name__ == "__main__":
    profile_workload()
    run_cprofile()
