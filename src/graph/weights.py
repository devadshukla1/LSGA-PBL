"""Apply deterministic speed estimates to directed road segments."""

import math
import re

import networkx as nx

SPEEDS = dict(
    motorway=80,
    trunk=60,
    primary=50,
    secondary=40,
    tertiary=35,
    residential=25,
    living_street=10,
    service=15,
    unclassified=25,
)


def travel_time(length: float, speed: float) -> float:
    if not math.isfinite(length) or length < 0 or not math.isfinite(speed) or speed <= 0:
        raise ValueError("Expected finite nonnegative length and positive speed")
    seconds = length / (speed / 3.6)
    if not math.isfinite(seconds):
        raise ValueError("Nonfinite travel time")
    return seconds


def apply_weights(graph: nx.MultiDiGraph) -> None:
    """Enrich an acquired graph in place, retaining original OSM tags."""
    for _, _, data in graph.edges(data=True):
        tags = data.get("maxspeed", [])
        speeds = []
        for tag in tags if isinstance(tags, list) else [tags]:
            for part in str(tag).lower().split(";"):
                match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(mph|km/h|kph)?\s*", part)
                if match and float(match[1]) > 0:
                    speeds.append(float(match[1]) * (1.609344 if match[2] == "mph" else 1))
        classes = data.get("highway", "unknown")
        speed = (
            min(speeds)
            if speeds
            else min(
                (SPEEDS.get(c, 25) for c in (classes if isinstance(classes, list) else [classes])),
                default=25,
            )
        )
        length = float(data["length"])
        data.update(
            length_m=length,
            speed_kph=speed,
            travel_time_s=travel_time(length, speed),
            speed_source="osm_maxspeed" if speeds else "estimated_fallback",
        )
