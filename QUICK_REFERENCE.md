# Quick Reference Guide

## 🚀 Quick Start (30 seconds)

```bash
# 1. Setup
./setup.sh

# 2. Run single detection
python3 traffic_management_system.py --mode single

# 3. Done! Check traffic_data/ folder for results
```

---

## 📋 Common Commands

### Run the System

```bash
# Single cycle (test/demo)
python3 traffic_management_system.py --mode single

# Continuous with 20s interval
python3 traffic_management_system.py --mode continuous --interval 20

# Run 10 cycles then stop
python3 traffic_management_system.py --mode continuous --max-cycles 10
```

### Choose Algorithm

```bash
# Linear (simple, predictable)
python3 traffic_management_system.py --algorithm linear

# Logarithmic (better for heavy traffic)
python3 traffic_management_system.py --algorithm logarithmic

# Adaptive (learns from data, recommended)
python3 traffic_management_system.py --algorithm adaptive
```

### View Results

```bash
# Generate report from existing data
python3 traffic_management_system.py --report

# Visualize data with charts
python3 visualize_data.py

# Export report to text file
python3 visualize_data.py --export
```

### Test Individual Components

```bash
# Test camera
python3 camera_capture_improved.py 0 single

# Test detection on image
python3 vehicle_detection_improved.py path/to/image.jpg

# Test signal timing (needs vehicle_count.txt)
python3 traffic_signal_improved.py
```

---

## 📁 File Locations

### Input Files (Required)
- `yolov3.weights` - YOLO model weights (~240 MB)
- `yolov3.cfg` - YOLO configuration
- `coco.names` - Class labels

### Output Files (Auto-created)
- `traffic_data/captures/` - Captured images
- `traffic_data/cycle_data.json` - All cycle records
- `signal_timing_history.json` - Signal timing log
- `traffic_system.log` - System logs

---

## 🎛️ Configuration Quick Edit

### Change Signal Timing Parameters

Edit `traffic_signal_improved.py`, find `TrafficSignalConfig`:

```python
min_green_time: int = 15       # Increase for safety
max_green_time: int = 120      # Decrease for fairness
base_green_time: int = 30      # Starting point
vehicle_multiplier: float = 2.0 # Seconds per vehicle
```

### Change Vehicle Weights

```python
bus_weight: float = 2.0    # Buses get priority
truck_weight: float = 1.5  # Trucks get some priority
car_weight: float = 1.0    # Normal weight
motorcycle_weight: float = 0.5  # Less priority
```

### Change Detection Settings

Edit `vehicle_detection_improved.py`, find `VehicleDetector`:

```python
confidence_threshold=0.5  # Lower = more detections, more false positives
nms_threshold=0.4        # Lower = fewer overlapping boxes
```

---

## 🔧 Troubleshooting Quick Fixes

### Camera not found
```bash
# Try different camera indices
python3 camera_capture_improved.py 1 single
python3 camera_capture_improved.py 2 single
```

### YOLO files missing
```bash
# Download automatically
./setup.sh

# Or manually
wget https://pjreddie.com/media/files/yolov3.weights
wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
```

### Low accuracy
```python
# Lower confidence threshold in vehicle_detection_improved.py
confidence_threshold=0.3  # Instead of 0.5
```

### System too slow
```python
# Reduce camera resolution in camera_capture_improved.py
camera.resolution = (1280, 720)  # Instead of (1920, 1080)
```

---

## 📊 Data Analysis Quick Commands

```bash
# View summary
python3 visualize_data.py

# Export report
python3 visualize_data.py --export

# Show only vehicle chart
python3 visualize_data.py --chart vehicles

# Show only timing chart
python3 visualize_data.py --chart time
```

---

## 🧪 Testing

```bash
# Run all tests
python3 test_system.py

# Check specific component
python3 -c "from vehicle_detection_improved import VehicleDetector; print('OK')"
```

---

## 💾 Backup Data

```bash
# Backup all data
tar -czf traffic_backup_$(date +%Y%m%d).tar.gz traffic_data/

# Restore backup
tar -xzf traffic_backup_20241214.tar.gz
```

---

## 🔄 Reset/Clear Data

```bash
# Clear all captured images (keeps data)
rm -rf traffic_data/captures/*

# Clear all data (fresh start)
rm -rf traffic_data/
rm signal_timing_history.json
rm traffic_system.log
```

---

## 📈 Performance Tips

### For Better Speed:
1. Use YOLOv3-tiny instead of YOLOv3
2. Reduce camera resolution
3. Increase cycle interval
4. Enable GPU (requires CUDA)

### For Better Accuracy:
1. Use YOLOv4 instead of YOLOv3
2. Increase camera resolution
3. Better lighting conditions
4. Lower confidence threshold

### For Better Timing:
1. Use adaptive algorithm
2. Let system collect data (10+ cycles)
3. Adjust vehicle weights for your needs
4. Fine-tune min/max times

---

## 🎯 Example Workflows

### Morning Setup (First Time)
```bash
./setup.sh                    # Install everything
python3 test_system.py        # Verify setup
python3 traffic_management_system.py --mode single  # Test run
```

### Daily Operation
```bash
# Start continuous monitoring
python3 traffic_management_system.py --mode continuous --interval 30

# Check progress in another terminal
tail -f traffic_system.log

# View statistics
python3 visualize_data.py
```

### End of Day Analysis
```bash
python3 visualize_data.py --export
# Check traffic_report_*.txt file
```

---

## 📞 Quick Help

```bash
# System help
python3 traffic_management_system.py --help

# Visualization help
python3 visualize_data.py --help

# View logs
tail -f traffic_system.log

# Check data
cat traffic_data/cycle_data.json | python3 -m json.tool | less
```

---

## 🎓 Learning Paths

### Beginner (Just Testing)
1. Run `./setup.sh`
2. Run single cycle
3. View the captured images
4. Check the logs

### Intermediate (Understanding)
1. Run with different algorithms
2. Compare results
3. View statistics
4. Modify configurations

### Advanced (Customization)
1. Edit algorithm parameters
2. Add new vehicle types
3. Modify weighting system
4. Integrate with hardware

---

## 🔗 Useful Links

- YOLO Project: https://pjreddie.com/darknet/yolo/
- OpenCV Docs: https://docs.opencv.org/
- Python CV Tutorial: https://opencv-python-tutroals.readthedocs.io/

---

**Last Updated**: December 2024  
**Version**: 2.0
