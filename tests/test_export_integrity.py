"""Tests verifying exported benchmark CSV and JSON files, schemas, and values."""

import json
from pathlib import Path

import pandas as pd

from config import BENCHMARKS_DIR
from scripts.generate_sample_graph import build_sample
from src.benchmarks.benchmark_models import BenchmarkConfig
from src.benchmarks.benchmark_runner import run_benchmarks
from src.benchmarks.report_export import export_benchmark_results, list_saved_experiments


def test_export_benchmark_csv_and_json(tmp_path: Path) -> None:
    """Verify exported benchmark folder contains valid CSVs and parseable manifest JSON."""
    graph = build_sample()
    config = BenchmarkConfig(
        dataset_id="offline_sample",
        graph_sizes=[len(graph)],
        algorithms=["dijkstra"],
        objectives=["distance"],
        query_count=2,
        repetitions=1,
        random_seed=42,
        memory_enabled=False,
    )
    raw, summaries, comparisons, datasets_meta, manifest = run_benchmarks(graph, config=config)

    out_dir = export_benchmark_results(
        raw,
        summaries,
        comparisons,
        datasets_meta,
        manifest,
        output_directory=tmp_path,
    )

    assert out_dir.is_dir()
    manifest_file = out_dir / "benchmark_manifest.json"
    summary_file = out_dir / "benchmark_summary.csv"
    raw_file = out_dir / "benchmark_raw.csv"

    assert manifest_file.is_file()
    assert summary_file.is_file()
    assert raw_file.is_file()

    # Parse JSON
    with manifest_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["dataset_id"] == "offline_sample"
    assert "experiment_id" in data

    # Parse CSVs
    sum_df = pd.read_csv(summary_file)
    assert not sum_df.empty
    assert "mean_runtime_ms" in sum_df.columns
    assert "route_validity_rate" in sum_df.columns

    raw_df = pd.read_csv(raw_file)
    assert not raw_df.empty
    assert "runtime_ns" in raw_df.columns


def test_list_saved_experiments() -> None:
    """Verify listing saved benchmark experiments discovers generated runs."""
    experiments = list_saved_experiments(BENCHMARKS_DIR)
    assert isinstance(experiments, list)
    if experiments:
        first = experiments[0]
        assert "id" in first
        assert "path" in first
        assert "manifest" in first
        assert "timestamp_utc" in first["manifest"]
