# Robin Logistics Environment

Professional multi-depot vehicle routing environment for hackathons and competitions.

## Features

- **Multi-Depot Vehicle Routing**: Solve complex logistics problems with multiple warehouses
- **Real-World Constraints**: Vehicle capacity, road networks, inventory management  
- **Interactive Dashboard**: Streamlit-based visualization with real-time validation
- **Headless Execution**: Automated testing and result generation
- **Comprehensive API**: Clean interface for algorithm development
- **Item-Level Tracking**: SKU-based inventory and fulfillment management
- **Atomic Operations**: Transaction-based inventory management with rollback

## Quick Start

### Installation
```bash
pip install robin-logistics-env
```

### Basic Usage
```python
from robin_logistics import LogisticsEnvironment

# Create environment
env = LogisticsEnvironment()

# Implement your solver
def my_solver(env):
    solution = {"routes": []}
    # Your algorithm here
    return solution

# Validate solution
solution = my_solver(env)
is_valid, message = env.validate_solution_complete(solution)
```

### Interactive Dashboard
```bash
python -m robin_logistics.cli --dashboard --solver my_solver.py
```

### Headless Execution
```bash
python -m robin_logistics.cli --headless --solver my_solver.py --output results
```

## API Overview

### Environment Access
```python
env = LogisticsEnvironment()

# Problem data
warehouses = env.warehouses       # Dict[str, Warehouse]
orders = env.orders              # Dict[str, Order]
vehicles = env.get_all_vehicles() # List[Vehicle]

# Road network
road_data = env.get_road_network_data()
distance = env.get_distance(node1, node2)
route_distance = env.get_route_distance([n1, n2, n3])
```

### Validation Methods
```python
# Route validation
is_valid, msg = env.validate_single_route(vehicle_id, route)

# Complete solution validation
is_valid, msg = env.validate_solution_complete(solution)

# Physical connectivity
is_valid, msg = env.validate_route_physical(route)
```

### Solution Analysis
```python
# Performance metrics
stats = env.get_solution_statistics(solution)
fulfillment = env.get_solution_fulfillment_summary(solution)

print(f"Cost: ${stats['total_cost']:.2f}")
print(f"Fulfillment: {fulfillment['average_fulfillment_rate']:.1f}%")
```

### Inventory Operations
```python
# Check inventory
inventory = env.get_warehouse_inventory(warehouse_id)
requirements = env.get_order_requirements(order_id)

# Simulate operations
success = env.pickup_sku_from_warehouse(vehicle_id, warehouse_id, sku_id, quantity)
success = env.deliver_sku_to_order(vehicle_id, order_id, sku_id, quantity)
```

### Atomic Transactions
```python
# Create transaction
transaction = env.create_inventory_transaction()

# Add operations
transaction.pickup_sku(vehicle_id, warehouse_id, sku_id, quantity)
transaction.deliver_sku(vehicle_id, order_id, sku_id, quantity)

# Execute atomically
success, message = transaction.commit()
```

## Problem Structure

### Multi-Depot Vehicle Routing Problem (MDVRP)
- **Multiple warehouses** with different inventory levels
- **Vehicle fleets** assigned to warehouses
- **Customer orders** requiring specific items
- **Real road network** connectivity constraints
- **Vehicle capacity** and distance limitations

### Constraints
- **Physical**: Road network connectivity
- **Capacity**: Vehicle weight and volume limits
- **Distance**: Maximum travel distance per vehicle
- **Inventory**: Item availability across warehouses
- **Home Base**: Vehicles start and end at assigned warehouse

### Solution Format
```python
solution = {
    "routes": [
        {
            "vehicle_id": "LightVan_WH-1_1",
            "route": [12345, 67890, 12345],  # Node IDs
            "pickup_operations": [           # Optional
                {"warehouse_id": "WH-1", "sku_id": "Light_Item", "quantity": 5}
            ],
            "delivery_operations": [         # Optional
                {"order_id": "ORD-1", "sku_id": "Light_Item", "quantity": 3}
            ]
        }
    ]
}
```

## CLI Usage

### Dashboard Mode
```bash
# Default dashboard
python -m robin_logistics.cli

# With custom solver
python -m robin_logistics.cli --dashboard --solver my_solver.py
```

### Headless Mode
```bash
# Basic headless execution
python -m robin_logistics.cli --headless --solver my_solver.py

# Full configuration
python -m robin_logistics.cli --headless \
    --solver my_solver.py \
    --config config.json \
    --output results \
    --run-id submission_v1
```

### Configuration
```json
{
    "num_warehouses": 3,
    "num_orders": 25,
    "num_vehicles_per_warehouse": 4,
    "distance_control": {
        "radius_km": 20,
        "density_strategy": "clustered"
    },
    "random_seed": 42
}
```

## Advanced Features

### Scenario Generation
```python
# Fixed seed for reproducible testing
env.set_random_seed(42)
env.generate_new_scenario()

# Custom configuration
config = {"num_warehouses": 5, "num_orders": 50}
env.generate_scenario_from_config(config)
```

### State Management
```python
# Vehicle state tracking
current_load = env.get_vehicle_current_load(vehicle_id)
capacity_usage = env.get_vehicle_current_capacity(vehicle_id)
remaining_capacity = env.get_vehicle_remaining_capacity(vehicle_id)

# Order fulfillment tracking
fulfillment_status = env.get_order_fulfillment_status(order_id)
```

### Distance Optimization
- **Pre-calculated distances** from road network data
- **Distance caching** for performance
- **Haversine fallback** when road distances unavailable

## Package Information

- **Name**: robin-logistics-env
- **Version**: 2.5.1
- **Author**: Robin
- **License**: MIT
- **Python**: >=3.8
- **Dependencies**: streamlit, pandas, networkx, folium, plotly

## Links

- **Source Code**: [GitHub Repository]
- **Documentation**: Comprehensive docstrings and examples
- **Examples**: `contestant_example/` directory
- **Issues**: Use GitHub Issues for bug reports

---

Build the next generation of logistics optimization algorithms with Robin Logistics Environment!