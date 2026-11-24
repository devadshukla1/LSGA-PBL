"""Rebuild the exact keyed edge sequence selected during relaxation."""

from collections.abc import Hashable, Mapping


def reconstruct_route(
    source: Hashable, target: Hashable, predecessors: Mapping
) -> tuple[tuple, tuple]:
    """Return ordered nodes and keyed edges, or empty tuples if unreachable."""
    if source == target:
        return (source,), ()
    if target not in predecessors:
        return (), ()
    nodes = [target]
    edges = []
    seen = {target}
    current = target
    while current != source:
        if current not in predecessors:
            raise ValueError("Broken predecessor chain")
        previous, key = predecessors[current]
        if previous in seen:
            raise ValueError("Cyclic predecessor chain")
        seen.add(previous)
        edges.append((previous, current, key))
        nodes.append(previous)
        current = previous
    return tuple(reversed(nodes)), tuple(reversed(edges))
