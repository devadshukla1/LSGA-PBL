import networkx as nx

from scripts.generate_sample_graph import build_sample
from src.graph.dataset_service import SAMPLE, metadata_for
from src.graph.validation import validate


def test_validation_errors():
    graph = build_sample()
    meta = metadata_for(graph, SAMPLE)
    report = validate(graph, meta)
    assert report.valid and report.weak_components == 2
    del graph.nodes[1]["x"]
    graph.edges[0, 1, 0]["travel_time_s"] = -1
    assert {i.code for i in validate(graph, meta).issues} >= {"coordinates", "weight"}
    assert not validate(nx.Graph(), meta).valid
    assert not validate(nx.MultiDiGraph(), meta).valid
