#!/usr/bin/env python3
"""
Smart Adaptive Traffic Management System
Complete Integration Module
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import logging
import argparse

# Import improved modules
from camera_capture_improved import CameraCapture
from vehicle_detection_improved import VehicleDetector
from traffic_signal_improved import TrafficSignalController


class TrafficManagementSystem:
    """Integrated traffic management system"""
    
    def __init__(self, camera_index: int = 0, algorithm: str = "adaptive"):
        """
        Initialize the traffic management system
        
        Args:
            camera_index: Camera device index
            algorithm: Signal timing algorithm to use
        """
        self.camera_index = camera_index
        self.algorithm = algorithm
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('traffic_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.camera = None
        self.detector = None
        self.controller = None
        
        # Data storage
        self.data_dir = Path("traffic_data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.cycle_data = []
        self.cycle_data_file = self.data_dir / "cycle_data.json"
        
        self._load_cycle_data()
    
    def _load_cycle_data(self):
        """Load historical cycle data"""
        if self.cycle_data_file.exists():
            try:
                with open(self.cycle_data_file, 'r') as f:
                    self.cycle_data = json.load(f)
            except Exception as e:
                self.logger.error(f"Could not load cycle data: {e}")
    
    def _save_cycle_data(self):
        """Save cycle data to file"""
        try:
            with open(self.cycle_data_file, 'w') as f:
                json.dump(self.cycle_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save cycle data: {e}")
    
    def initialize(self) -> bool:
        """
        Initialize all system components
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Initializing Traffic Management System...")
            
            # Initialize camera
            self.logger.info("Initializing camera...")
            self.camera = CameraCapture(
                camera_index=self.camera_index,
                output_dir=str(self.data_dir / "captures")
            )
            if not self.camera.initialize_camera():
                raise RuntimeError("Camera initialization failed")
            
            # Initialize vehicle detector
            self.logger.info("Initializing vehicle detector...")
            self.detector = VehicleDetector()
            
            # Initialize traffic signal controller
            self.logger.info("Initializing traffic signal controller...")
            self.controller = TrafficSignalController()
            
            self.logger.info("System initialization complete!")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def run_single_cycle(self) -> Optional[Dict]:
        """
        Run a single traffic management cycle
        
        Returns:
            Dictionary with cycle results or None if failed
        """
        try:
            cycle_start = time.time()
            timestamp = datetime.now()
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Starting traffic cycle at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"{'='*60}")
            
            # Step 1: Capture image
            self.logger.info("Step 1: Capturing image from camera...")
            image_path = self.camera.capture_single_image()
            
            if not image_path:
                raise RuntimeError("Failed to capture image")
            
            self.logger.info(f"Image captured: {image_path}")
            
            # Step 2: Detect vehicles
            self.logger.info("Step 2: Detecting vehicles in image...")
            import cv2
            image = cv2.imread(image_path)
            vehicles = self.detector.detect_vehicles(image)
            stats = self.detector.get_vehicle_statistics(vehicles)
            
            self.logger.info(f"Detected {stats['total']} total vehicles:")
            for vehicle_type, count in stats.items():
                if vehicle_type != 'total' and count > 0:
                    self.logger.info(f"  - {vehicle_type.capitalize()}: {count}")
            
            # Save detection result image
            result_image = self.detector.draw_detections(image, vehicles)
            result_path = str(Path(image_path).parent / f"detected_{Path(image_path).name}")
            cv2.imwrite(result_path, result_image)
            self.logger.info(f"Detection result saved: {result_path}")
            
            # Step 3: Calculate signal timing
            self.logger.info(f"Step 3: Calculating signal timing using {self.algorithm} algorithm...")
            timing = self.controller.calculate_signal_timing(
                vehicle_stats=stats,
                algorithm=self.algorithm
            )
            
            self.logger.info(f"Signal Timing Calculated:")
            self.logger.info(f"  - Green: {timing.green_time}s")
            self.logger.info(f"  - Yellow: {timing.yellow_time}s")
            self.logger.info(f"  - All-Red: {timing.all_red_time}s")
            self.logger.info(f"  - Total Cycle: {timing.total_cycle_time}s")
            
            # Step 4: Create cycle record
            cycle_time = time.time() - cycle_start
            
            cycle_record = {
                "timestamp": timestamp.isoformat(),
                "image_path": image_path,
                "result_path": result_path,
                "vehicle_count": stats['total'],
                "vehicle_stats": stats,
                "weighted_count": timing.weighted_vehicle_count,
                "green_time": timing.green_time,
                "yellow_time": timing.yellow_time,
                "all_red_time": timing.all_red_time,
                "total_cycle_time": timing.total_cycle_time,
                "algorithm": self.algorithm,
                "processing_time": round(cycle_time, 2)
            }
            
            # Save cycle data
            self.cycle_data.append(cycle_record)
            self._save_cycle_data()
            
            self.logger.info(f"Cycle completed in {cycle_time:.2f}s")
            self.logger.info(f"{'='*60}\n")
            
            return cycle_record
            
        except Exception as e:
            self.logger.error(f"Cycle failed: {e}")
            return None
    
    def run_continuous(self, interval: float = 30.0, max_cycles: Optional[int] = None):
        """
        Run continuous traffic management
        
        Args:
            interval: Time between cycles in seconds
            max_cycles: Maximum number of cycles (None for infinite)
        """
        self.logger.info(f"Starting continuous traffic management")
        self.logger.info(f"Cycle interval: {interval}s")
        if max_cycles:
            self.logger.info(f"Max cycles: {max_cycles}")
        
        cycle_count = 0
        
        try:
            while True:
                if max_cycles and cycle_count >= max_cycles:
                    self.logger.info(f"Reached maximum cycles ({max_cycles})")
                    break
                
                # Run cycle
                result = self.run_single_cycle()
                
                if result:
                    cycle_count += 1
                else:
                    self.logger.warning("Cycle failed, continuing...")
                
                # Wait for next cycle
                if max_cycles is None or cycle_count < max_cycles:
                    self.logger.info(f"Waiting {interval}s until next cycle...")
                    time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("\nStopping continuous mode (Ctrl+C pressed)")
        
        self.logger.info(f"Completed {cycle_count} cycles")
    
    def generate_report(self) -> Dict:
        """
        Generate system performance report
        
        Returns:
            Dictionary with system statistics
        """
        if not self.cycle_data:
            return {"message": "No data available"}
        
        total_vehicles = sum(c['vehicle_count'] for c in self.cycle_data)
        avg_vehicles = total_vehicles / len(self.cycle_data)
        
        avg_green = sum(c['green_time'] for c in self.cycle_data) / len(self.cycle_data)
        avg_processing = sum(c['processing_time'] for c in self.cycle_data) / len(self.cycle_data)
        
        # Vehicle type breakdown
        vehicle_types = {}
        for cycle in self.cycle_data:
            for v_type, count in cycle['vehicle_stats'].items():
                if v_type != 'total':
                    vehicle_types[v_type] = vehicle_types.get(v_type, 0) + count
        
        report = {
            "system_info": {
                "total_cycles": len(self.cycle_data),
                "algorithm": self.algorithm,
                "camera_index": self.camera_index
            },
            "traffic_statistics": {
                "total_vehicles_detected": total_vehicles,
                "average_vehicles_per_cycle": round(avg_vehicles, 2),
                "vehicle_type_breakdown": vehicle_types
            },
            "timing_statistics": {
                "average_green_time": round(avg_green, 2),
                "min_green_time": min(c['green_time'] for c in self.cycle_data),
                "max_green_time": max(c['green_time'] for c in self.cycle_data)
            },
            "performance": {
                "average_processing_time": round(avg_processing, 2),
                "total_time_saved": round(sum(c['green_time'] - 30 for c in self.cycle_data if c['green_time'] > 30), 2)
            }
        }
        
        return report
    
    def shutdown(self):
        """Shutdown the system and cleanup resources"""
        self.logger.info("Shutting down Traffic Management System...")
        
        if self.camera:
            self.camera.release()
        
        # Generate final report
        if self.cycle_data:
            report = self.generate_report()
            report_path = self.data_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Final report saved: {report_path}")
        
        self.logger.info("Shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Smart Adaptive Traffic Management System"
    )
    parser.add_argument(
        '--camera', type=int, default=0,
        help='Camera device index (default: 0)'
    )
    parser.add_argument(
        '--algorithm', choices=['linear', 'logarithmic', 'adaptive'],
        default='adaptive',
        help='Signal timing algorithm (default: adaptive)'
    )
    parser.add_argument(
        '--mode', choices=['single', 'continuous'],
        default='single',
        help='Operation mode (default: single)'
    )
    parser.add_argument(
        '--interval', type=float, default=30.0,
        help='Cycle interval in seconds for continuous mode (default: 30.0)'
    )
    parser.add_argument(
        '--max-cycles', type=int,
        help='Maximum number of cycles for continuous mode'
    )
    parser.add_argument(
        '--report', action='store_true',
        help='Generate report from existing data and exit'
    )
    
    args = parser.parse_args()
    
    # Create system instance
    system = TrafficManagementSystem(
        camera_index=args.camera,
        algorithm=args.algorithm
    )
    
    try:
        # Report mode
        if args.report:
            system._load_cycle_data()
            report = system.generate_report()
            
            print("\n" + "="*60)
            print("TRAFFIC MANAGEMENT SYSTEM REPORT")
            print("="*60)
            print(json.dumps(report, indent=2))
            print("="*60 + "\n")
            
            return
        
        # Initialize system
        if not system.initialize():
            print("Failed to initialize system")
            return
        
        # Run based on mode
        if args.mode == 'single':
            result = system.run_single_cycle()
            if not result:
                print("Cycle failed")
        else:
            system.run_continuous(
                interval=args.interval,
                max_cycles=args.max_cycles
            )
        
    except Exception as e:
        print(f"Error: {e}")
        logging.exception("System error")
    
    finally:
        system.shutdown()


if __name__ == "__main__":
    main()
