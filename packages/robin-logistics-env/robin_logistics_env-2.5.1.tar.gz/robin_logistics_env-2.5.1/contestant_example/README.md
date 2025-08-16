# 🚛 Contestant Guide - Robin Logistics Environment

Welcome to the Robin Logistics hackathon! This guide will help you build and test your multi-depot vehicle routing solver.

## 🎯 **Your Mission**

Design an algorithm that efficiently delivers items from multiple warehouses to customer orders using a vehicle fleet, while minimizing cost and maximizing order fulfillment.

## 📦 **What's Provided**

This `contestant_example/` directory contains everything you need to get started:

```
contestant_example/
├── my_solver.py          # Your solver template (EDIT THIS)
├── test_my_solver.py     # Local testing framework  
├── main.py               # Simple runner script
├── requirements.txt      # Dependencies
└── README.md            # This guide
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
cd contestant_example
pip install -r requirements.txt
```

### **2. Test the Template**
```bash
python test_my_solver.py
```

You should see:
```
============================================================
CONTESTANT SOLVER TESTING
============================================================
✓ Solution is VALID
Performance Metrics:
  Total Cost: $435.20
  Vehicles Used: 6/6
  Average Fulfillment: 0.0%
============================================================
ALL TESTS COMPLETED SUCCESSFULLY!
Your solver is ready for submission.
============================================================
```

### **3. Understand the Template**
Open `my_solver.py` and examine the basic structure:

```python
def my_solver(env: LogisticsEnvironment):
    """
    Your routing algorithm implementation.
    
    Args:
        env: LogisticsEnvironment with all problem data
        
    Returns:
        Dict with 'routes' containing vehicle routes
    """
    # Your algorithm goes here!
    return {"routes": [...]}
```

## 🏗️ **Development Workflow**

### **Step 1: Understand the Problem**
```python
# Explore the environment
env = LogisticsEnvironment()

print(f"Warehouses: {env.num_warehouses}")
print(f"Vehicles: {env.num_vehicles}")  
print(f"Orders: {env.num_orders}")

# Get data
warehouses = env.warehouses
orders = env.orders
vehicles = env.get_all_vehicles()
road_network = env.get_road_network_data()
```

### **Step 2: Build Your Algorithm**
Edit `my_solver.py` to implement your routing logic. Key areas to consider:

#### **🗺️ Pathfinding**
```python
def find_shortest_path(env, start_node, end_node):
    """Find shortest path between two nodes."""
    road_data = env.get_road_network_data()
    adjacency_list = road_data['adjacency_list']
    
    # Your pathfinding algorithm (BFS, Dijkstra, etc.)
    # Template includes basic BFS implementation
```

#### **📦 Order Assignment**
```python
def assign_orders_to_vehicles(env):
    """Decide which vehicle serves which orders."""
    assignments = {}
    
    for order_id in env.get_all_order_ids():
        # Find best vehicle for this order
        best_vehicle = find_best_vehicle(env, order_id)
        if best_vehicle:
            assignments[order_id] = best_vehicle
    
    return assignments
```

#### **🚛 Route Planning**
```python
def create_vehicle_route(env, vehicle_id, assigned_orders):
    """Create optimal route for a vehicle."""
    home_warehouse = env.get_vehicle_home_warehouse(vehicle_id)
    
    # Plan sequence of stops
    route_nodes = [home_warehouse]
    
    for order_id in assigned_orders:
        order_location = env.get_order_location(order_id)
        path = find_shortest_path(env, route_nodes[-1], order_location)
        route_nodes.extend(path[1:])  # Exclude duplicate start node
    
    # Return home
    path_home = find_shortest_path(env, route_nodes[-1], home_warehouse)
    route_nodes.extend(path_home[1:])
    
    return route_nodes
```

### **Step 3: Test Continuously**
```bash
# Test after each change
python test_my_solver.py

# Test specific scenarios
python -c "
from my_solver import my_solver
from robin_logistics import LogisticsEnvironment

env = LogisticsEnvironment()
env.set_random_seed(42)  # Reproducible testing

solution = my_solver(env)
is_valid, msg = env.validate_solution_complete(solution)
print(f'Valid: {is_valid}, Message: {msg}')
"
```

### **Step 4: Analyze Performance**
```python
# Get detailed metrics
stats = env.get_solution_statistics(solution)
fulfillment = env.get_solution_fulfillment_summary(solution)

print(f"Cost: ${stats['total_cost']:.2f}")
print(f"Distance: {stats['total_distance']:.1f} km")
print(f"Fulfillment: {fulfillment['average_fulfillment_rate']:.1f}%")
print(f"Vehicles Used: {stats['unique_vehicles_used']}/{stats['total_vehicles']}")
```

## 🎮 **Problem Details**

### **Environment Structure**
- **2-3 Warehouses**: Each with inventory and vehicle fleet
- **15-50 Orders**: Each requiring specific SKU quantities  
- **6-12 Vehicles**: Different types (Light Van, Medium Truck, Heavy Truck)
- **3 SKU Types**: Light, Medium, Heavy items with different weight/volume

### **Constraints You Must Handle**
1. **Vehicle Capacity**: Weight and volume limits
2. **Distance Limits**: Maximum travel distance per vehicle
3. **Road Network**: Must follow connected roads
4. **Home Warehouse**: Vehicles start and end at assigned warehouse
5. **Inventory**: Can only pick up what's available

### **Your Algorithm Must**
- ✅ **Return valid routes** that follow road network
- ✅ **Respect vehicle constraints** (capacity, distance)
- ✅ **Start/end at home** warehouse for each vehicle
- ✅ **Handle inventory** across multiple warehouses

### **Optimization Goals**
- 🎯 **Minimize total cost** (distance × cost_per_km + fixed_cost)
- 🎯 **Maximize order fulfillment** (% of requested items delivered)
- 🎯 **Efficient vehicle utilization** (don't waste capacity)

## 🛠️ **Essential Environment Methods**

### **Data Access**
```python
# Problem structure
env.get_all_order_ids()                    # List of order IDs
env.get_available_vehicles()               # List of vehicle IDs
env.get_order_requirements("ORD-1")        # Dict of SKU requirements
env.get_warehouse_inventory("WH-1")        # Dict of SKU quantities

# Locations  
env.get_order_location("ORD-1")            # Node ID for order delivery
env.get_vehicle_home_warehouse("VEH-1")    # Node ID for vehicle home

# Road network
env.get_road_network_data()                # Complete network structure
env.get_distance(node1, node2)            # Direct distance between nodes
env.get_route_distance([n1, n2, n3])      # Total route distance
```

### **Validation**
```python
# Route validation
is_valid, msg = env.validate_single_route(vehicle_id, route_nodes)

# Complete solution validation  
is_valid, msg = env.validate_solution_complete(solution)

# Check physical connectivity
is_valid, msg = env.validate_route_physical(route_nodes)
```

### **Inventory Simulation** (Optional)
```python
# Test pickup/delivery operations
success = env.pickup_sku_from_warehouse(vehicle_id, warehouse_id, sku_id, qty)
success = env.deliver_sku_to_order(vehicle_id, order_id, sku_id, qty)

# Get current vehicle load
current_load = env.get_vehicle_current_load(vehicle_id)
weight_used, volume_used = env.get_vehicle_current_capacity(vehicle_id)
```

## 💡 **Development Tips**

### **Start Simple**
1. **One vehicle per order** - Get basic functionality working
2. **Shortest paths only** - Use simple BFS pathfinding
3. **Ignore inventory** - Assume items are available
4. **Validate frequently** - Check each route before adding

### **Add Complexity Gradually**
1. **Multi-stop routes** - One vehicle serving multiple orders
2. **Inventory awareness** - Check availability before assignment
3. **Capacity optimization** - Pack vehicles efficiently
4. **Multi-warehouse** - Use inventory from different locations

### **Debugging Common Issues**

#### **❌ Route Validation Fails**
```python
# Check each segment
route = [n1, n2, n3, n4]
for i in range(len(route)-1):
    if not env.get_distance(route[i], route[i+1]):
        print(f"No connection: {route[i]} -> {route[i+1]}")
```

#### **❌ Vehicle Constraints Violated**
```python
# Check vehicle specs
vehicle = env.get_vehicle_by_id(vehicle_id)
print(f"Max weight: {vehicle.max_weight_kg}")
print(f"Max volume: {vehicle.max_volume_m3}")
print(f"Max distance: {vehicle.max_distance}")

# Check route distance
route_distance = env.get_route_distance(route)
print(f"Route distance: {route_distance}")
```

#### **❌ Orders Not Fulfilled**
```python
# Check order requirements vs delivery operations
requirements = env.get_order_requirements(order_id)
print(f"Order needs: {requirements}")

# Make sure you have delivery_operations in your route
route_with_ops = {
    "vehicle_id": vehicle_id,
    "route": route_nodes,
    "delivery_operations": [
        {"order_id": order_id, "sku_id": sku_id, "quantity": qty}
    ]
}
```

## 🧪 **Testing Strategies**

### **Local Testing**
```bash
# Full test suite
python test_my_solver.py

# Quick validation test
python -c "
from my_solver import my_solver
from robin_logistics import LogisticsEnvironment
env = LogisticsEnvironment()
solution = my_solver(env)
valid, msg = env.validate_solution_complete(solution)
print('✅ Valid' if valid else f'❌ Invalid: {msg}')
"
```

### **Scenario Testing**
```python
# Test different scenarios
seeds = [42, 123, 456, 789, 999]
for seed in seeds:
    env = LogisticsEnvironment()
    env.set_random_seed(seed)
    
    solution = my_solver(env)
    stats = env.get_solution_statistics(solution)
    
    print(f"Seed {seed}: Cost=${stats['total_cost']:.2f}, "
          f"Fulfillment={stats['orders_fulfillment_ratio']*100:.1f}%")
```

### **Performance Profiling**
```python
import time

start_time = time.time()
solution = my_solver(env)
execution_time = time.time() - start_time

print(f"Execution time: {execution_time:.3f} seconds")
```

## 📊 **Solution Format**

Your solver must return a dictionary with this structure:

```python
solution = {
    "routes": [
        {
            "vehicle_id": "LightVan_WH-1_1",
            "route": [12345, 67890, 54321, 12345],  # Node IDs
            
            # Optional: Specify exact operations
            "pickup_operations": [
                {
                    "warehouse_id": "WH-1",
                    "sku_id": "Light_Item", 
                    "quantity": 5
                }
            ],
            "delivery_operations": [
                {
                    "order_id": "ORD-1",
                    "sku_id": "Light_Item",
                    "quantity": 3
                }
            ]
        }
        # ... more routes
    ]
}
```

**Required**: `vehicle_id`, `route`  
**Optional**: `pickup_operations`, `delivery_operations`

## 🏆 **Advanced Features**

### **Multi-Warehouse Inventory**
```python
# Find warehouses with specific items
warehouses_with_item = env.get_warehouses_with_sku("Heavy_Item", min_quantity=2)

# Plan route visiting multiple warehouses
route = [home_warehouse]
route.extend(find_path(home_warehouse, best_warehouse))
route.extend(find_path(best_warehouse, order_location))
route.extend(find_path(order_location, home_warehouse))
```

### **Atomic Operations**
```python
# Ensure pickup/delivery operations are atomic
transaction = env.create_inventory_transaction()
transaction.pickup_sku(vehicle_id, warehouse_id, sku_id, qty)
transaction.deliver_sku(vehicle_id, order_id, sku_id, qty)
success, msg = transaction.commit()  # All or nothing
```

### **Route Optimization**
```python
# 2-opt improvement
def optimize_route(env, initial_route):
    best_route = initial_route[:]
    best_distance = env.get_route_distance(best_route)
    
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route)-2):
            for j in range(i+1, len(route)):
                new_route = two_opt_swap(best_route, i, j)
                new_distance = env.get_route_distance(new_route)
                
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
    
    return best_route
```

## 🎯 **Submission Checklist**

Before submitting your solver:

- [ ] ✅ **Runs without errors** on multiple scenarios
- [ ] ✅ **Returns valid solutions** (passes `validate_solution_complete`)
- [ ] ✅ **Handles edge cases** (no orders, no vehicles, unreachable orders)
- [ ] ✅ **Achieves reasonable performance** (>50% fulfillment, <$1000 cost)
- [ ] ✅ **Completes in reasonable time** (<30 seconds for 50 orders)
- [ ] ✅ **Uses proper solution format** (vehicle_id, route required)

## 🆘 **Common Pitfalls**

### **❌ Forgetting Route Structure**
Routes must start and end at vehicle's home warehouse:
```python
# Wrong
route = [order1_location, order2_location]

# Correct  
home = env.get_vehicle_home_warehouse(vehicle_id)
route = [home, order1_location, order2_location, home]
```

### **❌ Invalid Path Connections**
Every consecutive pair of nodes must be connected:
```python
# Always validate paths
path = find_shortest_path(env, start, end)
if path is None:
    print(f"No path from {start} to {end}")
    continue
```

### **❌ Ignoring Vehicle Constraints**
Check capacity and distance limits:
```python
vehicle = env.get_vehicle_by_id(vehicle_id)
route_distance = env.get_route_distance(route)

if route_distance > vehicle.max_distance:
    print(f"Route too long: {route_distance} > {vehicle.max_distance}")
```

### **❌ Empty or Invalid Solutions**
Always return proper structure:
```python
# Don't return empty routes
if not solution["routes"]:
    print("Warning: No routes generated!")

# Don't include invalid vehicles
for route in solution["routes"]:
    if not env.get_vehicle_by_id(route["vehicle_id"]):
        print(f"Invalid vehicle: {route['vehicle_id']}")
```

## 📁 **Project Structure Recommendation**

```
my_logistics_solution/
├── my_solver.py              # Main algorithm (REQUIRED)
├── pathfinding.py            # Pathfinding utilities  
├── optimization.py           # Route optimization
├── inventory_utils.py        # Inventory management helpers
├── test_my_solver.py         # Testing framework
├── config.json               # Custom test scenarios
└── results/                  # Test outputs
    ├── test_run_1/
    ├── test_run_2/
    └── ...
```

## 🎉 **Ready to Start?**

1. **Understand the template**: Read through `my_solver.py`
2. **Run the tests**: Execute `python test_my_solver.py`
3. **Start coding**: Implement your algorithm step by step
4. **Test frequently**: Validate after each major change
5. **Optimize gradually**: Focus on correctness first, then performance

**Good luck building the next generation of logistics algorithms!** 🚛💨

---

**Need help?** Check the environment docstrings, use the validation methods, and test with small scenarios first.