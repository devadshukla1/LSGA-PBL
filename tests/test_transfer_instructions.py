"""Tests for transfer counting, station detection, and passenger instructions."""

from src.algorithms.routing_models import RouteSegment
from src.algorithms.transfer_utils import (
    build_transfer_instructions,
    count_transfers,
    extract_transfer_stations,
    validate_line_sequence,
)


def test_count_transfers_empty_or_single():
    assert count_transfers([]) == 0
    assert count_transfers(["L1"]) == 0
    assert count_transfers(["L1", "L1", "L1"]) == 0
    assert count_transfers(["L1", "L2"]) == 1
    assert count_transfers(["L1", "L2", "L2", "L3", "L1"]) == 3


def test_extract_transfer_stations():
    segs = [
        RouteSegment("S1", "S2", "e1", "L1", "Line 1", "#FF0000", 2.0, 3.0),
        RouteSegment("S2", "S3", "e2", "L1", "Line 1", "#FF0000", 2.0, 3.0),
        RouteSegment("S3", "S4", "e3", "L2", "Line 2", "#0000FF", 2.0, 3.0),
        RouteSegment("S4", "S5", "e4", "L3", "Line 3", "#00FF00", 2.0, 3.0),
    ]
    interchanges = extract_transfer_stations(segs)
    assert len(interchanges) == 2
    assert interchanges[0]["station_id"] == "S3"
    assert interchanges[0]["from_line_id"] == "L1"
    assert interchanges[0]["to_line_id"] == "L2"
    assert interchanges[1]["station_id"] == "S4"
    assert interchanges[1]["from_line_id"] == "L2"
    assert interchanges[1]["to_line_id"] == "L3"


def test_build_transfer_instructions():
    segs = [
        RouteSegment("101", "102", "e1", "L1", "Red Line", "#FF0000", 1.5, 2.5),
        RouteSegment("102", "103", "e2", "L1", "Red Line", "#FF0000", 1.5, 2.5),
        RouteSegment("103", "104", "e3", "L2", "Blue Line", "#0000FF", 2.0, 3.0),
    ]
    path = ["101", "102", "103", "104"]
    names = {
        "101": "Central Park",
        "102": "Midtown",
        "103": "Times Square",
        "104": "Grand Station",
    }
    instructions = build_transfer_instructions(path, segs, names)
    assert len(instructions) == 4
    assert "Board **Red Line** at **Central Park**" in instructions[0]
    assert "transfer from **Red Line** to **Blue Line**" in instructions[1]
    assert "Ride **Blue Line** 1 stop" in instructions[2]
    assert "Alight at final destination: **Grand Station**" in instructions[3]


def test_validate_line_sequence():
    valid_segs = [
        RouteSegment("A", "B", "1", "L1", "L1", "#000", 1.0, 1.0),
        RouteSegment("B", "C", "2", "L1", "L1", "#000", 1.0, 1.0),
    ]
    assert validate_line_sequence(valid_segs) is True

    broken_segs = [
        RouteSegment("A", "B", "1", "L1", "L1", "#000", 1.0, 1.0),
        RouteSegment("C", "D", "2", "L1", "L1", "#000", 1.0, 1.0),
    ]
    assert validate_line_sequence(broken_segs) is False
