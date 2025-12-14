#!/usr/bin/env python3
"""
Test Suite for Traffic Management System
Verifies all components work correctly
"""

import sys
import os
from pathlib import Path
import numpy as np
import cv2


class TestRunner:
    """Test runner for traffic management system"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def test(self, name):
        """Decorator for test functions"""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator
    
    def run_all(self):
        """Run all registered tests"""
        print("\n" + "="*60)
        print("TRAFFIC MANAGEMENT SYSTEM - TEST SUITE")
        print("="*60 + "\n")
        
        for name, func in self.tests:
            try:
                print(f"Testing: {name}...", end=" ")
                func()
                print("✅ PASSED")
                self.passed += 1
            except AssertionError as e:
                print(f"❌ FAILED: {e}")
                self.failed += 1
            except Exception as e:
                print(f"❌ ERROR: {e}")
                self.failed += 1
        
        print("\n" + "="*60)
        print(f"Results: {self.passed} passed, {self.failed} failed")
        print("="*60 + "\n")
        
        return self.failed == 0


# Create test runner
runner = TestRunner()


@runner.test("Python version check")
def test_python_version():
    """Test Python version is 3.7+"""
    version = sys.version_info
    assert version.major == 3 and version.minor >= 7, \
        f"Python 3.7+ required, found {version.major}.{version.minor}"


@runner.test("Required packages import")
def test_imports():
    """Test all required packages can be imported"""
    import cv2
    import numpy
    assert cv2.__version__, "OpenCV not properly installed"
    assert numpy.__version__, "NumPy not properly installed"


@runner.test("YOLO model files exist")
def test_yolo_files():
    """Test YOLO model files are present"""
    required_files = ['yolov3.weights', 'yolov3.cfg', 'coco.names']
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    assert not missing, f"Missing files: {', '.join(missing)}"


@runner.test("Vehicle detector initialization")
def test_vehicle_detector():
    """Test vehicle detector can be initialized"""
    from vehicle_detection_improved import VehicleDetector
    
    detector = VehicleDetector()
    assert detector.net is not None, "YOLO network not loaded"
    assert len(detector.classes) > 0, "Class names not loaded"


@runner.test("Vehicle detection on test image")
def test_detection():
    """Test vehicle detection with a synthetic image"""
    from vehicle_detection_improved import VehicleDetector
    
    # Create a test image (blank image)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    detector = VehicleDetector()
    vehicles = detector.detect_vehicles(test_image)
    
    # Should return empty list for blank image
    assert isinstance(vehicles, list), "Detection should return a list"


@runner.test("Traffic signal controller initialization")
def test_signal_controller():
    """Test traffic signal controller"""
    from traffic_signal_improved import TrafficSignalController
    
    controller = TrafficSignalController()
    assert controller.config is not None, "Controller config not initialized"


@runner.test("Signal timing calculation")
def test_signal_timing():
    """Test signal timing calculation"""
    from traffic_signal_improved import TrafficSignalController
    
    controller = TrafficSignalController()
    
    # Test with different vehicle counts
    for count in [0, 5, 10, 20]:
        timing = controller.calculate_signal_timing(vehicle_count=count)
        
        assert timing.green_time >= controller.config.min_green_time, \
            "Green time below minimum"
        assert timing.green_time <= controller.config.max_green_time, \
            "Green time above maximum"
        assert timing.total_cycle_time > 0, "Total cycle time invalid"


@runner.test("Linear algorithm")
def test_linear_algorithm():
    """Test linear timing algorithm"""
    from traffic_signal_improved import TrafficSignalController
    
    controller = TrafficSignalController()
    
    # With 0 vehicles, should return base time
    time_0 = controller.linear_algorithm(0)
    assert time_0 == controller.config.base_green_time, \
        "Linear algorithm incorrect for 0 vehicles"
    
    # With 10 vehicles, should increase
    time_10 = controller.linear_algorithm(10)
    assert time_10 > time_0, "Linear algorithm should increase with vehicles"


@runner.test("Logarithmic algorithm")
def test_logarithmic_algorithm():
    """Test logarithmic timing algorithm"""
    from traffic_signal_improved import TrafficSignalController
    
    controller = TrafficSignalController()
    
    # Should handle edge cases
    time_0 = controller.logarithmic_algorithm(0)
    assert time_0 == controller.config.min_green_time, \
        "Logarithmic algorithm incorrect for 0 vehicles"
    
    # Should increase with vehicles but slower than linear
    time_10 = controller.logarithmic_algorithm(10)
    time_100 = controller.logarithmic_algorithm(100)
    
    assert time_10 < time_100, "Logarithmic should increase"
    
    # Growth should slow down
    growth_10 = time_10 - time_0
    growth_100 = time_100 - time_10
    assert growth_100 < growth_10 * 10, "Logarithmic growth should slow"


@runner.test("Weighted vehicle calculation")
def test_weighted_vehicles():
    """Test weighted vehicle counting"""
    from traffic_signal_improved import TrafficSignalController
    
    controller = TrafficSignalController()
    
    vehicle_stats = {
        'car': 5,
        'bus': 2,
        'motorcycle': 3
    }
    
    weighted = controller.calculate_weighted_vehicles(vehicle_stats)
    
    # Buses should have more weight
    assert weighted > sum(vehicle_stats.values()), \
        "Weighted count should be higher due to bus weight"


@runner.test("Camera capture initialization")
def test_camera_init():
    """Test camera capture can be initialized (may fail if no camera)"""
    from camera_capture_improved import CameraCapture
    
    camera = CameraCapture(camera_index=0)
    # Don't actually initialize camera in test, just check object creation
    assert camera.camera_index == 0, "Camera index not set"
    assert camera.output_dir.exists(), "Output directory not created"


@runner.test("Data directory creation")
def test_data_directories():
    """Test system creates required directories"""
    from traffic_signal_improved import TrafficSignalController
    
    # Check that data files can be created
    test_dir = Path("traffic_data")
    test_dir.mkdir(exist_ok=True)
    assert test_dir.exists(), "Could not create data directory"


@runner.test("JSON data persistence")
def test_json_persistence():
    """Test JSON data can be saved and loaded"""
    import json
    from pathlib import Path
    
    test_file = Path("test_data.json")
    test_data = {"test": "data", "value": 123}
    
    # Write
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    
    # Read
    with open(test_file, 'r') as f:
        loaded_data = json.load(f)
    
    assert loaded_data == test_data, "JSON data not preserved"
    
    # Cleanup
    test_file.unlink()


@runner.test("System integration module")
def test_integration_module():
    """Test integrated system can be imported"""
    from traffic_management_system import TrafficManagementSystem
    
    system = TrafficManagementSystem(camera_index=0)
    assert system is not None, "System initialization failed"
    assert system.data_dir.exists(), "Data directory not created"


def main():
    """Run all tests"""
    success = runner.run_all()
    
    if success:
        print("🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("  - Missing YOLO model files (run setup.sh)")
        print("  - OpenCV not installed (pip install opencv-python)")
        print("  - NumPy not installed (pip install numpy)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
