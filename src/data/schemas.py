"""Schemas and column type definitions for Metro datasets."""

from typing import Dict, List

STATIONS_REQUIRED_COLUMNS: List[str] = [
    "station_id",
    "station_name",
    "latitude",
    "longitude",
]

LINES_REQUIRED_COLUMNS: List[str] = [
    "line_id",
    "line_name",
    "color",
]

STATION_LINES_REQUIRED_COLUMNS: List[str] = [
    "station_id",
    "line_id",
]

CONNECTIONS_REQUIRED_COLUMNS: List[str] = [
    "source_station_id",
    "destination_station_id",
    "line_id",
]

# Column data type expectations
STATIONS_COLUMN_TYPES: Dict[str, type] = {
    "station_id": str,
    "station_name": str,
    "latitude": float,
    "longitude": float,
}

LINES_COLUMN_TYPES: Dict[str, type] = {
    "line_id": str,
    "line_name": str,
    "color": str,
}

STATION_LINES_COLUMN_TYPES: Dict[str, type] = {
    "station_id": str,
    "line_id": str,
}

CONNECTIONS_COLUMN_TYPES: Dict[str, type] = {
    "source_station_id": str,
    "destination_station_id": str,
    "line_id": str,
    "distance_km": float,
    "estimated_time_min": float,
    "weight_provenance": str,
}
