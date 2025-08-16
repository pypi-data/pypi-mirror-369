"""
Demo solver implementations for the Robin Logistics Environment.

These solvers demonstrate how to use the environment's API to create valid solutions.
They implement their own pathfinding that respects the road network structure.
"""

import random
from typing import Dict, List, Tuple, Optional
from collections import deque

def test_solver(env):
    """
    Enhanced demo solver that demonstrates item-level operations and partial fulfillment.
    
    This solver:
    1. Respects the road network structure (no direct node connections)
    2. Uses proper pathfinding between locations
    3. Demonstrates multi-warehouse inventory sharing
    4. Shows partial order fulfillment
    5. Tracks SKU operations throughout routes
    
    Args:
        env: LogisticsEnvironment instance
        
    Returns:
        dict: Solution with routes and SKU operations
    """
    solution = {'routes': []}
    
    # Get road network data for pathfinding
    road_network = env.get_road_network_data()
    adjacency_list = road_network['adjacency_list']
    
    # Assign vehicles to orders with proper pathfinding
    vehicle_assignments = assign_vehicles_to_orders(env)
    
    for vehicle_id, order_ids in vehicle_assignments.items():
        if not order_ids:
            continue
            
        # Create route for this vehicle
        route = create_vehicle_route(env, vehicle_id, order_ids, adjacency_list)
        
        if route:
            solution['routes'].append(route)
    
    return solution

def assign_vehicles_to_orders(env):
    """Assign available vehicles to orders."""
    available_vehicles = env.get_available_vehicles()
    order_ids = env.get_all_order_ids()
    
    assignments = {vehicle_id: [] for vehicle_id in available_vehicles}
    
    # Simple assignment: distribute orders among vehicles
    for i, order_id in enumerate(order_ids):
        vehicle_idx = i % len(available_vehicles)
        vehicle_id = available_vehicles[vehicle_idx]
        assignments[vehicle_id].append(order_id)
    
    return assignments

def create_vehicle_route(env, vehicle_id, order_ids, adjacency_list):
    """Create a complete route for a vehicle serving multiple orders."""
    if not order_ids:
        return None
    
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
    if home_warehouse is None:
        return None
    
    # Plan warehouse visits and delivery sequence
    warehouse_visits = plan_warehouse_visits(env, vehicle_id, order_ids)
    delivery_sequence = plan_delivery_sequence(env, vehicle_id, order_ids)
    
    # Build route with proper pathfinding
    route_nodes = build_route_with_pathfinding(
        env, vehicle_id, home_warehouse, warehouse_visits, delivery_sequence, adjacency_list
    )
    
    if not route_nodes:
        return None
    
    # Execute the route plan to track SKU operations
    pickup_ops, delivery_ops = execute_route_plan(
        env, vehicle_id, route_nodes, warehouse_visits, delivery_sequence
    )
    
    # Calculate route distance
    route_distance = env.get_route_distance(route_nodes)
    
    return {
        'vehicle_id': vehicle_id,
        'route': route_nodes,
        'distance': route_distance,
        'pickup_operations': pickup_ops,
        'delivery_operations': delivery_ops
    }

def plan_warehouse_visits(env, vehicle_id, order_ids):
    """Plan which warehouses to visit for SKU pickup."""
    warehouse_visits = []
    
    for order_id in order_ids:
        order_requirements = env.get_order_requirements(order_id)
        
        for sku_id, quantity in order_requirements.items():
            # Find warehouses with this SKU
            warehouses_with_sku = env.get_warehouses_with_sku(sku_id, quantity)
            
            if warehouses_with_sku:
                # Prefer home warehouse if it has the SKU
                home_warehouse_id = env.vehicles[vehicle_id].home_warehouse_id
                if home_warehouse_id in warehouses_with_sku:
                    warehouse_visits.append({
                        'warehouse_id': home_warehouse_id,
                                    'sku_id': sku_id,
                        'quantity': quantity,
                        'order_id': order_id
                    })
                else:
                    # Use first available warehouse
                    warehouse_visits.append({
                        'warehouse_id': warehouses_with_sku[0],
                        'sku_id': sku_id,
                        'quantity': quantity,
                        'order_id': order_id
                    })
    
    return warehouse_visits

def plan_delivery_sequence(env, vehicle_id, order_ids):
    """Plan the sequence of order deliveries."""
    delivery_sequence = []
    
    for order_id in order_ids:
        order_requirements = env.get_order_requirements(order_id)
        order_location = env.get_order_location(order_id)
        
        delivery_sequence.append({
            'order_id': order_id,
            'location': order_location,
            'requirements': order_requirements
        })
    
    return delivery_sequence

def build_route_with_pathfinding(env, vehicle_id, home_warehouse, warehouse_visits, delivery_sequence, adjacency_list):
    """Build route using proper pathfinding between nodes."""
    route_nodes = [home_warehouse]
    current_node = home_warehouse
    
    # Visit warehouses for pickup
    for visit in warehouse_visits:
        warehouse = env.warehouses[visit['warehouse_id']]
        warehouse_node = warehouse.location.id
        
        if warehouse_node != current_node:
            # Find path to warehouse
            path = find_shortest_path(current_node, warehouse_node, adjacency_list)
            if path:
                route_nodes.extend(path[1:])  # Skip first node (already in route)
                current_node = warehouse_node
            else:
                return None  # No valid path found
    
    # Visit orders for delivery
    for delivery in delivery_sequence:
        order_node = delivery['location']
        
        if order_node != current_node:
            # Find path to order
            path = find_shortest_path(current_node, order_node, adjacency_list)
            if path:
                route_nodes.extend(path[1:])  # Skip first node (already in route)
                current_node = order_node
            else:
                return None  # No valid path found
    
    # Return to home warehouse
    if current_node != home_warehouse:
        path = find_shortest_path(current_node, home_warehouse, adjacency_list)
        if path:
            route_nodes.extend(path[1:])  # Skip first node (already in route)
        else:
            return None  # No valid path found
    
    return route_nodes

def execute_route_plan(env, vehicle_id, route_nodes, warehouse_visits, delivery_sequence):
    """Execute the route plan and track SKU operations."""
    pickup_ops = []
    delivery_ops = []
    
    # Track current vehicle load
    current_load = {}
    current_weight = 0.0
    current_volume = 0.0
    
    # Process warehouse visits (pickup operations)
    for visit in warehouse_visits:
        warehouse_id = visit['warehouse_id']
        sku_id = visit['sku_id']
        quantity = visit['quantity']
        
        # Check if vehicle can pick up this SKU
        if env.pickup_sku_from_warehouse(vehicle_id, warehouse_id, sku_id, quantity):
            pickup_ops.append({
                'warehouse_id': warehouse_id,
                'sku_id': sku_id,
                'quantity': quantity
            })
            
            # Update current load tracking
            current_load[sku_id] = current_load.get(sku_id, 0) + quantity
            
            # Update weight and volume
            sku_details = env.get_sku_details(sku_id)
            if sku_details:
                current_weight += sku_details['weight'] * quantity
                current_volume += sku_details['volume'] * quantity
    
    # Process deliveries
    for delivery in delivery_sequence:
        order_id = delivery['order_id']
        requirements = delivery['requirements']
        
        for sku_id, requested_quantity in requirements.items():
            available_quantity = current_load.get(sku_id, 0)
            if available_quantity > 0:
                # Deliver what we can
                delivery_quantity = min(requested_quantity, available_quantity)
                
                if env.deliver_sku_to_order(vehicle_id, order_id, sku_id, delivery_quantity):
                    delivery_ops.append({
                        'order_id': order_id,
                        'sku_id': sku_id,
                        'quantity': delivery_quantity
                    })
                    
                    # Update current load
                    current_load[sku_id] -= delivery_quantity
                    if current_load[sku_id] <= 0:
                        del current_load[sku_id]
                    
                    # Update weight and volume
                    sku_details = env.get_sku_details(sku_id)
                    if sku_details:
                        current_weight -= sku_details['weight'] * delivery_quantity
                        current_volume -= sku_details['volume'] * delivery_quantity
    
    # Return remaining items to home warehouse
    if current_load:
        env.return_vehicle_to_home(vehicle_id)
    
    return pickup_ops, delivery_ops

def find_shortest_path(start_node, end_node, adjacency_list, max_path_length=500):
    """
    Find shortest path using Breadth-First Search.
    
    This is SOLVING LOGIC that contestants should implement themselves.
    This example shows one approach using BFS.
    
    Args:
        start_node: Starting node ID
        end_node: Destination node ID
        adjacency_list: Road network adjacency list from environment
        max_path_length: Maximum path length to prevent infinite loops
        
    Returns:
        list: Path as list of node IDs, or None if no path found
    """
    if start_node == end_node:
        return [start_node]
    
    queue = deque([(start_node, [start_node])])
    visited = {start_node}
    
    while queue:
        current, path = queue.popleft()
        
        # Prevent infinite loops
        if len(path) >= max_path_length:
            continue
        
        # Get neighbors from road network (provided by environment)
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                new_path = path + [neighbor_int]
                
                if neighbor_int == end_node:
                    return new_path
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, new_path))
    
    return None

def advanced_test_solver(env):
    """Advanced test solver that calls the enhanced demo solver."""
    return test_solver(env)

def create_simple_route(home_warehouse, order_location, road_network):
    """
    Create a simple route from warehouse to order location.
    
    This is SOLVING LOGIC - contestants implement their own route planning.
    This example shows a basic round-trip approach.
    
    Args:
        home_warehouse: Starting node ID
        order_location: Destination node ID
        road_network: Road network data from environment
        
    Returns:
        list: Route as list of node IDs, or None if no path found
    """
    adjacency_list = road_network['adjacency_list']
    
    # Find path to order location
    path_to_order = find_shortest_path(home_warehouse, order_location, adjacency_list)
    if not path_to_order:
        return None
    
    # Find path back to warehouse
    path_to_warehouse = find_shortest_path(order_location, home_warehouse, adjacency_list)
    if not path_to_warehouse:
        return None
    
    # Combine paths (avoid duplicate order_location)
    route = path_to_order + path_to_warehouse[1:]
    
    return route
