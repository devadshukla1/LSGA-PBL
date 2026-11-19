"""Acquire or reuse the configured OpenStreetMap dataset."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph.dataset_service import acquire
from src.graph.loader import DEFAULT_BBOX

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bbox", nargs=4, type=float, default=DEFAULT_BBOX, metavar=("W", "S", "E", "N")
    )
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()
    result = acquire(tuple(args.bbox), args.force_refresh)
    print(result.origin, result.metadata, result.notice)
    sys.exit(int(bool(result.notice)))
