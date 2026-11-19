"""Inspect a registered local dataset."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph.dataset_service import SAMPLE, load
from src.graph.representation import build_adjacency
from src.graph.statistics import statistics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=SAMPLE)
    result = load(parser.parse_args().dataset)
    print(result.origin, asdict(result.metadata))
    print(asdict(statistics(result.graph)))
    adjacency = build_adjacency(result.graph)
    print("Sample outgoing roads:", adjacency[next(iter(adjacency))][:3])
