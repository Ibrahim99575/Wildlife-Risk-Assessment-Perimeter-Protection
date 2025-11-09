"""
API Routes - REST endpoints for the application
"""

from flask import jsonify, request, Response
import cv2
import numpy as np
from datetime import datetime

def register_routes(app, detection_service, alert_service, camera_service):
    """Register all API routes"""
    
    @app.route('/api/cameras', methods=['GET'])
    def get_cameras():
        """Get list of all cameras"""
        cameras = camera_service.get_camera_list()
        return jsonify({'cameras': cameras})
    
    @app.route('/api/cameras/<int:camera_id>/start', methods=['POST'])
    def start_camera(camera_id):
        """Start a specific camera"""
        success = camera_service.start_camera(camera_id)
        return jsonify({'success': success, 'camera_id': camera_id})
    
    @app.route('/api/cameras/<int:camera_id>/stop', methods=['POST'])
    def stop_camera(camera_id):
        """Stop a specific camera"""
        success = camera_service.stop_camera(camera_id)
        return jsonify({'success': success, 'camera_id': camera_id})
    
    @app.route('/api/cameras/<int:camera_id>/stream')
    def video_stream(camera_id):
        """Video stream endpoint"""
        def generate():
            # Initialize detection service if needed
            if not detection_service.is_ready():
                detection_service.initialize()
            
            while True:
                frame = camera_service.get_frame(camera_id)
                if frame is None:
                    break
                
                # Process frame
                results = detection_service.process_frame(frame)
                
                # Annotate frame
                annotated = detection_service.annotate_frame(frame, results)
                
                # Write frame to video file if recording
                camera_service.write_frame_if_recording(camera_id, annotated)
                
                # Check for alerts
                if results['max_danger_level'] == 'high':
                    for det in results['detections']:
                        if det['danger_level'] == 'high':
                            alert_service.send_danger_alert(
                                'high',
                                det['yolo_class'],
                                det['distance_cm'],
                                camera_id
                            )
                
                # Encode frame
                ret, buffer = cv2.imencode('.jpg', annotated)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    @app.route('/api/detection/analyze', methods=['POST'])
    def analyze_image():
        """Analyze a single image"""
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        # Read image
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400
        
        # Initialize detection service if needed
        if not detection_service.is_ready():
            detection_service.initialize()
        
        # Process frame
        results = detection_service.process_frame(frame)
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/alerts/history', methods=['GET'])
    def get_alert_history():
        """Get alert history"""
        limit = request.args.get('limit', 100, type=int)
        history = alert_service.get_alert_history(limit)
        return jsonify({'alerts': history, 'count': len(history)})
    
    @app.route('/api/alerts/test', methods=['POST'])
    def test_alert():
        """Test alert system"""
        data = request.json
        alert_type = data.get('type', 'test')
        
        if alert_type == 'sms':
            number = data.get('number')
            message = data.get('message', 'Test SMS from Wildlife Alert System')
            success = alert_service.send_sms(number, message)
        elif alert_type == 'email':
            email = data.get('email')
            subject = data.get('subject', 'Test Alert')
            body = data.get('body', 'This is a test email from Wildlife Alert System')
            success = alert_service.send_email(email, subject, body)
        else:
            success = False
        
        return jsonify({'success': success})
    
    @app.route('/api/recordings', methods=['GET'])
    def get_recordings():
        """Get list of recorded videos"""
        import os
        
        # Use absolute path
        recordings_dir = os.path.abspath('recordings')
        
        if not os.path.exists(recordings_dir):
            return jsonify({'recordings': []})
        
        recordings = []
        for filename in os.listdir(recordings_dir):
            # Support multiple video formats
            if filename.endswith(('.mp4', '.avi', '.webm')):
                filepath = os.path.join(recordings_dir, filename)
                stat = os.stat(filepath)
                recordings.append({
                    'filename': filename,
                    'size': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'url': f'/api/recordings/{filename}/stream'
                })
        
        recordings.sort(key=lambda x: x['created'], reverse=True)
        return jsonify({'recordings': recordings, 'count': len(recordings)})
    
    @app.route('/api/recordings/<filename>/stream')
    def stream_recording(filename):
        """Stream a recorded video file"""
        import os
        from flask import send_file, abort
        
        # Security check: ensure filename doesn't contain path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            abort(400, 'Invalid filename')
        
        # Support multiple video formats
        if not filename.endswith(('.mp4', '.avi', '.webm')):
            abort(400, 'Invalid file type')
        
        # Use absolute path
        recordings_dir = os.path.abspath('recordings')
        filepath = os.path.join(recordings_dir, filename)
        
        if not os.path.exists(filepath):
            abort(404, f'Recording not found: {filename}')
        
        # Determine MIME type based on file extension
        if filename.endswith('.webm'):
            mimetype = 'video/webm'
        elif filename.endswith('.avi'):
            mimetype = 'video/avi'
        else:
            mimetype = 'video/mp4'
        
        # Send file with proper headers for video streaming
        return send_file(
            filepath, 
            mimetype=mimetype,
            as_attachment=False,
            download_name=filename,
            conditional=True,
            max_age=3600
        )
    
    @app.route('/api/recordings/<filename>', methods=['DELETE'])
    def delete_recording(filename):
        """Delete a recorded video"""
        import os
        import time
        
        # Use absolute path
        recordings_dir = os.path.abspath('recordings')
        filepath = os.path.join(recordings_dir, filename)
        
        # Support multiple video formats
        if not os.path.exists(filepath) or not filename.endswith(('.mp4', '.avi', '.webm')):
            return jsonify({'error': 'Recording not found'}), 404
        
        try:
            # Make sure recording is stopped first
            for camera_id in camera_service.cameras:
                camera_service.stop_recording(camera_id)
            
            # Wait a bit for file to be released
            time.sleep(0.5)
            
            # Try to delete
            if os.path.exists(filepath):
                os.remove(filepath)
                return jsonify({'success': True, 'message': 'Recording deleted'})
            else:
                return jsonify({'error': 'File already deleted'}), 404
        except PermissionError:
            return jsonify({'error': 'File is in use. Stop recording first.'}), 403
        except Exception as e:
            return jsonify({'error': f'Failed to delete: {str(e)}'}), 500
    
    @app.route('/api/cameras/<int:camera_id>/recording/start', methods=['POST'])
    def start_recording(camera_id):
        """Start recording on a camera"""
        success = camera_service.start_recording(camera_id)
        return jsonify({'success': success, 'camera_id': camera_id})
    
    @app.route('/api/cameras/<int:camera_id>/recording/stop', methods=['POST'])
    def stop_recording(camera_id):
        """Stop recording on a camera"""
        success = camera_service.stop_recording(camera_id)
        return jsonify({'success': success, 'camera_id': camera_id})
    
    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        """Get system statistics"""
        alert_history = alert_service.get_alert_history()
        
        # Calculate statistics
        total_alerts = len(alert_history)
        danger_alerts = sum(1 for a in alert_history if a.get('data', {}).get('danger_level') == 'high')
        
        stats = {
            'total_alerts': total_alerts,
            'danger_alerts': danger_alerts,
            'cameras_active': sum(1 for c in camera_service.get_camera_list() if c['active']),
            'cameras_recording': sum(1 for c in camera_service.get_camera_list() if c['recording']),
            'detection_ready': detection_service.is_ready(),
            'alert_system_ready': alert_service.is_configured()
        }
        
        return jsonify(stats)
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """Get current configuration"""
        config = {
            'detection': {
                'enabled': detection_service.is_ready(),
                'model': 'YOLOv8'
            },
            'alerts': {
                'sms_enabled': alert_service.is_configured(),
                'email_enabled': bool(alert_service.sender_email)
            },
            'cameras': camera_service.get_camera_list()
        }
        return jsonify(config)
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """Update configuration"""
        data = request.json
        # Implement configuration updates
        return jsonify({'success': True, 'message': 'Configuration updated'})
