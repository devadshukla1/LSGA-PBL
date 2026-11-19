"""Tests verifying defensive error handling, input validation, and boundary conditions."""

import networkx as nx
import pytest

from scripts.generate_sample_graph import build_sample
from src.algorithms.bfs import bfs
from src.partitioning.partition_models import PartitionResult
from src.partitioning.partition_validation import assert_valid_partition
from src.routing.routing_service import find_route
from src.simulation.scenario_builder import create_scenario
from src.utils.paths import project_path


def test_invalid_routing_parameters() -> None:
    """Verify routing raises ValueError for unknown node IDs or unsupported algorithms."""
    graph = build_sample()

    with pytest.raises(ValueError):
        find_route(graph, 9999, 1, "dijkstra", "distance")

    with pytest.raises(ValueError):
        find_route(graph, 0, 9999, "dijkstra", "distance")

    with pytest.raises(ValueError):
        find_route(graph, 0, 1, "unknown_algo", "distance")

    with pytest.raises(ValueError):
        find_route(graph, 0, 1, "dijkstra", "unsupported_objective")


def test_invalid_traversal_graph() -> None:
    """Verify traversal preparation rejects unknown start node on empty graph."""
    empty_g = nx.MultiDiGraph()
    with pytest.raises(ValueError):
        bfs(empty_g, 0)


def test_invalid_scenario_parameters() -> None:
    """Verify scenario creation validates congestion parameters."""
    graph = build_sample()

    with pytest.raises(ValueError):
        create_scenario(graph, "sample", "unknown_level", 42, 0.5)

    with pytest.raises(ValueError):
        create_scenario(graph, "sample", "normal", 42, 1.5)  # Coverage > 1.0


def test_invalid_partition_validation() -> None:
    """Verify partition validation rejects invalid K or missing node assignments."""
    graph = build_sample()

    # Incomplete assignment missing nodes
    incomplete_result = PartitionResult(
        algorithm="test",
        requested_partition_count=2,
        actual_partition_count=2,
        node_to_partition={0: 0},
        partition_to_nodes={0: [0], 1: []},
    )
    with pytest.raises(ValueError):
        assert_valid_partition(graph, incomplete_result, expected_k=2)


def test_path_traversal_security() -> None:
    """Verify project_path blocks directory traversal attacks."""
    with pytest.raises(ValueError):
        project_path("../../../secret.txt")
