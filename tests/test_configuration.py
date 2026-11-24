"""Unit tests for central application configuration and paths."""

from config import (
    APP_NAME,
    CACHE_DIR,
    DATA_DIR,
    DEFAULT_CITY,
    DEFAULT_DATASET,
    DEFAULT_RANDOM_SEED,
    DEFAULT_ROUTE_OBJECTIVE,
    DEFAULT_THEME,
    DEFAULT_TRANSFER_PENALTY_MINUTES,
    EXPORTS_DIR,
    LOGS_DIR,
    PROJECT_ROOT,
    SAMPLE_DATA_DIR,
)


def test_paths_resolve_correctly():
    """Verify that all core application paths are absolute and exist or can be created."""
    assert PROJECT_ROOT.is_absolute()
    assert DATA_DIR.is_absolute()
    assert SAMPLE_DATA_DIR.is_absolute()
    assert LOGS_DIR.is_absolute()
    assert EXPORTS_DIR.is_absolute()

    assert DATA_DIR.exists()
    assert SAMPLE_DATA_DIR.exists()
    assert LOGS_DIR.exists()
    assert EXPORTS_DIR.exists()
    assert CACHE_DIR.exists()


def test_default_configuration_values():
    """Verify default parameters adhere to requirements."""
    assert APP_NAME == "MetroGraph Analytics"
    assert DEFAULT_CITY == "Delhi"
    assert DEFAULT_DATASET == "synthetic"
    assert DEFAULT_RANDOM_SEED == 42
    assert DEFAULT_ROUTE_OBJECTIVE == "minimum_stops"
    assert DEFAULT_TRANSFER_PENALTY_MINUTES == 5.0
    assert DEFAULT_THEME == "dark"


def test_sample_files_exist_under_sample_dir():
    """Verify that the synthetic dataset CSV files exist in SAMPLE_DATA_DIR."""
    assert (SAMPLE_DATA_DIR / "stations.csv").is_file()
    assert (SAMPLE_DATA_DIR / "lines.csv").is_file()
    assert (SAMPLE_DATA_DIR / "connections.csv").is_file()
