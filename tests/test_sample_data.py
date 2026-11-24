"""Unit tests for sample synthetic metro dataset integrity."""

import pytest

from src.core.exceptions import SchemaValidationError
from src.data.loader import load_raw_dataset, validate_dataset


def test_sample_csv_files_load():
    """Verify raw dataset loads without disk I/O errors."""
    stations_df, lines_df, connections_df, station_lines_df, metadata = load_raw_dataset()
    assert not stations_df.empty
    assert not lines_df.empty
    assert not connections_df.empty
    assert len(stations_df) >= 10
    assert len(lines_df) >= 3


def test_station_ids_unique():
    """Verify that every station ID in stations.csv is unique."""
    stations_df, _, _, _, _ = load_raw_dataset()
    assert stations_df["station_id"].is_unique


def test_line_ids_unique():
    """Verify that every line ID in lines.csv is unique."""
    _, lines_df, _, _, _ = load_raw_dataset()
    assert lines_df["line_id"].is_unique


def test_connection_referential_integrity():
    """Verify connection endpoints and line references exist in station/line tables."""
    stations_df, lines_df, connections_df, _, _ = load_raw_dataset()
    valid_stations = set(stations_df["station_id"])
    valid_lines = set(lines_df["line_id"])

    assert set(connections_df["source_station_id"]).issubset(valid_stations)
    assert set(connections_df["destination_station_id"]).issubset(valid_stations)
    assert set(connections_df["line_id"]).issubset(valid_lines)


def test_numeric_weights_strictly_positive():
    """Verify distance_km and estimated_time_min are strictly greater than zero."""
    _, _, connections_df, _, _ = load_raw_dataset()
    assert (connections_df["distance_km"] > 0).all()
    assert (connections_df["estimated_time_min"] > 0).all()


def test_validation_detects_corrupt_data():
    """Verify validator flags invalid data schemas properly."""
    stations_df, lines_df, connections_df, station_lines_df, _ = load_raw_dataset()
    bad_connections = connections_df.copy()
    bad_connections.loc[0, "distance_km"] = -5.0

    with pytest.raises(SchemaValidationError):
        validate_dataset(stations_df, lines_df, bad_connections, station_lines_df)
