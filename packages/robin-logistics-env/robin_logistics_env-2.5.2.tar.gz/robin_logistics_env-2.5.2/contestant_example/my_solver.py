"""
Example solver implementation for hackathon contestants.

This file shows the basic structure you need to implement your own solver.
Study this code to understand how to:
1. Access environment data (what the environment provides)
2. Implement your own pathfinding (what YOU implement)
3. Create valid routes using the road network
4. Validate solutions and return results

IMPORTANT: The environment provides DATA and VALIDATION only.
YOU implement the solving logic (pathfinding, optimization, etc.)
"""

from collections import deque

def my_solver(env):
    """
    Your logistics optimization algorithm.
    
    This is a simple example that assigns orders to vehicles sequentially.
    You should replace this with your own optimization logic.
    
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
                # YOU implement pathfinding - this is solving logic!
                route = create_simple_route(home_warehouse, order_location, road_network)
                
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

def create_simple_route(home_warehouse, order_location, road_network):
    """
    Create a simple route from warehouse to order location.
    
    THIS IS YOUR SOLVING LOGIC - you implement the pathfinding algorithm.
    The environment only provides the road network data.
    
    Args:
        home_warehouse: Starting node ID  
        order_location: Destination node ID
        road_network: Road network data from environment (DATA ONLY)
                     Contains: nodes, edges, adjacency_list
        
    Returns:
        list: Route as list of node IDs, or None if no path found
    """
    adjacency_list = road_network['adjacency_list']  # Environment provides this DATA
    
    # Find path to order location (YOU implement this)
    path_to_order = find_shortest_path(home_warehouse, order_location, adjacency_list)
    if not path_to_order:
        return None
    
    # Find path back to warehouse (YOU implement this)
    path_to_warehouse = find_shortest_path(order_location, home_warehouse, adjacency_list)
    if not path_to_warehouse:
        return None
    
    # Combine paths (avoid duplicate order_location)
    route = path_to_order + path_to_warehouse[1:]
    
    return route

def find_shortest_path(start_node, end_node, adjacency_list, max_path_length=500):
    """
    Find shortest path using Breadth-First Search.
    
    THIS IS YOUR SOLVING LOGIC - you choose the pathfinding algorithm.
    You could use BFS (shown here), Dijkstra, A*, or any other algorithm.
    
    Args:
        start_node: Starting node ID
        end_node: Destination node ID
        adjacency_list: Road network adjacency list from environment (DATA ONLY)
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
        
        # Get neighbors from road network (environment provides this DATA)
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


