"""Structured integrity checks for road graphs."""

import math
import re

import networkx as nx
from pyproj import CRS
from pyproj.exceptions import CRSError

from src.graph.models import GraphMetadata, ValidationIssue, ValidationReport
from src.graph.weights import travel_time


def validate(g: nx.MultiDiGraph, metadata: GraphMetadata | None = None) -> ValidationReport:
    report = ValidationReport()

    def issue(code: str, message: str, severity: str = "ERROR", **context) -> None:
        report.issues.append(ValidationIssue(severity, code, message, context))

    if not isinstance(g, nx.MultiDiGraph) or not g.is_directed():
        issue("graph_type", "Expected directed MultiDiGraph")
        return report
    if not len(g) or not g.number_of_edges():
        issue("empty", "Expected nodes and roads")
    try:
        geographic = CRS.from_user_input(g.graph.get("crs")).is_geographic
    except CRSError:
        geographic = False
        issue("crs", "Missing or unrecognized CRS")
    for n, d in g.nodes(data=True):
        try:
            x, y = float(d["x"]), float(d["y"])
            if not (math.isfinite(x) and math.isfinite(y)) or (
                geographic and not (-180 <= x <= 180 and -90 <= y <= 90)
            ):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            issue("coordinates", "Invalid node coordinates", node=n)
    for u, v, k, d in g.edges(keys=True, data=True):
        try:
            expected = travel_time(d["length_m"], d["speed_kph"])
            if not math.isclose(expected, d["travel_time_s"], rel_tol=1e-8):
                raise ValueError
        except (KeyError, TypeError, ValueError):
            issue("weight", "Missing or inconsistent road weight", edge=(u, v, k))
    report.weak_components = nx.number_weakly_connected_components(g)
    report.strong_components = nx.number_strongly_connected_components(g)
    isolated = list(nx.isolates(g))
    if isolated:
        issue("isolates", "Nodes without incident roads", "WARNING", nodes=isolated)
    if report.weak_components > 1:
        issue("disconnected", "Multiple weak components", "WARNING")
    if metadata is None or not (
        isinstance(metadata.dataset_id, str)
        and re.fullmatch(r"[a-z0-9_-]{1,64}", metadata.dataset_id)
        and metadata.source
        and metadata.study_area
        and metadata.dataset_name
        and metadata.created_at_utc
        and metadata.graph_type == "MultiDiGraph"
        and metadata.weighting_version == "1"
        and metadata.node_count == len(g)
        and metadata.edge_count == g.number_of_edges()
    ):
        issue("metadata", "Missing or incompatible dataset metadata")
    return report
