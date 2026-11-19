"""Integrity and consistency validation for graph partitioning assignments."""

import networkx as nx

from src.partitioning.partition_models import PartitionResult


def validate_partition_result(
    graph: nx.MultiDiGraph,
    result: PartitionResult,
    expected_k: int | None = None,
) -> tuple[bool, list[str]]:
    """Validate completeness, uniqueness, and consistency of partition assignments.

    Returns:
        A tuple of (is_valid, list_of_issue_messages).
    """
    issues: list[str] = []
    total_nodes = len(graph)
    target_k = expected_k if expected_k is not None else result.requested_partition_count

    if target_k < 1:
        issues.append(f"Requested partition count K must be >= 1, got {target_k}")
    if total_nodes == 0:
        issues.append("Cannot validate partition for an empty graph")
        return False, issues
    if target_k > total_nodes:
        issues.append(f"Requested partition count K={target_k} exceeds node count {total_nodes}")

    # Check node assignments coverage and validity
    assigned_nodes = set(result.node_to_partition.keys())
    graph_nodes = set(graph.nodes)

    if assigned_nodes != graph_nodes:
        missing = graph_nodes - assigned_nodes
        extra = assigned_nodes - graph_nodes
        if missing:
            issues.append(f"Missing partition assignments for {len(missing)} nodes")
        if extra:
            issues.append(f"Unknown node IDs found in partition assignments: {len(extra)}")

    # Check partition IDs range
    valid_partition_ids = set(range(target_k))
    assigned_partition_ids = set(result.node_to_partition.values())
    invalid_ids = assigned_partition_ids - valid_partition_ids
    if invalid_ids:
        issues.append(f"Invalid partition IDs assigned: {invalid_ids}")

    # Check partition_to_nodes mapping consistency
    total_in_partitions = sum(len(nodes) for nodes in result.partition_to_nodes.values())
    if total_in_partitions != total_nodes:
        issues.append(
            f"Total nodes in partition_to_nodes ({total_in_partitions}) "
            f"does not match graph node count ({total_nodes})"
        )

    # Check bijection between node_to_partition and partition_to_nodes
    reconstructed_assignment = {}
    for p, nodes in result.partition_to_nodes.items():
        for n in nodes:
            if n in reconstructed_assignment:
                issues.append(f"Node {n} assigned to multiple partitions")
            reconstructed_assignment[n] = p

    if reconstructed_assignment != result.node_to_partition:
        issues.append("Discrepancy between node_to_partition and partition_to_nodes")

    # Check for empty partitions when target_k <= total_nodes
    if target_k <= total_nodes:
        empty_partitions = [
            p for p in range(target_k) if len(result.partition_to_nodes.get(p, [])) == 0
        ]
        if empty_partitions:
            issues.append(f"Unintended empty partitions found: {empty_partitions}")

    if result.actual_partition_count != target_k:
        issues.append(
            f"Actual partition count {result.actual_partition_count} "
            f"does not match expected K={target_k}"
        )

    return len(issues) == 0, issues


def assert_valid_partition(
    graph: nx.MultiDiGraph,
    result: PartitionResult,
    expected_k: int | None = None,
) -> None:
    """Raise ValueError if partition assignments fail any structural validation rule."""
    valid, issues = validate_partition_result(graph, result, expected_k)
    if not valid:
        raise ValueError(f"Partition validation failed: {'; '.join(issues)}")
