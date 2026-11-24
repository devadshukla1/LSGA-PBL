import shutil
import subprocess
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import config


def test_project_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    assert config.PROJECT_ROOT == root
    paths = {
        "DATA_DIR": "data",
        "RAW_DATA_DIR": "data/raw",
        "PROCESSED_DATA_DIR": "data/processed",
        "SCENARIOS_DIR": "data/scenarios",
        "SAMPLES_DIR": "data/samples",
        "RESULTS_DIR": "results",
        "BENCHMARKS_DIR": "results/benchmarks",
        "FIGURES_DIR": "results/figures",
        "EXPORTS_DIR": "results/exports",
        "LOGS_DIR": "logs",
    }
    for name, suffix in paths.items():
        assert getattr(config, name) == root / suffix


def test_defaults_and_immutability() -> None:
    settings = config.CONFIG
    assert settings.name == "SmartRoute Analytics"
    assert settings.default_city == "New Delhi, India"
    assert settings.random_seed == 42
    assert settings.routing_objective == "travel_time"
    assert settings.algorithm == "dijkstra"
    assert settings.partition_count == 4
    assert settings.benchmark_repetitions == 3
    assert settings.benchmark_pairs == 30
    with pytest.raises(FrozenInstanceError):
        settings.random_seed = 10


def test_import_creates_no_directories(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    shutil.copy(config.__file__, project)
    shutil.copytree(config.PROJECT_ROOT / "src", project / "src")
    subprocess.run(
        [sys.executable, "-B", "-c", "import config, src.utils.paths, src.utils.logger"],
        cwd=project,
        check=True,
    )
    assert {path.name for path in project.iterdir()} == {"config.py", "src"}
