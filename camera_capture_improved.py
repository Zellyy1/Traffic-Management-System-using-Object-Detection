import cv2
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import threading
import queue
import logging


class CameraCapture:
    """Enhanced camera capture system with error handling and multi-camera support"""
    
    def __init__(self, camera_index: int = 0, output_dir: str = "captures"):
        """
        Initialize camera capture system
        
        Args:
            camera_index: Camera device index
            output_dir: Directory to save captured images
        """
        self.camera_index = camera_index
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.cap = None
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=10)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Camera settings
        self.resolution = (1920, 1080)  # Default HD resolution
        self.fps = 30
    
    def initialize_camera(self) -> bool:
        """
        Initialize camera with error handling and retry logic
        
        Returns:
            True if successful, False otherwise
        """
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempting to open camera {self.camera_index} (attempt {attempt + 1}/{max_retries})")
                
                self.cap = cv2.VideoCapture(self.camera_index)
                
                if not self.cap.isOpened():
                    raise RuntimeError("Camera failed to open")
                
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                
                # Verify camera is working by reading a test frame
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    raise RuntimeError("Camera opened but cannot read frames")
                
                self.logger.info(f"Camera {self.camera_index} initialized successfully")
                self.logger.info(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Camera initialization failed: {e}")
                
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        
        self.logger.error("Failed to initialize camera after all retries")
        return False
    
    def capture_single_image(self, filename: Optional[str] = None) -> Optional[str]:
        """
        Capture a single image from the camera
        
        Args:
            filename: Custom filename (optional)
            
        Returns:
            Path to saved image or None if failed
        """
        if self.cap is None or not self.cap.isOpened():
            if not self.initialize_camera():
                return None
        
        try:
            # Read frame
            ret, frame = self.cap.read()
            
            if not ret or frame is None:
                self.logger.error("Failed to read frame from camera")
                return None
            
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
            
            # Ensure filename has extension
            if not filename.endswith(('.jpg', '.jpeg', '.png')):
                filename += '.jpg'
            
            # Save image
            output_path = self.output_dir / filename
            
            # Apply image quality settings
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 95]
            success = cv2.imwrite(str(output_path), frame, encode_params)
            
            if success:
                self.logger.info(f"Image saved: {output_path}")
                return str(output_path)
            else:
                self.logger.error("Failed to save image")
                return None
                
        except Exception as e:
            self.logger.error(f"Error during capture: {e}")
            return None
    
    def capture_burst(self, count: int = 5, interval: float = 0.5) -> List[str]:
        """
        Capture multiple images in quick succession
        
        Args:
            count: Number of images to capture
            interval: Time between captures in seconds
            
        Returns:
            List of paths to saved images
        """
        captured_images = []
        
        for i in range(count):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"burst_{timestamp}_{i:03d}.jpg"
            
            image_path = self.capture_single_image(filename)
            if image_path:
                captured_images.append(image_path)
            
            if i < count - 1:  # Don't sleep after last capture
                time.sleep(interval)
        
        self.logger.info(f"Burst capture complete: {len(captured_images)}/{count} images saved")
        return captured_images
    
    def start_continuous_capture(self, interval: float = 5.0):
        """
        Start continuous image capture in a background thread
        
        Args:
            interval: Time between captures in seconds
        """
        if self.is_running:
            self.logger.warning("Continuous capture already running")
            return
        
        self.is_running = True
        
        def capture_loop():
            self.logger.info("Starting continuous capture...")
            
            while self.is_running:
                try:
                    image_path = self.capture_single_image()
                    
                    if image_path:
                        self.frame_queue.put(image_path)
                    else:
                        self.logger.warning("Failed to capture image, attempting to reinitialize camera")
                        if not self.initialize_camera():
                            self.logger.error("Camera reinitialization failed")
                            time.sleep(5)  # Wait before retry
                    
                    # Wait for next capture
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Error in continuous capture: {e}")
                    time.sleep(1)
            
            self.logger.info("Continuous capture stopped")
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=capture_loop, daemon=True)
        self.capture_thread.start()
    
    def stop_continuous_capture(self):
        """Stop continuous capture"""
        if self.is_running:
            self.logger.info("Stopping continuous capture...")
            self.is_running = False
            
            if hasattr(self, 'capture_thread'):
                self.capture_thread.join(timeout=5)
    
    def get_latest_capture(self, timeout: float = 1.0) -> Optional[str]:
        """
        Get the latest captured image path from queue
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Path to latest image or None
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_camera_info(self) -> dict:
        """
        Get information about the camera
        
        Returns:
            Dictionary with camera properties
        """
        if self.cap is None or not self.cap.isOpened():
            return {"status": "Camera not initialized"}
        
        return {
            "status": "Active",
            "index": self.camera_index,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": int(self.cap.get(cv2.CAP_PROP_FPS)),
            "backend": self.cap.getBackendName()
        }
    
    def release(self):
        """Release camera resources"""
        self.stop_continuous_capture()
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.logger.info("Camera released")
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize_camera()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


def main():
    """Main function for testing camera capture"""
    import sys
    
    # Parse command line arguments
    camera_index = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    mode = sys.argv[2] if len(sys.argv) > 2 else "single"
    
    print(f"\nCamera Capture System")
    print(f"Camera Index: {camera_index}")
    print(f"Mode: {mode}\n")
    
    # Create camera capture instance
    with CameraCapture(camera_index=camera_index) as camera:
        # Display camera info
        info = camera.get_camera_info()
        print("Camera Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
        
        if mode == "single":
            # Capture single image
            print("Capturing single image...")
            image_path = camera.capture_single_image()
            if image_path:
                print(f"Success! Image saved to: {image_path}")
            else:
                print("Failed to capture image")
        
        elif mode == "burst":
            # Capture burst
            count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
            print(f"Capturing burst of {count} images...")
            images = camera.capture_burst(count=count)
            print(f"Captured {len(images)} images")
        
        elif mode == "continuous":
            # Continuous capture
            interval = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
            duration = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0
            
            print(f"Starting continuous capture (interval: {interval}s, duration: {duration}s)")
            print("Press Ctrl+C to stop early\n")
            
            camera.start_continuous_capture(interval=interval)
            
            try:
                end_time = time.time() + duration
                while time.time() < end_time:
                    image_path = camera.get_latest_capture(timeout=1.0)
                    if image_path:
                        print(f"Captured: {Path(image_path).name}")
            except KeyboardInterrupt:
                print("\nStopping capture...")
            
            camera.stop_continuous_capture()
            print("Capture complete!")
        
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: single, burst, continuous")


if __name__ == "__main__":
    main()
