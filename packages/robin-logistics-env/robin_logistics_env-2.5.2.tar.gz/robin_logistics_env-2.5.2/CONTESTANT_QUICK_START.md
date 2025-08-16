# 🚀 Quick Start for Contestants

## Installation & Setup (2 minutes)

```bash
# Install the package
pip install robin-logistics-env

# Verify installation
python -c "from robin_logistics import LogisticsEnvironment; print('✅ Ready!')"
```

## Create Your Solver (5 minutes)

```python
# my_solver.py
from robin_logistics import LogisticsEnvironment

def my_solver(env: LogisticsEnvironment):
    """Your algorithm goes here!"""
    solution = {"routes": []}
    
    # Get problem data
    vehicles = env.get_available_vehicles()
    orders = env.get_all_order_ids()
    
    # Simple assignment: one vehicle per order
    for i, order_id in enumerate(orders):
        if i < len(vehicles):
            vehicle_id = vehicles[i]
            
            # Get locations
            home = env.get_vehicle_home_warehouse(vehicle_id)
            order_location = env.get_order_location(order_id)
            
            # Create simple route: home -> order -> home
            route = [home, order_location, home]
            
            solution["routes"].append({
                "vehicle_id": vehicle_id,
                "route": route
            })
    
    return solution
```

## Test Your Solver (1 minute)

```python
# test_solver.py
from robin_logistics import LogisticsEnvironment
from my_solver import my_solver

# Create environment and test
env = LogisticsEnvironment()
solution = my_solver(env)

# Validate solution
is_valid, message = env.validate_solution_complete(solution)
print(f"✅ Valid: {is_valid}")

# Get metrics
stats = env.get_solution_statistics(solution)
print(f"Cost: ${stats['total_cost']:.2f}")
print(f"Distance: {stats['total_distance']:.1f} km")
```

## Interactive Dashboard

```bash
python -m robin_logistics.cli --dashboard --solver my_solver.py
```

## Automated Results

```bash
python -m robin_logistics.cli --headless --solver my_solver.py --output results
```

## What You Get

- **✅ Complete environment** with warehouses, vehicles, orders
- **✅ Road network** for realistic routing
- **✅ Validation system** that checks all constraints
- **✅ Performance metrics** for solution analysis
- **✅ Interactive dashboard** for visualization
- **✅ Headless mode** for automated testing
- **✅ Full documentation** and examples

## Next Steps

1. **Improve pathfinding** - Add BFS/Dijkstra for optimal routes
2. **Handle inventory** - Check warehouse stock before assignment
3. **Optimize packing** - Use vehicle capacity efficiently
4. **Multi-warehouse** - Use inventory from different locations
5. **Test scenarios** - Use different seeds for robust testing

**You're ready to build world-class logistics algorithms!** 🏆
