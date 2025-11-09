"""
Enhanced Main Application - Improved version with advanced features
This is a drop-in replacement for the original main.py with better integration
"""

import cv2
import numpy as np
from datetime import datetime
import os
import sys
import time
import argparse

# Add backend to path
sys.path.append('backend')
sys.path.append('ai_models')

from backend.services.detection_service import DetectionService
from backend.services.alert_service import AlertService
from backend.services.camera_service import CameraService
from backend.models.database import init_db, save_detection, save_alert

# Import audio playback
try:
    import pygame
    pygame.init()
    AUDIO_ENABLED = True
except ImportError:
    print("pygame not installed. Audio alerts disabled.")
    AUDIO_ENABLED = False


class WildlifeMonitoringSystem:
    """Enhanced Wildlife Monitoring System"""
    
    def __init__(self, camera_id=0, enable_gui=True):
        """Initialize the monitoring system"""
        print("🦁 Wildlife Risk Assessment System v2.0")
        print("Initializing...")
        
        # Initialize database
        init_db()
        
        # Initialize services
        self.detection_service = DetectionService()
        self.detection_service.initialize()
        
        self.alert_service = AlertService()
        self.camera_service = CameraService()
        
        # Start camera
        self.camera_id = camera_id
        self.camera_service.add_camera(camera_id)
        
        # Configuration
        self.enable_gui = enable_gui
        self.recording = False
        self.detection_history = []
        self.alert_cooldown = {}
        self.min_alert_interval = 60  # seconds
        
        # Counters for alert logic
        self.danger_count = 0
        self.safe_count = 0
        self.reset_time = time.time()
        
        # Audio files
        self.audio_files = {
            'danger': 'audio/Divert.mp3',
            'proximity': 'audio/CCTV.mp3',
            'normal': 'audio/monitored.mp3',
            'start': 'audio/ok.mp3',
            'stop': 'audio/off.mp3'
        }
        
        print("✅ System initialized successfully")
    
    def play_audio(self, audio_type):
        """Play audio alert"""
        if not AUDIO_ENABLED:
            return
        
        audio_file = self.audio_files.get(audio_type)
        if audio_file and os.path.exists(audio_file):
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"Error playing audio: {e}")
    
    def should_send_alert(self, alert_type):
        """Check if enough time has passed to send alert"""
        current_time = time.time()
        
        if alert_type in self.alert_cooldown:
            elapsed = current_time - self.alert_cooldown[alert_type]
            if elapsed < self.min_alert_interval:
                return False
        
        self.alert_cooldown[alert_type] = current_time
        return True
    
    def process_detections(self, frame, results):
        """Process detection results and trigger appropriate responses"""
        current_time = time.time()
        
        # Reset counters every 10 seconds
        if current_time - self.reset_time > 10:
            self.danger_count = 0
            self.safe_count = 0
            self.reset_time = current_time
        
        # Update counters
        if results['max_danger_level'] == 'high':
            self.danger_count += 1
        else:
            self.safe_count += 1
        
        print(f"Danger Count: {self.danger_count} | Safe Count: {self.safe_count}")
        
        # Process each detection
        for detection in results['detections']:
            danger_level = detection['danger_level']
            distance = detection['distance_cm']
            species = detection['yolo_class']
            
            # Save to database
            save_detection(self.camera_id, detection)
            
            # High danger alert
            if danger_level == 'high' and self.danger_count >= 15:
                if self.should_send_alert('high_danger'):
                    print(f"⚠️ HIGH DANGER: {species} detected!")
                    self.alert_service.send_danger_alert('high', species, distance, self.camera_id)
                    self.play_audio('danger')
                    
                    # Save alert to database
                    save_alert('danger', self.camera_id, 
                             f"High danger: {species} at {distance}cm",
                             self.alert_service.farmer_numbers + self.alert_service.forest_numbers,
                             detection)
            
            # Proximity alert (human detection)
            elif danger_level == 'human' and distance <= 30:
                if self.should_send_alert('proximity'):
                    print(f"⚠️ PROXIMITY ALERT: Person at {distance}cm")
                    self.alert_service.send_proximity_alert(distance, self.camera_id)
                    self.play_audio('proximity')
            
            # Medium danger alert
            elif danger_level == 'medium' and 30 < distance <= 50:
                if self.should_send_alert('medium_danger'):
                    print(f"⚠️ ALERT: {species} detected at {distance}cm")
                    self.alert_service.send_danger_alert('medium', species, distance, self.camera_id)
                    self.play_audio('normal')
    
    def run(self):
        """Main monitoring loop"""
        print("\n🚀 Starting Wildlife Monitoring...")
        print("Press 'q' to quit, 'r' to toggle recording, 's' to take snapshot")
        
        self.play_audio('start')
        
        # Setup window if GUI is enabled
        if self.enable_gui:
            window_name = 'Wildlife Risk Assessment System'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1280, 720)
        
        frame_count = 0
        fps_start_time = time.time()
        fps = 0
        
        try:
            while True:
                # Get frame
                frame = self.camera_service.get_frame(self.camera_id)
                
                if frame is None:
                    print("Failed to get frame from camera")
                    time.sleep(0.1)
                    continue
                
                # Process frame with AI detection
                results = self.detection_service.process_frame(frame)
                
                # Annotate frame
                annotated_frame = self.detection_service.annotate_frame(frame, results)
                
                # Process detections and trigger alerts
                if results['detections']:
                    self.process_detections(frame, results)
                
                # Record if enabled
                if self.recording:
                    camera = self.camera_service.cameras.get(self.camera_id)
                    if camera:
                        camera.write_frame(annotated_frame)
                
                # Calculate FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    fps = 30 / (time.time() - fps_start_time)
                    fps_start_time = time.time()
                
                # Add overlays
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(annotated_frame, f"TIME: {timestamp}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"FPS: {fps:.1f}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                if self.recording:
                    cv2.putText(annotated_frame, "● REC", 
                               (annotated_frame.shape[1] - 120, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Display frame
                if self.enable_gui:
                    cv2.imshow(window_name, annotated_frame)
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        print("\n🛑 Shutting down...")
                        self.play_audio('stop')
                        self.alert_service.send_system_alert("System stopped by user", self.camera_id)
                        break
                    elif key == ord('r'):
                        self.toggle_recording()
                    elif key == ord('s'):
                        self.save_snapshot(annotated_frame)
                else:
                    # Small delay if no GUI
                    time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        finally:
            self.cleanup()
    
    def toggle_recording(self):
        """Toggle video recording"""
        if not self.recording:
            if self.camera_service.start_recording(self.camera_id):
                self.recording = True
                print("📹 Recording started")
        else:
            self.camera_service.stop_recording(self.camera_id)
            self.recording = False
            print("⏹️ Recording stopped")
    
    def save_snapshot(self, frame):
        """Save a snapshot of current frame"""
        os.makedirs('snapshots', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshots/snapshot_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Snapshot saved: {filename}")
    
    def cleanup(self):
        """Cleanup resources"""
        print("🧹 Cleaning up...")
        
        if self.recording:
            self.camera_service.stop_recording(self.camera_id)
        
        self.camera_service.cleanup()
        
        if self.enable_gui:
            cv2.destroyAllWindows()
        
        if AUDIO_ENABLED:
            pygame.quit()
        
        print("✅ Cleanup complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Wildlife Risk Assessment System')
    parser.add_argument('--camera', type=int, default=0, help='Camera ID (default: 0)')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI')
    args = parser.parse_args()
    
    # Create and run system
    system = WildlifeMonitoringSystem(
        camera_id=args.camera,
        enable_gui=not args.no_gui
    )
    
    system.run()


if __name__ == "__main__":
    main()
