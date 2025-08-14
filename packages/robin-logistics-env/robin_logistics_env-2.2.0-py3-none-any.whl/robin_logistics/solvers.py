"""Demo solver implementation for hackathon contestants.

This file contains a working example solver that contestants can study
to understand how to implement their own logistics optimization algorithms.
"""

from typing import Dict, List, Tuple, Optional

def test_solver(env):
    """
    Demo solver that demonstrates basic logistics optimization.
    
    This solver shows the essential structure that contestants need to implement:
    1. Get road network data from environment
    2. Access orders and vehicles
    3. Create routes using pathfinding
    4. Validate routes with environment
    5. Return solution in correct format
    
    Args:
        env: LogisticsEnvironment instance with problem data
        
    Returns:
        dict: Solution with 'routes' list containing route dictionaries
    """
    solution = {'routes': []}
    
    road_network = env.get_road_network_data()
    order_ids = env.get_all_order_ids()
    available_vehicles = env.get_available_vehicles()
    
    for i, order_id in enumerate(order_ids):
        if i < len(available_vehicles):
            vehicle_id = available_vehicles[i]
            order_location = env.get_order_location(order_id)
            home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
            
            if order_location is not None and home_warehouse is not None:
                # Ensure both are integers
                order_location = int(order_location)
                home_warehouse = int(home_warehouse)
                
                # Solver decides which warehouse to get inventory from
                best_warehouse_id = None
                best_warehouse_distance = float('inf')
                
                # Check home warehouse first
                if env.warehouse_can_fulfill_order(vehicle_id.split('_')[1], order_id):
                    best_warehouse_id = vehicle_id.split('_')[1]
                else:
                    # Find nearest warehouse with sufficient inventory
                    for warehouse_id, warehouse in env.warehouses.items():
                        if env.warehouse_can_fulfill_order(warehouse_id, order_id):
                            # Calculate distance from home warehouse to this warehouse
                            home_wh_node = env.get_vehicle_home_warehouse(vehicle_id)
                            warehouse_node = warehouse.location.id
                            distance = env.get_distance(home_wh_node, warehouse_node)
                            
                            if distance is not None and distance < best_warehouse_distance:
                                best_warehouse_distance = distance
                                best_warehouse_id = warehouse_id
                
                # Create route based on inventory decision
                if best_warehouse_id:
                    if best_warehouse_id == vehicle_id.split('_')[1]:
                        # Use home warehouse
                        route = create_simple_route(home_warehouse, order_location, road_network)
                    else:
                        # Need to visit another warehouse for inventory
                        inventory_warehouse_node = env.warehouses[best_warehouse_id].location.id
                        route = create_simple_route(home_warehouse, order_location, road_network, inventory_warehouse_node)
                else:
                    # No warehouse can fulfill this order
                    print(f"Warning: No warehouse can fulfill order {order_id}")
                    route = None
                
                if route:
                    is_valid, error_msg = env.validate_single_route(vehicle_id, route)
                    
                    if is_valid:
                        solution['routes'].append({
                            'vehicle_id': vehicle_id,
                            'route': route,
                            'distance': env.get_route_distance(route),
                            'order_id': order_id
                        })
    
    return solution

def create_simple_route(home_warehouse, order_location, road_network, inventory_warehouse=None):
    """
    Create a route from warehouse to order location and back.
    Supports multi-depot inventory sharing if inventory_warehouse is specified.
    
    This is a basic pathfinding implementation using BFS for directed graphs.
    Contestants can replace this with their own algorithms.
    
    Args:
        home_warehouse: Starting node ID (vehicle's home warehouse)
        order_location: Destination node ID
        road_network: Road network data from environment
        inventory_warehouse: Optional warehouse node to pick up inventory from
        
    Returns:
        list: Route as list of node IDs, or None if no path found
    """
    adjacency_list = road_network['adjacency_list']
    
    # Check if both nodes exist in the adjacency list
    if home_warehouse not in adjacency_list:
        print(f"Warning: Warehouse node {home_warehouse} not connected to road network")
        return None
        
    if order_location not in adjacency_list:
        print(f"Warning: Order location {order_location} not connected to road network")
        return None
    
    # Build route based on inventory pickup needs
    if inventory_warehouse and inventory_warehouse != home_warehouse:
        # Multi-depot route: home -> inventory -> order -> home
        path1 = find_shortest_path(home_warehouse, inventory_warehouse, adjacency_list)
        if not path1:
            return None
            
        path2 = find_shortest_path(inventory_warehouse, order_location, adjacency_list)
        if not path2:
            return None
            
        path3 = find_shortest_path(order_location, home_warehouse, adjacency_list)
        if not path3:
            return None
        
        # Combine paths, avoiding duplicate nodes
        route = path1 + path2[1:] + path3[1:]
        return route
    else:
        # Simple route: home -> order -> home
        forward_path = find_shortest_path(home_warehouse, order_location, adjacency_list)
        if not forward_path:
            return None

        return_path = find_shortest_path(order_location, home_warehouse, adjacency_list)
        if not return_path or len(return_path) < 2:
            return None

        # Concatenate, skipping the duplicate middle node
        return forward_path + return_path[1:]

def find_shortest_path(start_node, end_node, adjacency_list, max_path_length=500):
    """
    Find shortest path using Breadth-First Search.
    
    Args:
        start_node: Starting node ID
        end_node: Destination node ID
        adjacency_list: Graph adjacency list
        max_path_length: Maximum path length to prevent infinite loops
        
    Returns:
        list: Path as list of node IDs, or None if no path found
    """
    if start_node == end_node:
        return [start_node]
    
    queue = [(start_node, [start_node])]
    visited = {start_node}
    
    while queue and len(queue[0][1]) < max_path_length:
        current, path = queue.pop(0)
        
        neighbors = adjacency_list.get(current, [])
        for neighbor in neighbors:
            neighbor_int = int(neighbor) if hasattr(neighbor, '__int__') else neighbor
            
            if neighbor_int not in visited:
                if neighbor_int == end_node:
                    return path + [neighbor_int]
                
                visited.add(neighbor_int)
                queue.append((neighbor_int, path + [neighbor_int]))
    
    return None

if __name__ == "__main__":
    print("Demo solver for Robin Logistics Environment")
    print("Import and use with: from robin_logistics.solvers import test_solver")
