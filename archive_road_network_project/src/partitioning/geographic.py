"""Geographic graph partitioning using balanced recursive bisection."""

import math
import time
from collections import defaultdict
from collections.abc import Hashable

import networkx as nx

from src.indexing.spatial_index import extract_node_coordinates
from src.partitioning.partition_models import PartitionResult


def geographic_partition(
    graph: nx.MultiDiGraph,
    k: int,
    seed: int = 42,
) -> PartitionResult:
    """Partition a road network into K balanced regions using recursive geographic bisection.

    Selects the geographic axis with the largest physical spread at each step,
    sorts nodes with deterministic tie-breaking, and recursively divides the node set
    until exactly K balanced partitions are formed.

    Args:
        graph: Directed MultiDiGraph with geographic node coordinates.
        k: Number of desired partitions (1 <= K <= len(graph)).
        seed: Random seed (retained for signature consistency; algorithm is deterministic).

    Returns:
        PartitionResult containing node assignments and execution time.
    """
    total_nodes = len(graph)
    if total_nodes == 0:
        raise ValueError("Cannot partition an empty graph")
    if k < 1:
        raise ValueError(f"Partition count K must be >= 1, got {k}")
    if k > total_nodes:
        raise ValueError(f"Partition count K={k} cannot exceed node count {total_nodes}")

    start_time = time.perf_counter()
    coords = extract_node_coordinates(graph)

    # Initial node list sorted canonically by string ID
    all_nodes = sorted(coords.keys(), key=lambda n: str(n))
    node_to_partition: dict[Hashable, int] = {}

    def _bisect(nodes: list[Hashable], num_partitions: int, part_offset: int) -> None:
        if num_partitions == 1:
            for n in nodes:
                node_to_partition[n] = part_offset
            return

        # Determine physical spread along latitude and longitude
        lats = [coords[n][0] for n in nodes]
        lons = [coords[n][1] for n in nodes]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        mid_lat = (min_lat + max_lat) / 2.0

        # Physical meters per degree
        meters_lat = (max_lat - min_lat) * 111_320.0
        meters_lon = (max_lon - min_lon) * 111_320.0 * math.cos(math.radians(mid_lat))

        # Select axis with largest physical spread
        if meters_lat >= meters_lon:
            # Sort primarily along latitude (Y-axis)
            sorted_nodes = sorted(
                nodes,
                key=lambda n: (coords[n][0], coords[n][1], str(n)),
            )
        else:
            # Sort primarily along longitude (X-axis)
            sorted_nodes = sorted(
                nodes,
                key=lambda n: (coords[n][1], coords[n][0], str(n)),
            )

        # Split into balanced groups for arbitrary K
        left_k = num_partitions // 2
        right_k = num_partitions - left_k

        split_index = round(len(sorted_nodes) * (left_k / num_partitions))
        # Ensure at least left_k nodes for left and right_k nodes for right
        split_index = max(left_k, min(len(sorted_nodes) - right_k, split_index))

        left_nodes = sorted_nodes[:split_index]
        right_nodes = sorted_nodes[split_index:]

        _bisect(left_nodes, left_k, part_offset)
        _bisect(right_nodes, right_k, part_offset + left_k)

    _bisect(all_nodes, k, 0)

    # Invert mapping to partition_to_nodes
    partition_to_nodes: dict[int, list[Hashable]] = defaultdict(list)
    for n, p in node_to_partition.items():
        partition_to_nodes[p].append(n)

    # Sort node lists deterministically
    for p in range(k):
        partition_to_nodes[p].sort(key=lambda n: str(n))

    elapsed = time.perf_counter() - start_time

    return PartitionResult(
        algorithm="geographic",
        requested_partition_count=k,
        actual_partition_count=k,
        node_to_partition=node_to_partition,
        partition_to_nodes=dict(partition_to_nodes),
        parameters={"seed": seed},
        runtime_seconds=round(elapsed, 6),
    )
