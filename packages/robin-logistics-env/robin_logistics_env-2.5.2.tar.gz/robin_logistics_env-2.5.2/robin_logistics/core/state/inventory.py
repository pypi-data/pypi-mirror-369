"""Inventory transaction system for robust operations."""

from typing import List, Dict, Tuple, Any
from dataclasses import dataclass


@dataclass
class InventoryOperation:
    """Represents a single inventory operation that can be committed or rolled back."""
    operation_type: str  # 'pickup' or 'delivery'
    vehicle_id: str
    warehouse_id: str = None
    order_id: str = None
    sku_id: str = None
    quantity: int = 0
    sku_weight: float = 0.0
    sku_volume: float = 0.0
    original_warehouse_inventory: int = 0
    original_vehicle_load: int = 0
    original_order_delivered: int = 0


class InventoryTransaction:
    """Transaction-like system for inventory operations with rollback capability."""
    
    def __init__(self, environment):
        self.env = environment
        self.operations: List[InventoryOperation] = []
        self.committed = False
    
    def pickup_sku(self, vehicle_id: str, warehouse_id: str, sku_id: str, quantity: int) -> bool:
        """
        Record a pickup operation for later execution.
        
        Args:
            vehicle_id: ID of the vehicle
            warehouse_id: ID of the warehouse
            sku_id: ID of the SKU to pick up
            quantity: Quantity to pick up
            
        Returns:
            True if operation can be added, False if invalid
        """
        if self.committed:
            raise ValueError("Transaction already committed")
        
        # Validate operation before adding
        warehouse = self.env.warehouses.get(warehouse_id)
        vehicle = self.env.vehicles.get(vehicle_id)
        
        if not warehouse or not vehicle:
            return False
        
        # Check current warehouse inventory
        current_inventory = warehouse.inventory.get(sku_id, 0)
        if current_inventory < quantity:
            return False
        
        # Check vehicle capacity
        sku_details = self.env.get_sku_details(sku_id)
        if sku_details:
            additional_weight = sku_details['weight'] * quantity
            additional_volume = sku_details['volume'] * quantity
            
            current_weight, current_volume = self.env.get_vehicle_current_capacity(vehicle_id)
            
            if (current_weight + additional_weight > vehicle.capacity_weight or
                current_volume + additional_volume > vehicle.capacity_volume):
                return False
        
        # Record operation
        current_vehicle_load = self.env.get_vehicle_current_load(vehicle_id).get(sku_id, 0)
        
        operation = InventoryOperation(
            operation_type='pickup',
            vehicle_id=vehicle_id,
            warehouse_id=warehouse_id,
            sku_id=sku_id,
            quantity=quantity,
            sku_weight=sku_details['weight'] if sku_details else 0.0,
            sku_volume=sku_details['volume'] if sku_details else 0.0,
            original_warehouse_inventory=current_inventory,
            original_vehicle_load=current_vehicle_load
        )
        
        self.operations.append(operation)
        return True
    
    def deliver_sku(self, vehicle_id: str, order_id: str, sku_id: str, quantity: int) -> bool:
        """
        Record a delivery operation for later execution.
        
        Args:
            vehicle_id: ID of the vehicle
            order_id: ID of the order
            sku_id: ID of the SKU to deliver
            quantity: Quantity to deliver
            
        Returns:
            True if operation can be added, False if invalid
        """
        if self.committed:
            raise ValueError("Transaction already committed")
        
        # Validate operation before adding
        vehicle = self.env.vehicles.get(vehicle_id)
        order = self.env.orders.get(order_id)
        
        if not vehicle or not order:
            return False
        
        # Check if order needs this SKU
        if sku_id not in order.requested_items:
            return False
        
        # Check if vehicle has this SKU
        current_vehicle_load = self.env.get_vehicle_current_load(vehicle_id).get(sku_id, 0)
        if current_vehicle_load < quantity:
            return False
        
        # Record operation
        sku_details = self.env.get_sku_details(sku_id)
        current_delivered = getattr(order, '_delivered_items', {}).get(sku_id, 0)
        
        operation = InventoryOperation(
            operation_type='delivery',
            vehicle_id=vehicle_id,
            order_id=order_id,
            sku_id=sku_id,
            quantity=quantity,
            sku_weight=sku_details['weight'] if sku_details else 0.0,
            sku_volume=sku_details['volume'] if sku_details else 0.0,
            original_vehicle_load=current_vehicle_load,
            original_order_delivered=current_delivered
        )
        
        self.operations.append(operation)
        return True
    
    def commit(self) -> Tuple[bool, str]:
        """
        Execute all recorded operations.
        
        Returns:
            Tuple of (success, message)
        """
        if self.committed:
            return False, "Transaction already committed"
        
        # Execute all operations
        for operation in self.operations:
            if operation.operation_type == 'pickup':
                success = self.env.pickup_sku_from_warehouse(
                    operation.vehicle_id,
                    operation.warehouse_id,
                    operation.sku_id,
                    operation.quantity
                )
                if not success:
                    # Rollback and return error
                    self.rollback()
                    return False, f"Failed to execute pickup operation for {operation.sku_id}"
                    
            elif operation.operation_type == 'delivery':
                success = self.env.deliver_sku_to_order(
                    operation.vehicle_id,
                    operation.order_id,
                    operation.sku_id,
                    operation.quantity
                )
                if not success:
                    # Rollback and return error
                    self.rollback()
                    return False, f"Failed to execute delivery operation for {operation.sku_id}"
        
        self.committed = True
        return True, f"Successfully committed {len(self.operations)} operations"
    
    def rollback(self) -> Tuple[bool, str]:
        """
        Undo all operations in reverse order.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.operations:
            return True, "No operations to rollback"
        
        # Rollback in reverse order
        for operation in reversed(self.operations):
            if operation.operation_type == 'pickup':
                # Restore warehouse inventory
                warehouse = self.env.warehouses[operation.warehouse_id]
                warehouse.inventory[operation.sku_id] = operation.original_warehouse_inventory
                
                # Remove from vehicle
                vehicle = self.env.vehicles[operation.vehicle_id]
                if hasattr(vehicle, '_current_load') and operation.sku_id in vehicle._current_load:
                    vehicle._current_load[operation.sku_id] = operation.original_vehicle_load
                    if vehicle._current_load[operation.sku_id] <= 0:
                        del vehicle._current_load[operation.sku_id]
                    
                    # Restore weight and volume
                    if hasattr(vehicle, '_current_weight'):
                        vehicle._current_weight -= operation.sku_weight * operation.quantity
                    if hasattr(vehicle, '_current_volume'):
                        vehicle._current_volume -= operation.sku_volume * operation.quantity
                        
            elif operation.operation_type == 'delivery':
                # Restore vehicle load
                vehicle = self.env.vehicles[operation.vehicle_id]
                if not hasattr(vehicle, '_current_load'):
                    vehicle._current_load = {}
                vehicle._current_load[operation.sku_id] = operation.original_vehicle_load
                
                # Restore order delivered items
                order = self.env.orders[operation.order_id]
                if hasattr(order, '_delivered_items'):
                    if operation.original_order_delivered > 0:
                        order._delivered_items[operation.sku_id] = operation.original_order_delivered
                    elif operation.sku_id in order._delivered_items:
                        del order._delivered_items[operation.sku_id]
                
                # Restore weight and volume
                if hasattr(vehicle, '_current_weight'):
                    vehicle._current_weight += operation.sku_weight * operation.quantity
                if hasattr(vehicle, '_current_volume'):
                    vehicle._current_volume += operation.sku_volume * operation.quantity
        
        self.operations.clear()
        return True, "Successfully rolled back all operations"
    
    def get_operation_summary(self) -> Dict[str, Any]:
        """Get summary of all operations in this transaction."""
        pickup_ops = [op for op in self.operations if op.operation_type == 'pickup']
        delivery_ops = [op for op in self.operations if op.operation_type == 'delivery']
        
        return {
            'total_operations': len(self.operations),
            'pickup_operations': len(pickup_ops),
            'delivery_operations': len(delivery_ops),
            'committed': self.committed,
            'vehicles_involved': list(set(op.vehicle_id for op in self.operations)),
            'warehouses_involved': list(set(op.warehouse_id for op in self.operations if op.warehouse_id)),
            'orders_involved': list(set(op.order_id for op in self.operations if op.order_id))
        }
