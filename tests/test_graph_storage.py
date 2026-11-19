import pytest
from shapely.geometry import LineString

from scripts.generate_sample_graph import build_sample
from src.graph.dataset_service import SAMPLE, metadata_for
from src.graph.storage import load_graph, load_metadata, save_graph, save_metadata


def test_round_trip(tmp_path):
    g = build_sample()
    g.edges[0, 1, 7]["geometry"] = LineString([(77.21, 28.63), (77.211, 28.63)])
    meta = metadata_for(g, SAMPLE)
    path = tmp_path / "roads.graphml"
    sidecar = tmp_path / "meta.json"
    save_graph(g, path, meta)
    save_metadata(meta, sidecar)
    assert load_metadata(sidecar) == meta
    restored = load_graph(path, meta)
    assert dict(restored.edges) == dict(g.edges) and dict(restored.nodes) == dict(g.nodes)
    path.write_text("invalid")
    with pytest.raises(ValueError):
        load_graph(path)
