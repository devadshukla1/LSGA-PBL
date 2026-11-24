"""ETL importer to transform raw transit datasets into standardized MetroGraph CSV tables."""

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.core.exceptions import DatasetError
from src.core.logging_config import get_logger
from src.core.settings import DEFAULT_ASSUMED_SPEED_KMPH, METRO_DATA_DIR

logger = get_logger("metrograph.importer")


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates straight-line great-circle distance between two GPS points in kilometers."""
    r = 6371.0  # Earth radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 3)


def normalize_station_name(raw_name: str) -> str:
    """Standardizes station names by stripping line connection tags and layout labels.

    Examples:
        'Welcome [Conn: Red]' -> 'Welcome'
        'Shaheed Sthal(First Station)' -> 'Shaheed Sthal'
        'Inderlok Conn:Red' -> 'Inderlok'
    """
    cleaned = re.sub(r"\[.*?\]", "", str(raw_name))
    cleaned = re.sub(r"\(First\s+[Ss]tation\)", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"Conn:.*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def compute_dataset_fingerprint(directory: Path | str) -> str:
    """Calculates a deterministic SHA256 hash of all CSV files in a dataset directory."""
    dir_path = Path(directory)
    hasher = hashlib.sha256()
    csv_files = sorted(dir_path.glob("*.csv"))
    for file in csv_files:
        hasher.update(file.name.encode("utf-8"))
        hasher.update(file.read_bytes())
    return hasher.hexdigest()[:16]


def import_raw_delhi_metro_dataset(
    raw_csv_path: Path | str,
    output_dir: Path | str = METRO_DATA_DIR,
    assumed_speed_kmph: float = DEFAULT_ASSUMED_SPEED_KMPH,
) -> Dict[str, any]:
    """Transforms raw Delhi-Metro-Network.csv into normalized MetroGraph CSV tables.

    Output files:
    - stations.csv: Unique stations with averaged coordinates.
    - lines.csv: Standard line metadata with color mappings.
    - station_lines.csv: Explicit station-to-line memberships (foreign key relation).
    - connections.csv: Segment connections with distance_km, estimated_time_min, and provenance.
    - metadata.json: Provenance, license, generation timestamp, and statistics.
    """
    raw_path = Path(raw_csv_path)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not raw_path.is_file():
        raise DatasetError(f"Raw Delhi Metro CSV file not found at: {raw_path}")

    raw_df = pd.read_csv(raw_path)
    required_raw_cols = ["Station ID", "Station Name", "Distance from Start (km)", "Line", "Latitude", "Longitude"]
    for col in required_raw_cols:
        if col not in raw_df.columns:
            raise DatasetError(f"Raw CSV missing expected column: {col}")

    # 1. Clean station names
    raw_df["clean_name"] = raw_df["Station Name"].apply(normalize_station_name)

    # Line colors lookup
    line_color_map = {
        "Red line": "#EF4444",
        "Yellow line": "#EAB308",
        "Blue line": "#3B82F6",
        "Blue line branch": "#60A5FA",
        "Green line": "#22C55E",
        "Green line branch": "#4ADE80",
        "Voilet line": "#8B5CF6",
        "Pink line": "#EC4899",
        "Magenta line": "#D946EF",
        "Aqua line": "#06B6D4",
        "Orange line": "#F97316",
        "Gray line": "#64748B",
        "Rapid Metro": "#6366F1",
    }

    # 2. Build Lines Table
    raw_lines = sorted(raw_df["Line"].unique().tolist())
    lines_list: List[Dict[str, str]] = []
    line_id_map: Dict[str, str] = {}
    for i, line_name in enumerate(raw_lines, start=1):
        lid = f"L{i:02d}"
        line_id_map[line_name] = lid
        lines_list.append({
            "line_id": lid,
            "line_name": line_name.strip(),
            "color": line_color_map.get(line_name, "#94A3B8"),
            "operator": "DMRC / NMRC / Rapid Metro",
        })
    lines_df = pd.DataFrame(lines_list)

    # 3. Build Stations Table (unique by clean_name, stable IDs)
    unique_station_names = sorted(raw_df["clean_name"].unique().tolist())
    station_id_map: Dict[str, str] = {}
    stations_list: List[Dict[str, any]] = []

    for i, name in enumerate(unique_station_names, start=1):
        sid = f"STN{i:03d}"
        station_id_map[name] = sid
        sub = raw_df[raw_df["clean_name"] == name]
        mean_lat = round(float(sub["Latitude"].mean()), 6)
        mean_lon = round(float(sub["Longitude"].mean()), 6)
        stations_list.append({
            "station_id": sid,
            "station_name": name,
            "latitude": mean_lat,
            "longitude": mean_lon,
        })
    stations_df = pd.DataFrame(stations_list)

    # 4. Build Station-Lines Table
    station_lines_list: List[Dict[str, str]] = []
    seen_sl = set()
    for _, row in raw_df.iterrows():
        sid = station_id_map[row["clean_name"]]
        lid = line_id_map[row["Line"]]
        pair = (sid, lid)
        if pair not in seen_sl:
            seen_sl.add(pair)
            station_lines_list.append({"station_id": sid, "line_id": lid})
    station_lines_df = pd.DataFrame(station_lines_list)

    # 5. Build Connections Table
    connections_list: List[Dict[str, any]] = []
    for line_name, group in raw_df.groupby("Line"):
        lid = line_id_map[line_name]
        sorted_group = group.sort_values("Distance from Start (km)")
        stn_names = sorted_group["clean_name"].tolist()
        cum_dists = sorted_group["Distance from Start (km)"].tolist()

        for j in range(len(stn_names) - 1):
            u_name = stn_names[j]
            v_name = stn_names[j + 1]
            u_id = station_id_map[u_name]
            v_id = station_id_map[v_name]

            # Calculate track distance difference
            dist_diff = round(cum_dists[j + 1] - cum_dists[j], 2)
            u_row = stations_df[stations_df["station_id"] == u_id].iloc[0]
            v_row = stations_df[stations_df["station_id"] == v_id].iloc[0]

            if dist_diff > 0:
                dist_km = dist_diff
                provenance = "published"
            else:
                # Proxy fallback to geodesic distance if difference is zero or missing
                geo_dist = haversine_distance_km(
                    u_row["latitude"], u_row["longitude"], v_row["latitude"], v_row["longitude"]
                )
                dist_km = max(0.5, round(geo_dist, 2))
                provenance = "geodesic_distance_km"

            # Travel time estimation: t = d / v * 60 (with 1.0 min station dwell time)
            est_time = round((dist_km / assumed_speed_kmph) * 60.0 + 1.0, 1)

            connections_list.append({
                "source_station_id": u_id,
                "destination_station_id": v_id,
                "line_id": lid,
                "distance_km": dist_km,
                "estimated_time_min": est_time,
                "weight_provenance": provenance,
            })

    # Add physical interchange pedestrian transfer between Noida Sector 51 (Aqua) & Noida Sector 52 (Blue)
    # Both stations are linked by a dedicated 300m pedestrian walkway / e-rickshaw corridor
    if "Noida Sector 51" in station_id_map and "Noida Sector 52" in station_id_map:
        s51_id = station_id_map["Noida Sector 51"]
        s52_id = station_id_map["Noida Sector 52"]
        # Inter-line pedestrian connection link
        connections_list.append({
            "source_station_id": s51_id,
            "destination_station_id": s52_id,
            "line_id": line_id_map.get("Aqua line", "L01"),
            "distance_km": 0.3,
            "estimated_time_min": 5.0,  # 5 min pedestrian transfer
            "weight_provenance": "derived",
        })

    connections_df = pd.DataFrame(connections_list)

    # 6. Save Normalized CSV Files
    stations_csv_path = out_dir / "stations.csv"
    lines_csv_path = out_dir / "lines.csv"
    station_lines_csv_path = out_dir / "station_lines.csv"
    connections_csv_path = out_dir / "connections.csv"

    stations_df.to_csv(stations_csv_path, index=False)
    lines_df.to_csv(lines_csv_path, index=False)
    station_lines_df.to_csv(station_lines_csv_path, index=False)
    connections_df.to_csv(connections_csv_path, index=False)

    fingerprint = compute_dataset_fingerprint(out_dir)

    # 7. Save Provenance Metadata
    metadata = {
        "dataset_name": "Delhi Metro Network Dataset (Normalized)",
        "source_organization": "Delhi Metro Rail Corporation (DMRC) open transit feeds via community archive",
        "original_url": "https://raw.githubusercontent.com/heyamay/Delhi-Metro-Network-Analysis/main/Delhi-Metro-Network.csv",
        "access_date": "2026-11-20",
        "license": "Open Data Commons Open Database License (ODbL) / Public Community Transit Data",
        "version": "2.0.0",
        "geographic_coverage": "National Capital Region (NCR), Delhi, Noida, Gurgaon, India",
        "station_count": len(stations_df),
        "line_count": len(lines_df),
        "connection_count": len(connections_df),
        "station_line_memberships": len(station_lines_df),
        "fingerprint": fingerprint,
        "assumed_speed_kmph": assumed_speed_kmph,
        "data_limitations": (
            "Segment distances derived from sequential distance-from-start metrics; "
            "Pedestrian walkway between Noida Sector 51 and Sector 52 added to link Aqua line; "
            "Estimated travel times computed via commercial average speed (35 km/h) plus dwell times."
        ),
    }

    metadata_path = out_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(
        "Successfully imported Delhi Metro dataset: %d stations, %d lines, %d connections. Fingerprint: %s",
        len(stations_df),
        len(lines_df),
        len(connections_df),
        fingerprint,
    )
    return metadata
