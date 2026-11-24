"""Unit tests for Phase 2 data model, interchange detection, and GraphML caching."""

import networkx as nx
import pandas as pd
import pytest

from src.core.settings import METRO_DATA_DIR, SAMPLE_DATA_DIR
from src.data.importer import (
    compute_dataset_fingerprint,
    haversine_distance_km,
    normalize_station_name,
)
from src.data.loader import (
    is_metro_dataset_available,
    load_validated_dataset,
)
from src.graph.interchanges import detect_interchange_stations
from src.graph.metro_builder import (
    build_metro_graph,
    load_graph_from_graphml,
    save_graph_to_graphml,
)
from src.graph.validator import validate_metro_graph
from src.visualization.metro_plot import create_metro_network_plot


def test_station_name_normalization():
    """Verify regex normalization cleans interchange notes and suffixes without data loss."""
    assert normalize_station_name("Welcome [Conn: Red]") == "Welcome"
    assert normalize_station_name("Shaheed Sthal(First Station)") == "Shaheed Sthal"
    assert normalize_station_name("Inderlok Conn:Red") == "Inderlok"
    assert normalize_station_name("  Central  Secretariat  ") == "Central Secretariat"


def test_haversine_formula():
    """Verify great-circle distance computation between known GPS coordinates."""
    # Delhi Connaught Place to New Delhi Railway Station (~1.5 km)
    dist = haversine_distance_km(28.6315, 77.2167, 28.6430, 77.2195)
    assert 1.0 <= dist <= 2.0


def test_dataset_fingerprint():
    """Verify SHA256 directory fingerprinting is deterministic."""
    fp1 = compute_dataset_fingerprint(SAMPLE_DATA_DIR)
    fp2 = compute_dataset_fingerprint(SAMPLE_DATA_DIR)
    assert fp1 == fp2
    assert len(fp1) == 16


def test_station_lines_membership_schema():
    """Verify station_lines table loads and matches foreign key constraints."""
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    assert not sl.empty
    assert set(sl["station_id"]).issubset(set(stns["station_id"]))
    assert set(sl["line_id"]).issubset(set(lines["line_id"]))


def test_interchange_detection_logic():
    """Verify structural detection correctly identifies multi-line stations."""
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    res = detect_interchange_stations(sl, stns, lines)
    assert res["interchange_count"] == 4
    assert set(res["interchange_station_ids"]) == {"S01", "S04", "S10", "S12"}
    assert not res["interchange_details"].empty


def test_graphml_cache_serialization_and_roundtrip(tmp_path):
    """Verify MultiGraph can be serialized to GraphML and restored without loss."""
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stns, lines, conns, sl)

    test_file = tmp_path / "cache_test.graphml"
    save_graph_to_graphml(graph, test_file, fingerprint="test_hash")
    assert test_file.is_file()
    assert test_file.with_suffix(".json").is_file()

    reloaded = load_graph_from_graphml(test_file)
    assert isinstance(reloaded, nx.MultiGraph)
    assert reloaded.number_of_nodes() == graph.number_of_nodes()
    assert reloaded.number_of_edges() == graph.number_of_edges()

    # Invariants on reloaded node attributes
    for node, data in reloaded.nodes(data=True):
        assert isinstance(data["lines"], set)
        assert isinstance(data["lat"], float)
        assert isinstance(data["lon"], float)


def test_disconnected_dataset_validation():
    """Verify validator correctly identifies disconnected components."""
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    # Add an isolated station
    iso_stn = pd.DataFrame([{
        "station_id": "S99",
        "station_name": "Isolated Station",
        "latitude": 28.50,
        "longitude": 77.10,
    }])
    extended_stns = pd.concat([stns, iso_stn], ignore_index=True)
    extended_sl = pd.concat([sl, pd.DataFrame([{"station_id": "S99", "line_id": "L01"}])], ignore_index=True)

    g = build_metro_graph(extended_stns, lines, conns, extended_sl)
    diag = validate_metro_graph(g)
    assert diag["is_connected"] is False
    assert diag["connected_components"] == 2
    assert "S99" in diag["isolated_nodes"]


def test_delhi_metro_real_dataset_integrity():
    """Verify real Delhi Metro dataset passes validation when present."""
    if not is_metro_dataset_available(METRO_DATA_DIR):
        pytest.skip("Real Delhi Metro dataset not downloaded or present.")

    stns, lines, conns, sl, meta = load_validated_dataset(METRO_DATA_DIR)
    assert len(stns) >= 200
    assert len(lines) >= 10
    assert len(conns) >= 200
    assert len(sl) >= 200

    graph = build_metro_graph(stns, lines, conns, sl)
    diag = validate_metro_graph(graph)
    assert diag["is_valid"] is True
    assert diag["is_connected"] is True
    assert diag["interchange_station_count"] >= 20


def test_plotly_visualization_with_filters():
    """Verify Plotly schematic can render with line filters and interchange toggles."""
    stns, lines, conns, sl, meta = load_validated_dataset(SAMPLE_DATA_DIR)
    graph = build_metro_graph(stns, lines, conns, sl)

    fig_all = create_metro_network_plot(graph)
    assert len(fig_all.data) > 0

    fig_filtered = create_metro_network_plot(graph, selected_line="Red Line", filter_interchanges_only=True)
    assert len(fig_filtered.data) > 0
