"""Portable GraphML with JSON-encoded OSM tags and WKT road geometry."""

import json
import os
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

import networkx as nx
from shapely import wkt

from src.graph.models import GraphMetadata
from src.graph.validation import validate


@contextmanager
def atomic_path(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        yield temporary
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def save_metadata(metadata: GraphMetadata, path: Path) -> None:
    with atomic_path(path) as tmp:
        tmp.write_text(json.dumps(asdict(metadata), sort_keys=True, indent=2), encoding="utf8")


def load_metadata(path: Path) -> GraphMetadata:
    return GraphMetadata(**json.loads(path.read_text(encoding="utf8")))


def encoded(attrs: dict) -> str:
    data = dict(attrs)
    if "geometry" in data:
        data["geometry"] = data["geometry"].wkt
    if "crs" in data:
        data["crs"] = str(data["crs"])
    return json.dumps(data, sort_keys=True, allow_nan=False)


def save_graph(graph: nx.MultiDiGraph, path: Path, metadata: GraphMetadata) -> None:
    if not validate(graph, metadata).valid:
        raise ValueError("Graph failed validation before save")
    stored = nx.MultiDiGraph(attrs=encoded(graph.graph), metadata=json.dumps(asdict(metadata)))
    for n, d in graph.nodes(data=True):
        if type(n) is not int:
            raise ValueError("Persistent OSM node IDs must be integers")
        stored.add_node(n, attrs=encoded(d))
    for u, v, k, d in graph.edges(keys=True, data=True):
        if type(k) is not int:
            raise ValueError("Persistent edge keys must be integers")
        stored.add_edge(u, v, key=k, attrs=encoded(d))
    with atomic_path(path) as tmp:
        nx.write_graphml(stored, tmp)
        recovered = load_graph(tmp, metadata)
        if (
            set(recovered) != set(graph)
            or set(recovered.edges(keys=True)) != set(graph.edges(keys=True))
            or any(encoded(graph.nodes[n]) != encoded(recovered.nodes[n]) for n in graph)
            or any(
                encoded(graph.edges[e]) != encoded(recovered.edges[e])
                for e in graph.edges(keys=True)
            )
        ):
            raise ValueError("GraphML round-trip mismatch")


def load_graph(path: Path, metadata: GraphMetadata | None = None) -> nx.MultiDiGraph:
    try:
        stored = nx.read_graphml(path, node_type=int, edge_key_type=int, force_multigraph=True)
        embedded = GraphMetadata(**json.loads(stored.graph["metadata"]))
        if not stored.is_directed() or (metadata is not None and embedded != metadata):
            raise ValueError("Incompatible topology or sidecar")
        graph = nx.MultiDiGraph()
        graph.graph.update(json.loads(stored.graph["attrs"]))
        graph.add_nodes_from((n, json.loads(d["attrs"])) for n, d in stored.nodes(data=True))
        for u, v, k, d in stored.edges(keys=True, data=True):
            attrs = json.loads(d["attrs"])
            if "geometry" in attrs:
                attrs["geometry"] = wkt.loads(attrs["geometry"])
            graph.add_edge(u, v, key=k, **attrs)
        if not validate(graph, embedded).valid:
            raise ValueError("Invalid road graph")
        return graph
    except Exception as error:
        raise ValueError(f"Cannot load road GraphML {path.name}: {error}") from error
