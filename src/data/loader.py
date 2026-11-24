"""Data loading, dataset registration, and schema integrity verification service."""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

from src.core.exceptions import DatasetNotFoundError, SchemaValidationError
from src.core.logging_config import get_logger
from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.schemas import (
    CONNECTIONS_REQUIRED_COLUMNS,
    LINES_REQUIRED_COLUMNS,
    STATION_LINES_REQUIRED_COLUMNS,
    STATIONS_REQUIRED_COLUMNS,
)

logger = get_logger("metrograph.data_loader")


def is_metro_dataset_available(data_dir: Path | str = METRO_DATA_DIR) -> bool:
    """Checks whether the normalized real Delhi Metro dataset exists on disk."""
    dir_path = Path(data_dir)
    required = ["stations.csv", "lines.csv", "connections.csv", "station_lines.csv"]
    return all((dir_path / fname).is_file() for fname in required)


def load_raw_dataset(
    data_dir: Path | str = SAMPLE_DATA_DIR,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, any]]:
    """Loads stations.csv, lines.csv, connections.csv, station_lines.csv, and metadata.json.

    Returns:
        (stations_df, lines_df, connections_df, station_lines_df, metadata_dict)
    """
    directory = Path(data_dir)
    stations_path = directory / "stations.csv"
    lines_path = directory / "lines.csv"
    connections_path = directory / "connections.csv"
    station_lines_path = directory / "station_lines.csv"
    metadata_path = directory / "metadata.json"

    # Verify existence of core tables
    for path in [stations_path, lines_path, connections_path]:
        if not path.is_file():
            err_msg = f"Required dataset file not found: {path}"
            logger.error(err_msg)
            raise DatasetNotFoundError(err_msg)

    try:
        stations_df = pd.read_csv(stations_path)
        lines_df = pd.read_csv(lines_path)
        connections_df = pd.read_csv(connections_path)

        # Handle station_lines.csv (derive from connections if absent for backwards compatibility)
        if station_lines_path.is_file():
            station_lines_df = pd.read_csv(station_lines_path)
        else:
            # Fallback derivation
            derived = []
            for _, row in connections_df.iterrows():
                derived.append({"station_id": str(row["source_station_id"]), "line_id": str(row["line_id"])})
                derived.append({"station_id": str(row["destination_station_id"]), "line_id": str(row["line_id"])})
            station_lines_df = pd.DataFrame(derived).drop_duplicates()

        # Handle metadata.json
        if metadata_path.is_file():
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        else:
            metadata = {
                "dataset_name": directory.name,
                "version": "1.0.0",
                "station_count": len(stations_df),
                "line_count": len(lines_df),
                "connection_count": len(connections_df),
            }

    except Exception as e:
        err_msg = f"Failed to parse CSV/JSON files in {directory}: {e}"
        logger.error(err_msg)
        raise SchemaValidationError(err_msg) from e

    logger.info(
        "Loaded dataset from %s: %d stations, %d lines, %d connections, %d memberships.",
        directory.name,
        len(stations_df),
        len(lines_df),
        len(connections_df),
        len(station_lines_df),
    )
    return stations_df, lines_df, connections_df, station_lines_df, metadata


def validate_dataset(
    stations_df: pd.DataFrame,
    lines_df: pd.DataFrame,
    connections_df: pd.DataFrame,
    station_lines_df: Optional[pd.DataFrame] = None,
) -> Dict[str, any]:
    """Validates structural and relational integrity of the dataset.

    Returns structured report with 'status', 'errors', 'warnings', and 'info'.
    """
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # 1. Required columns
    for df, name, req_cols in [
        (stations_df, "stations", STATIONS_REQUIRED_COLUMNS),
        (lines_df, "lines", LINES_REQUIRED_COLUMNS),
        (connections_df, "connections", CONNECTIONS_REQUIRED_COLUMNS),
    ]:
        missing = [col for col in req_cols if col not in df.columns]
        if missing:
            errors.append(f"Missing required columns in {name}: {missing}")

    if station_lines_df is not None:
        missing_sl = [col for col in STATION_LINES_REQUIRED_COLUMNS if col not in station_lines_df.columns]
        if missing_sl:
            errors.append(f"Missing required columns in station_lines: {missing_sl}")

    if errors:
        raise SchemaValidationError("; ".join(errors))

    # 2. Check nulls in critical identifiers
    for df, name, req_cols in [
        (stations_df, "stations", ["station_id", "station_name", "latitude", "longitude"]),
        (lines_df, "lines", ["line_id", "line_name", "color"]),
        (connections_df, "connections", ["source_station_id", "destination_station_id", "line_id"]),
    ]:
        null_counts = df[req_cols].isnull().sum()
        if null_counts.any():
            errors.append(f"Null values in {name}: {null_counts[null_counts > 0].to_dict()}")

    # 3. Duplicate station_id / line_id
    dup_stns = stations_df[stations_df.duplicated("station_id", keep=False)]
    if not dup_stns.empty:
        errors.append(f"Duplicate station_id(s): {dup_stns['station_id'].unique().tolist()}")

    dup_lines = lines_df[lines_df.duplicated("line_id", keep=False)]
    if not dup_lines.empty:
        errors.append(f"Duplicate line_id(s): {dup_lines['line_id'].unique().tolist()}")

    # 4. Foreign key integrity
    valid_station_ids = set(stations_df["station_id"].astype(str))
    valid_line_ids = set(lines_df["line_id"].astype(str))

    invalid_sources = set(connections_df["source_station_id"].astype(str)) - valid_station_ids
    if invalid_sources:
        errors.append(f"Connections reference invalid source_station_id(s): {invalid_sources}")

    invalid_dests = set(connections_df["destination_station_id"].astype(str)) - valid_station_ids
    if invalid_dests:
        errors.append(f"Connections reference invalid destination_station_id(s): {invalid_dests}")

    invalid_lines = set(connections_df["line_id"].astype(str)) - valid_line_ids
    if invalid_lines:
        errors.append(f"Connections reference invalid line_id(s): {invalid_lines}")

    if station_lines_df is not None:
        invalid_sl_stns = set(station_lines_df["station_id"].astype(str)) - valid_station_ids
        if invalid_sl_stns:
            errors.append(f"station_lines reference invalid station_id(s): {invalid_sl_stns}")
        invalid_sl_lines = set(station_lines_df["line_id"].astype(str)) - valid_line_ids
        if invalid_sl_lines:
            errors.append(f"station_lines reference invalid line_id(s): {invalid_sl_lines}")

    # 5. Coordinate bounds check (lat roughly -90 to 90, lon -180 to 180)
    invalid_coords = stations_df[
        (stations_df["latitude"] < -90.0)
        | (stations_df["latitude"] > 90.0)
        | (stations_df["longitude"] < -180.0)
        | (stations_df["longitude"] > 180.0)
    ]
    if not invalid_coords.empty:
        errors.append(f"Invalid GPS coordinates found: {invalid_coords[['station_id', 'latitude', 'longitude']]}")

    # 6. Numeric weights validation
    if "distance_km" in connections_df.columns:
        non_pos_dist = connections_df[connections_df["distance_km"] <= 0]
        if not non_pos_dist.empty:
            errors.append(f"Non-positive distance_km found in {len(non_pos_dist)} connections")
    else:
        warnings.append("Optional column 'distance_km' not found in connections")

    if "estimated_time_min" in connections_df.columns:
        non_pos_time = connections_df[connections_df["estimated_time_min"] <= 0]
        if not non_pos_time.empty:
            errors.append(f"Non-positive estimated_time_min found in {len(non_pos_time)} connections")
    else:
        warnings.append("Optional column 'estimated_time_min' not found in connections")

    # 7. Check self-loops
    self_loops = connections_df[connections_df["source_station_id"] == connections_df["destination_station_id"]]
    if not self_loops.empty:
        errors.append(f"Self-loop connections detected: {len(self_loops)}")

    if errors:
        raise SchemaValidationError("; ".join(errors))

    report = {
        "status": "VALID",
        "station_count": len(stations_df),
        "line_count": len(lines_df),
        "connection_count": len(connections_df),
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }
    logger.info("Dataset validation report: %s", report)
    return report


def load_validated_dataset(
    data_dir: Path | str = SAMPLE_DATA_DIR,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, any]]:
    """Loads and validates all tables in a single atomic operation."""
    stations_df, lines_df, connections_df, station_lines_df, metadata = load_raw_dataset(data_dir)
    validate_dataset(stations_df, lines_df, connections_df, station_lines_df)
    return stations_df, lines_df, connections_df, station_lines_df, metadata
