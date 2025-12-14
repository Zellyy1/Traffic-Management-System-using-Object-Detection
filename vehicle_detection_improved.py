import cv2
import numpy as np
import os
from typing import List, Tuple, Dict
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DetectedVehicle:
    """Data class to store vehicle detection information"""
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    class_name: str
    center: Tuple[int, int]

class VehicleDetector:
    """Enhanced vehicle detection system using YOLO"""
    
    # Vehicle class IDs in COCO dataset
    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle', 
        5: 'bus',
        7: 'truck'
    }
    
    def __init__(self, model_path: str = "yolov3.weights", 
                 config_path: str = "yolov3.cfg",
                 names_path: str = "coco.names",
                 confidence_threshold: float = 0.5,
                 nms_threshold: float = 0.4):
        """
        Initialize the vehicle detector
        
        Args:
            model_path: Path to YOLO weights file
            config_path: Path to YOLO config file
            names_path: Path to class names file
            confidence_threshold: Minimum confidence for detections
            nms_threshold: Non-maximum suppression threshold
        """
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        
        # Validate files exist
        if not all(os.path.exists(p) for p in [model_path, config_path, names_path]):
            raise FileNotFoundError(
                "Required model files not found. Please ensure yolov3.weights, "
                "yolov3.cfg, and coco.names are in the project directory."
            )
        
        # Load YOLO model
        try:
            self.net = cv2.dnn.readNet(model_path, config_path)
            # Use CUDA if available for better performance
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
            else:
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
        
        # Load class names
        with open(names_path, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        
        # Get output layer names
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
    
    def detect_vehicles(self, image: np.ndarray) -> List[DetectedVehicle]:
        """
        Detect vehicles in an image
        
        Args:
            image: Input image as numpy array
            
        Returns:
            List of DetectedVehicle objects
        """
        height, width = image.shape[:2]
        
        # Prepare image for YOLO
        blob = cv2.dnn.blobFromImage(
            image, 1/255.0, (416, 416), 
            swapRB=True, crop=False
        )
        
        # Perform detection
        self.net.setInput(blob)
        outputs = self.net.forward(self.output_layers)
        
        # Process detections
        boxes = []
        confidences = []
        class_ids = []
        
        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # Filter for vehicles only
                if confidence > self.confidence_threshold and class_id in self.VEHICLE_CLASSES:
                    # Get bounding box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Apply non-maximum suppression to remove duplicate detections
        indices = cv2.dnn.NMSBoxes(
            boxes, confidences, 
            self.confidence_threshold, 
            self.nms_threshold
        )
        
        # Create DetectedVehicle objects
        vehicles = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                center_x = x + w // 2
                center_y = y + h // 2
                
                vehicle = DetectedVehicle(
                    bbox=(x, y, w, h),
                    confidence=confidences[i],
                    class_name=self.VEHICLE_CLASSES[class_ids[i]],
                    center=(center_x, center_y)
                )
                vehicles.append(vehicle)
        
        return vehicles
    
    def draw_detections(self, image: np.ndarray, vehicles: List[DetectedVehicle]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            vehicles: List of detected vehicles
            
        Returns:
            Image with drawn detections
        """
        result = image.copy()
        
        # Define colors for different vehicle types
        colors = {
            'car': (0, 255, 0),      # Green
            'motorcycle': (255, 0, 0),  # Blue
            'bus': (0, 0, 255),      # Red
            'truck': (255, 255, 0)   # Cyan
        }
        
        for vehicle in vehicles:
            x, y, w, h = vehicle.bbox
            color = colors.get(vehicle.class_name, (0, 255, 0))
            
            # Draw bounding box
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            
            # Draw label with confidence
            label = f"{vehicle.class_name.capitalize()}: {vehicle.confidence:.2f}"
            
            # Calculate label size and position
            (label_w, label_h), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Draw label background
            cv2.rectangle(
                result, (x, y - label_h - 10), 
                (x + label_w, y), color, -1
            )
            
            # Draw label text
            cv2.putText(
                result, label, (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
        
        return result
    
    def get_vehicle_statistics(self, vehicles: List[DetectedVehicle]) -> Dict[str, int]:
        """
        Get statistics about detected vehicles
        
        Args:
            vehicles: List of detected vehicles
            
        Returns:
            Dictionary with vehicle counts by type
        """
        stats = {'total': len(vehicles)}
        for vehicle_type in self.VEHICLE_CLASSES.values():
            count = sum(1 for v in vehicles if v.class_name == vehicle_type)
            stats[vehicle_type] = count
        return stats


def detect_vehicles_from_image(image_path: str, output_path: str = None) -> int:
    """
    Detect vehicles in an image and optionally save the result
    
    Args:
        image_path: Path to input image
        output_path: Path to save output image (optional)
        
    Returns:
        Number of vehicles detected
    """
    # Validate input
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Failed to load image: {image_path}")
    
    # Initialize detector
    detector = VehicleDetector()
    
    # Detect vehicles
    vehicles = detector.detect_vehicles(image)
    
    # Get statistics
    stats = detector.get_vehicle_statistics(vehicles)
    print(f"\nVehicle Detection Results:")
    print(f"Total vehicles detected: {stats['total']}")
    for vehicle_type, count in stats.items():
        if vehicle_type != 'total' and count > 0:
            print(f"  {vehicle_type.capitalize()}: {count}")
    
    # Draw detections
    result_image = detector.draw_detections(image, vehicles)
    
    # Save or display
    if output_path:
        cv2.imwrite(output_path, result_image)
        print(f"\nResult saved to: {output_path}")
    else:
        cv2.imshow("Vehicle Detection", result_image)
        print("\nPress any key to close the window...")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return stats['total']


if __name__ == "__main__":
    import sys
    
    # Get image path from command line or prompt user
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter the path to the image: ").strip()
    
    try:
        vehicle_count = detect_vehicles_from_image(image_path, "detected_vehicles.jpg")
        
        # Save count to file for traffic signal adjustment
        with open("vehicle_count.txt", "w") as f:
            f.write(str(vehicle_count))
        print(f"\nVehicle count saved to vehicle_count.txt")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
