#!/bin/bash

# Smart Adaptive Traffic Management System
# Quick Start Setup Script

echo "=============================================="
echo "Traffic Management System - Quick Setup"
echo "=============================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Install Python packages
echo "Installing required Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python packages installed successfully"
else
    echo "❌ Failed to install Python packages"
    exit 1
fi
echo ""

# Check for YOLO model files
echo "Checking for YOLO model files..."
MISSING_FILES=0

if [ ! -f "yolov3.weights" ]; then
    echo "⚠️  yolov3.weights not found"
    MISSING_FILES=1
fi

if [ ! -f "yolov3.cfg" ]; then
    echo "⚠️  yolov3.cfg not found"
    MISSING_FILES=1
fi

if [ ! -f "coco.names" ]; then
    echo "⚠️  coco.names not found"
    MISSING_FILES=1
fi

if [ $MISSING_FILES -eq 1 ]; then
    echo ""
    echo "YOLO model files are missing. Would you like to download them now?"
    echo "This will download approximately 240 MB of data."
    read -p "Download YOLO files? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Downloading YOLO model files..."
        
        # Download weights
        if [ ! -f "yolov3.weights" ]; then
            echo "Downloading yolov3.weights..."
            wget -q --show-progress https://pjreddie.com/media/files/yolov3.weights
        fi
        
        # Download config
        if [ ! -f "yolov3.cfg" ]; then
            echo "Downloading yolov3.cfg..."
            wget -q --show-progress https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg
        fi
        
        # Download class names
        if [ ! -f "coco.names" ]; then
            echo "Downloading coco.names..."
            wget -q --show-progress https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names
        fi
        
        echo "✅ YOLO files downloaded successfully"
    else
        echo "⚠️  Please download YOLO files manually:"
        echo "   - yolov3.weights: https://pjreddie.com/media/files/yolov3.weights"
        echo "   - yolov3.cfg: https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg"
        echo "   - coco.names: https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
    fi
else
    echo "✅ All YOLO model files found"
fi

echo ""
echo "=============================================="
echo "Setup Complete!"
echo "=============================================="
echo ""
echo "Quick Start Commands:"
echo ""
echo "1. Run a single detection cycle:"
echo "   python3 traffic_management_system.py --mode single"
echo ""
echo "2. Run continuous monitoring (30s intervals):"
echo "   python3 traffic_management_system.py --mode continuous"
echo ""
echo "3. Test camera capture:"
echo "   python3 camera_capture_improved.py 0 single"
echo ""
echo "4. View help for all options:"
echo "   python3 traffic_management_system.py --help"
echo ""
echo "For detailed documentation, see README.md"
echo ""
