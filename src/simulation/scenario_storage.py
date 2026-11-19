"""Atomic scenario JSON storage beneath an approved directory."""

import json
import re
from dataclasses import asdict
from pathlib import Path

from config import SCENARIOS_DIR
from src.graph.storage import atomic_path
from src.simulation.scenario_models import TrafficScenario
from src.simulation.scenario_validation import validate_scenario


def scenario_path(identifier: str, directory: Path = SCENARIOS_DIR) -> Path:
    if not re.fullmatch(r"[a-f0-9]{24}", identifier):
        raise ValueError("Invalid scenario ID")
    root = directory.resolve()
    path = (root / f"{identifier}.json").resolve()
    if not path.is_relative_to(root):
        raise ValueError("Scenario path escapes storage directory")
    return path


def save_scenario(scenario, graph, dataset_id, directory=SCENARIOS_DIR) -> Path:
    validate_scenario(graph, scenario, dataset_id)
    path = scenario_path(scenario.scenario_id, directory)
    with atomic_path(path) as temporary:
        temporary.write_text(
            json.dumps(asdict(scenario), sort_keys=True, indent=2, allow_nan=False), encoding="utf8"
        )
    return path


def load_scenario(identifier, graph, dataset_id, directory=SCENARIOS_DIR):
    try:
        data = json.loads(scenario_path(identifier, directory).read_text(encoding="utf8"))
        data["closed_edges"] = tuple(tuple(edge) for edge in data["closed_edges"])
        data["blocked_nodes"] = tuple(data["blocked_nodes"])
        data["parameters"] = tuple(data["parameters"])
        scenario = TrafficScenario(**data)
        validate_scenario(graph, scenario, dataset_id)
        if scenario.scenario_id != identifier:
            raise ValueError("Scenario file identity mismatch")
        return scenario
    except (TypeError, KeyError) as error:
        raise ValueError("Malformed scenario JSON") from error


def list_scenarios(directory=SCENARIOS_DIR) -> list[str]:
    return sorted(p.stem for p in directory.glob("*.json") if re.fullmatch(r"[a-f0-9]{24}", p.stem))


def delete_scenario(identifier, directory=SCENARIOS_DIR) -> None:
    scenario_path(identifier, directory).unlink(missing_ok=True)
