#!/usr/bin/env python3
"""
Example of running Robin Logistics Environment in headless mode.
This demonstrates how to use the headless runner without the dashboard.
"""

import sys
import os

# Add parent directory to path to import robin_logistics
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from robin_logistics.headless import HeadlessRunner
from robin_logistics.solvers import test_solver


def main():
    """Run example headless execution."""
    print("🚛 Robin Logistics - Headless Example")
    print("=" * 40)
    
    # Create headless runner
    runner = HeadlessRunner(output_base_dir="example_results")
    
    # Setup environment
    runner.setup_environment(seed=42)  # Use fixed seed for reproducible results
    
    # Run the demo solver
    results = runner.run_solver(test_solver, "demo_solver", "example_run")
    
    print("\n🎉 Example completed!")
    print(f"📁 Results saved to: {results['output_directory']}")
    
    # Show what files were created
    print("\n📄 Generated files:")
    for file_type, file_path in results['file_paths'].items():
        print(f"  - {file_type}: {os.path.basename(file_path)}")


if __name__ == "__main__":
    main()
