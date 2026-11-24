"""Configuration settings for MetroGraph Analytics."""

from pathlib import Path

# Base Paths (robust absolute paths derived from project root)
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
METRO_DATA_DIR = DATA_DIR / "metro"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
RESULTS_DIR = PROJECT_ROOT / "results"
BENCHMARKS_DIR = RESULTS_DIR / "benchmarks"
EXPORTS_DIR = RESULTS_DIR / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"

# Application Metadata
APP_NAME = "MetroGraph Analytics"
APP_TITLE = "Intelligent Metro Route Optimization and Critical Station Analysis"
APP_SUBTITLE = "Academic Graph Algorithms & Transit Network Analytics Framework"
APP_ICON = "🚇"

# Defaults
DEFAULT_CITY = "Delhi"
DEFAULT_DATASET = "synthetic"  # Default dataset as required by Phase 1/2 tests
DEFAULT_RANDOM_SEED = 42
DEFAULT_ROUTE_OBJECTIVE = "minimum_stops"
DEFAULT_TRANSFER_PENALTY_MINUTES = 5.0
DEFAULT_THEME = "dark"
DEFAULT_ASSUMED_SPEED_KMPH = 35.0  # Commercial average speed for estimated travel time

# Ensure runtime directories exist
RUNTIME_DIRS = [
    DATA_DIR,
    SAMPLE_DATA_DIR,
    METRO_DATA_DIR,
    PROCESSED_DATA_DIR,
    CACHE_DIR,
    RESULTS_DIR,
    BENCHMARKS_DIR,
    EXPORTS_DIR,
    LOGS_DIR,
]
for _dir in RUNTIME_DIRS:
    _dir.mkdir(parents=True, exist_ok=True)
