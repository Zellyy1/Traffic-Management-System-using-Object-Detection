import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import statistics


@dataclass
class TrafficSignalConfig:
    """Configuration for traffic signal timing"""
    min_green_time: int = 15  # Minimum green time in seconds
    max_green_time: int = 120  # Maximum green time in seconds
    base_green_time: int = 30  # Base green time in seconds
    vehicle_multiplier: float = 2.0  # Additional seconds per vehicle
    yellow_time: int = 3  # Yellow signal duration
    all_red_time: int = 2  # All-red clearance time
    
    # Priority multipliers for different vehicle types
    car_weight: float = 1.0
    motorcycle_weight: float = 0.5
    bus_weight: float = 2.0  # Buses get priority
    truck_weight: float = 1.5


@dataclass
class SignalTiming:
    """Traffic signal timing result"""
    green_time: int
    yellow_time: int
    all_red_time: int
    total_cycle_time: int
    vehicle_count: int
    weighted_vehicle_count: float
    timestamp: str
    algorithm: str


class TrafficSignalController:
    """Intelligent traffic signal controller with multiple algorithms"""
    
    def __init__(self, config: Optional[TrafficSignalConfig] = None):
        """
        Initialize traffic signal controller
        
        Args:
            config: Traffic signal configuration
        """
        self.config = config or TrafficSignalConfig()
        self.history: List[SignalTiming] = []
        self.history_file = Path("signal_timing_history.json")
        
        # Load existing history
        self._load_history()
    
    def _load_history(self):
        """Load signal timing history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [SignalTiming(**item) for item in data]
            except Exception as e:
                print(f"Warning: Could not load history: {e}")
    
    def _save_history(self):
        """Save signal timing history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump([asdict(t) for t in self.history], f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def calculate_weighted_vehicles(self, vehicle_stats: Dict[str, int]) -> float:
        """
        Calculate weighted vehicle count based on vehicle types
        
        Args:
            vehicle_stats: Dictionary with vehicle counts by type
            
        Returns:
            Weighted vehicle count
        """
        weights = {
            'car': self.config.car_weight,
            'motorcycle': self.config.motorcycle_weight,
            'bus': self.config.bus_weight,
            'truck': self.config.truck_weight
        }
        
        weighted_count = 0.0
        for vehicle_type, count in vehicle_stats.items():
            if vehicle_type in weights:
                weighted_count += count * weights[vehicle_type]
        
        return weighted_count
    
    def linear_algorithm(self, vehicle_count: float) -> int:
        """
        Linear timing algorithm: base_time + (vehicles * multiplier)
        
        Args:
            vehicle_count: Number of vehicles (can be weighted)
            
        Returns:
            Green signal time in seconds
        """
        green_time = self.config.base_green_time + (vehicle_count * self.config.vehicle_multiplier)
        return self._clamp_time(int(green_time))
    
    def logarithmic_algorithm(self, vehicle_count: float) -> int:
        """
        Logarithmic timing algorithm: better for high traffic volumes
        Prevents excessively long green times when traffic is heavy
        
        Args:
            vehicle_count: Number of vehicles (can be weighted)
            
        Returns:
            Green signal time in seconds
        """
        import math
        if vehicle_count <= 0:
            return self.config.min_green_time
        
        # Use logarithmic scaling for better handling of high volumes
        green_time = self.config.base_green_time + (15 * math.log(vehicle_count + 1))
        return self._clamp_time(int(green_time))
    
    def adaptive_algorithm(self, vehicle_count: float) -> int:
        """
        Adaptive algorithm using historical data
        Adjusts based on average wait times and traffic patterns
        
        Args:
            vehicle_count: Number of vehicles (can be weighted)
            
        Returns:
            Green signal time in seconds
        """
        # Start with linear calculation
        base_time = self.linear_algorithm(vehicle_count)
        
        # Adjust based on historical data if available
        if len(self.history) >= 10:
            recent_history = self.history[-20:]
            avg_vehicles = statistics.mean([h.weighted_vehicle_count for h in recent_history])
            
            # If current count is significantly higher than average, increase time
            if vehicle_count > avg_vehicles * 1.5:
                base_time = int(base_time * 1.2)
            elif vehicle_count < avg_vehicles * 0.5:
                base_time = int(base_time * 0.8)
        
        return self._clamp_time(base_time)
    
    def _clamp_time(self, time_seconds: int) -> int:
        """Ensure time is within configured bounds"""
        return max(self.config.min_green_time, 
                   min(self.config.max_green_time, time_seconds))
    
    def calculate_signal_timing(self, 
                               vehicle_count: int = None,
                               vehicle_stats: Dict[str, int] = None,
                               algorithm: str = "adaptive") -> SignalTiming:
        """
        Calculate optimal signal timing
        
        Args:
            vehicle_count: Total vehicle count (if not using weighted stats)
            vehicle_stats: Dictionary with vehicle counts by type
            algorithm: Algorithm to use ('linear', 'logarithmic', 'adaptive')
            
        Returns:
            SignalTiming object with calculated times
        """
        # Determine weighted vehicle count
        if vehicle_stats:
            weighted_count = self.calculate_weighted_vehicles(vehicle_stats)
            total_count = vehicle_stats.get('total', sum(vehicle_stats.values()))
        else:
            weighted_count = float(vehicle_count or 0)
            total_count = vehicle_count or 0
        
        # Select algorithm
        algorithms = {
            'linear': self.linear_algorithm,
            'logarithmic': self.logarithmic_algorithm,
            'adaptive': self.adaptive_algorithm
        }
        
        if algorithm not in algorithms:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        green_time = algorithms[algorithm](weighted_count)
        
        # Create timing result
        timing = SignalTiming(
            green_time=green_time,
            yellow_time=self.config.yellow_time,
            all_red_time=self.config.all_red_time,
            total_cycle_time=green_time + self.config.yellow_time + self.config.all_red_time,
            vehicle_count=total_count,
            weighted_vehicle_count=weighted_count,
            timestamp=datetime.now().isoformat(),
            algorithm=algorithm
        )
        
        # Add to history
        self.history.append(timing)
        self._save_history()
        
        return timing
    
    def get_statistics(self) -> Dict:
        """Get statistics from historical data"""
        if not self.history:
            return {"message": "No historical data available"}
        
        recent = self.history[-50:]  # Last 50 cycles
        
        return {
            "total_cycles": len(self.history),
            "recent_cycles": len(recent),
            "avg_green_time": statistics.mean([h.green_time for h in recent]),
            "avg_vehicle_count": statistics.mean([h.vehicle_count for h in recent]),
            "max_green_time": max([h.green_time for h in recent]),
            "min_green_time": min([h.green_time for h in recent]),
            "total_wait_time_saved": sum([h.green_time - self.config.base_green_time 
                                         for h in recent if h.green_time > self.config.base_green_time])
        }


def main():
    """Main function to calculate and display signal timing"""
    import sys
    
    # Initialize controller
    controller = TrafficSignalController()
    
    # Get algorithm from command line or use default
    algorithm = sys.argv[1] if len(sys.argv) > 1 else "adaptive"
    
    try:
        # Try to read vehicle count from file
        vehicle_count_file = Path("vehicle_count.txt")
        if vehicle_count_file.exists():
            with open(vehicle_count_file, 'r') as f:
                vehicle_count = int(f.read().strip())
            
            if vehicle_count < 0:
                print("Error: Invalid vehicle count. Must be non-negative.")
                return
            
            # Calculate timing
            timing = controller.calculate_signal_timing(
                vehicle_count=vehicle_count,
                algorithm=algorithm
            )
            
            # Display results
            print("\n" + "="*60)
            print("TRAFFIC SIGNAL TIMING CALCULATION")
            print("="*60)
            print(f"\nAlgorithm Used: {timing.algorithm.upper()}")
            print(f"Timestamp: {timing.timestamp}")
            print(f"\nVehicle Count: {timing.vehicle_count}")
            print(f"Weighted Count: {timing.weighted_vehicle_count:.1f}")
            print(f"\n--- Signal Phases ---")
            print(f"Green Signal:    {timing.green_time} seconds")
            print(f"Yellow Signal:   {timing.yellow_time} seconds")
            print(f"All-Red Clear:   {timing.all_red_time} seconds")
            print(f"Total Cycle:     {timing.total_cycle_time} seconds")
            
            # Show statistics if available
            if len(controller.history) >= 5:
                print(f"\n--- Historical Statistics ---")
                stats = controller.get_statistics()
                print(f"Average Green Time: {stats['avg_green_time']:.1f}s")
                print(f"Average Vehicle Count: {stats['avg_vehicle_count']:.1f}")
            
            print("\n" + "="*60)
            
        else:
            print("Error: vehicle_count.txt not found.")
            print("Please run vehicle detection first or create the file manually.")
            return
        
    except ValueError:
        print("Error: Invalid data in vehicle_count.txt. Please ensure it contains a valid integer.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
