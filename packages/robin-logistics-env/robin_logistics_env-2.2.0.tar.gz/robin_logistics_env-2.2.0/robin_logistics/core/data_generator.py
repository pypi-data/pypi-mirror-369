"""Data generation utilities for the multi-depot vehicle routing problem."""

import random
import pandas as pd
from .models.node import Node
from .models.sku import SKU
from .models.order import Order
from .models.vehicle import Vehicle
from .models.warehouse import Warehouse


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    import math
    
    R = 6371
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def _generate_orders_with_dispersion(custom_config, warehouses, skus, all_node_ids, nodes_df, max_dispersion_km):
    """Generate orders with dispersion constraints."""
    orders = []
    num_orders = custom_config.get('num_orders', 15)
    min_items = custom_config.get('min_items_per_order', 3)
    max_items = custom_config.get('max_items_per_order', 8)
    
    warehouse_locations = []
    for warehouse in warehouses:
        warehouse_locations.append((warehouse.location.lat, warehouse.location.lon))
    
    available_nodes = []
    for node_id in all_node_ids:
        node_row = nodes_df[nodes_df['node_id'] == node_id].iloc[0]
        node_lat, node_lon = node_row['lat'], node_row['lon']
        
        within_range = False
        for wh_lat, wh_lon in warehouse_locations:
            distance = calculate_distance(node_lat, node_lon, wh_lat, wh_lon)
            if distance <= max_dispersion_km:
                within_range = True
                break
        
        if within_range:
            available_nodes.append(node_id)
    
    if len(available_nodes) < num_orders:
        available_nodes = list(all_node_ids)
    
    customer_nodes = random.sample(available_nodes, min(num_orders, len(available_nodes)))
    
    for i, node_id in enumerate(customer_nodes):
        node_row = nodes_df[nodes_df['node_id'] == node_id].iloc[0]
        dest_node = Node(int(node_id), float(node_row['lat']), float(node_row['lon']))
        
        order = Order(f"ORD-{i+1}", dest_node)
        
        num_skus = random.randint(min_items, max_items)
        selected_skus = random.sample(skus, min(num_skus, len(skus)))
        
        sku_percentages = custom_config.get('sku_percentages', [33.33, 33.33, 33.34])
        
        for j, sku in enumerate(selected_skus):
            if j < len(sku_percentages):
                # Honor zero-demand by allowing zero quantity
                base_quantity = int(sku_percentages[j] / 10)
                if base_quantity <= 0:
                    quantity = 0
                else:
                    quantity = random.randint(base_quantity, base_quantity * 2)
                if quantity > 0:
                    order.requested_items[sku.id] = quantity
        
        orders.append(order)
    
    return orders


def generate_scenario_from_config(base_config, nodes_df_raw, edges_df_raw, custom_config):
    """Generate problem instance from dashboard configuration."""
    nodes_df = nodes_df_raw.copy()
    nodes_df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)

    all_node_ids = set(nodes_df['node_id'].tolist())

    existing_edges = []
    if edges_df_raw is not None and not edges_df_raw.empty:
        edges_df = edges_df_raw.copy()

        if 'u' in edges_df.columns and 'v' in edges_df.columns:
            edges_df.rename(columns={'u': 'start_node', 'v': 'end_node'}, inplace=True)

        for _, edge in edges_df.iterrows():
            start_node = int(edge['start_node'])
            end_node = int(edge['end_node'])

            if 'length' in edges_df.columns:
                distance_km = float(edge['length']) / 1000
            elif 'distance_km' in edges_df.columns:
                distance_km = float(edge['distance_km'])
            else:
                if start_node in nodes_df['node_id'].values and end_node in nodes_df['node_id'].values:
                    start_row = nodes_df[nodes_df['node_id'] == start_node].iloc[0]
                    end_row = nodes_df[nodes_df['node_id'] == end_node].iloc[0]
                    distance_km = calculate_distance(start_row['lat'], start_row['lon'],
                                                     end_row['lat'], end_row['lon'])
                else:
                    continue

            existing_edges.append({
                'start_node': start_node,
                'end_node': end_node,
                'distance_km': distance_km
            })

    # Determine node connectivity (directed): nodes with outgoing and incoming edges
    outgoing_node_ids = set()
    incoming_node_ids = set()
    for edge in existing_edges:
        outgoing_node_ids.add(edge['start_node'])
        incoming_node_ids.add(edge['end_node'])
    # Prefer nodes that have both incoming and outgoing edges for depot/destination placement
    bidirectional_candidate_nodes = outgoing_node_ids.intersection(incoming_node_ids)

    # Use existing edges directly - no artificial connectivity needed
    all_edges = existing_edges

    nodes_df_final = nodes_df[['node_id', 'lat', 'lon']].copy()
    edges_df_final = pd.DataFrame(all_edges)

    nodes = []
    for _, row in nodes_df_final.iterrows():
        nodes.append(Node(int(row['node_id']), float(row['lat']), float(row['lon'])))

    skus = []
    for s in base_config.SKU_DEFINITIONS:
        try:
            sku = SKU(
                sku_id=s['sku_id'],
                weight_kg=s['weight_kg'],
                volume_m3=s['volume_m3']
            )
            skus.append(sku)
        except Exception:
            continue

    warehouses = []
    num_warehouses = custom_config.get('num_warehouses', len(base_config.WAREHOUSE_LOCATIONS))
    num_warehouses_to_use = min(num_warehouses, len(base_config.WAREHOUSE_LOCATIONS))
    
    used_nodes = set()  # Track nodes already used by warehouses
    
    for i in range(num_warehouses_to_use):
        wh_id = base_config.WAREHOUSE_LOCATIONS[i]['id']
        wh_lat = base_config.WAREHOUSE_LOCATIONS[i]['lat']
        wh_lon = base_config.WAREHOUSE_LOCATIONS[i]['lon']

        closest_node = None
        min_distance = float('inf')

        for node in nodes:
            # Skip nodes already used by other warehouses
            if node.id in used_nodes:
                continue
            # Ensure warehouse is placed on a node with both in/out edges for better routing
            if node.id not in bidirectional_candidate_nodes:
                continue
                
            distance = calculate_distance(wh_lat, wh_lon, node.lat, node.lon)
            if distance < min_distance:
                min_distance = distance
                closest_node = node

        if closest_node:
            wh = Warehouse(wh_id, closest_node)
            used_nodes.add(closest_node.id)  # Mark this node as used

            if i < len(custom_config.get('warehouse_configs', [])):
                warehouse_config = custom_config['warehouse_configs'][i]
                vehicle_counts = warehouse_config.get('vehicle_counts', {})
            else:
                vehicle_counts = base_config.DEFAULT_SETTINGS.get('default_vehicle_counts', {})

            for vehicle_type, count in vehicle_counts.items():
                vehicle_specs = None
                for spec in base_config.VEHICLE_FLEET_SPECS:
                    if spec['type'] == vehicle_type:
                        vehicle_specs = spec
                        break

                if vehicle_specs:
                    for j in range(count):
                        v_id = f"{vehicle_type}_{wh_id}_{j+1}"
                        try:
                            vehicle = Vehicle(v_id, vehicle_type, wh_id, **vehicle_specs)
                            wh.vehicles.append(vehicle)
                        except Exception:
                            continue

            warehouses.append(wh)



    # Generate orders FIRST to get actual demand
    orders = _generate_orders_with_dispersion(
        custom_config, warehouses, skus, bidirectional_candidate_nodes, nodes_df,
        custom_config.get('order_dispersion', 50)
    )

    # NOW calculate inventory based on ACTUAL orders generated
    if 'warehouse_configs' in custom_config:
        for i, warehouse_config in enumerate(custom_config['warehouse_configs']):
            if i >= len(warehouses):
                break

            warehouse = warehouses[i]
            if 'sku_inventory_percentages' in warehouse_config:
                # Calculate ACTUAL demand from generated orders
                actual_sku_demand = {}
                for order in orders:
                    for sku_id, quantity in order.requested_items.items():
                        if sku_id not in actual_sku_demand:
                            actual_sku_demand[sku_id] = 0
                        actual_sku_demand[sku_id] += quantity

                for j, sku in enumerate(skus):
                    if j < len(warehouse_config['sku_inventory_percentages']):
                        warehouse_supply_percentage = warehouse_config['sku_inventory_percentages'][j]
                        
                        # Use ACTUAL demand instead of expected
                        actual_demand = actual_sku_demand.get(sku.id, 0)
                        
                        # Warehouse supply percentage represents portion of ACTUAL demand
                        warehouse_inventory = (warehouse_supply_percentage / 100.0) * actual_demand

                        # Allow zero inventory when supply percentage is 0%
                        warehouse.inventory[sku.id] = max(0, int(round(warehouse_inventory)))
                    else:
                        warehouse.inventory[sku.id] = 0
            else:
                for sku in skus:
                    warehouse.inventory[sku.id] = 50

    return {
        'nodes': nodes,
        'edges_df': edges_df_final,
        'warehouses': warehouses,
        'orders': orders,
        'skus': skus
    }