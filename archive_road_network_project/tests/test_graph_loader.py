from unittest.mock import patch

from scripts.generate_sample_graph import build_sample
from src.graph.loader import download


def test_configurable_acquisition():
    with patch("src.graph.loader.ox.graph_from_bbox", return_value=build_sample()) as api:
        graph = download((10, 20, 11, 21))
    assert graph.is_directed() and graph.is_multigraph()
    api.assert_called_once_with(
        bbox=[10, 20, 11, 21],
        network_type="drive",
        simplify=True,
        retain_all=True,
        truncate_by_edge=False,
    )
