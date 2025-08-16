"""Dashboard interface for the Robin Logistics Environment."""

import streamlit as st
import pandas as pd
import folium
import os
import traceback
from robin_logistics.core import config as config_module
from robin_logistics import LogisticsEnvironment
from robin_logistics.core.data_generator import generate_scenario_from_config
from robin_logistics.core.config import (
    SKU_DEFINITIONS,
    WAREHOUSE_LOCATIONS,
    VEHICLE_FLEET_SPECS,
    DEFAULT_SETTINGS,
    DEFAULT_WAREHOUSE_SKU_ALLOCATIONS
)

def run_dashboard(env, solver_function=None):
    """
    Main dashboard function.
    
    Args:
        env: LogisticsEnvironment instance
        solver_function: Optional solver function to use instead of default demo solver
    """
    st.set_page_config(
        page_title="Robin Logistics Environment",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚛 Robin Logistics Environment")
    st.write("Configure and solve multi-depot vehicle routing problems with real-world constraints.")

    # Set solver (custom or default)
    if solver_function:
        current_solver = solver_function
    else:
        from robin_logistics.solvers import test_solver
        current_solver = test_solver

    st.header("🏗️ Fixed Infrastructure")

    st.subheader("📦 SKU Types")
    sku_data = [
        {
            'SKU ID': sku_info['sku_id'],
            'Weight (kg)': sku_info['weight_kg'],
            'Volume (m³)': sku_info['volume_m3']
        }
        for sku_info in SKU_DEFINITIONS
    ]
    if sku_data:
        st.dataframe(pd.DataFrame(sku_data), use_container_width=True)

    st.subheader("🚚 Vehicle Fleet Specifications")
    vehicle_data = [
        {
            'Type': vehicle_spec['type'],
            'Name': vehicle_spec['name'],
            'Weight Capacity (kg)': vehicle_spec['capacity_weight_kg'],
            'Volume Capacity (m³)': vehicle_spec['capacity_volume_m3'],
            'Max Distance (km)': vehicle_spec['max_distance_km'],
            'Cost per km': f"${vehicle_spec['cost_per_km']:.2f}",
            'Fixed Cost': f"${vehicle_spec['fixed_cost']:.2f}",
            'Description': vehicle_spec['description']
        }
        for vehicle_spec in VEHICLE_FLEET_SPECS
    ]
    if vehicle_data:
        st.dataframe(pd.DataFrame(vehicle_data), use_container_width=True)

    st.subheader("🏭 Warehouse Locations")
    warehouse_data = [
        {
            'ID': warehouse['id'],
            'Name': warehouse['name'],
            'Latitude': f"{warehouse['lat']:.4f}",
            'Longitude': f"{warehouse['lon']:.4f}"
        }
        for warehouse in WAREHOUSE_LOCATIONS
    ]
    if warehouse_data:
        st.dataframe(pd.DataFrame(warehouse_data), use_container_width=True)

    st.divider()

    tab1, tab2 = st.tabs(["📋 Demand Configuration", "📦 Supply Configuration"])

    with tab1:
        st.subheader("📋 Demand Configuration")

        num_orders = st.number_input(
            "Number of Orders",
            min_value=5,
            max_value=DEFAULT_SETTINGS.get('max_orders', 50),
            value=DEFAULT_SETTINGS['num_orders'],
            key="main_num_orders",
            help="Total number of customer orders to generate"
        )

        min_items_per_order = st.number_input(
            "Min Items per Order",
            min_value=1,
            max_value=DEFAULT_SETTINGS['max_items_per_order'],
            value=DEFAULT_SETTINGS['min_items_per_order'],
            key="main_min_items_per_order",
            help="Minimum number of items in each order"
        )

        max_items_per_order = st.number_input(
            "Max Items per Order",
            min_value=1,
            max_value=DEFAULT_SETTINGS['max_items_per_order'],
            value=DEFAULT_SETTINGS['max_items_per_order'],
            key="main_max_items_per_order",
            help="Maximum number of items in each order"
        )

        order_dispersion = st.slider(
            "Order Dispersion (km)",
            min_value=DEFAULT_SETTINGS.get('min_dispersion_km', 10),
            max_value=DEFAULT_SETTINGS.get('max_dispersion_km', 300),
            value=DEFAULT_SETTINGS['order_dispersion'],
            step=10,
            key="main_order_dispersion",
            help="How far orders are dispersed from each other (max distance between any two orders)"
        )

        st.subheader("📊 SKU Distribution (%)")
        sku_names = [sku_info['sku_id'] for sku_info in SKU_DEFINITIONS]

        sku_percentages = []
        for i, sku_name in enumerate(sku_names):
            default_val = int(DEFAULT_SETTINGS['default_sku_distribution'][i]) if i < len(DEFAULT_SETTINGS['default_sku_distribution']) else 0
            percentage = st.slider(
                f"{sku_name}",
                min_value=0,
                max_value=100,
                value=default_val,
                step=1,
                key=f"demand_sku_{i}_percentage",
                help=f"Percentage of {sku_name} in total demand"
            )
            sku_percentages.append(percentage)

        st.subheader("📈 Demand SKU Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**SKU Distribution:**")
            for i, sku_name in enumerate(sku_names):
                st.write(f"• {sku_name}: {sku_percentages[i]}%")

        with col2:
            total_percentage = sum(sku_percentages)
            if total_percentage == 100:
                st.success(f"Total: {total_percentage}% (Valid)")
            else:
                st.error(f"Total: {total_percentage}% (Must equal 100%)")


    with tab2:
        st.subheader("📦 Supply Configuration")

        selected_warehouse_indices = []
        default_n = min(DEFAULT_SETTINGS['num_warehouses'], len(WAREHOUSE_LOCATIONS))
        cols = st.columns(3)
        for idx, wh in enumerate(WAREHOUSE_LOCATIONS):
            with cols[idx % 3]:
                use_wh = st.checkbox(
                    f"Use {wh['id']} ({wh['name']})",
                    value=(idx < default_n),
                    key=f"use_wh_{wh['id']}"
                )
                if use_wh:
                    selected_warehouse_indices.append(idx)

        if not selected_warehouse_indices:
            st.error("Please select at least one warehouse")
            st.stop()

        num_warehouses = len(selected_warehouse_indices)
        warehouse_tabs = st.tabs([f"{WAREHOUSE_LOCATIONS[idx]['id']} ({WAREHOUSE_LOCATIONS[idx]['name']})" for idx in selected_warehouse_indices])
        warehouse_configs = []

        for tab_idx, warehouse_idx in enumerate(selected_warehouse_indices):
            with warehouse_tabs[tab_idx]:
                st.write(f"**{WAREHOUSE_LOCATIONS[warehouse_idx]['id']} ({WAREHOUSE_LOCATIONS[warehouse_idx]['name']}) Configuration**")
                
                st.subheader("📦 SKU Inventory Distribution")
                sku_inventory_percentages = []

                for j in range(len(sku_names)):
                    current_key = f"warehouse_{warehouse_idx}_sku_{j}_percentage"
                    default_value = DEFAULT_WAREHOUSE_SKU_ALLOCATIONS[warehouse_idx][j] if warehouse_idx < len(DEFAULT_WAREHOUSE_SKU_ALLOCATIONS) else 0
                    current_value = st.session_state.get(current_key, default_value)
                    percentage = st.slider(
                        f"{sku_names[j]} %",
                        min_value=0,
                        max_value=100,
                        value=int(current_value),
                        step=1,
                        key=current_key,
                        help=f"Percentage of {sku_names[j]} supplied by this warehouse (0-100%, allows overstock)"
                    )
                    sku_inventory_percentages.append(percentage)

                st.write("**📊 SKU Division:**")
                for j, sku_name in enumerate(sku_names):
                    st.write(f"• {sku_name}: {sku_inventory_percentages[j]}% of this SKU's demand")

                st.subheader("🚚 Vehicle Fleet")
                vehicle_counts = {}

                for vehicle_spec in VEHICLE_FLEET_SPECS:
                    vehicle_type = vehicle_spec['type']
                    current_count = DEFAULT_SETTINGS['default_vehicle_counts'].get(vehicle_type, 0)
                    count = st.number_input(
                        f"Number of {vehicle_type}",
                        min_value=0,
                        max_value=DEFAULT_SETTINGS.get('max_vehicles_per_warehouse', 10),
                        value=current_count,
                        key=f"warehouse_{warehouse_idx}_vehicle_{vehicle_type}",
                        help=f"Number of {vehicle_type} vehicles in this warehouse"
                    )
                    vehicle_counts[vehicle_type] = count

                warehouse_configs.append({
                    'sku_inventory_percentages': sku_inventory_percentages,
                    'vehicle_counts': vehicle_counts
                })

        st.subheader("📊 Warehouse Allocation Summary")
        coverage_messages = []
        coverage_ok = True
        for j in range(len(sku_names)):
            sku_demand_percentage = sku_percentages[j]
            total_supply_percentage = sum(cfg['sku_inventory_percentages'][j] for cfg in warehouse_configs)
            effective_supply = (total_supply_percentage / 100.0) * sku_demand_percentage
            
            demand = sku_percentages[j]
            delta = effective_supply - demand
            if delta < 0:
                coverage_ok = False
                coverage_messages.append(f"❌ **{sku_names[j]}**: Understocked by {-delta:.1f}% (Supply {effective_supply:.1f}%, Demand {demand}%)")
            elif delta > 0:
                coverage_messages.append(f"⚠️ **{sku_names[j]}**: Overstocked by {delta:.1f}% (Supply {effective_supply:.1f}%, Demand {demand}%)")

        if coverage_ok:
            st.success("✅ All SKU demand is covered across warehouses (overstock allowed)")
        else:
            for msg in coverage_messages:
                st.markdown(msg)

    st.divider()

    st.header("⚙️ Configuration Summary")
    summary_col1, summary_col2, summary_col3 = st.columns(3)

    with summary_col1:
        st.metric("Orders", num_orders)
        st.metric("Warehouses", num_warehouses)
        st.metric("Dispersion", f"{order_dispersion} km")

        st.write("**🚚 Vehicle Fleet:**")
        vehicle_type_counts = {}
        for config in warehouse_configs:
            for vehicle_type, count in config['vehicle_counts'].items():
                vehicle_type_counts[vehicle_type] = vehicle_type_counts.get(vehicle_type, 0) + count
        for vehicle_type, count in vehicle_type_counts.items():
            if count > 0:
                st.write(f"• {vehicle_type}: {count}")

    with summary_col2:
        st.write("**📦 Inventory Coverage by SKU:**")
        for j, sku_name in enumerate(sku_names):
            sku_demand = sku_percentages[j]
            total_supply_percentage = sum(cfg['sku_inventory_percentages'][j]
                                           for i, cfg in enumerate(warehouse_configs) if selected_warehouse_indices[i] < len(DEFAULT_WAREHOUSE_SKU_ALLOCATIONS))
            effective_supply = (total_supply_percentage / 100.0) * sku_demand
            
            warehouse_splits = []
            for i, config in enumerate(warehouse_configs):
                if config['sku_inventory_percentages'][j] > 0:
                    warehouse_idx = selected_warehouse_indices[i]
                    warehouse_name = WAREHOUSE_LOCATIONS[warehouse_idx]['name']
                    warehouse_splits.append(f"{warehouse_name}: {config['sku_inventory_percentages'][j]}%")
            
            if effective_supply >= sku_demand:
                if effective_supply == sku_demand:
                    status = f"✅ Perfect Match ({effective_supply:.1f}% of {sku_demand}% demand)"
                else:
                    overstock = effective_supply - sku_demand
                    status = f"⚠️ Overstocked by {overstock:.1f}% ({effective_supply:.1f}% of {sku_demand}% demand)"
            else:
                understock = sku_demand - effective_supply
                status = f"❌ Understocked by {understock:.1f}% ({effective_supply:.1f}% of {sku_demand}% demand)"
            
            st.write(f"• {sku_name}: {status}")
            if warehouse_splits:
                st.write(f"  └─ Supply: {', '.join(warehouse_splits)}")

    with summary_col3:
        st.write("**Configuration Status:**")
        all_valid = True
        validation_messages = []
        for j, sku_name in enumerate(sku_names):
            sku_demand = sku_percentages[j]
            total_supply_percentage = sum(cfg['sku_inventory_percentages'][j]
                                          for i, cfg in enumerate(warehouse_configs) if selected_warehouse_indices[i] < len(DEFAULT_WAREHOUSE_SKU_ALLOCATIONS))
            effective_supply = (total_supply_percentage / 100.0) * sku_demand
            if effective_supply < sku_demand:
                all_valid = False
                validation_messages.append(f"❌ **{sku_name}**: Supply {effective_supply:.1f}% < Demand {sku_demand}%")

        if all_valid:
            st.success("✅ Configuration Valid - All SKU demand is covered")
        else:
            st.error("❌ Configuration Invalid - Some SKU demand is not covered")
            for msg in validation_messages:
                st.markdown(msg)

    st.divider()
    st.subheader("🎲 Seed Control")
    
    use_seed = st.checkbox("🔒 Use Fixed Seed (Reproducible results)", help="Check to use a fixed seed for consistent results")
    
    if use_seed:
        seed_value = st.number_input(
            "Seed Value",
            min_value=1,
            max_value=999999,
            value=42,
            help="Enter a seed value for reproducible results"
        )
    else:
        seed_value = None

    if st.button("Run Simulation", type="primary", key="run_sim"):
        st.info("⚙️ Configuration captured! Updating vehicle fleet and running solver...")
        st.info("🔄 Regenerating environment with new demand configuration...")

        custom_config = {
            'num_orders': num_orders,
            'min_items_per_order': min_items_per_order,
            'max_items_per_order': max_items_per_order,
            'order_dispersion': order_dispersion,
            'sku_percentages': sku_percentages,
            'warehouse_configs': warehouse_configs,
            'num_warehouses': num_warehouses,
            'random_seed': seed_value if use_seed else None
        }

        try:
            class BaseConfig:
                SKU_DEFINITIONS = config_module.SKU_DEFINITIONS
                WAREHOUSE_LOCATIONS = config_module.WAREHOUSE_LOCATIONS
                VEHICLE_FLEET_SPECS = config_module.VEHICLE_FLEET_SPECS
                DEFAULT_SETTINGS = config_module.DEFAULT_SETTINGS

            base_config = BaseConfig()

            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            nodes_df = pd.read_csv(os.path.join(data_dir, 'nodes.csv'))
            edges_df = pd.read_csv(os.path.join(data_dir, 'edges.csv'))

            scenario_data = generate_scenario_from_config(
                base_config,
                nodes_df,
                edges_df,
                custom_config
            )
            
            env = LogisticsEnvironment()
            env.generate_scenario_from_config(custom_config)

            st.session_state['env'] = env
            st.success("✅ Environment regenerated successfully!")

            solution = current_solver(env)
            if solution and solution.get('routes'):
                st.success("🎯 Solver completed successfully!")
                st.session_state['solution'] = solution
            else:
                st.error("❌ Solver failed or returned no routes")
                st.session_state['solution'] = None

        except Exception as e:
            st.error(f"💥 An error occurred during simulation: {str(e)}")
            st.error(f"Exception type: {type(e).__name__}")
            st.error(f"Full traceback: {traceback.format_exc()}")
            st.session_state['solution'] = None

    # After the button logic, check for the solution to display analysis
    if st.session_state.get('solution'):
        solution = st.session_state['solution']
        env = st.session_state['env']
        st.divider()
        st.subheader("Solution Analysis")

        tab1, tab2, tab3 = st.tabs([
            "📊 Solution Overview",
            "📦 Supply & Demand Management",
            "🚛 Route Optimization"
        ])

        with tab1:
            st.subheader("📊 Solution Overview")
            
            # Display current seed information
            current_seed = env.get_current_seed()
            if current_seed is not None:
                st.info(f"🔒 **Current Seed**: {current_seed} (Reproducible results)")
            else:
                st.info("🔀 **Current Seed**: Random (New scenario each time)")
            
                        # SOLUTION VALIDATION
            st.write("🔍 **SOLUTION VALIDATION**")
            
            # Validate solution business logic
            is_valid_logic, logic_error = env.validate_solution_business_logic(solution)
            if is_valid_logic:
                st.success("✅ Business Logic: Valid")
            else:
                st.error(f"❌ Business Logic: {logic_error}")
            
            # Validate complete solution
            is_valid_complete, complete_error = env.validate_solution_complete(solution)
            if is_valid_complete:
                st.success("✅ Complete Solution: Valid")
            else:
                st.error(f"❌ Complete Solution: {complete_error}")
            
            # Get solution statistics
            stats = env.get_solution_statistics(solution)
            st.write("📊 **Solution Statistics**")
            st.write(f"Total Routes: {stats.get('total_routes', 0)}")
            st.write(f"Unique Orders Served: {stats.get('unique_orders_served', 0)}")
            st.write(f"Unique Vehicles Used: {stats.get('unique_vehicles_used', 0)}")
            st.write(f"Orders Fulfillment: {stats.get('orders_fulfillment_ratio', 0):.1%}")
            st.write(f"Vehicle Utilization: {stats.get('vehicle_utilization_ratio', 0):.1%}")
            
            # Use validated statistics for metrics
            total_routes = stats.get('total_routes', 0)
            total_distance = stats.get('total_distance', 0)
            orders_served = stats.get('unique_orders_served', 0)
            total_cost = stats.get('total_cost', 0)
            total_orders = env.num_orders
            
            # Calculate derived metrics
            avg_cost_per_order = total_cost / orders_served if orders_served > 0 else 0
            avg_distance_per_order = total_distance / orders_served if orders_served > 0 else 0
            fulfillment_ratio = (orders_served / total_orders * 100) if total_orders > 0 else 0
            total_vehicles = sum(len(wh.vehicles) for wh in env.warehouses.values())
            vehicle_utilization = (total_routes / total_vehicles * 100) if total_vehicles > 0 else 0

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Cost", f"${total_cost:.2f}")
                st.caption(f"Avg: ${avg_cost_per_order:.2f}/order")
            with col2:
                st.metric("Total Distance", f"{total_distance:.2f} km")
                st.caption(f"Avg: {avg_distance_per_order:.2f} km/order")
            with col3:
                st.metric("Orders Served", f"{orders_served}/{total_orders}")
                st.caption(f"Fulfillment: {fulfillment_ratio:.1f}%")
            with col4:
                st.metric("Active Vehicles", total_routes)
                st.caption(f"Utilization: {vehicle_utilization:.1f}%")

            if total_routes > 0:
                st.divider()
                st.write("🚚 Route Distribution by Vehicle Type")
                vehicle_type_counts = {}
                vehicle_type_distances = {}
                for route in solution['routes']:
                    vehicle_id = route['vehicle_id']
                    vehicle_type = vehicle_id.split('_')[0]
                    distance = route.get('distance', 0)
                    vehicle_type_counts[vehicle_type] = vehicle_type_counts.get(vehicle_type, 0) + 1
                    if vehicle_type not in vehicle_type_distances:
                        vehicle_type_distances[vehicle_type] = {'total_distance': 0, 'count': 0}
                    vehicle_type_distances[vehicle_type]['total_distance'] += distance
                    vehicle_type_distances[vehicle_type]['count'] += 1

                if vehicle_type_counts:
                    cols = st.columns(len(vehicle_type_counts))
                    for i, (vehicle_type, count) in enumerate(vehicle_type_counts.items()):
                        with cols[i]:
                            st.metric(vehicle_type, count)
                    
                    st.divider()
                    st.write("📏 Average Distance by Vehicle Type:")
                    cols = st.columns(len(vehicle_type_distances))
                    for i, (vehicle_type, data) in enumerate(vehicle_type_distances.items()):
                        with cols[i]:
                            avg_dist = data['total_distance'] / data['count'] if data['count'] > 0 else 0
                            st.metric(f"{vehicle_type} Avg", f"{avg_dist:.2f} km")
                
                # Add overall solution map to Solution Overview tab
                st.divider()
                st.subheader("🗺️ Overall Solution Map")
                
                if env.warehouses and env.orders:
                    # Calculate map center
                    all_lats = [wh.location.lat for wh in env.warehouses.values()] + [order.destination.lat for order in env.orders.values()]
                    all_lons = [wh.location.lon for wh in env.warehouses.values()] + [order.destination.lon for order in env.orders.values()]
                    
                    center_lat = sum(all_lats) / len(all_lats)
                    center_lon = sum(all_lons) / len(all_lons)
                    
                    # Create map
                    m = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=DEFAULT_SETTINGS.get('map_zoom_start', 10)
                    )
                    
                    # Add warehouses
                    for warehouse in env.warehouses.values():
                        folium.Marker(
                            [warehouse.location.lat, warehouse.location.lon],
                            popup=f"Warehouse {warehouse.id}",
                            icon=folium.Icon(color='red', icon='warehouse')
                        ).add_to(m)
                    
                    # Add orders
                    for order_id, order in env.orders.items():
                        folium.Marker(
                            [order.destination.lat, order.destination.lon],
                            popup=f"Order {order_id}",
                            icon=folium.Icon(color='blue', icon='info-sign')
                        ).add_to(m)
                    
                    # Add all routes with different colors per vehicle type
                    if solution and 'routes' in solution:
                        vehicle_types = {}
                        for route in solution['routes']:
                            vehicle_id = route['vehicle_id']
                            vehicle_type = vehicle_id.split('_')[0]
                            if vehicle_type not in vehicle_types:
                                vehicle_types[vehicle_type] = []
                            vehicle_types[vehicle_type].append(vehicle_id)
                        
                        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'darkblue', 'darkgreen']
                        
                        for i, route in enumerate(solution['routes']):
                            vehicle_id = route['vehicle_id']
                            vehicle_type = vehicle_id.split('_')[0]
                            color_idx = list(vehicle_types.keys()).index(vehicle_type) % len(colors)
                            color = colors[color_idx]
                            
                            route_coords = []
                            for node_id in route['route']:
                                if node_id in env.nodes:
                                    node = env.nodes[node_id]
                                    route_coords.append([node.lat, node.lon])
                                elif node_id in env.warehouses:
                                    warehouse = env.warehouses[node_id]
                                    route_coords.append([warehouse.location.lat, warehouse.location.lon])
                                elif node_id in env.orders:
                                    order = env.orders[node_id]
                                    route_coords.append([order.destination.lat, order.destination.lon])
                            
                            if len(route_coords) >= 2:
                                folium.PolyLine(
                                    route_coords,
                                    color=color,
                                    weight=3,
                                    opacity=0.8,
                                    popup=f"Route {i+1}: {vehicle_id} ({route.get('distance', 0):.1f} km)"
                                ).add_to(m)
                                
                                # Add route markers
                                for j, coord in enumerate(route_coords):
                                    if j == 0:
                                        folium.CircleMarker(
                                            coord,
                                            radius=8,
                                            color=color,
                                            fill=True,
                                            popup=f"Start: {vehicle_id}"
                                        ).add_to(m)
                                    elif j == len(route_coords) - 1:
                                        folium.CircleMarker(
                                            coord,
                                            radius=8,
                                            color=color,
                                            fill=True,
                                            popup=f"End: {vehicle_id}"
                                        ).add_to(m)
                                    else:
                                        folium.CircleMarker(
                                            coord,
                                            radius=6,
                                            color=color,
                                            fill=True,
                                            popup=f"Order {route.get('order_id', 'Unknown')}"
                                        ).add_to(m)
                        
                        # Add legend
                        legend_html = '''
                        <div style="position: fixed; 
                                    bottom: 50px; left: 50px; width: 200px; height: auto; 
                                    background-color: white; border:2px solid grey; z-index:9999; 
                                    font-size:14px; padding: 10px; border-radius: 5px;">
                        <p><b>Vehicle Routes</b></p>
                        '''
                        
                        for i, (vehicle_type, vehicle_ids) in enumerate(vehicle_types.items()):
                            color = colors[i % len(colors)]
                            legend_html += f'<p><i class="fa fa-circle" style="color:{color}"></i> {vehicle_type}</p>'
                        
                        legend_html += '</div>'
                        m.get_root().html.add_child(folium.Element(legend_html))
                    
                    # Display map
                    st.markdown("""
                        <style>
                        .map-container {
                            width: 100% !important;
                            max-width: none !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                    
                    with st.container():
                        st.components.v1.html(m._repr_html_(), height=600, scrolling=False)
                else:
                    st.info("No location data available for map visualization.")

        with tab2:
            st.subheader("📦 Inventory Management")
            st.write("📊 SKU Distribution Across Warehouses:")
            sku_distribution = {}
            for warehouse in env.warehouses.values():
                for sku_id, quantity in warehouse.inventory.items():
                    sku_distribution.setdefault(sku_id, {})[warehouse.id] = quantity
            if sku_distribution:
                warehouse_ids = [wh.id for wh in env.warehouses.values()]
                sku_data = [{'SKU': sku_id, **{wh_id: warehouse_data.get(wh_id, 0) for wh_id in warehouse_ids}} for sku_id, warehouse_data in sku_distribution.items()]
                st.dataframe(pd.DataFrame(sku_data), use_container_width=True)

            st.divider()
            st.subheader("📋 Order Item Counts by SKU")
            actual_sku_counts = {}
            total_items = 0
            for order in env.orders.values():
                for sku_id, quantity in order.requested_items.items():
                    actual_sku_counts.setdefault(sku_id, 0)
                    actual_sku_counts[sku_id] += quantity
                    total_items += quantity
            
            if actual_sku_counts:
                comparison_data = []
                for sku_name in sku_names:
                    actual_count = actual_sku_counts.get(sku_name, 0)
                    actual_pct = (actual_count / total_items * 100) if total_items > 0 else 0
                    comparison_data.append({
                        'SKU': sku_name,
                        'Count': actual_count,
                        'Percentage': f"{actual_pct:.1f}%"
                    })
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
                st.write(f"**Total Items Generated:** {total_items}")
                st.write(f"**Total Orders:** {len(env.orders)}")
            else:
                st.info("No order data available for SKU analysis.")
            
            st.divider()
            st.subheader("📋 Overall Orders Status")
            
            # Create orders overview table
            orders_data = []
            for order_id, order in env.orders.items():
                # Find which vehicle serves this order
                serving_vehicle = None
                delivery_cost = 0
                for route in solution['routes']:
                    if 'order_id' in route and route['order_id'] == order_id:
                        serving_vehicle = route['vehicle_id']
                        # Calculate delivery cost
                        vehicle_type = serving_vehicle.split('_')[0]
                        vehicle_specs = next((spec for spec in VEHICLE_FLEET_SPECS if spec['type'] == vehicle_type), None)
                        if vehicle_specs:
                            distance = route.get('distance', 0)
                            delivery_cost = (vehicle_specs['cost_per_km'] * distance) + vehicle_specs['fixed_cost']
                        break
                
                # Calculate order totals
                total_items = sum(order.requested_items.values())
                total_weight = sum(sku_info['weight_kg'] * quantity for sku_id_val, quantity in order.requested_items.items() for sku_info in SKU_DEFINITIONS if sku_info['sku_id'] == sku_id_val)
                total_volume = sum(sku_info['volume_m3'] * quantity for sku_id_val, quantity in order.requested_items.items() for sku_info in SKU_DEFINITIONS if sku_info['sku_id'] == sku_id_val)
                
                orders_data.append({
                    'Order ID': order_id,
                    'Status': 'Fulfilled' if serving_vehicle else 'Unfulfilled',
                    'Vehicle': serving_vehicle if serving_vehicle else 'N/A',
                    'Node ID': order.destination.id if hasattr(order, 'destination') and hasattr(order.destination, 'id') else 'N/A',
                    'Location': f"({order.destination.lat:.4f}, {order.destination.lon:.4f})" if hasattr(order, 'destination') else 'N/A',
                    'Total Items': total_items,
                    'Total Weight (kg)': f"{total_weight:.1f}",
                    'Total Volume (m³)': f"{total_volume:.3f}",
                    'Delivery Cost ($)': f"${delivery_cost:.2f}" if delivery_cost > 0 else 'N/A'
                })
            
            if orders_data:
                st.dataframe(pd.DataFrame(orders_data), use_container_width=True)
                
                # Order selection dropdown for detailed view
                st.write("**📦 Select Order to View SKU Details:**")
                order_options = [order['Order ID'] for order in orders_data]
                selected_order_detail = st.selectbox(
                    "Choose Order:",
                    options=order_options,
                    key="order_detail_select"
                )
                
                if selected_order_detail in env.orders:
                    selected_order = env.orders[selected_order_detail]
                    st.write(f"**📋 Order {selected_order_detail} SKU Breakdown:**")
                    
                    order_sku_data = []
                    for sku_id_val, quantity in selected_order.requested_items.items():
                        sku_info = next((sku for sku in SKU_DEFINITIONS if sku['sku_id'] == sku_id_val), None)
                        if sku_info:
                            order_sku_data.append({
                                'SKU': sku_id_val,
                                'Quantity': quantity,
                                'Weight (kg)': f"{sku_info['weight_kg'] * quantity:.1f}",
                                'Volume (m³)': f"{sku_info['volume_m3'] * quantity:.3f}"
                            })
                    
                    if order_sku_data:
                        st.dataframe(pd.DataFrame(order_sku_data), use_container_width=True)
            else:
                st.info("No orders available for analysis.")

        with tab3:
            st.subheader("🚛 Route Optimization")
            vehicle_options = [route['vehicle_id'] for route in solution['routes']]
            if not vehicle_options:
                st.info("No routes were generated by the solver.")
                st.stop()

            selected_vehicle = st.selectbox(
                "🚚 Select Vehicle to Analyze:",
                options=vehicle_options,
                key="selected_vehicle_analysis"
            )
            
            if selected_vehicle and env.warehouses and env.orders:
                selected_route = next((route for route in solution['routes'] if route['vehicle_id'] == selected_vehicle), None)
                
                if selected_route:
                    vehicle_id = selected_vehicle
                    vehicle_type = vehicle_id.split('_')[0]
                    order_id = selected_route['order_id']
                    route_nodes = selected_route['route']
                    distance = selected_route.get('distance', 0)
                    
                    vehicle_specs = next((spec for spec in VEHICLE_FLEET_SPECS if spec['type'] == vehicle_type), None)
                    

                    
                    st.subheader("🗺️ Route Map")
                    all_lats = [wh.location.lat for wh in env.warehouses.values()] + [order.destination.lat for order in env.orders.values()]
                    all_lons = [wh.location.lon for wh in env.warehouses.values()] + [order.destination.lon for order in env.orders.values()]
                    
                    center_lat = sum(all_lats) / len(all_lats)
                    center_lon = sum(all_lons) / len(all_lons)
                    
                    m = folium.Map(
                        location=[center_lat, center_lon],
                        zoom_start=DEFAULT_SETTINGS.get('map_zoom_start', 10)
                    )
                    
                    for warehouse in env.warehouses.values():
                        folium.Marker([warehouse.location.lat, warehouse.location.lon], popup=f"Warehouse {warehouse.id}", icon=folium.Icon(color='red', icon='warehouse')).add_to(m)
                    
                    for order_id_val, order in env.orders.items():
                        folium.Marker([order.destination.lat, order.destination.lon], popup=f"Order {order_id_val}", icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)
                    
                    route_coords = []
                    for node_id in route_nodes:
                        if node_id in env.nodes:
                            node = env.nodes[node_id]
                            route_coords.append([node.lat, node.lon])
                        elif node_id in env.warehouses:
                            warehouse = env.warehouses[node_id]
                            route_coords.append([warehouse.location.lat, warehouse.location.lon])
                        elif node_id in env.orders:
                            order_node = env.orders[node_id]
                            route_coords.append([order_node.destination.lat, order_node.destination.lon])
                    
                    if len(route_coords) >= 2:
                        folium.PolyLine(route_coords, color='green', weight=5, opacity=0.8, popup=f"Route: {vehicle_id} ({distance:.1f} km)").add_to(m)
                        
                        for j, coord in enumerate(route_coords):
                            color_marker = 'green'
                            if j == 0 or j == len(route_coords) - 1:
                                folium.CircleMarker(coord, radius=10, color=color_marker, fill=True, popup=f"Depot {route_nodes[j]}").add_to(m)
                            else:
                                folium.CircleMarker(coord, radius=8, color=color_marker, fill=True, popup=f"Order {route_nodes[j]}").add_to(m)
                    
                    legend_html = '''
                    <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: 90px;
                                background-color: white; border:2px solid grey; z-index:9999;
                                font-size:14px; padding: 10px; border-radius: 5px;">
                    <p><b>Route Legend</b></p>
                    <p><i class="fa fa-circle" style="color:red"></i> Warehouse</p>
                    <p><i class="fa fa-circle" style="color:blue"></i> Order</p>
                    <p><i class="fa fa-circle" style="color:green"></i> Selected Route</p>
                    </div>
                    '''
                    m.get_root().html.add_child(folium.Element(legend_html))
                    st.components.v1.html(m._repr_html_(), height=500, scrolling=False)
                    
                    # Get all orders in this route (supports any solver output format)
                    route_orders = []
                    
                    # Check for direct order_id field (single order per route)
                    if 'order_id' in selected_route:
                        route_orders.append(selected_route['order_id'])
                    
                    # Check for order_ids field (multiple orders per route)
                    elif 'order_ids' in selected_route:
                        route_orders.extend(selected_route['order_ids'])
                    
                    # Check if route nodes contain order IDs
                    for node_id in route_nodes:
                        if node_id in env.orders:
                            route_orders.append(node_id)
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_route_orders = []
                    for order_id in route_orders:
                        if order_id not in seen:
                            seen.add(order_id)
                            unique_route_orders.append(order_id)
                    route_orders = unique_route_orders
                    
                    st.subheader("📊 Route Overview")
                    if vehicle_specs and route_orders:
                        total_weight = 0
                        total_volume = 0
                        total_items = 0
                        all_sku_breakdown = {}
                        
                        for route_order_id in route_orders:
                            if route_order_id in env.orders:
                                order = env.orders[route_order_id]
                                order_weight, order_volume = env.get_order_requirements(route_order_id)
                                order_items = sum(order.requested_items.values())
                                
                                total_weight += order_weight
                                total_volume += order_volume
                                total_items += order_items
                                
                                for sku_id_val, quantity in order.requested_items.items():
                                    if sku_id_val not in all_sku_breakdown:
                                        all_sku_breakdown[sku_id_val] = 0
                                    all_sku_breakdown[sku_id_val] += quantity
                        
                        total_distance = 0
                        total_cost = 0
                        if len(route_nodes) > 1:
                            for i in range(len(route_nodes) - 1):
                                node1, node2 = route_nodes[i], route_nodes[i + 1]
                                try:
                                    leg_distance = env.get_distance(node1, node2) or 0.0
                                except KeyError:
                                    loc1 = env.warehouses.get(node1) or (env.orders.get(node1) and env.orders[node1].destination)
                                    loc2 = env.warehouses.get(node2) or (env.orders.get(node2) and env.orders[node2].destination)
                                    if loc1 and loc2:
                                        leg_distance = ((loc1.lat - loc2.lat)**2 + (loc1.lon - loc2.lon)**2)**0.5 * 111.32
                                    else:
                                        leg_distance = 0.0
                                
                                total_distance += leg_distance
                                if vehicle_specs:
                                    leg_cost = leg_distance * vehicle_specs['cost_per_km']
                                    total_cost += leg_cost
                            if vehicle_specs:
                                total_cost += vehicle_specs['fixed_cost']
                        
                        col1, col2 = st.columns(2)
                        with col1: st.metric("💰 Total Route Cost", f"${total_cost:.2f}")
                        with col2: st.metric("📊 Cost per Order", f"${total_cost / len(route_orders):.2f}" if len(route_orders) > 0 else "$0.00")
                        
                        st.divider()
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1: 
                            st.metric("📦 Orders", len(route_orders))
                            if len(route_orders) > 1:
                                st.caption(f"Multi-order route")
                        with col2: st.metric("⚖️ Total Weight", f"{total_weight:.1f} kg")
                        with col3: st.metric("📏 Total Volume", f"{total_volume:.3f} m³")
                        with col4: st.metric("🛣️ Total Distance", f"{total_distance:.2f} km")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1: st.metric("📦 Total Items", total_items)
                        with col2:
                            if vehicle_specs:
                                weight_utilization = (total_weight / vehicle_specs['capacity_weight_kg'] * 100) if vehicle_specs['capacity_weight_kg'] > 0 else 0
                                st.metric("📊 Weight Utilization", f"{weight_utilization:.1f}%")
                        with col3:
                            if vehicle_specs:
                                volume_utilization = (total_volume / vehicle_specs['capacity_volume_m3'] * 100) if vehicle_specs['capacity_volume_m3'] > 0 else 0
                                st.metric("📏 Volume Utilization", f"{volume_utilization:.1f}%")
                        with col4:
                            if vehicle_specs:
                                max_distance = vehicle_specs.get('max_distance_km', 1000)
                                vehicle_utilization = (total_distance / max_distance * 100) if max_distance > 0 else 0
                                st.metric("🚚 Vehicle Utilization", f"{vehicle_utilization:.1f}%")


                    st.subheader("📈 Load & Cost Progression")
                    if vehicle_specs and route_orders:
                        progression_data = []
                        initial_weight = 0
                        initial_volume = 0
                        for route_order_id in route_orders:
                            if route_order_id in env.orders:
                                order_weight, order_volume = env.get_order_requirements(route_order_id)
                                initial_weight += order_weight
                                initial_volume += order_volume
                        
                        current_weight = initial_weight
                        current_volume = initial_volume
                        cumulative_cost = 0
                        
                        for j, node_id in enumerate(route_nodes):
                            leg_distance = 0.0
                            leg_cost = 0.0
                            if j < len(route_nodes) - 1:
                                next_node_id = route_nodes[j + 1]
                                try:
                                    leg_distance = env.get_distance(node_id, next_node_id) or 0.0
                                except KeyError:
                                    loc1 = env.warehouses.get(node_id) or (env.orders.get(node_id) and env.orders[node_id].destination)
                                    loc2 = env.warehouses.get(next_node_id) or (env.orders.get(next_node_id) and env.orders[next_node_id].destination)
                                    if loc1 and loc2:
                                        leg_distance = ((loc1.lat - loc2.lat)**2 + (loc1.lon - loc2.lon)**2)**0.5 * 111.32
                            
                            leg_cost = (vehicle_specs['cost_per_km'] * leg_distance) + (vehicle_specs['fixed_cost'] if j == 0 else 0)
                            
                            if j == 0:
                                node_type = "Warehouse (Start)"
                                load_change = "Pickup load"
                                weight_after = current_weight
                                volume_after = current_volume
                            elif j == len(route_nodes) - 1:
                                node_type = "Warehouse (Return)"
                                load_change = "Unload remaining"
                                weight_after = 0
                                volume_after = 0
                                current_weight = 0
                                current_volume = 0
                            elif node_id in env.orders:
                                node_type = f"Delivery - Order {node_id}"
                                load_change = "Deliver order"
                                order_weight, order_volume = env.get_order_requirements(node_id)
                                current_weight -= order_weight
                                current_volume -= order_volume
                                weight_after = current_weight
                                volume_after = current_volume
                            elif node_id in env.warehouses and j > 0:
                                node_type = f"Inventory Pickup - Warehouse {node_id}"
                                load_change = "Pickup additional inventory"
                                weight_after = current_weight
                                volume_after = current_volume
                            else:
                                is_order_destination = False
                                for oid, order in env.orders.items():
                                    if hasattr(order, 'destination') and hasattr(order.destination, 'id') and order.destination.id == node_id:
                                        is_order_destination = True
                                        break
                                
                                if is_order_destination:
                                    node_type = f"Delivery - Order Destination"
                                    load_change = "Deliver order"
                                    order_weight, order_volume = env.get_order_requirements(oid)
                                    current_weight -= order_weight
                                    current_volume -= order_volume
                                    weight_after = current_weight
                                    volume_after = current_volume
                                else:
                                    node_type = "Path Node"
                                    load_change = "In transit"
                                    weight_after = current_weight
                                    volume_after = current_volume
                            
                            cumulative_cost += leg_cost
                            
                            node_loc = env.nodes.get(node_id) or env.warehouses.get(node_id) or (env.orders.get(node_id) and env.orders[node_id].destination)
                            coordinates = f"({node_loc.lat:.4f}, {node_loc.lon:.4f})" if node_loc else "N/A"
                            
                            progression_data.append({
                                'Step': j + 1,
                                'Node ID': node_id,
                                'Node Type': node_type,
                                'Coordinates': coordinates,
                                'Load Change': load_change,
                                'Weight (kg)': f"{weight_after:.1f}",
                                'Volume (m³)': f"{volume_after:.3f}",
                                'Leg Distance (km)': f"{leg_distance:.2f}",
                                'Leg Cost ($)': f"{leg_cost:.2f}",
                                'Cumulative Cost ($)': f"{cumulative_cost:.2f}"
                            })
                        
                        progression_df = pd.DataFrame(progression_data)
                        st.dataframe(progression_df, use_container_width=True)

    # The rest of the script for the static map and "How to Use" section remains unchanged
    st.divider()
    st.header("📖 How to Use")
    st.write("""
    1. **🏗️ Review Infrastructure**: Examine the fixed SKU types, vehicle fleet, and warehouse locations above
    2. **📋 Configure Demand**: Set order count, items per order, and SKU distribution in the Demand tab
    3. **📦 Configure Supply**: Set inventory distribution and vehicle fleet for each warehouse in the Supply tab
    4. **🚀 Run Simulation**: Click "Run Simulation" to generate and solve the problem
    5. **📊 Analyze Results**: The comprehensive dashboard will open with detailed analysis tabs

    **💡 Tip**: Start with smaller problems (5-10 orders) to test your solver, then scale up!
    """)

    # Overall solution map is now shown in the Solution Overview tab - no need for duplicate here

if __name__ == "__main__":
    if 'env' not in st.session_state or st.session_state.get('env') is None:
        try:
            st.session_state['env'] = LogisticsEnvironment()
        except Exception as e:
            st.error(f"Failed to create environment: {str(e)}")
            st.stop()

    if 'solution' not in st.session_state:
        st.session_state['solution'] = None

    run_dashboard(st.session_state['env'])