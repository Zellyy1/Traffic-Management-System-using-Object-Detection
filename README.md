# Smart Traffic Management System

An intelligent traffic management system that uses computer vision and adaptive algorithms to optimize traffic signal timing based on real-time vehicle detection.

## 🚀 Features

### Core Capabilities
- **Real-time Vehicle Detection**: Uses YOLOv3 deep learning model to detect and classify vehicles (cars, motorcycles, buses, trucks)
- **Adaptive Signal Timing**: Multiple algorithms (linear, logarithmic, adaptive) to calculate optimal green light duration
- **Multi-Camera Support**: Supports multiple camera sources with automatic failover and recovery
- **Weighted Vehicle Priority**: Gives priority to buses and larger vehicles
- **Historical Analytics**: Tracks performance metrics and generates detailed reports
- **Continuous Monitoring**: Can run indefinitely with configurable cycle intervals

### Improvements Over Original Version

#### 1. **Enhanced Vehicle Detection**
- ✅ Fixed missing `numpy` import
- ✅ Added proper error handling and validation
- ✅ Support for multiple vehicle types with classification
- ✅ Non-maximum suppression to eliminate duplicate detections
- ✅ Configurable confidence thresholds
- ✅ Colored bounding boxes by vehicle type
- ✅ Vehicle statistics and counting by type
- ✅ GPU acceleration support (if available)

#### 2. **Intelligent Signal Control**
- ✅ Multiple timing algorithms (linear, logarithmic, adaptive)
- ✅ Weighted vehicle counting (buses get higher priority)
- ✅ Min/max time constraints for safety
- ✅ Historical data analysis for better predictions
- ✅ Yellow and all-red clearance phases
- ✅ Complete cycle time calculation
- ✅ Performance tracking and statistics

#### 3. **Robust Camera Capture**
- ✅ Automatic retry logic for camera failures
- ✅ Multi-camera support
- ✅ Configurable resolution and FPS
- ✅ Burst capture mode
- ✅ Continuous capture with threading
- ✅ High-quality image encoding
- ✅ Proper resource cleanup

#### 4. **System Integration**
- ✅ Complete end-to-end pipeline
- ✅ Data logging and persistence
- ✅ JSON-based data storage
- ✅ Comprehensive error handling
- ✅ Command-line interface
- ✅ Report generation
- ✅ Production-ready logging

## 📋 Prerequisites

- Python 3.7 or higher
- OpenCV (cv2)
- NumPy
- YOLO model files (yolov3.weights, yolov3.cfg, coco.names)

## 🔧 Installation

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd traffic-management-system
```

### 2. Install Required Packages
```bash
pip install opencv-python numpy
```

### 3. Download YOLO Model Files

You need three files for YOLO to work:

**Option A: Download Pre-trained YOLOv3 (Recommended)**
```bash
# Download weights (~240 MB)
wget https://pjreddie.com/media/files/yolov3.weights

# Download config
wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg

# Download class names
wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
```

**Option B: Use YOLOv4 (Better accuracy, larger file)**
```bash
# Download weights (~250 MB)
wget https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights

# Download config
wget https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg

# Download class names
wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
```

Place all three files in the project directory.

### 4. Verify Installation
```bash
python traffic_management_system.py --help
```

## 📖 Usage

### Basic Usage

#### Single Cycle Mode
Run one complete detection and timing calculation:
```bash
python traffic_management_system.py --mode single
```

#### Continuous Mode
Run continuously with 30-second intervals:
```bash
python traffic_management_system.py --mode continuous --interval 30
```

#### Limited Continuous Mode
Run 10 cycles then stop:
```bash
python traffic_management_system.py --mode continuous --max-cycles 10
```

### Advanced Options

#### Use Different Camera
```bash
python traffic_management_system.py --camera 1
```

#### Choose Algorithm
```bash
# Linear algorithm (simple, predictable)
python traffic_management_system.py --algorithm linear

# Logarithmic algorithm (better for high traffic)
python traffic_management_system.py --algorithm logarithmic

# Adaptive algorithm (learns from history)
python traffic_management_system.py --algorithm adaptive
```

#### Generate Report
```bash
python traffic_management_system.py --report
```

### Individual Module Usage

#### Vehicle Detection Only
```bash
python vehicle_detection_improved.py path/to/image.jpg
```

#### Traffic Signal Timing Only
First create a `vehicle_count.txt` file with a number, then:
```bash
# Uses adaptive algorithm by default
python traffic_signal_improved.py

# Specify algorithm
python traffic_signal_improved.py linear
python traffic_signal_improved.py logarithmic
```

#### Camera Capture Only
```bash
# Single capture
python camera_capture_improved.py 0 single

# Burst capture (5 images)
python camera_capture_improved.py 0 burst 5

# Continuous capture for 60 seconds with 5s interval
python camera_capture_improved.py 0 continuous 5 60
```

## 🎯 Algorithm Comparison

### Linear Algorithm
- **Formula**: `green_time = base_time + (vehicles × multiplier)`
- **Best for**: Low to medium traffic, predictable patterns
- **Pros**: Simple, predictable, easy to understand
- **Cons**: Can give excessively long green times in heavy traffic

### Logarithmic Algorithm
- **Formula**: `green_time = base_time + (15 × log(vehicles + 1))`
- **Best for**: High traffic volumes, rush hours
- **Pros**: Prevents excessive wait times, scales well
- **Cons**: Less responsive to small changes in traffic

### Adaptive Algorithm
- **Formula**: Uses linear + historical data adjustments
- **Best for**: Variable traffic patterns, real-world deployment
- **Pros**: Learns from patterns, self-optimizing, balanced
- **Cons**: Requires historical data to be most effective

## 📊 Output Files and Data

### Directory Structure
```
traffic-management-system/
├── traffic_data/
│   ├── captures/              # Captured images
│   │   ├── capture_20241214_120530.jpg
│   │   └── detected_capture_20241214_120530.jpg
│   ├── cycle_data.json        # Cycle records
│   └── report_20241214_123045.json
├── signal_timing_history.json  # Signal timing log
└── traffic_system.log          # System logs
```

### Data Files

#### cycle_data.json
Records every traffic cycle with complete information:
```json
{
  "timestamp": "2024-12-14T12:05:30",
  "vehicle_count": 8,
  "vehicle_stats": {
    "car": 6,
    "motorcycle": 1,
    "bus": 1,
    "total": 8
  },
  "green_time": 46,
  "algorithm": "adaptive"
}
```

#### Reports
Comprehensive statistics including:
- Total cycles processed
- Average vehicles per cycle
- Vehicle type breakdown
- Average/min/max green times
- Processing performance
- Time saved vs. fixed timing

## 🎨 Configuration

### Traffic Signal Settings

Edit `traffic_signal_improved.py` to customize:
```python
@dataclass
class TrafficSignalConfig:
    min_green_time: int = 15      # Minimum green (safety)
    max_green_time: int = 120     # Maximum green (fairness)
    base_green_time: int = 30     # Starting point
    vehicle_multiplier: float = 2.0  # Seconds per vehicle
    yellow_time: int = 3          # Yellow light duration
    all_red_time: int = 2         # All-red clearance
    
    # Vehicle weights
    car_weight: float = 1.0
    motorcycle_weight: float = 0.5
    bus_weight: float = 2.0       # Buses get priority
    truck_weight: float = 1.5
```

### Vehicle Detection Settings

Edit `vehicle_detection_improved.py`:
```python
detector = VehicleDetector(
    confidence_threshold=0.5,  # Detection confidence (0.0-1.0)
    nms_threshold=0.4         # Overlap threshold for NMS
)
```

### Camera Settings

Edit `camera_capture_improved.py`:
```python
camera.resolution = (1920, 1080)  # HD resolution
camera.fps = 30                    # Frame rate
```

## 🔍 Troubleshooting

### Camera Not Found
- Check camera index: Try 0, 1, 2, etc.
- Verify camera is connected and not used by another application
- Linux: Check permissions with `ls -l /dev/video*`

### YOLO Model Not Loading
- Ensure all three files are in the project directory
- Check file names match exactly (case-sensitive)
- Verify files are not corrupted (download again)

### Low Detection Accuracy
- Ensure good lighting conditions
- Check camera focus and positioning
- Lower confidence threshold for more detections
- Consider upgrading to YOLOv4

### Slow Performance
- Reduce camera resolution
- Use YOLOv3-tiny (faster but less accurate)
- Enable GPU acceleration if available

## 🚦 Example Scenarios

### Intersection with Variable Traffic
```bash
# Use adaptive algorithm with 20-second cycles
python traffic_management_system.py \
  --mode continuous \
  --algorithm adaptive \
  --interval 20
```

### High-Traffic Rush Hour
```bash
# Use logarithmic to prevent excessive wait times
python traffic_management_system.py \
  --mode continuous \
  --algorithm logarithmic \
  --interval 15
```

### Testing and Development
```bash
# Single cycle with detailed output
python traffic_management_system.py --mode single
```

## 📈 Performance Metrics

Expected performance on modern hardware:
- **Image Capture**: < 0.5s
- **Vehicle Detection**: 1-3s (CPU), 0.1-0.5s (GPU)
- **Signal Calculation**: < 0.01s
- **Total Cycle Time**: 2-4s (plus configured interval)

## 🤝 Contributing

Suggestions for further improvements:
1. Real traffic light hardware integration
2. Multi-intersection coordination
3. Deep learning model training on local traffic
4. Mobile app for monitoring
5. Weather condition adaptation
6. Emergency vehicle detection and priority
7. Pedestrian detection and crossing time
8. Web dashboard with real-time visualization

## 📝 License

This project is provided as-is for educational and research purposes.

## 🙏 Acknowledgments

- YOLO (You Only Look Once) by Joseph Redmon
- OpenCV library
- COCO dataset for pre-trained models

## 📧 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files in `traffic_system.log`
3. Verify all prerequisites are installed
4. Ensure YOLO model files are correct

---

**Version**: 2.0  
**Last Updated**: December 2024  
**Status**: Production Ready
