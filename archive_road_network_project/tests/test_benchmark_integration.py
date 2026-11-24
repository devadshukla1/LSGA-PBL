"""Integration tests running end-to-end benchmarking over the offline road network sample."""

import copy

from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.report_export import export_benchmark_results, load_benchmark_experiment
from src.graph.dataset_service import load
from src.visualization.benchmark_charts import (
    chart_algorithm_speedup,
    chart_correctness_summary,
    chart_explored_nodes,
    chart_memory_by_algorithm,
    chart_runtime_by_algorithm,
    chart_runtime_distribution,
    chart_runtime_vs_graph_size,
)


def test_end_to_end_benchmark_workflow(tmp_path):
    info = load()
    graph = info.graph
    nodes_before = copy.deepcopy(dict(graph.nodes(data=True)))
    edges_before = copy.deepcopy(list(graph.edges(keys=True, data=True)))

    # Full config with 3 algorithms and both objectives
    cfg = BenchmarkConfig(
        dataset_id="offline_sample",
        graph_sizes=[12],
        algorithms=["dijkstra", "astar", "bidirectional_dijkstra"],
        objectives=["distance", "travel_time"],
        query_count=4,
        repetitions=2,
        warmup_runs=1,
        memory_enabled=True,
        correctness_enabled=True,
    )

    raw, summaries, comparisons, datasets, manifest = run_benchmarks(graph, config=cfg)

    # Export to tmp_path
    out_dir = export_benchmark_results(
        raw, summaries, comparisons, datasets, manifest, output_directory=tmp_path
    )
    loaded = load_benchmark_experiment(out_dir)

    summary_df = loaded["summary"]
    raw_df = loaded["raw"]
    comp_df = loaded["comparisons"]

    assert not summary_df.empty
    assert not raw_df.empty

    # Verify chart generation works without exception
    fig1 = chart_runtime_by_algorithm(summary_df)
    fig2 = chart_runtime_vs_graph_size(summary_df)
    fig3 = chart_explored_nodes(summary_df)
    fig4 = chart_memory_by_algorithm(summary_df)
    fig5 = chart_runtime_distribution(raw_df)
    fig6 = chart_correctness_summary(summary_df)
    if not comp_df.empty:
        fig7 = chart_algorithm_speedup(comp_df)
        assert fig7 is not None

    for fig in (fig1, fig2, fig3, fig4, fig5, fig6):
        assert fig is not None

    # Verify original graph immutability
    assert dict(graph.nodes(data=True)) == nodes_before
    assert list(graph.edges(keys=True, data=True)) == edges_before
