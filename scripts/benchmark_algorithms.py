"""Comprehensive algorithm microbenchmarking and empirical scaling analysis.

Measures runtime using time.perf_counter_ns() across warm-up and repeated trials.
Saves:
- results/benchmarks/algorithm_benchmarks.csv
- results/benchmarks/benchmark_summary.json
- results/benchmarks/runtime_comparison.html
- results/benchmarks/scaling_analysis.html
"""

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.algorithms.bfs import find_route_bfs
from src.algorithms.dijkstra import find_route_dijkstra
from src.algorithms.minimum_transfers import find_route_min_transfers_then_fastest, find_route_minimum_transfers
from src.algorithms.transfer_aware_dijkstra import find_route_transfer_aware_dijkstra
from src.analytics.articulation_points import find_articulation_points
from src.analytics.betweenness_centrality import compute_betweenness_centrality
from src.analytics.degree_centrality import compute_degree_centrality
from src.analytics.graph_projection import build_analysis_graph
from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.loader import is_metro_dataset_available, load_validated_dataset
from src.graph.metro_builder import build_metro_graph
from src.simulation.closure_engine import simulate_station_closure


def benchmark_task(func, *args, warmups: int = 3, repetitions: int = 15, **kwargs):
    # Warmup runs
    for _ in range(warmups):
        func(*args, **kwargs)

    latencies_ms = []
    for _ in range(repetitions):
        t0 = time.perf_counter_ns()
        func(*args, **kwargs)
        t_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        latencies_ms.append(t_ms)

    arr = np.array(latencies_ms)
    return {
        "median_ms": float(np.median(arr)),
        "mean_ms": float(np.mean(arr)),
        "std_ms": float(np.std(arr)),
        "min_ms": float(np.min(arr)),
        "max_ms": float(np.max(arr)),
    }


def run_benchmarks(repetitions: int = 15):
    print("=" * 80)
    print("STARTING METROGRAPH ALGORITHM BENCHMARKING SUITE")
    print("=" * 80)

    datasets_to_test = []
    # Sample
    s_df, l_df, c_df, sl_df, _ = load_validated_dataset(SAMPLE_DATA_DIR)
    g_sample = build_metro_graph(s_df, l_df, c_df, sl_df)
    datasets_to_test.append(("Sample Graph (12 Stns)", g_sample, "S01", "S06", "S02"))

    # Delhi Metro
    if is_metro_dataset_available():
        ms_df, ml_df, mc_df, msl_df, _ = load_validated_dataset(METRO_DATA_DIR)
        g_delhi = build_metro_graph(ms_df, ml_df, mc_df, msl_df)
        datasets_to_test.append(("Delhi Metro Network (260 Stns)", g_delhi, "STN199", "STN026", "STN199"))

    results = []

    for ds_name, graph, src, dst, closure_target in datasets_to_test:
        v = graph.number_of_nodes()
        e = graph.number_of_edges()
        print(f"\nBenchmarking on: {ds_name} (|V|={v}, |E|={e})")

        # 1. BFS
        b_res = benchmark_task(find_route_bfs, graph, src, dst, repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "BFS (Min Stops)", "Complexity": "O(V + E)", **b_res,
        })
        print(f"  [BFS] Median: {b_res['median_ms']:.3f} ms")

        # 2. Dijkstra Time
        b_res = benchmark_task(find_route_dijkstra, graph, src, dst, objective="minimum_time", repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Dijkstra (Min Time)", "Complexity": "O((V + E) log V)", **b_res,
        })
        print(f"  [Dijkstra Time] Median: {b_res['median_ms']:.3f} ms")

        # 3. 0-1 BFS Transfers
        b_res = benchmark_task(find_route_minimum_transfers, graph, src, dst, repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "0-1 BFS (Min Transfers)", "Complexity": "O(L * (V + E))", **b_res,
        })
        print(f"  [0-1 BFS] Median: {b_res['median_ms']:.3f} ms")

        # 4. Lexicographic Dijkstra
        b_res = benchmark_task(find_route_min_transfers_then_fastest, graph, src, dst, repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Lexicographic Dijkstra", "Complexity": "O(S log S)", **b_res,
        })
        print(f"  [Lexicographic Dijkstra] Median: {b_res['median_ms']:.3f} ms")

        # 5. Transfer-Aware Dijkstra
        b_res = benchmark_task(
            find_route_transfer_aware_dijkstra,
            graph,
            src,
            dst,
            transfer_penalty_min=5.0,
            repetitions=repetitions,
        )
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Transfer-Aware Dijkstra", "Complexity": "O(S log S)", **b_res,
        })
        print(f"  [Transfer-Aware Dijkstra] Median: {b_res['median_ms']:.3f} ms")

        # 6. Graph Projection
        analysis_g = build_analysis_graph(graph)

        # 7. Degree Centrality
        b_res = benchmark_task(compute_degree_centrality, analysis_g, repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Degree Centrality", "Complexity": "O(V + E)", **b_res,
        })
        print(f"  [Degree Centrality] Median: {b_res['median_ms']:.3f} ms")

        # 8. Betweenness Centrality
        b_res = benchmark_task(compute_betweenness_centrality, analysis_g, repetitions=max(3, repetitions // 3))
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Betweenness Centrality", "Complexity": "O(V * E)", **b_res,
        })
        print(f"  [Betweenness Centrality] Median: {b_res['median_ms']:.3f} ms")

        # 9. Articulation Points
        b_res = benchmark_task(find_articulation_points, analysis_g, repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Articulation Points (Tarjan)", "Complexity": "O(V + E)", **b_res,
        })
        print(f"  [Articulation Points] Median: {b_res['median_ms']:.3f} ms")

        # 10. Closure Simulation & Recalculation
        b_res = benchmark_task(simulate_station_closure, graph, [closure_target], repetitions=repetitions)
        results.append({
            "Dataset": ds_name, "Nodes": v, "Edges": e,
            "Algorithm": "Closure Simulation Engine", "Complexity": "O(V + E)", **b_res,
        })
        print(f"  [Closure Engine] Median: {b_res['median_ms']:.3f} ms")

    bench_df = pd.DataFrame(results)

    # Save CSV
    out_csv = PROJECT_ROOT / "results" / "benchmarks" / "algorithm_benchmarks.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    bench_df.to_csv(out_csv, index=False)
    print(f"\n[SAVED] Benchmark metrics CSV: {out_csv}")

    # Save JSON summary with machine metadata
    meta = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python_version": platform.python_version(),
        "operating_system": platform.platform(),
        "processor": platform.processor(),
        "benchmarked_algorithms_count": len(bench_df),
        "repetitions": repetitions,
    }
    out_json = PROJECT_ROOT / "results" / "benchmarks" / "benchmark_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({"metadata": meta, "results": results}, f, indent=2)
    print(f"[SAVED] Benchmark JSON metadata: {out_json}")

    # Plot Comparison Charts
    fig_comp = px.bar(
        bench_df[bench_df["Dataset"].str.contains("Delhi")],
        x="Algorithm",
        y="median_ms",
        error_y="std_ms",
        title="Algorithm Execution Latency on Delhi Metro Network (260 Stations)",
        color="Algorithm",
    )
    chart_html1 = PROJECT_ROOT / "results" / "benchmarks" / "runtime_comparison.html"
    fig_comp.write_html(str(chart_html1))

    fig_scale = px.bar(
        bench_df,
        x="Algorithm",
        y="median_ms",
        color="Dataset",
        barmode="group",
        title="Empirical Algorithm Scaling: Sample (12 Nodes) vs. Delhi Metro (260 Nodes)",
    )
    chart_html2 = PROJECT_ROOT / "results" / "benchmarks" / "scaling_analysis.html"
    fig_scale.write_html(str(chart_html2))
    print(f"[SAVED] Plotly interactive comparison charts: {chart_html1.name}, {chart_html2.name}")

    print("=" * 80)
    print("BENCHMARK SUITE COMPLETE: ALL METRICS RECORDED")
    print("=" * 80)
    return bench_df


if __name__ == "__main__":
    run_benchmarks()
