# Changelog

All notable changes to the Robin Logistics Environment will be documented in this file.

## [2.5.1] - 2024-12-20

### Critical Fixes & Architecture Improvements

#### Fixed
- **State Management Inconsistency** - Fully integrated VehicleStateManager across all operations
- **Distance Calculation Optimization** - Prioritize pre-calculated distances from edges data over Haversine
- **Inventory Transaction Integration** - Added atomic transaction support with rollback capabilities
- **Environment Architecture** - Merged duplicate environment files into single clean implementation

#### Added
- `create_inventory_transaction()` method for atomic operations
- `execute_route_operations()` method for complete route execution with rollback
- Enhanced warning for missing distance data in edges

#### Removed
- `robin_logistics/core/environment.py` - Merged into main environment for cleaner architecture
- Environment delegation pattern - Direct implementation for better maintainability

## [2.5.0] - 2024-12-20

### Major Architecture Improvements

#### Added
- **Headless execution mode** - Run solvers without dashboard, save organized results
- **Comprehensive testing framework** - Mock solvers and environment validation tests
- **Skeleton testing script** - Local testing tools for contestants
- **Centralized utilities** - Distance calculations and state management
- **Transaction-based inventory** - Rollback capabilities for operations
- **Command-line interface** - Support for both headless and dashboard modes

#### Fixed
- **Vehicle state management** - Unified and consistent state tracking
- **Code duplication** - Eliminated duplicate distance calculations and pathfinding
- **Architecture separation** - Environment provides data only, contestants implement solving logic
- **Documentation** - Complete contestant guide and API documentation

#### Changed
- **Removed pathfinding from environment** - Contestants now implement their own algorithms
- **Cleaned codebase** - Removed excessive prints, comments, and emojis (except dashboard)
- **Dashboard logo** - Replaced emoji with Robin colored logo
- **Professional output** - Clean, minimal logging and output

#### Technical Improvements
- Centralized distance calculations with caching
- Single source of truth for route validation
- Comprehensive metrics calculation
- Improved error handling and validation
- Better separation of concerns

### Breaking Changes
- Pathfinding utilities removed from environment - contestants must implement their own
- Vehicle state management API updated for consistency

### Migration Guide
- Update solver implementations to include pathfinding algorithms
- Use new centralized distance utilities: `env.get_distance()` and `env.get_route_distance()`
- Update testing to use new skeleton tester: `python test_my_solver.py`

---

## [Previous Versions]

### [2.4.x] - Pre-Architecture Improvements
- Basic multi-depot vehicle routing environment
- Dashboard interface with Streamlit
- Problem data generation and validation
- Initial solver examples
