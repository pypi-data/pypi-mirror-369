#!/usr/bin/env python3
"""
Contestant Example - Simple Demo
Shows how to use the robin-logistics-env package.
"""

import subprocess
import sys
import os

def main():
    """Simple demo of environment usage."""
    try:
        import robin_logistics
        from robin_logistics import LogisticsEnvironment
        from robin_logistics.solvers import test_solver
        
        env = LogisticsEnvironment()
        
        solution = test_solver(env)
        dashboard_path = os.path.join(os.path.dirname(robin_logistics.__file__), 'dashboard.py')
        subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path], check=True)
        
    except ImportError:
        sys.exit(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
