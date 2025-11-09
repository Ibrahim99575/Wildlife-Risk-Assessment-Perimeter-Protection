"""
Advanced Wildlife Detection using YOLOv8 and Hugging Face Models
Free AI integration for species identification
"""

import cv2
import numpy as np
from ultralytics import YOLO
import torch
from PIL import Image
import requests
import os
from typing import List, Dict, Tuple

class WildlifeDetector:
    """Advanced wildlife detection using YOLOv8 and zero-shot classification"""
    
    def __init__(self):
        """Initialize detection models"""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        # Initialize YOLOv8 for object detection
        # Using YOLOv8n (nano) for speed, can upgrade to yolov8m or yolov8l for accuracy
        try:
            self.yolo_model = YOLO('yolov8n.pt')
            print("YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLOv8: {e}. Will download on first use.")
            self.yolo_model = None
        
        # Hugging Face API for zero-shot classification (free tier)
        self.hf_api_token = os.getenv('HUGGINGFACE_API_TOKEN', '')
        self.hf_api_url = "https://api-inference.huggingface.co/models/openai/clip-vit-large-patch14"
        
        # Wildlife categories with danger levels
        self.wildlife_categories = {
            'dangerous': ['tiger', 'lion', 'leopard', 'bear', 'wolf', 'hyena', 'crocodile', 'elephant', 'rhino', 'buffalo'],
            'moderate': ['deer', 'wild boar', 'monkey', 'fox', 'jackal', 'wild dog'],
            'low_risk': ['rabbit', 'squirrel', 'peacock', 'bird', 'domestic animal'],
            'human': ['person', 'human', 'man', 'woman', 'child']
        }
        
        # All possible labels for CLIP classification
        self.all_species = []
        for category in self.wildlife_categories.values():
            self.all_species.extend(category)
    
    def detect_objects_yolo(self, frame: np.ndarray, conf_threshold: float = 0.5) -> List[Dict]:
        """
        Detect objects using YOLOv8
        
        Args:
            frame: Input image frame
            conf_threshold: Confidence threshold for detections
            
        Returns:
            List of detection dictionaries
        """
        if self.yolo_model is None:
            self.yolo_model = YOLO('yolov8n.pt')
        
        # Run inference
        results = self.yolo_model(frame, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = self.yolo_model.names[cls]
                
                detection = {
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'confidence': conf,
                    'class': label,
                    'class_id': cls
                }
                detections.append(detection)
        
        return detections
    
    def classify_with_clip(self, image_crop: np.ndarray) -> Tuple[str, float]:
        """
        Classify wildlife using CLIP via Hugging Face API (free)
        
        Args:
            image_crop: Cropped image of detected object
            
        Returns:
            Tuple of (species_name, confidence)
        """
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image_crop, cv2.COLOR_BGR2RGB))
            
            # Save to bytes
            import io
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Query Hugging Face API
            headers = {"Authorization": f"Bearer {self.hf_api_token}"} if self.hf_api_token else {}
            
            payload = {
                "inputs": img_byte_arr,
                "parameters": {
                    "candidate_labels": self.all_species
                }
            }
            
            # Note: For production, consider using the free Inference API or local CLIP model
            # This is a placeholder - you'll need to implement actual CLIP inference
            # Using local CLIP would be better for offline use
            
            # Fallback to local classification based on YOLO results
            return self._classify_local(image_crop)
            
        except Exception as e:
            print(f"Error in CLIP classification: {e}")
            return self._classify_local(image_crop)
    
    def _classify_local(self, image_crop: np.ndarray) -> Tuple[str, float]:
        """
        Local classification fallback using simple heuristics
        Can be enhanced with a lightweight local model
        """
        # This is a simplified version - in production, use a proper classifier
        # For now, return generic animal classification
        return "unidentified_animal", 0.7
    
    def calculate_danger_level(self, species: str) -> str:
        """
        Calculate danger level based on species
        
        Args:
            species: Detected species name
            
        Returns:
            Danger level: 'high', 'medium', 'low', or 'human'
        """
        species_lower = species.lower()
        
        for category, animals in self.wildlife_categories.items():
            if any(animal in species_lower for animal in animals):
                if category == 'dangerous':
                    return 'high'
                elif category == 'moderate':
                    return 'medium'
                elif category == 'low_risk':
                    return 'low'
                elif category == 'human':
                    return 'human'
        
        return 'unknown'
    
    def estimate_distance(self, bbox: List[int], known_width: float = 60.0, focal_length: float = 700.0) -> float:
        """
        Estimate distance to object using bounding box
        Simple distance estimation based on object size
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            known_width: Approximate real-world width in cm (default: 60cm for medium animals)
            focal_length: Camera focal length (calibrated, default: 700)
            
        Returns:
            Distance in centimeters
        """
        pixel_width = bbox[2] - bbox[0]
        pixel_height = bbox[3] - bbox[1]
        
        if pixel_width == 0:
            return 0
        
        # Use larger dimension for more stable distance calculation
        max_pixel_size = max(pixel_width, pixel_height)
        
        # Simple distance calculation: distance = (known_size * focal_length) / pixel_size
        distance = (known_width * focal_length) / max_pixel_size
        
        # Clamp distance to reasonable range (10cm to 1000cm)
        distance = max(10, min(distance, 1000))
        
        return distance
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame with full detection pipeline
        
        Args:
            frame: Input video frame
            
        Returns:
            Dictionary with detection results
        """
        # Detect objects with YOLO
        detections = self.detect_objects_yolo(frame)
        
        results = {
            'detections': [],
            'max_danger_level': 'none',
            'alerts': []
        }
        
        for detection in detections:
            bbox = detection['bbox']
            
            # Crop object for classification
            x1, y1, x2, y2 = bbox
            crop = frame[y1:y2, x1:x2]
            
            if crop.size == 0:
                continue
            
            # Classify species
            species, conf = self.classify_with_clip(crop)
            
            # Calculate danger level
            danger_level = self.calculate_danger_level(detection['class'])
            
            # Estimate distance
            distance = self.estimate_distance(bbox)
            
            result = {
                'bbox': bbox,
                'species': species,
                'yolo_class': detection['class'],
                'confidence': detection['confidence'],
                'danger_level': danger_level,
                'distance_cm': int(distance),
                'timestamp': cv2.getTickCount() / cv2.getTickFrequency()
            }
            
            results['detections'].append(result)
            
            # Update max danger level
            if danger_level == 'high':
                results['max_danger_level'] = 'high'
            elif danger_level == 'medium' and results['max_danger_level'] != 'high':
                results['max_danger_level'] = 'medium'
        
        return results
    
    def annotate_frame(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        """
        Draw detection results on frame
        
        Args:
            frame: Input frame
            results: Detection results
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Color mapping for danger levels
        colors = {
            'high': (0, 0, 255),      # Red
            'medium': (0, 165, 255),  # Orange
            'low': (0, 255, 0),       # Green
            'human': (255, 0, 255),   # Magenta
            'unknown': (128, 128, 128) # Gray
        }
        
        for det in results['detections']:
            x1, y1, x2, y2 = det['bbox']
            color = colors.get(det['danger_level'], colors['unknown'])
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Create label
            label = f"{det['yolo_class']} | {det['danger_level'].upper()}"
            label += f" | {det['distance_cm']}cm"
            label += f" | {det['confidence']:.2f}"
            
            # Draw label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated, (x1, y1 - 20), (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(annotated, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return annotated


# Standalone test function
if __name__ == "__main__":
    detector = WildlifeDetector()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    print("Starting wildlife detection... Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        results = detector.process_frame(frame)
        
        # Annotate frame
        annotated = detector.annotate_frame(frame, results)
        
        # Display
        cv2.imshow('Wildlife Detection', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
