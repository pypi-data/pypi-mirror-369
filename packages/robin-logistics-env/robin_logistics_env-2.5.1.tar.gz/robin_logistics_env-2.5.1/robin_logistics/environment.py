"""
Main interface for hackathon contestants.
Provides clean access to problem data, inventory tracking, and constraint validation.
NO solving logic - contestants implement their own routing algorithms.
"""

import networkx as nx
import pandas as pd
import os
from typing import Dict, List, Tuple, Optional

from .core.models import Node, SKU, Order, Vehicle, Warehouse
from .core.utils.distance import DistanceUtils, DistanceCache
from .core.state.vehicle_state import VehicleStateManager
from .core.state.inventory import InventoryTransaction
from .core.data_generator import generate_problem_instance, generate_scenario_from_config


class LogisticsEnvironment:
    """
    Main interface for hackathon contestants.
    Provides clean access to problem data, inventory tracking, and constraint validation.
    NO solving logic - contestants implement their own routing algorithms.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the logistics environment."""
        self._current_seed = None
        
        # Generate initial scenario
        self._load_problem_instance()
        self._reset_vehicle_states()
        
    def _load_problem_instance(self):
        """Load and initialize the problem instance."""
        # Generate problem data
        nodes_df, edges_df, warehouses, orders, skus, vehicles = generate_problem_instance()
        
        # Initialize the environment directly (no delegation)
        self._initialize_environment(nodes_df, edges_df, warehouses, orders, skus, vehicles)
        
        # Store current seed (will be None for default generation)
        self._current_seed = None
    
    def _initialize_environment(self, nodes_df, edges_df, warehouses, orders, skus, vehicles):
        """Initialize the environment with problem data."""
        # Validation
        if nodes_df is None or nodes_df.empty:
            raise ValueError("nodes_df cannot be None or empty")
        if edges_df is None:
            raise ValueError("edges_df cannot be None")
        if not warehouses:
            raise ValueError("warehouses cannot be empty")
        if not orders:
            raise ValueError("orders cannot be empty")
        if not skus:
            raise ValueError("skus cannot be empty")
        if not vehicles:
            raise ValueError("vehicles cannot be empty")
            
        required_node_cols = ['node_id', 'lat', 'lon']
        if not all(col in nodes_df.columns for col in required_node_cols):
            raise ValueError(f"nodes_df must contain columns: {required_node_cols}")
            
        if not all(-90 <= lat <= 90 for lat in nodes_df['lat']):
            raise ValueError("Latitude values must be between -90 and 90")
        if not all(-180 <= lon <= 180 for lon in nodes_df['lon']):
            raise ValueError("Longitude values must be between -180 and 180")

        # Initialize nodes
        self.nodes = {}
        for _, row in nodes_df.iterrows():
            node = Node(
                node_id=row['node_id'],
                lat=row['lat'],
                lon=row['lon']
            )
            self.nodes[node.id] = node

        # Initialize data structures
        self.warehouses = {warehouse.id: warehouse for warehouse in warehouses}
        self.orders = {order.id: order for order in orders}
        self.skus = {sku.id: sku for sku in skus}
        self.vehicles = vehicles

        # Initialize state management
        self.vehicle_state_manager = VehicleStateManager()
        
        # Build road network and initialize distance cache
        self._build_road_network(edges_df)
        self._validate_environment()
        self.distance_cache = DistanceCache(self._graph)

    def _build_road_network(self, edges_df_raw):
        """Build the road network graph from edges data."""
        if edges_df_raw.empty:
            self._graph = nx.DiGraph()
            return

        if 'u' in edges_df_raw.columns and 'v' in edges_df_raw.columns:
            edges_df = edges_df_raw[['u', 'v']].copy()
        elif 'start_node' in edges_df_raw.columns and 'end_node' in edges_df_raw.columns:
            edges_df = edges_df_raw[['start_node', 'end_node']].copy()
            edges_df.columns = ['u', 'v']
        else:
            raise ValueError("Edges must have either ['u', 'v'] or ['start_node', 'end_node'] columns")

        # Prioritize pre-calculated distances from edges data
        if 'distance_km' in edges_df_raw.columns:
            edges_df['distance_km'] = edges_df_raw['distance_km']
        elif 'length' in edges_df_raw.columns:
            edges_df['distance_km'] = edges_df_raw['length'] / 1000
        else:
            # Only calculate distances if not provided in data
            print("Warning: No distance data found in edges. Calculating using Haversine (may be inaccurate for road networks).")
            distances = []
            for _, row in edges_df.iterrows():
                u, v = row['u'], row['v']
                if u in self.nodes and v in self.nodes:
                    nu, nv = self.nodes[u], self.nodes[v]
                    distances.append(DistanceUtils.haversine_km(nu.lat, nu.lon, nv.lat, nv.lon))
                else:
                    distances.append(0.0)
            edges_df['distance_km'] = distances

        self._graph = nx.DiGraph()
        
        for _, row in edges_df.iterrows():
            u, v = int(row['u']), int(row['v'])
            distance = row.get('distance_km', 1.0)
            
            if u in self.nodes and v in self.nodes:
                self._graph.add_edge(u, v, weight=distance)

    def _validate_environment(self):
        """Validate the environment configuration."""
        if not self.warehouses:
            raise ValueError("No warehouses defined")
        if not self.orders:
            raise ValueError("No orders defined")
        if not self.skus:
            raise ValueError("No SKUs defined")
        if not self.vehicles:
            raise ValueError("No vehicles defined")
        
        # Validate warehouse locations exist in road network
        for warehouse in self.warehouses.values():
            if warehouse.location.id not in self.nodes:
                raise ValueError(f"Warehouse {warehouse.id} location {warehouse.location.id} not in road network")
        
        # Validate order destinations exist in road network
        for order in self.orders.values():
            if order.destination.id not in self.nodes:
                raise ValueError(f"Order {order.id} destination {order.destination.id} not in road network")
    
    def _reset_vehicle_states(self):
        """Reset vehicle load, weight, volume, and location states using state manager."""
        if hasattr(self, 'vehicle_state_manager'):
            self.vehicle_state_manager.reset_all_vehicles()
    
    # ===== PROPERTY ACCESSORS =====
    
    @property
    def num_orders(self):
        """Get total number of orders."""
        return len(self.orders)
    
    @property  
    def num_warehouses(self):
        """Get total number of warehouses."""
        return len(self.warehouses)
    
    @property
    def num_vehicles(self):
        """Get total number of vehicles."""
        return len(self.get_all_vehicles())
    
    # ===== CORE DATA ACCESS METHODS =====
    
    def get_all_vehicles(self):
        """Get all vehicles from all warehouses."""
        all_vehicles = []
        for warehouse in self.warehouses.values():
            all_vehicles.extend(warehouse.vehicles)
        return all_vehicles

    def get_vehicle_by_id(self, vehicle_id):
        """Get vehicle by ID."""
        for warehouse in self.warehouses.values():
            for vehicle in warehouse.vehicles:
                if vehicle.id == vehicle_id:
                    return vehicle
        return None

    def get_warehouse_by_id(self, warehouse_id):
        """Get warehouse by ID."""
        return self.warehouses.get(warehouse_id)
    
    def get_road_network_data(self) -> Dict:
        """Get complete road network data for pathfinding."""
        nodes = {}
        for node_id, node in self.nodes.items():
            nodes[node_id] = {'lat': node.lat, 'lon': node.lon}
        
        edges = []
        adjacency_list = {}
        
        for u, v, data in self._graph.edges(data=True):
            edges.append({
                'from': u,
                'to': v,
                'distance': data['weight']
            })

            if u not in adjacency_list:
                adjacency_list[u] = []
            adjacency_list[u].append(v)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'adjacency_list': adjacency_list
        }

    def get_available_edges(self) -> List[Dict]:
        """Return the road network edges with distances for solver use."""
        edges = []
        for u, v, data in self._graph.edges(data=True):
            edges.append({
                'start_node': u,
                'end_node': v,
                'distance_km': data['weight']
            })
        return edges

    # ===== DISTANCE AND ROUTE METHODS =====

    def get_distance(self, node1: int, node2: int) -> Optional[float]:
        """
        Get direct distance between two connected nodes.
        Returns None if no direct connection exists.
        """
        return self.distance_cache.get_distance(node1, node2)

    def get_route_distance(self, route: List[int]) -> float:
        """
        Calculate total distance for a route (list of node IDs).
        Uses actual road network distances from edges.
        """
        return self.distance_cache.get_route_distance(route)

    # ===== HELPER METHODS FOR CONTESTANTS =====
    
    def get_all_order_ids(self) -> List[str]:
        """Get list of all order IDs."""
        return list(self.orders.keys())
    
    def get_available_vehicles(self) -> List[str]:
        """Get list of all available vehicle IDs."""
        all_vehicles = self.get_all_vehicles()
        return [v.id for v in all_vehicles]
    
    def get_order_location(self, order_id: str) -> int:
        """Get the delivery location node ID for an order."""
        if order_id in self.orders:
            return self.orders[order_id].destination.id
        raise ValueError(f"Order {order_id} not found")
    
    def get_vehicle_home_warehouse(self, vehicle_id: str) -> int:
        """Get the home warehouse node ID for a vehicle."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if vehicle:
            warehouse_id = vehicle.home_warehouse_id
            
            for warehouse in self.warehouses.values():
                if warehouse.id == warehouse_id:
                    return warehouse.location.id
            
            raise ValueError(f"Warehouse {warehouse_id} not found for vehicle {vehicle_id}")
        raise ValueError(f"Vehicle {vehicle_id} not found")
    
    def get_order_requirements(self, order_id: str) -> Dict[str, int]:
        """Get SKU requirements for an order."""
        if order_id in self.orders:
            return self.orders[order_id].requested_items.copy()
        return {}
    
    def get_warehouse_inventory(self, warehouse_id: str) -> Dict[str, int]:
        """Get current inventory levels for a specific warehouse."""
        if warehouse_id in self.warehouses:
            return self.warehouses[warehouse_id].inventory.copy()
        return {}
    
    def get_vehicle_current_load(self, vehicle_id: str) -> Dict[str, int]:
        """Get current SKU quantities loaded on a vehicle."""
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if vehicle:
            return self.vehicle_state_manager.get_vehicle_load(vehicle_id)
        return {}
        
    def get_vehicle_current_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get current weight and volume usage for a vehicle."""
        if self.get_vehicle_by_id(vehicle_id):
            return self.vehicle_state_manager.get_vehicle_capacity_usage(vehicle_id)
        return 0.0, 0.0
    
    def get_vehicle_remaining_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get remaining weight and volume capacity for a vehicle."""
        if self.get_vehicle_by_id(vehicle_id):
            return self.vehicle_state_manager.get_vehicle_remaining_capacity(vehicle_id)
        return 0.0, 0.0
    
    def get_order_fulfillment_status(self, order_id: str) -> Dict[str, Dict[str, int]]:
        """Get detailed fulfillment status for an order."""
        if order_id not in self.orders:
            return {}
        
        order = self.orders[order_id]
        result = {
            'requested': order.requested_items.copy(),
            'delivered': getattr(order, '_delivered_items', {}),
            'remaining': {}
        }
        
        # Calculate remaining quantities
        for sku_id in order.requested_items:
            requested = order.requested_items[sku_id]
            delivered = result['delivered'].get(sku_id, 0)
            result['remaining'][sku_id] = max(0, requested - delivered)
        
        return result
    
    def get_warehouses_with_sku(self, sku_id: str, min_quantity: int = 1) -> List[str]:
        """Find all warehouses that have a specific SKU in stock."""
        warehouses_with_sku = []
        
        for warehouse_id, warehouse in self.warehouses.items():
            if sku_id in warehouse.inventory and warehouse.inventory[sku_id] >= min_quantity:
                warehouses_with_sku.append(warehouse_id)
        
        return warehouses_with_sku
    
    def get_sku_details(self, sku_id: str) -> Optional[Dict]:
        """Get SKU specifications (weight, volume)."""
        if sku_id in self.skus:
            sku = self.skus[sku_id]
            return {
                'id': sku.id,
                'weight': sku.weight,
                'volume': sku.volume
            }
        return None

    # ===== INVENTORY OPERATIONS =====
    
    def pickup_sku_from_warehouse(self, vehicle_id: str, warehouse_id: str, sku_id: str, quantity: int) -> bool:
        """
        Pick up SKU from warehouse and load onto vehicle.
        
        Args:
            vehicle_id: ID of the vehicle
            warehouse_id: ID of the warehouse
            sku_id: ID of the SKU to pick up
            quantity: Quantity to pick up
            
        Returns:
            True if successful, False if vehicle not found
        """
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False
        
        warehouse = self.warehouses[warehouse_id]
        
        # Check warehouse inventory
        if sku_id not in warehouse.inventory or warehouse.inventory[sku_id] < quantity:
            return False
        
        # Check vehicle capacity using state manager
        sku_details = self.get_sku_details(sku_id)
        if sku_details:
            success = self.vehicle_state_manager.add_sku_to_vehicle(
                vehicle, sku_id, quantity, sku_details['weight'], sku_details['volume']
            )
            if not success:
                return False
        
        # Update warehouse inventory
        warehouse.inventory[sku_id] -= quantity
        
        return True
    
    def deliver_sku_to_order(self, vehicle_id: str, order_id: str, sku_id: str, quantity: int) -> bool:
        """
        Deliver SKU from vehicle to order.
        
        Args:
            vehicle_id: ID of the vehicle
            order_id: ID of the order
            sku_id: ID of the SKU to deliver
            quantity: Quantity to deliver
            
        Returns:
            True if successful, False if operation fails
        """
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False
        
        order = self.orders[order_id]
        
        # Check if order needs this SKU
        if sku_id not in order.requested_items:
            return False
        
        # Check if vehicle has this SKU and remove using state manager
        sku_details = self.get_sku_details(sku_id)
        if sku_details:
            success = self.vehicle_state_manager.remove_sku_from_vehicle(
                vehicle, sku_id, quantity, sku_details['weight'], sku_details['volume']
            )
            if not success:
                return False
        
        # Update order delivered items
        if not hasattr(order, '_delivered_items'):
            order._delivered_items = {}
        if sku_id not in order._delivered_items:
            order._delivered_items[sku_id] = 0
        order._delivered_items[sku_id] += quantity
        
        return True
    
    def return_vehicle_to_home(self, vehicle_id: str) -> bool:
        """
        Return vehicle to home warehouse and unload remaining items.
        
        Args:
            vehicle_id: ID of the vehicle
            
        Returns:
            True if successful, False if vehicle not found
        """
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False
        
        home_warehouse_id = vehicle.home_warehouse_id
        
        # Unload remaining items back to home warehouse
        current_load = self.vehicle_state_manager.get_vehicle_load(vehicle_id)
        for sku_id, quantity in current_load.items():
            if home_warehouse_id in self.warehouses:
                warehouse = self.warehouses[home_warehouse_id]
                if sku_id not in warehouse.inventory:
                    warehouse.inventory[sku_id] = 0
                warehouse.inventory[sku_id] += quantity
        
        # Reset vehicle state
        self.vehicle_state_manager.reset_vehicle(vehicle_id)
        
        return True

    # ===== TRANSACTION OPERATIONS =====
    
    def create_inventory_transaction(self) -> InventoryTransaction:
        """
        Create a new inventory transaction for atomic operations.
        
        Returns:
            InventoryTransaction instance with rollback capabilities
        """
        return InventoryTransaction(self)
    
    def execute_route_operations(self, vehicle_id: str, pickup_operations: List[Dict], 
                                delivery_operations: List[Dict]) -> Tuple[bool, str]:
        """
        Execute a complete route's pickup and delivery operations atomically.
        
        Args:
            vehicle_id: ID of the vehicle
            pickup_operations: List of pickup operation dicts
            delivery_operations: List of delivery operation dicts
            
        Returns:
            Tuple of (success, message)
        """
        transaction = self.create_inventory_transaction()
        
        try:
            # Add all pickup operations
            for pickup in pickup_operations:
                success = transaction.pickup_sku(
                    vehicle_id, 
                    pickup['warehouse_id'], 
                    pickup['sku_id'], 
                    pickup['quantity']
                )
                if not success:
                    return False, f"Failed to add pickup operation: {pickup}"
            
            # Add all delivery operations
            for delivery in delivery_operations:
                success = transaction.deliver_sku(
                    vehicle_id,
                    delivery['order_id'],
                    delivery['sku_id'], 
                    delivery['quantity']
                )
                if not success:
                    return False, f"Failed to add delivery operation: {delivery}"
            
            # Commit all operations atomically
            return transaction.commit()
            
        except Exception as e:
            # Rollback on any error
            transaction.rollback()
            return False, f"Route execution failed: {e}"

    # ===== SCENARIO GENERATION =====
    
    def set_random_seed(self, seed: int):
        """Set random seed for reproducible scenarios."""
        self._current_seed = seed
    
    def get_current_seed(self) -> Optional[int]:
        """Get current random seed."""
        return self._current_seed
    
    def generate_new_scenario(self, seed: Optional[int] = None):
        """Generate a new problem scenario."""
        if seed is not None:
            self.set_random_seed(seed)
        self._load_problem_instance()
        self._reset_vehicle_states()
    
    def generate_scenario_from_config(self, config: Dict):
        """Generate scenario from dashboard configuration."""
        # Store seed if provided
        if 'random_seed' in config and config['random_seed'] is not None:
            self._current_seed = config['random_seed']
        else:
            self._current_seed = None
        
        # Load data files
        from .core import config as core_config
        
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
        edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))
        
        # Generate scenario with custom config
        problem_data = generate_scenario_from_config(core_config, nodes_df, edges_df, config)
        
        # Extract components
        nodes = problem_data['nodes']
        edges_df_final = problem_data['edges_df']
        warehouses = problem_data['warehouses']
        orders, _ = problem_data['orders']  # Unpack orders and metadata
        skus = problem_data['skus']
        
        # Extract all vehicles
        all_vehicles = []
        for warehouse in warehouses:
            all_vehicles.extend(warehouse.vehicles)
        
        # Convert nodes to DataFrame format
        nodes_df_final = pd.DataFrame([
            {'node_id': node.id, 'lat': node.lat, 'lon': node.lon} 
            for node in nodes
        ])
        
        # Re-initialize environment with new data
        self._initialize_environment(nodes_df_final, edges_df_final, warehouses, orders, skus, all_vehicles)
        self._reset_vehicle_states()

    # ===== VALIDATION METHODS =====
    
    def validate_route_physical(self, route: List[int]) -> Tuple[bool, str]:
        """
        Validate that a route follows the actual road network.
        This is the single source of truth for route validation.
        """
        if not route or len(route) < 2:
            return False, "Route must have at least 2 nodes"
        
        for i in range(len(route) - 1):
            if not self._graph.has_edge(route[i], route[i+1]):
                return False, f"No road connection from node {route[i]} to {route[i+1]}"
        
        return True, "Route follows road network"

    def validate_single_route(self, vehicle_id: str, route: List[int]) -> Tuple[bool, str]:
        """
        Validate a single route against all constraints.
        This is the single source of truth for route validation.
        """
        # Get vehicle
        vehicle = self.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            return False, f"Unknown vehicle {vehicle_id}"
        
        # Get home warehouse
        warehouse = self.get_warehouse_by_id(vehicle.home_warehouse_id)
        if not warehouse:
            return False, f"Warehouse {vehicle.home_warehouse_id} not found for vehicle {vehicle_id}"
        
        warehouse_node_id = warehouse.location.id
        
        # Check route structure
        if not route or len(route) < 2:
            return False, "Route must have at least 2 nodes"
        
        # Check start/end at home warehouse
        if route[0] != warehouse_node_id or route[-1] != warehouse_node_id:
            return False, f"Route must start and end at home warehouse node {warehouse_node_id}"
        
        # Check physical constraints (road network)
        is_physical_valid, physical_msg = self.validate_route_physical(route)
        if not is_physical_valid:
            return False, physical_msg
        
        # Check distance constraints
        route_distance = self.get_route_distance(route)
        if route_distance > vehicle.max_distance:
            return False, f"Route distance {route_distance:.2f} km exceeds vehicle max distance {vehicle.max_distance} km"
        
        return True, "Route is valid"

    def validate_solution_business_logic(self, solution: Dict) -> Tuple[bool, str]:
        """
        Validate solution business logic.
        This is the single source of truth for business logic validation.
        """
        if not solution or 'routes' not in solution:
            return False, "Solution must contain routes"
        
        routes = solution['routes']
        if not isinstance(routes, list):
            return False, "Routes must be a list"
        
        # Track assigned vehicles
        assigned_vehicles = set()
        
        for route in routes:
            vehicle_id = route.get('vehicle_id')
            if not vehicle_id:
                return False, "Each route must have a vehicle_id"
            
            if vehicle_id in assigned_vehicles:
                return False, f"Vehicle {vehicle_id} assigned to multiple routes"
            
            assigned_vehicles.add(vehicle_id)
            
            # Check if vehicle exists
            vehicle = self.get_vehicle_by_id(vehicle_id)
            if not vehicle:
                return False, f"Unknown vehicle {vehicle_id}"
        
        return True, "Solution business logic is valid"

    def validate_solution_complete(self, solution: Dict) -> Tuple[bool, str]:
        """
        Comprehensive solution validation.
        This is the single source of truth for complete solution validation.
        """
        # Validate business logic first
        is_business_valid, business_msg = self.validate_solution_business_logic(solution)
        if not is_business_valid:
            return False, f"Business logic validation failed: {business_msg}"
        
        # Validate each route
        for i, route in enumerate(solution.get('routes', [])):
            vehicle_id = route.get('vehicle_id')
            route_path = route.get('route', [])
            
            if not vehicle_id or not route_path:
                return False, f"Route {i} missing vehicle_id or route path"
            
            is_valid, error_msg = self.validate_single_route(vehicle_id, route_path)
            if not is_valid:
                return False, f"Route {i} validation failed: {error_msg}"
        
        return True, "Solution is completely valid"

    # ===== METRICS AND STATISTICS =====
    
    def calculate_solution_cost(self, solution: Dict) -> float:
        """
        Calculate the total operational cost of a solution.
        This is the single source of truth for cost calculation.
        """
        total_cost = 0.0
        routes = solution.get("routes", [])
        
        for route_info in routes:
            vehicle_id = route_info.get('vehicle_id')
            route = route_info.get('route', [])
            
            if vehicle_id and route:
                vehicle = self.get_vehicle_by_id(vehicle_id)
                if vehicle:
                    # Fixed cost for using vehicle
                    total_cost += vehicle.fixed_cost
                    
                    # Variable cost based on distance
                    route_distance = self.get_route_distance(route)
                    total_cost += route_distance * vehicle.cost_per_km
        
        return total_cost

    def get_solution_statistics(self, solution: Dict) -> Dict:
        """
        Get comprehensive solution statistics.
        This is the single source of truth for solution statistics.
        """
        routes = solution.get('routes', [])
        
        # Count unique entities
        vehicles_used = set()
        orders_served = set()
        total_distance = 0.0
        
        for route in routes:
            vehicle_id = route.get('vehicle_id')
            route_path = route.get('route', [])
            
            if vehicle_id and route_path:
                vehicles_used.add(vehicle_id)
                route_distance = self.get_route_distance(route_path)
                total_distance += route_distance
                
                # Track orders served by this route through delivery operations
                delivery_ops = route.get('delivery_operations', [])
                for delivery_op in delivery_ops:
                    order_id = delivery_op.get('order_id')
                    if order_id:
                        orders_served.add(order_id)
                
                # Also check if any orders are directly in the route path
                for node_id in route_path:
                    if node_id in self.orders:
                        orders_served.add(node_id)
        
        # Calculate costs
        total_cost = self.calculate_solution_cost(solution)
        
        # Get accurate fulfillment metrics from fulfillment summary
        fulfillment_summary = self.get_solution_fulfillment_summary(solution)
        
        # Calculate ratios
        total_vehicles = len(self.get_all_vehicles())
        total_orders = len(self.orders)
        
        vehicle_utilization_ratio = len(vehicles_used) / total_vehicles if total_vehicles > 0 else 0
        
        return {
            'total_routes': len(routes),
            'unique_vehicles_used': len(vehicles_used),
            'total_vehicles': total_vehicles,
            'unique_orders_served': len(orders_served),
            'total_orders': total_orders,
            'total_distance': total_distance,
            'total_cost': total_cost,
            'vehicle_utilization_ratio': vehicle_utilization_ratio,
            'orders_fulfillment_ratio': fulfillment_summary['average_fulfillment_rate'] / 100.0,
            'average_fulfillment_rate': fulfillment_summary['average_fulfillment_rate'],
            'fully_fulfilled_orders': fulfillment_summary['fully_fulfilled_orders']
        }

    def get_solution_fulfillment_summary(self, solution: Dict) -> Dict:
        """
        Get comprehensive fulfillment summary for entire solution.
        This is the single source of truth for fulfillment analysis.
        """
        routes = solution.get('routes', [])
        
        # Initialize tracking
        order_fulfillment = {}
        vehicles_used = set()
        total_distance = 0.0
        total_cost = 0.0
        
        # Process each order
        for order_id, order in self.orders.items():
            order_fulfillment[order_id] = {
                'requested': order.requested_items.copy(),
                'delivered': {},
                'remaining': {}
            }
        
        # Process routes for fulfillment tracking
        for route in routes:
            vehicle_id = route.get('vehicle_id')
            route_path = route.get('route', [])
            
            if vehicle_id and route_path:
                vehicles_used.add(vehicle_id)
                route_distance = self.get_route_distance(route_path)
                total_distance += route_distance
                
                # Track SKU operations if provided
                delivery_ops = route.get('delivery_operations', [])
                for delivery_op in delivery_ops:
                    order_id = delivery_op.get('order_id')
                    sku_id = delivery_op.get('sku_id')
                    quantity = delivery_op.get('quantity', 0)
                    
                    if order_id in order_fulfillment and sku_id in order_fulfillment[order_id]['requested']:
                        if sku_id not in order_fulfillment[order_id]['delivered']:
                            order_fulfillment[order_id]['delivered'][sku_id] = 0
                        order_fulfillment[order_id]['delivered'][sku_id] += quantity
        
        # Calculate fulfillment metrics
        total_fulfillment_rate = 0.0
        fully_fulfilled_orders = 0
        
        for order_id, fulfillment in order_fulfillment.items():
            total_requested = sum(fulfillment['requested'].values())
            total_delivered = sum(fulfillment['delivered'].values())
            
            # Calculate remaining quantities per SKU
            for sku_id in fulfillment['requested']:
                requested = fulfillment['requested'][sku_id]
                delivered = fulfillment['delivered'].get(sku_id, 0)
                fulfillment['remaining'][sku_id] = max(0, requested - delivered)
            
            # Calculate fulfillment rate
            if total_requested > 0:
                fulfillment['fulfillment_rate'] = (total_delivered / total_requested) * 100
                total_fulfillment_rate += fulfillment['fulfillment_rate']
                
                if total_delivered >= total_requested:
                    fully_fulfilled_orders += 1
            else:
                fulfillment['fulfillment_rate'] = 100.0
                total_fulfillment_rate += 100.0
                fully_fulfilled_orders += 1
        
        avg_fulfillment_rate = total_fulfillment_rate / len(order_fulfillment) if order_fulfillment else 0
        
        # Calculate total cost
        total_cost = self.calculate_solution_cost(solution)
        
        return {
            'total_orders': len(self.orders),
            'orders_served': len([o for o in order_fulfillment.values() if sum(o['delivered'].values()) > 0]),
            'fully_fulfilled_orders': fully_fulfilled_orders,
            'total_vehicles': len(self.get_all_vehicles()),
            'vehicles_used': len(vehicles_used),
            'total_distance': total_distance,
            'total_cost': total_cost,
            'average_fulfillment_rate': avg_fulfillment_rate,
            'order_fulfillment_details': order_fulfillment,
            'vehicle_utilization': (len(vehicles_used) / len(self.get_all_vehicles())) * 100 if self.get_all_vehicles() else 0
        }