"""
Dijkstra's Shortest Path Algorithm
=================================

Classic O(V² + E) implementation of Dijkstra's algorithm
for finding shortest paths in weighted graphs.
"""

import heapq
from typing import Dict, List, Optional, Union
import networkx as nx


def dijkstra(graph: nx.Graph, source: Union[int, str]) -> Dict[Union[int, str], float]:
    """
    Find shortest paths from source to all other vertices using Dijkstra's algorithm.

    Args:
        graph: NetworkX graph with edge weights
        source: Starting vertex

    Returns:
        Dictionary mapping each vertex to its shortest distance from source

    Raises:
        ValueError: If source vertex not in graph

    Example:
        >>> import networkx as nx
        >>> from logarithma.algorithms.shortest_path import dijkstra
        >>>
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', weight=4)
        >>> G.add_edge('A', 'C', weight=2)
        >>> G.add_edge('B', 'C', weight=1)
        >>>
        >>> distances = dijkstra(G, 'A')
        >>> print(distances)
        {'A': 0, 'C': 2, 'B': 3}
    """
    # Validate input
    if source not in graph:
        raise ValueError(f"Source vertex '{source}' not found in graph")

    # Initialize distances
    distances = {node: float('inf') for node in graph.nodes()}
    distances[source] = 0

    # Priority queue: (distance, vertex)
    pq = [(0, source)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        # Skip if already processed
        if current in visited:
            continue

        visited.add(current)

        # Check all neighbors
        for neighbor in graph.neighbors(current):
            # Get edge weight
            weight = graph[current][neighbor].get('weight', 1)
            new_distance = current_dist + weight

            # Update if shorter path found
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                heapq.heappush(pq, (new_distance, neighbor))

    return distances


def dijkstra_with_path(graph: nx.Graph, source: Union[int, str],
                       target: Optional[Union[int, str]] = None) -> Dict:
    """
    Dijkstra algorithm that also returns the shortest paths.

    Args:
        graph: NetworkX graph with edge weights
        source: Starting vertex
        target: Target vertex (if None, finds paths to all vertices)

    Returns:
        Dictionary with 'distances' and 'paths' keys

    Example:
        >>> result = dijkstra_with_path(G, 'A', 'B')
        >>> print(result['distances']['B'])  # Distance to B
        >>> print(result['paths']['B'])      # Path to B
    """
    # Validate input
    if source not in graph:
        raise ValueError(f"Source vertex '{source}' not found in graph")
    if target and target not in graph:
        raise ValueError(f"Target vertex '{target}' not found in graph")

    # Initialize
    distances = {node: float('inf') for node in graph.nodes()}
    distances[source] = 0
    previous = {node: None for node in graph.nodes()}

    # Priority queue
    pq = [(0, source)]
    visited = set()

    while pq:
        current_dist, current = heapq.heappop(pq)

        # Early termination if target found
        if target and current == target:
            break

        if current in visited:
            continue

        visited.add(current)

        # Process neighbors
        for neighbor in graph.neighbors(current):
            weight = graph[current][neighbor].get('weight', 1)
            new_distance = current_dist + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current
                heapq.heappush(pq, (new_distance, neighbor))

    # Reconstruct paths
    def get_path(target_node):
        if distances[target_node] == float('inf'):
            return []

        path = []
        current = target_node
        while current is not None:
            path.append(current)
            current = previous[current]
        return path[::-1]

    # Build paths dictionary
    if target:
        paths = {target: get_path(target)}
    else:
        paths = {node: get_path(node) for node in graph.nodes()
                 if distances[node] != float('inf')}

    return {
        'distances': distances,
        'paths': paths
    }