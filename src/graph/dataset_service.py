"""Select verified local datasets or explicitly acquire a road network."""

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

from config import PROCESSED_DATA_DIR, SAMPLES_DIR
from src.graph import loader
from src.graph.models import DatasetInfo, GraphMetadata
from src.graph.storage import load_graph, load_metadata, save_graph, save_metadata
from src.graph.validation import validate
from src.graph.weights import apply_weights

SAMPLE = "offline_sample"


def dataset_id(bbox: tuple = loader.DEFAULT_BBOX) -> str:
    payload = json.dumps(loader.parameters(bbox), sort_keys=True)
    return "osm_" + hashlib.sha256(payload.encode()).hexdigest()[:20]


def metadata_for(graph, identifier: str, bbox: tuple = loader.DEFAULT_BBOX) -> GraphMetadata:
    sample = identifier == SAMPLE
    return GraphMetadata(
        identifier,
        "Offline sample" if sample else f"OSM roads · {bbox}",
        "SYNTHETIC" if sample else "OpenStreetMap",
        "Synthetic New Delhi grid" if sample else str(bbox),
        datetime.now(UTC).isoformat(),
        len(graph),
        graph.number_of_edges(),
        "MultiDiGraph",
        "1",
        {} if sample else loader.parameters(bbox),
        sample,
    )


def directory(identifier: str) -> Path:
    if identifier == SAMPLE:
        return SAMPLES_DIR
    if not re.fullmatch(r"osm_[0-9a-f]{20}", identifier):
        raise ValueError("Invalid dataset identifier")
    return PROCESSED_DATA_DIR


def metadata_for_id(identifier: str) -> GraphMetadata:
    meta = load_metadata(directory(identifier) / f"{identifier}.metadata.json")
    if meta.dataset_id != identifier or meta.is_offline_sample != (identifier == SAMPLE):
        raise ValueError("Dataset identity mismatch")
    return meta


def load(identifier: str = SAMPLE) -> DatasetInfo:
    meta = metadata_for_id(identifier)
    graph = load_graph(directory(identifier) / f"{identifier}.graphml", meta)
    return DatasetInfo(
        graph, meta, "Synthetic offline sample" if identifier == SAMPLE else "Cached OpenStreetMap"
    )


def list_datasets() -> list[str]:
    return [SAMPLE, *sorted(p.stem for p in PROCESSED_DATA_DIR.glob("osm_*.graphml"))]


def register(graph, meta: GraphMetadata) -> None:
    folder = directory(meta.dataset_id)
    save_graph(graph, folder / f"{meta.dataset_id}.graphml", meta)
    save_metadata(meta, folder / f"{meta.dataset_id}.metadata.json")


def acquire(bbox: tuple = loader.DEFAULT_BBOX, force_refresh: bool = False) -> DatasetInfo:
    identifier = dataset_id(bbox)
    try:
        cached = load(identifier)
    except (OSError, ValueError, TypeError) as error:
        cached = None
        cache_reason = str(error)
    if cached and not force_refresh:
        return cached
    try:
        graph = loader.download(bbox)
        apply_weights(graph)
        meta = metadata_for(graph, identifier, bbox)
        if not validate(graph, meta).valid:
            raise ValueError("Downloaded graph failed validation")
        register(graph, meta)
        return DatasetInfo(graph, meta, "Online OpenStreetMap")
    except Exception as error:
        fallback = cached or load()
        notice = f"Acquisition failed: {error}. Using {fallback.origin}."
        if not cached:
            notice += f" Cache unavailable: {cache_reason}"
        return DatasetInfo(fallback.graph, fallback.metadata, fallback.origin, notice)
