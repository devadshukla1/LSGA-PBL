"""Manual Yen enumeration with keyed exclusions and a persistent candidate heap."""

import heapq
from itertools import count

import networkx as nx

from src.algorithms.dijkstra import dijkstra
from src.algorithms.routing_tiebreak import rank
from src.routing.route_alternatives import result_from_edges, validate_request


def yen_k_shortest_paths(graph, source, target, k=3, objective="distance", max_k=5):
    """Return up to K node-loopless routes, unique by exact edge sequence."""
    if type(k) is not int or k < 1 or k > max_k:
        raise ValueError(f"K must be an integer between 1 and {max_k}")
    validate_request(graph, source, target, objective)
    first = dijkstra(graph, source, target, objective)
    if not first.is_reachable:
        return []
    accepted = [first]
    candidates = []
    queued = set()
    signatures = {first.edge_path}
    serial = count()
    while len(accepted) < k:
        previous = accepted[-1]
        for index, spur_node in enumerate(previous.node_path[:-1]):
            root = previous.edge_path[:index]
            banned_nodes = set(previous.node_path[:index])
            banned_edges = {
                route.edge_path[index]
                for route in accepted
                if len(route.edge_path) > index and route.edge_path[:index] == root
            }
            view = nx.subgraph_view(
                graph,
                filter_node=lambda n: n not in banned_nodes,
                filter_edge=lambda u, v, key: (u, v, key) not in banned_edges,
            )
            spur = dijkstra(view, spur_node, target, objective)
            if not spur.is_reachable:
                continue
            edges = root + spur.edge_path
            nodes = (source,) + tuple(v for _, v, _ in edges)
            if len(set(nodes)) != len(nodes) or edges in signatures or edges in queued:
                continue
            route = result_from_edges(graph, source, target, edges, "yen_k_shortest", objective)
            heapq.heappush(candidates, (rank(route), next(serial), route))
            queued.add(edges)
        if not candidates:
            break
        _, _, chosen = heapq.heappop(candidates)
        queued.remove(chosen.edge_path)
        signatures.add(chosen.edge_path)
        accepted.append(chosen)
    return sorted(accepted, key=rank)
