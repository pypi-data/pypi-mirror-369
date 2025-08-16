#!/usr/bin/env python3
"""
Local testing script for contestants to test their solvers.
This script helps validate your solver implementation before submission.
"""

import sys
import os
import time

# Add the parent directory to import robin_logistics
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from robin_logistics import LogisticsEnvironment
from my_solver import my_solver


def test_solver_basic():
    """Test basic solver functionality."""
    print("Testing basic solver functionality...")
    
    # Create environment with fixed seed for reproducible testing
    env = LogisticsEnvironment()
    env.set_random_seed(42)
    env.generate_new_scenario(42)
    
    print(f"Environment: {env.num_warehouses} warehouses, {env.num_vehicles} vehicles, {env.num_orders} orders")
    
    # Run solver
    start_time = time.time()
    solution = my_solver(env)
    execution_time = time.time() - start_time
    
    print(f"Solver execution time: {execution_time:.2f} seconds")
    
    # Basic solution structure validation
    assert isinstance(solution, dict), "Solution must be a dictionary"
    assert 'routes' in solution, "Solution must contain 'routes' key"
    assert isinstance(solution['routes'], list), "Routes must be a list"
    
    print(f"Solution contains {len(solution['routes'])} routes")
    
    return solution, env


def test_solver_validation():
    """Test solver output validation."""
    print("Testing solution validation...")
    
    solution, env = test_solver_basic()
    
    # Validate complete solution
    is_valid, message = env.validate_solution_complete(solution)
    
    if is_valid:
        print("✓ Solution is VALID")
    else:
        print(f"✗ Solution is INVALID: {message}")
        return False
    
    # Individual route validation
    for i, route in enumerate(solution['routes']):
        vehicle_id = route.get('vehicle_id')
        route_path = route.get('route', [])
        
        if vehicle_id and route_path:
            is_route_valid, route_message = env.validate_single_route(vehicle_id, route_path)
            if is_route_valid:
                print(f"✓ Route {i+1} ({vehicle_id}) is valid")
            else:
                print(f"✗ Route {i+1} ({vehicle_id}) is invalid: {route_message}")
                return False
    
    return True


def test_solver_metrics():
    """Test solver performance metrics."""
    print("Testing performance metrics...")
    
    solution, env = test_solver_basic()
    
    # Calculate comprehensive metrics
    stats = env.get_solution_statistics(solution)
    fulfillment = env.get_solution_fulfillment_summary(solution)
    
    print("Performance Metrics:")
    print(f"  Total Cost: ${stats.get('total_cost', 0):.2f}")
    print(f"  Total Distance: {stats.get('total_distance', 0):.1f} km")
    print(f"  Vehicles Used: {stats.get('unique_vehicles_used', 0)}/{stats.get('total_vehicles', 0)}")
    print(f"  Orders Served: {stats.get('unique_orders_served', 0)}/{stats.get('total_orders', 0)}")
    print(f"  Vehicle Utilization: {stats.get('vehicle_utilization_ratio', 0)*100:.1f}%")
    print(f"  Average Fulfillment: {fulfillment.get('average_fulfillment_rate', 0):.1f}%")
    print(f"  Fully Fulfilled Orders: {fulfillment.get('fully_fulfilled_orders', 0)}")
    
    return stats, fulfillment


def test_multiple_scenarios():
    """Test solver on multiple random scenarios."""
    print("Testing on multiple scenarios...")
    
    results = []
    seeds = [42, 123, 456, 789, 999]
    
    for seed in seeds:
        print(f"  Testing scenario {seed}...")
        
        env = LogisticsEnvironment()
        env.set_random_seed(seed)
        env.generate_new_scenario(seed)
        
        try:
            solution = my_solver(env)
            is_valid, _ = env.validate_solution_complete(solution)
            stats = env.get_solution_statistics(solution)
            
            results.append({
                'seed': seed,
                'valid': is_valid,
                'cost': stats.get('total_cost', float('inf')),
                'distance': stats.get('total_distance', 0),
                'fulfillment': stats.get('average_fulfillment_rate', 0)
            })
            
            status = "✓" if is_valid else "✗"
            print(f"    {status} Cost: ${stats.get('total_cost', 0):.2f}, Fulfillment: {stats.get('average_fulfillment_rate', 0):.1f}%")
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            results.append({
                'seed': seed,
                'valid': False,
                'error': str(e)
            })
    
    # Summary statistics
    valid_results = [r for r in results if r.get('valid', False)]
    if valid_results:
        avg_cost = sum(r['cost'] for r in valid_results) / len(valid_results)
        avg_fulfillment = sum(r['fulfillment'] for r in valid_results) / len(valid_results)
        print(f"Summary: {len(valid_results)}/{len(results)} scenarios valid")
        print(f"Average Cost: ${avg_cost:.2f}, Average Fulfillment: {avg_fulfillment:.1f}%")
    
    return results


def run_comprehensive_test():
    """Run all tests comprehensively."""
    print("=" * 60)
    print("CONTESTANT SOLVER TESTING")
    print("=" * 60)
    
    try:
        # Test 1: Basic functionality
        print("\n1. BASIC FUNCTIONALITY TEST")
        print("-" * 30)
        test_solver_basic()
        
        # Test 2: Validation
        print("\n2. SOLUTION VALIDATION TEST")
        print("-" * 30)
        validation_passed = test_solver_validation()
        
        if not validation_passed:
            print("CRITICAL: Solver produces invalid solutions!")
            return False
        
        # Test 3: Performance metrics
        print("\n3. PERFORMANCE METRICS TEST")
        print("-" * 30)
        test_solver_metrics()
        
        # Test 4: Multiple scenarios
        print("\n4. MULTIPLE SCENARIOS TEST")
        print("-" * 30)
        test_multiple_scenarios()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("Your solver is ready for submission.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        print("Please fix your solver and try again.")
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
