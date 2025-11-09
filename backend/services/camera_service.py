"""
Camera Service - Manages multiple camera streams and recording
"""

import cv2
import threading
import queue
from datetime import datetime
import os
import numpy as np

class Camera:
    """Individual camera handler"""
    
    def __init__(self, camera_id, name="Camera"):
        """Initialize camera"""
        self.camera_id = camera_id
        self.name = f"{name}_{camera_id}"
        self.cap = None
        self.is_active = False
        self.frame_queue = queue.Queue(maxsize=5)
        self.recording = False
        self.video_writer = None
        self.last_frame = None
        
    def start(self):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if self.cap.isOpened():
                self.is_active = True
                return True
            return False
        except Exception as e:
            print(f"Error starting camera {self.camera_id}: {e}")
            return False
    
    def stop(self):
        """Stop camera capture"""
        self.is_active = False
        if self.cap:
            self.cap.release()
        self.stop_recording()
    
    def read_frame(self):
        """Read a frame from camera"""
        if not self.is_active or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame
            return frame
        return None
    
    def get_last_frame(self):
        """Get the last captured frame"""
        return self.last_frame
    
    def start_recording(self, output_path=None):
        """Start video recording"""
        if self.recording:
            return False
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"recordings/{self.name}_{timestamp}.webm"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Get frame dimensions
        if self.cap:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 20
            
            # Try VP8/VP9 (WebM) first - excellent browser support
            # Then fall back to other codecs
            codecs_to_try = [
                ('VP80', 'webm', 'VP8 (WebM)'),           # VP8 - excellent browser support
                ('VP90', 'webm', 'VP9 (WebM)'),           # VP9 - better compression
                ('MJPG', 'avi', 'MJPEG'),                 # MJPEG fallback
                ('XVID', 'avi', 'XVID'),                  # XVID fallback
            ]
            
            for codec, ext, codec_name in codecs_to_try:
                try:
                    # Update output path extension
                    output_path_test = f"recordings/{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                    fourcc = cv2.VideoWriter_fourcc(*codec)
                    test_writer = cv2.VideoWriter(output_path_test, fourcc, fps, (width, height))
                    
                    if test_writer.isOpened():
                        self.video_writer = test_writer
                        self.recording = True
                        print(f"Recording started: {output_path_test} ({codec_name} codec)")
                        return True
                    else:
                        test_writer.release()
                        # Clean up failed file
                        if os.path.exists(output_path_test):
                            os.remove(output_path_test)
                except Exception as e:
                    print(f"Codec {codec_name} failed: {e}")
                    continue
            
            print(f"Failed to start recording: No suitable codec available")
            return False
        
        return False
    
    def stop_recording(self):
        """Stop video recording"""
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        self.recording = False
    
    def write_frame(self, frame):
        """Write frame to video file"""
        if self.recording and self.video_writer:
            self.video_writer.write(frame)


class CameraService:
    """Service for managing multiple cameras"""
    
    def __init__(self):
        """Initialize camera service"""
        self.cameras = {}
        self.capture_threads = {}
        self.running = False
    
    def add_camera(self, camera_id, name=None):
        """
        Add a camera to the service
        
        Args:
            camera_id: Camera device ID or stream URL
            name: Optional camera name
            
        Returns:
            Success status
        """
        if camera_id in self.cameras:
            print(f"Camera {camera_id} already exists")
            return False
        
        camera_name = name or f"Camera"
        camera = Camera(camera_id, camera_name)
        
        if camera.start():
            self.cameras[camera_id] = camera
            print(f"Camera {camera_id} added successfully")
            return True
        else:
            print(f"Failed to start camera {camera_id}")
            return False
    
    def remove_camera(self, camera_id):
        """Remove a camera from the service"""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop()
            del self.cameras[camera_id]
            return True
        return False
    
    def start_camera(self, camera_id):
        """Start a specific camera"""
        if camera_id not in self.cameras:
            return self.add_camera(camera_id)
        
        camera = self.cameras[camera_id]
        if not camera.is_active:
            return camera.start()
        return True
    
    def stop_camera(self, camera_id):
        """Stop a specific camera"""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop()
            return True
        return False
    
    def get_frame(self, camera_id):
        """Get latest frame from camera"""
        if camera_id in self.cameras:
            return self.cameras[camera_id].read_frame()
        return None
    
    def get_camera_list(self):
        """Get list of all cameras"""
        return [{
            'id': cam_id,
            'name': cam.name,
            'active': cam.is_active,
            'recording': cam.recording
        } for cam_id, cam in self.cameras.items()]
    
    def start_recording(self, camera_id):
        """Start recording on a camera"""
        if camera_id in self.cameras:
            return self.cameras[camera_id].start_recording()
        return False
    
    def stop_recording(self, camera_id):
        """Stop recording on a camera"""
        if camera_id in self.cameras:
            self.cameras[camera_id].stop_recording()
            return True
        return False
    
    def write_frame_if_recording(self, camera_id, frame):
        """Write frame to video file if recording is active"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            if camera.recording:
                camera.write_frame(frame)
    
    def is_available(self):
        """Check if any camera is available"""
        # Try to access default camera
        cap = cv2.VideoCapture(0)
        available = cap.isOpened()
        cap.release()
        return available
    
    def cleanup(self):
        """Cleanup all cameras"""
        for camera_id in list(self.cameras.keys()):
            self.remove_camera(camera_id)
