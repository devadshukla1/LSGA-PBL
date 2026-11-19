"""Immutable application settings and project paths."""

from dataclasses import dataclass
from pathlib import Path

APP_NAME = "SmartRoute Analytics"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = (
    "Study how road direction, estimated travel time, congestion, and closures "
    "affect simulated emergency routes and urban road network resilience."
)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SCENARIOS_DIR = DATA_DIR / "scenarios"
SAMPLES_DIR = DATA_DIR / "samples"
RESULTS_DIR = PROJECT_ROOT / "results"
BENCHMARKS_DIR = RESULTS_DIR / "benchmarks"
FIGURES_DIR = RESULTS_DIR / "figures"
EXPORTS_DIR = RESULTS_DIR / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"
WORKSPACE_DIRECTORIES = (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    SCENARIOS_DIR,
    SAMPLES_DIR,
    BENCHMARKS_DIR,
    FIGURES_DIR,
    EXPORTS_DIR,
)

DEFAULT_CITY = "New Delhi, India"
DEFAULT_RANDOM_SEED = 42
DEFAULT_ROUTING_OBJECTIVE = "travel_time"
DEFAULT_ALGORITHM = "dijkstra"
DEFAULT_PARTITION_COUNT = 4
DEFAULT_BENCHMARK_REPETITIONS = 3
DEFAULT_BENCHMARK_PAIRS = 30


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Application metadata, path root, and experiment defaults."""

    name: str = APP_NAME
    version: str = APP_VERSION
    description: str = APP_DESCRIPTION
    project_root: Path = PROJECT_ROOT
    default_city: str = DEFAULT_CITY
    random_seed: int = DEFAULT_RANDOM_SEED
    routing_objective: str = DEFAULT_ROUTING_OBJECTIVE
    algorithm: str = DEFAULT_ALGORITHM
    partition_count: int = DEFAULT_PARTITION_COUNT
    benchmark_repetitions: int = DEFAULT_BENCHMARK_REPETITIONS
    benchmark_pairs: int = DEFAULT_BENCHMARK_PAIRS


CONFIG = AppConfig()
