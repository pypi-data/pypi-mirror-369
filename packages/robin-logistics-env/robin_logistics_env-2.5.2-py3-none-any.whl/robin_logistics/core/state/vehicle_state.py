"""Vehicle state management for consistent tracking across operations."""

from typing import Dict, Tuple, Optional
from ..models.vehicle import Vehicle
from ..models.sku import SKU


class VehicleState:
    """Represents the current state of a vehicle."""
    
    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle
        self.current_load: Dict[str, int] = {}  # SKU_ID -> quantity
        self.current_weight: float = 0.0
        self.current_volume: float = 0.0
        self.current_location: str = vehicle.home_warehouse_id
    
    def reset(self):
        """Reset vehicle to empty state at home warehouse."""
        self.current_load.clear()
        self.current_weight = 0.0
        self.current_volume = 0.0
        self.current_location = self.vehicle.home_warehouse_id
    
    def get_remaining_capacity(self) -> Tuple[float, float]:
        """Get remaining weight and volume capacity."""
        remaining_weight = max(0.0, self.vehicle.capacity_weight - self.current_weight)
        remaining_volume = max(0.0, self.vehicle.capacity_volume - self.current_volume)
        return remaining_weight, remaining_volume
    
    def is_overloaded(self) -> bool:
        """Check if vehicle is over capacity."""
        return (self.current_weight > self.vehicle.capacity_weight or 
                self.current_volume > self.vehicle.capacity_volume)
    
    def can_accommodate(self, sku_weight: float, sku_volume: float, quantity: int) -> bool:
        """Check if vehicle can accommodate additional load."""
        additional_weight = sku_weight * quantity
        additional_volume = sku_volume * quantity
        
        return (self.current_weight + additional_weight <= self.vehicle.capacity_weight and
                self.current_volume + additional_volume <= self.vehicle.capacity_volume)
    
    def get_load_summary(self) -> Dict:
        """Get summary of current vehicle load."""
        return {
            'skus_loaded': dict(self.current_load),
            'total_weight': self.current_weight,
            'total_volume': self.current_volume,
            'weight_utilization': self.current_weight / self.vehicle.capacity_weight,
            'volume_utilization': self.current_volume / self.vehicle.capacity_volume,
            'current_location': self.current_location
        }


class VehicleStateManager:
    """Manages vehicle states and operations consistently."""
    
    def __init__(self):
        self.vehicle_states: Dict[str, VehicleState] = {}
    
    def get_vehicle_state(self, vehicle: Vehicle) -> VehicleState:
        """Get or create vehicle state."""
        if vehicle.id not in self.vehicle_states:
            self.vehicle_states[vehicle.id] = VehicleState(vehicle)
        return self.vehicle_states[vehicle.id]
    
    def reset_vehicle(self, vehicle_id: str):
        """Reset vehicle to initial state."""
        if vehicle_id in self.vehicle_states:
            self.vehicle_states[vehicle_id].reset()
    
    def reset_all_vehicles(self):
        """Reset all vehicles to initial state."""
        for state in self.vehicle_states.values():
            state.reset()
    
    def add_sku_to_vehicle(self, vehicle: Vehicle, sku_id: str, quantity: int, 
                          sku_weight: float, sku_volume: float) -> bool:
        """
        Add SKU to vehicle with proper state tracking.
        
        Args:
            vehicle: Vehicle to load
            sku_id: SKU identifier
            quantity: Quantity to load
            sku_weight: Weight per unit of SKU
            sku_volume: Volume per unit of SKU
            
        Returns:
            True if successful, False if vehicle cannot accommodate
        """
        state = self.get_vehicle_state(vehicle)
        
        # Check capacity constraints
        if not state.can_accommodate(sku_weight, sku_volume, quantity):
            return False
        
        # Update load
        if sku_id not in state.current_load:
            state.current_load[sku_id] = 0
        state.current_load[sku_id] += quantity
        
        # Update weight and volume
        state.current_weight += sku_weight * quantity
        state.current_volume += sku_volume * quantity
        
        return True
    
    def remove_sku_from_vehicle(self, vehicle: Vehicle, sku_id: str, quantity: int,
                               sku_weight: float, sku_volume: float) -> bool:
        """
        Remove SKU from vehicle with proper state tracking.
        
        Args:
            vehicle: Vehicle to unload
            sku_id: SKU identifier
            quantity: Quantity to remove
            sku_weight: Weight per unit of SKU
            sku_volume: Volume per unit of SKU
            
        Returns:
            True if successful, False if insufficient quantity
        """
        state = self.get_vehicle_state(vehicle)
        
        # Check if vehicle has enough of this SKU
        current_quantity = state.current_load.get(sku_id, 0)
        if current_quantity < quantity:
            return False
        
        # Update load
        state.current_load[sku_id] -= quantity
        if state.current_load[sku_id] <= 0:
            del state.current_load[sku_id]
        
        # Update weight and volume
        state.current_weight -= sku_weight * quantity
        state.current_volume -= sku_volume * quantity
        
        # Ensure non-negative values
        state.current_weight = max(0.0, state.current_weight)
        state.current_volume = max(0.0, state.current_volume)
        
        return True
    
    def move_vehicle(self, vehicle_id: str, new_location: str):
        """Update vehicle location."""
        if vehicle_id in self.vehicle_states:
            self.vehicle_states[vehicle_id].current_location = new_location
    
    def get_vehicle_load(self, vehicle_id: str) -> Dict[str, int]:
        """Get current load for a vehicle."""
        if vehicle_id in self.vehicle_states:
            return self.vehicle_states[vehicle_id].current_load.copy()
        return {}
    
    def get_vehicle_capacity_usage(self, vehicle_id: str) -> Tuple[float, float]:
        """Get current weight and volume usage for a vehicle."""
        if vehicle_id in self.vehicle_states:
            state = self.vehicle_states[vehicle_id]
            return state.current_weight, state.current_volume
        return 0.0, 0.0
    
    def get_vehicle_remaining_capacity(self, vehicle_id: str) -> Tuple[float, float]:
        """Get remaining capacity for a vehicle."""
        if vehicle_id in self.vehicle_states:
            return self.vehicle_states[vehicle_id].get_remaining_capacity()
        return 0.0, 0.0
    
    def validate_vehicle_constraints(self, vehicle_id: str) -> Tuple[bool, str]:
        """Validate that vehicle is not violating constraints."""
        if vehicle_id not in self.vehicle_states:
            return True, "Vehicle state not tracked"
        
        state = self.vehicle_states[vehicle_id]
        
        if state.is_overloaded():
            return False, f"Vehicle {vehicle_id} is overloaded: {state.current_weight:.1f}kg/{state.vehicle.capacity_weight}kg, {state.current_volume:.2f}m³/{state.vehicle.capacity_volume}m³"
        
        return True, "Vehicle constraints satisfied"
