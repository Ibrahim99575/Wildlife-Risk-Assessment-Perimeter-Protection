"""
Detection Service - Manages wildlife detection pipeline
"""

import cv2
import threading
import queue
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..'))

from ai_models.yolo_detector import WildlifeDetector

class DetectionService:
    """Service for managing wildlife detection"""
    
    def __init__(self):
        """Initialize detection service"""
        self.detector = None
        self.is_running = False
        self.detection_thread = None
        self.frame_queue = queue.Queue(maxsize=10)
        self.result_queue = queue.Queue(maxsize=10)
        
    def initialize(self):
        """Initialize the AI detector"""
        try:
            self.detector = WildlifeDetector()
            return True
        except Exception as e:
            print(f"Error initializing detector: {e}")
            return False
    
    def is_ready(self):
        """Check if detection service is ready"""
        return self.detector is not None
    
    def process_frame(self, frame):
        """
        Process a single frame
        
        Args:
            frame: Input video frame
            
        Returns:
            Detection results
        """
        if not self.is_ready():
            self.initialize()
        
        try:
            results = self.detector.process_frame(frame)
            return results
        except Exception as e:
            print(f"Error processing frame: {e}")
            return {'detections': [], 'max_danger_level': 'none', 'alerts': []}
    
    def annotate_frame(self, frame, results):
        """
        Annotate frame with detection results
        
        Args:
            frame: Input frame
            results: Detection results
            
        Returns:
            Annotated frame
        """
        if not self.is_ready():
            return frame
        
        return self.detector.annotate_frame(frame, results)
    
    def start_detection_thread(self):
        """Start background detection thread"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop)
        self.detection_thread.start()
        return True
    
    def stop_detection_thread(self):
        """Stop background detection thread"""
        self.is_running = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
    
    def _detection_loop(self):
        """Background detection loop"""
        while self.is_running:
            try:
                # Get frame from queue
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get(timeout=1)
                    
                    # Process frame
                    results = self.process_frame(frame)
                    
                    # Put results in queue
                    if not self.result_queue.full():
                        self.result_queue.put({
                            'results': results,
                            'timestamp': datetime.now().isoformat()
                        })
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in detection loop: {e}")
    
    def add_frame(self, frame):
        """Add frame to detection queue"""
        if not self.frame_queue.full():
            self.frame_queue.put(frame)
    
    def get_results(self):
        """Get detection results from queue"""
        if not self.result_queue.empty():
            return self.result_queue.get()
        return None
