"""Heuristic structural screening using normalized centrality scores."""

import math

from src.algorithms.traversal_models import canonical

DEFAULT_WEIGHTS = {"betweenness": 0.4, "degree": 0.25, "closeness": 0.2, "pagerank": 0.15}


def critical_nodes(graph, metrics, top_k=10, weights=None) -> list[dict]:
    """Renormalize available metric weights and min-max scores; constants contribute zero."""
    weights = DEFAULT_WEIGHTS if weights is None else weights
    if type(top_k) is not int or top_k < 0:
        raise ValueError("Invalid top K")
    available = {name: weight for name, weight in weights.items() if name in metrics}
    if (
        not available
        or any(not math.isfinite(w) or w < 0 for w in available.values())
        or sum(available.values()) <= 0
    ):
        raise ValueError("No valid available centrality weights")
    if any(set(metrics[name].scores) != set(graph) for name in available):
        raise ValueError("Centrality results must cover all graph nodes")
    normalized = {}
    for name in available:
        values = metrics[name].scores
        low, high = min(values.values(), default=0), max(values.values(), default=0)
        normalized[name] = {
            n: (value - low) / (high - low) if high > low else 0 for n, value in values.items()
        }
    total = sum(available.values())
    rows = []
    for node in graph:
        row = {
            "node_id": node,
            "combined_score": sum(available[m] * normalized[m][node] / total for m in available),
            "available_metrics": tuple(available),
            "x": graph.nodes[node].get("x"),
            "y": graph.nodes[node].get("y"),
        }
        row.update(
            {
                f"{m}_score": metrics[m].scores[node] if m in metrics else None
                for m in DEFAULT_WEIGHTS
            }
        )
        rows.append(row)
    rows.sort(key=lambda r: (-r["combined_score"], canonical(r["node_id"])))
    return [dict(row, rank=i) for i, row in enumerate(rows[:top_k], 1)]
