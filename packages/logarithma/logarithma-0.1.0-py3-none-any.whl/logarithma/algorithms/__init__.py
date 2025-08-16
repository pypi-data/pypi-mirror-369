"""
LOGARITHMA Algorithms Module
===========================

Graph algorithms collection including shortest paths,
minimum spanning trees, and advanced optimization algorithms.

Modules:
- shortest_path: Single-source and all-pairs shortest path algorithms
"""

from .shortest_path import dijkstra, dijkstra_with_path

__all__ = [
    'dijkstra',
    'dijkstra_with_path'
]