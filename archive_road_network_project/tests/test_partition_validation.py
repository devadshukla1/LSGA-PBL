"""Tests for partition result validation rules."""

import networkx as nx
import pytest

from src.partitioning.partition_models import PartitionResult
from src.partitioning.partition_validation import (
    assert_valid_partition,
    validate_partition_result,
)


def _build_test_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(4):
        g.add_node(i, x=77.20 + i * 0.01, y=28.60)
    g.add_edge(0, 1, length_m=10.0, speed_kph=30.0, travel_time_s=1.2)
    return g


def test_valid_partition():
    g = _build_test_graph()
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 1, 3: 1},
        partition_to_nodes={0: [0, 1], 1: [2, 3]},
    )
    is_valid, issues = validate_partition_result(g, result, expected_k=2)
    assert is_valid
    assert len(issues) == 0
    assert_valid_partition(g, result, expected_k=2)


def test_missing_node_assignment():
    g = _build_test_graph()
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 1},  # Node 3 missing!
        partition_to_nodes={0: [0, 1], 1: [2]},
    )
    is_valid, issues = validate_partition_result(g, result, expected_k=2)
    assert not is_valid
    assert any("Missing partition assignments" in issue for issue in issues)
    with pytest.raises(ValueError, match="Partition validation failed"):
        assert_valid_partition(g, result, expected_k=2)


def test_unknown_node_assignment():
    g = _build_test_graph()
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 1, 3: 1, 999: 1},  # 999 not in graph
        partition_to_nodes={0: [0, 1], 1: [2, 3, 999]},
    )
    is_valid, issues = validate_partition_result(g, result, expected_k=2)
    assert not is_valid
    assert any("Unknown node IDs" in issue for issue in issues)


def test_invalid_partition_id():
    g = _build_test_graph()
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 1, 3: 5},  # Partition 5 is >= K=2
        partition_to_nodes={0: [0, 1], 1: [2], 5: [3]},
    )
    is_valid, issues = validate_partition_result(g, result, expected_k=2)
    assert not is_valid
    assert any("Invalid partition IDs" in issue for issue in issues)


def test_empty_partition_detected():
    g = _build_test_graph()
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0, 1: 0, 2: 0, 3: 0},
        partition_to_nodes={0: [0, 1, 2, 3], 1: []},  # Partition 1 is empty!
    )
    is_valid, issues = validate_partition_result(g, result, expected_k=2)
    assert not is_valid
    assert any("Unintended empty partitions" in issue for issue in issues)


def test_k_exceeds_node_count():
    g = _build_test_graph()
    result = PartitionResult(
        algorithm="test",
        requested_partition_count=10,
        actual_partition_count=10,
        node_to_partition={0: 0, 1: 1, 2: 2, 3: 3},
        partition_to_nodes={0: [0], 1: [1], 2: [2], 3: [3]},
    )
    is_valid, issues = validate_partition_result(g, result, expected_k=10)
    assert not is_valid
    assert any("exceeds node count" in issue for issue in issues)
