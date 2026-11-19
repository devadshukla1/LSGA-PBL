"""Export and loading utilities for benchmark CSV reports and JSON manifests."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import pandas as pd

from config import BENCHMARKS_DIR
from src.benchmarks.benchmark_models import (
    BenchmarkComparison,
    BenchmarkDataset,
    BenchmarkManifest,
    BenchmarkRunResult,
    BenchmarkSummary,
)


def export_benchmark_results(
    raw_results: list[BenchmarkRunResult],
    summaries: list[BenchmarkSummary],
    comparisons: list[BenchmarkComparison],
    datasets: list[BenchmarkDataset],
    manifest: BenchmarkManifest,
    output_directory: Path | str | None = None,
) -> Path:
    """Export benchmark run results, summaries, comparisons, datasets, and manifest.

    Creates structured CSV files and a JSON manifest in the target directory.
    """
    target_dir = (
        Path(output_directory)
        if output_directory is not None
        else (BENCHMARKS_DIR / manifest.experiment_id)
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Raw results
    raw_df = pd.DataFrame([asdict(r) for r in raw_results])
    raw_df.to_csv(target_dir / "benchmark_raw.csv", index=False)

    # 2. Summaries
    summary_df = pd.DataFrame([asdict(s) for s in summaries])
    summary_df.to_csv(target_dir / "benchmark_summary.csv", index=False)

    # 3. Comparisons
    comp_df = pd.DataFrame([asdict(c) for c in comparisons])
    comp_df.to_csv(target_dir / "benchmark_comparisons.csv", index=False)

    # 4. Correctness table (filtered view of raw timing runs)
    timing_runs = [r for r in raw_results if r.measurement_mode == "timing"]
    correctness_cols = [
        "experiment_id",
        "dataset_id",
        "graph_size_label",
        "source",
        "target",
        "algorithm",
        "objective",
        "route_found",
        "route_valid",
        "optimality_verified",
        "route_cost",
        "reference_cost",
        "absolute_cost_error",
        "relative_cost_error",
        "status",
        "error_message",
    ]
    corr_df = pd.DataFrame([asdict(r) for r in timing_runs])
    if not corr_df.empty:
        corr_df = corr_df[[c for c in correctness_cols if c in corr_df.columns]]
    corr_df.to_csv(target_dir / "benchmark_correctness.csv", index=False)

    # 5. Datasets metadata
    dataset_records = []
    for d in datasets:
        dataset_records.append(
            {
                "dataset_id": d.dataset_id,
                "dataset_origin": d.dataset_origin,
                "node_count": d.node_count,
                "edge_count": d.edge_count,
                "directed_density": d.directed_density,
                "weak_component_count": d.weak_component_count,
                "strong_component_count": d.strong_component_count,
                "sampling_method": d.sampling_method,
                "random_seed": d.random_seed,
            }
        )
    pd.DataFrame(dataset_records).to_csv(target_dir / "benchmark_datasets.csv", index=False)

    # 6. JSON manifest
    manifest_path = target_dir / "benchmark_manifest.json"
    manifest_dict = asdict(manifest)
    manifest_path.write_text(json.dumps(manifest_dict, indent=2), encoding="utf-8")

    return target_dir


def load_benchmark_experiment(experiment_dir: Path | str) -> dict[str, Any]:
    """Load all exported CSV files and manifest from an experiment directory."""
    path = Path(experiment_dir)
    if not path.is_dir():
        raise FileNotFoundError(f"Experiment directory not found: {path}")

    data: dict[str, Any] = {"path": path}

    # Manifest
    manifest_file = path / "benchmark_manifest.json"
    if manifest_file.is_file():
        data["manifest"] = json.loads(manifest_file.read_text(encoding="utf-8"))

    # CSV files
    csv_map = {
        "raw": "benchmark_raw.csv",
        "summary": "benchmark_summary.csv",
        "comparisons": "benchmark_comparisons.csv",
        "correctness": "benchmark_correctness.csv",
        "datasets": "benchmark_datasets.csv",
    }
    for key, filename in csv_map.items():
        csv_path = path / filename
        if csv_path.is_file():
            data[key] = pd.read_csv(csv_path)
        else:
            data[key] = pd.DataFrame()

    return data


def list_saved_experiments(base_dir: Path | str = BENCHMARKS_DIR) -> list[dict[str, Any]]:
    """List all saved benchmark experiments found in the base directory."""
    base = Path(base_dir)
    experiments: list[dict[str, Any]] = []

    if not base.is_dir():
        return experiments

    # Check for direct manifest in base_dir
    if (base / "benchmark_manifest.json").is_file():
        try:
            m = json.loads((base / "benchmark_manifest.json").read_text(encoding="utf-8"))
            experiments.append(
                {"id": m.get("experiment_id", base.name), "path": base, "manifest": m}
            )
        except Exception:
            pass

    # Check subdirectories
    for subdir in sorted(base.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        if subdir.is_dir() and (subdir / "benchmark_manifest.json").is_file():
            try:
                m = json.loads((subdir / "benchmark_manifest.json").read_text(encoding="utf-8"))
                experiments.append(
                    {"id": m.get("experiment_id", subdir.name), "path": subdir, "manifest": m}
                )
            except Exception:
                continue

    return experiments
