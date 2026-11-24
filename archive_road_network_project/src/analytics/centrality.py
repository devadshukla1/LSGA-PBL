"""Directed multigraph centrality with explicit cost and sampling semantics."""

import math
from time import perf_counter

import networkx as nx

from src.algorithms.traversal_models import canonical
from src.analytics.analytics_models import CentralityResult


def centrality(
    graph,
    metric="degree",
    objective="distance",
    direction="incoming",
    sample_size=100,
    seed=42,
    exact_threshold=500,
    allow_large_exact=False,
    approximate=None,
    alpha=0.85,
    max_iter=200,
    tol=1e-8,
) -> CentralityResult:
    """Calculate one requested metric; large betweenness defaults to sampled sources."""
    start = perf_counter()
    if not isinstance(graph, nx.MultiDiGraph):
        raise ValueError("Expected directed MultiDiGraph")
    if objective not in ("distance", "travel_time") or direction not in ("incoming", "outgoing"):
        raise ValueError("Invalid objective or accessibility direction")
    if type(sample_size) is not int or sample_size < 1 or type(seed) is not int:
        raise ValueError("Invalid sample size or seed")
    weight = "length_m" if objective == "distance" else "travel_time_s"
    weighted = metric in ("betweenness", "closeness")
    if weighted:
        for _, _, data in graph.edges(data=True):
            value = data.get(weight)
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or value < 0
                or (metric == "betweenness" and value == 0)
            ):
                raise ValueError(
                    "Centrality requires finite costs; betweenness costs must be positive"
                )
    sampled = False
    parameters = {"objective": objective if weighted else None}
    if metric in ("degree", "in_degree", "out_degree", "unique_neighbors"):
        if metric == "unique_neighbors":
            scores = {n: len(set(graph.predecessors(n)) | set(graph.successors(n))) for n in graph}
        else:
            degrees = {
                "degree": graph.degree,
                "in_degree": graph.in_degree,
                "out_degree": graph.out_degree,
            }[metric]
            scores = dict(degrees())
        parameters["normalized"] = {
            n: value / max(1, len(graph) - 1) for n, value in scores.items()
        }
    elif metric == "betweenness":
        sampled = len(graph) > exact_threshold if approximate is None else approximate
        if not sampled and len(graph) > exact_threshold and not allow_large_exact:
            raise ValueError("Exact large-graph betweenness requires explicit override")
        ordered = nx.MultiDiGraph()
        ordered.add_nodes_from(sorted(graph, key=canonical))
        ordered.add_edges_from(
            sorted(
                graph.edges(keys=True, data=True),
                key=lambda e: (canonical(e[0]), canonical(e[1]), canonical(e[2])),
            )
        )
        k = min(sample_size, len(graph)) if sampled and len(graph) else None
        scores = nx.betweenness_centrality(ordered, k=k, weight=weight, seed=seed)
        parameters.update(sample_size=k, seed=seed)
    elif metric == "closeness":
        view = graph if direction == "incoming" else graph.reverse(copy=False)
        scores = nx.closeness_centrality(view, distance=weight, wf_improved=True)
        parameters.update(direction=direction, normalization="Wasserman-Faust")
    elif metric == "pagerank":
        if (
            not math.isfinite(alpha)
            or not 0 < alpha < 1
            or max_iter < 1
            or not math.isfinite(tol)
            or tol <= 0
        ):
            raise ValueError("Invalid PageRank convergence settings")
        try:
            scores = nx.pagerank(graph, alpha=alpha, weight=None, max_iter=max_iter, tol=tol)
        except nx.PowerIterationFailedConvergence as error:
            raise ValueError("PageRank did not converge within the iteration limit") from error
        parameters.update(alpha=alpha, max_iter=max_iter, tolerance=tol, strength="unweighted")
    else:
        raise ValueError("Unknown centrality metric")
    ranking = tuple(sorted(scores, key=lambda n: (-scores[n], canonical(n))))
    return CentralityResult(
        metric,
        scores,
        ranking,
        len(graph),
        graph.number_of_edges(),
        True,
        weighted,
        bool(sampled),
        parameters,
        perf_counter() - start,
    )
