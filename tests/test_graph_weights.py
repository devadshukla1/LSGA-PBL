import pytest

from scripts.generate_sample_graph import build_sample
from src.graph.weights import apply_weights, travel_time


def test_mph_and_fallback():
    g = build_sample()
    d = g.edges[0, 1, 0]
    d["maxspeed"] = "30 mph"
    apply_weights(g)
    assert d["speed_kph"] == pytest.approx(48.28032)
    assert d["travel_time_s"] == pytest.approx(100 * 3.6 / 48.28032)
    assert g.edges[0, 1, 7]["speed_kph"] == 50


@pytest.mark.parametrize("length,speed", [(-1, 20), (0, 0), (1, float("inf"))])
def test_invalid(length, speed):
    with pytest.raises(ValueError):
        travel_time(length, speed)
