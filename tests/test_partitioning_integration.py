"""End-to-end integration tests using the verified offline road network sample."""

import copy

from src.graph.dataset_service import load
from src.indexing.nearest_node import brute_force_nearest_node
from src.indexing.spatial_index import build_spatial_index
from src.partitioning.partition_service import (
    compare_partitioning_methods,
    partition_graph,
)
from src.partitioning.partition_validation import assert_valid_partition


def test_offline_sample_partitioning_integration():
    dataset_info = load()
    graph = dataset_info.graph
    before_nodes = copy.deepcopy(dict(graph.nodes(data=True)))
    before_edges = copy.deepcopy(list(graph.edges(keys=True, data=True)))

    # 1. Geographic Partitioning
    geo_res, geo_qual = partition_graph(graph, method="geographic", k=4)
    assert_valid_partition(graph, geo_res, expected_k=4)
    assert geo_res.actual_partition_count == 4
    assert geo_qual.total_nodes == len(graph)
    assert geo_qual.total_edges == graph.number_of_edges()
    assert geo_qual.empty_partition_count == 0

    # 2. Graph-Aware Partitioning
    aware_res, aware_qual = partition_graph(graph, method="graph_aware", k=4)
    assert_valid_partition(graph, aware_res, expected_k=4)
    assert aware_res.actual_partition_count == 4
    assert aware_qual.total_nodes == len(graph)
    assert aware_qual.total_edges == graph.number_of_edges()
    assert aware_qual.empty_partition_count == 0

    # 3. Method Comparison
    comp = compare_partitioning_methods(graph, k=4)
    assert comp.geographic_quality.total_nodes == len(graph)
    assert comp.graph_aware_quality.total_nodes == len(graph)
    assert "geographic_cut_edges" in comp.quality_metrics
    assert "graph_aware_cut_edges" in comp.quality_metrics

    # 4. Spatial Indexing & Nearest Node Lookup
    spatial_index = build_spatial_index(graph)
    assert spatial_index.node_count == len(graph)

    # Query centroid
    q_lat = 28.6315
    q_lon = 77.2115
    res_idx = spatial_index.nearest_node(q_lat, q_lon)
    res_bf = brute_force_nearest_node(graph, q_lat, q_lon)

    assert res_idx.node_id == res_bf.node_id
    assert abs(res_idx.distance_m - res_bf.distance_m) < 0.05
    assert res_idx.node_id in graph.nodes

    # 5. Immutability
    assert dict(graph.nodes(data=True)) == before_nodes
    assert list(graph.edges(keys=True, data=True)) == before_edges
