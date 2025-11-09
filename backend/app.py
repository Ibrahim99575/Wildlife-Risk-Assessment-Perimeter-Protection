"""
Wildlife Risk Assessment - Main Backend Application
Advanced perimeter protection system with AI-powered detection
"""

from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import os
import sys

# Add parent directory to path to access frontend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import custom services
from services.detection_service import DetectionService
from services.alert_service import AlertService
from services.camera_service import CameraService
from api.routes import register_routes
from models.database import init_db

# Initialize Flask app with template and static folders pointing to frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'public')
app = Flask(__name__, 
            static_folder=frontend_path,
            static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for frontend communication
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Create necessary directories first
os.makedirs('logs', exist_ok=True)
os.makedirs('recordings', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('../database', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize services
detection_service = DetectionService()
alert_service = AlertService()
camera_service = CameraService()

# Initialize database
init_db()

# Register API routes
register_routes(app, detection_service, alert_service, camera_service)

@app.route('/')
def index():
    """Serve the main dashboard"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'name': 'Wildlife Risk Assessment API',
        'version': '2.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'features': [
            'Real-time wildlife detection with YOLOv8',
            'Multi-species identification',
            'Distance estimation',
            'SMS and Email alerts',
            'Video recording and streaming',
            'Multi-camera support',
            'Historical analytics'
        ]
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'detection': detection_service.is_ready(),
            'camera': camera_service.is_available(),
            'alerts': alert_service.is_configured()
        }
    })

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

@socketio.on('start_detection')
def handle_start_detection(data):
    """Start detection on specified camera"""
    camera_id = data.get('camera_id', 0)
    logger.info(f'Starting detection on camera {camera_id}')
    camera_service.start_camera(camera_id)
    emit('detection_started', {'camera_id': camera_id})

@socketio.on('stop_detection')
def handle_stop_detection(data):
    """Stop detection on specified camera"""
    camera_id = data.get('camera_id', 0)
    logger.info(f'Stopping detection on camera {camera_id}')
    camera_service.stop_camera(camera_id)
    emit('detection_stopped', {'camera_id': camera_id})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('recordings', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    logger.info('Starting Wildlife Risk Assessment System...')
    
    # Run the application (debug=False for faster startup with heavy AI libraries)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
