"""Centralized distance calculation utilities."""

import math
from typing import List, Optional


class DistanceUtils:
    """Single source of truth for all distance calculations."""
    
    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1, lon1: Latitude and longitude of first point
            lat2, lon2: Latitude and longitude of second point
            
        Returns:
            Distance in kilometers
        """
        R = 6371.0  # Earth's radius in kilometers
        
        # Convert to radians
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlmb = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(dphi / 2) ** 2 + 
             math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def from_graph(graph, node1: int, node2: int) -> Optional[float]:
        """
        Get direct distance between two connected nodes from graph.
        
        Args:
            graph: NetworkX graph with edge weights
            node1, node2: Node IDs
            
        Returns:
            Distance if direct connection exists, None otherwise
        """
        if graph.has_edge(node1, node2):
            return graph[node1][node2]['weight']
        return None
    
    @staticmethod
    def route_distance(graph, route: List[int]) -> float:
        """
        Calculate total distance for a route using graph edges.
        
        Args:
            graph: NetworkX graph with edge weights
            route: List of node IDs representing the route
            
        Returns:
            Total route distance in kilometers
        """
        if len(route) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(route) - 1):
            distance = DistanceUtils.from_graph(graph, route[i], route[i+1])
            if distance is not None:
                total_distance += distance
            else:
                # Invalid route - no direct connection
                return 0.0
        
        return total_distance


class DistanceCache:
    """Caching layer for distance calculations to improve performance."""
    
    def __init__(self, graph=None):
        self.graph = graph
        self._direct_cache = {}
        self._route_cache = {}
    
    def get_distance(self, node1: int, node2: int) -> Optional[float]:
        """Get cached distance between two nodes."""
        key = (min(node1, node2), max(node1, node2))
        
        if key not in self._direct_cache:
            distance = DistanceUtils.from_graph(self.graph, node1, node2)
            self._direct_cache[key] = distance
        
        return self._direct_cache[key]
    
    def get_route_distance(self, route: List[int]) -> float:
        """Get cached route distance."""
        route_key = tuple(route)
        
        if route_key not in self._route_cache:
            distance = DistanceUtils.route_distance(self.graph, route)
            self._route_cache[route_key] = distance
        
        return self._route_cache[route_key]
    
    def clear_cache(self):
        """Clear all cached distances."""
        self._direct_cache.clear()
        self._route_cache.clear()
