"""Manual forward/outgoing and backward/incoming Dijkstra search."""

import heapq
import math
from itertools import count

from src.algorithms.path_reconstruction import reconstruct_route
from src.algorithms.routing_tiebreak import signature
from src.routing.route_alternatives import result_from_edges, validate_request


def bidirectional_dijkstra(graph, source, target, objective="distance"):
    """Stop only when clean frontier lower bounds reach the best complete cost."""
    field = validate_request(graph, source, target, objective)
    if source == target:
        return result_from_edges(graph, source, target, (), "bidirectional_dijkstra", objective)
    distances = [{source: 0.0}, {target: 0.0}]
    links = [{}, {}]
    settled = [set(), set()]
    serial = count()
    heaps = [[(0.0, next(serial), source)], [(0.0, next(serial), target)]]
    mu = math.inf
    meeting = None
    expanded = examined = 0
    while heaps[0] and heaps[1]:
        for side in (0, 1):
            while heaps[side] and (
                heaps[side][0][2] in settled[side]
                or heaps[side][0][0] != distances[side][heaps[side][0][2]]
            ):
                heapq.heappop(heaps[side])
        if not heaps[0] or not heaps[1] or heaps[0][0][0] + heaps[1][0][0] >= mu:
            break
        side = 0 if heaps[0][0][0] <= heaps[1][0][0] else 1
        cost, _, node = heapq.heappop(heaps[side])
        settled[side].add(node)
        expanded += 1
        edges = (
            graph.out_edges(node, keys=True, data=True)
            if side == 0
            else graph.in_edges(node, keys=True, data=True)
        )
        for u, v, key, data in sorted(edges, key=lambda item: signature((item[:3],))):
            examined += 1
            neighbor = v if side == 0 else u
            candidate = cost + data[field]
            if not math.isfinite(candidate):
                raise ValueError("Nonfinite accumulated cost")
            if candidate < distances[side].get(neighbor, math.inf):
                distances[side][neighbor] = candidate
                links[side][neighbor] = (node, key)
                heapq.heappush(heaps[side], (candidate, next(serial), neighbor))
            complete = distances[side].get(neighbor, math.inf) + distances[1 - side].get(
                neighbor, math.inf
            )
            if complete < mu:
                mu = complete
                meeting = neighbor
    if meeting is None:
        return result_from_edges(
            graph, source, target, None, "bidirectional_dijkstra", objective, expanded, examined
        )
    _, forward = reconstruct_route(source, meeting, links[0])
    _, reverse = reconstruct_route(target, meeting, links[1])
    edges = forward + tuple((v, u, k) for u, v, k in reversed(reverse))
    return result_from_edges(
        graph, source, target, edges, "bidirectional_dijkstra", objective, expanded, examined
    )
