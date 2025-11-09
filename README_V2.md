# 🦁 Wildlife Risk Assessment & Perimeter Protection System v2.0

## Advanced Full-Fledged Application

A comprehensive, AI-powered wildlife detection and perimeter protection system featuring real-time detection, multi-camera support, intelligent alerts, and a modern web dashboard.

## 🌟 Key Features

### 🤖 Advanced AI Detection
- **YOLOv8 Integration**: Real-time object detection with high accuracy
- **Multi-Species Classification**: Identifies specific animal species
- **Danger Level Assessment**: Automatic risk categorization (High/Medium/Low)
- **Distance Estimation**: Calculates object distance from camera
- **Human Detection**: Distinguishes between wildlife and humans

### 📹 Camera Management
- **Multi-Camera Support**: Monitor multiple locations simultaneously
- **Live Video Streaming**: Real-time video feed in web browser
- **Automatic Recording**: Triggers recording on detection
- **360° Servo Control**: Arduino-based camera rotation (hardware integration)

### ⚠️ Smart Alert System
- **SMS Alerts**: Instant notifications via Twilio
- **Email Notifications**: Detailed alerts with detection images
- **Multi-Recipient Support**: Alert farmers, forest officials simultaneously
- **Rate Limiting**: Prevents alert spam
- **Customizable Thresholds**: Configure sensitivity and distance triggers

### 💻 Modern Web Dashboard
- **Live Video Feed**: Monitor cameras in real-time
- **Detection Overlay**: Visual bounding boxes and labels
- **Alert History**: View all past alerts
- **Statistics Dashboard**: Track detections, alerts, system uptime
- **Settings Panel**: Configure system parameters
- **Responsive Design**: Works on desktop, tablet, and mobile

### 📊 Data Management
- **SQLite Database**: Stores all detection history
- **Analytics**: Track patterns and statistics
- **Export Capabilities**: Download detection reports
- **System Logs**: Comprehensive logging for debugging

## 🏗️ Architecture

```
Wildlife-Risk-Assessment-Perimeter-Protection/
├── backend/                    # Flask backend server
│   ├── app.py                 # Main application entry point
│   ├── api/
│   │   └── routes.py          # REST API endpoints
│   ├── services/
│   │   ├── detection_service.py    # AI detection service
│   │   ├── alert_service.py        # SMS/Email alerts
│   │   └── camera_service.py       # Camera management
│   └── models/
│       └── database.py        # Database models
├── frontend/                  # Web dashboard
│   └── public/
│       ├── index.html        # Main HTML page
│       ├── styles.css        # Styling
│       └── app.js            # Frontend JavaScript
├── ai_models/                # AI detection models
│   └── yolo_detector.py      # YOLOv8 + CLIP integration
├── database/                 # SQLite database storage
├── recordings/               # Video recordings
├── audio/                    # Alert sound files
├── servo/                    # Arduino servo control
│   └── servo.ino             # Arduino code for 360° rotation
├── requirements.txt          # Python dependencies
├── .env.example             # Environment configuration template
└── README.md                # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Webcam or IP camera
- (Optional) Arduino with servo motor for camera rotation
- (Optional) GPU for faster inference

### Step 1: Clone Repository
```bash
git clone https://github.com/Ibrahim99575/Wildlife-Risk-Assessment-Perimeter-Protection.git
cd Wildlife-Risk-Assessment-Perimeter-Protection
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment
```powershell
# Copy example environment file
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

### Step 5: Download AI Models
The YOLOv8 model will download automatically on first run. For faster setup:
```powershell
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

## 🎯 Usage

### Starting the Backend Server
```powershell
cd backend
python app.py
```
The server will start on `http://localhost:5000`

### Opening the Web Dashboard
```powershell
# Open in browser
start http://localhost:5000
# Or navigate to frontend
cd frontend/public
start index.html
```

### Using the Dashboard

1. **Start Camera**: Click "Start" button to begin video feed
2. **View Detections**: See real-time bounding boxes and classifications
3. **Monitor Alerts**: Check the alerts panel for notifications
4. **Start Recording**: Click "Record" to save video
5. **Adjust Settings**: Configure detection thresholds and alert preferences

## 🔧 Configuration

### Camera Settings
Edit `.env` file:
```env
DEFAULT_CAMERA_ID=0          # 0 for default webcam, or RTSP URL
FRAME_WIDTH=1280
FRAME_HEIGHT=720
```

### Detection Thresholds
```env
CONFIDENCE_THRESHOLD=0.5     # Detection confidence (0-1)
MIN_DISTANCE_ALERT=50        # Alert if object closer than 50cm
```

### Alert Configuration
```env
# Twilio SMS
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_NUMBER=+1234567890

# Recipient Numbers
FARMER_NUMBERS=+1234567890,+0987654321
FOREST_NUMBERS=+1122334455

# Email Settings
SMTP_SERVER=smtp.gmail.com
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

## 🤖 AI Models

### Current Models
- **YOLOv8n**: Fast, lightweight object detection (nano version)
- **COCO Dataset**: Pre-trained on 80 object classes
- **Custom Classification**: Danger level assessment

### Upgrading Models
For better accuracy, upgrade to YOLOv8m or YOLOv8l:
```python
# In ai_models/yolo_detector.py, change:
self.yolo_model = YOLO('yolov8m.pt')  # Medium
# or
self.yolo_model = YOLO('yolov8l.pt')  # Large
```

### Using Free AI APIs

#### Hugging Face Integration (Optional)
For species-specific classification:
```python
# Get free API token from huggingface.co
# Add to .env:
HUGGINGFACE_API_TOKEN=your_token

# Enables CLIP-based zero-shot classification
```

## 📱 API Endpoints

### Camera Management
- `GET /api/cameras` - List all cameras
- `POST /api/cameras/<id>/start` - Start camera
- `POST /api/cameras/<id>/stop` - Stop camera
- `GET /api/cameras/<id>/stream` - Video stream

### Detection
- `POST /api/detection/analyze` - Analyze single image
- `GET /api/detection/history` - Get detection history

### Alerts
- `GET /api/alerts/history` - Get alert history
- `POST /api/alerts/test` - Test alert system

### System
- `GET /api/health` - System health check
- `GET /api/statistics` - System statistics
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration

## 🔒 Security

### Best Practices
1. **Change Default Credentials**: Update SECRET_KEY in .env
2. **Use Environment Variables**: Never commit .env to Git
3. **Enable Authentication**: Implement JWT in production
4. **HTTPS**: Use SSL certificates for production
5. **Firewall**: Restrict API access to trusted IPs

## 🐛 Troubleshooting

### Camera Not Working
```powershell
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed')"
```

### Missing Dependencies
```powershell
pip install --upgrade -r requirements.txt
```

### YOLO Model Download Issues
```powershell
# Manual download
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### SMS Not Sending
- Verify Twilio credentials in .env
- Check phone number format (+1234567890)
- Ensure account has credit

## 🎨 Customization

### Adding Custom Animal Categories
Edit `ai_models/yolo_detector.py`:
```python
self.wildlife_categories = {
    'dangerous': ['tiger', 'lion', 'your_animal'],
    'moderate': ['deer', 'your_animal'],
    # ...
}
```

### Changing Alert Sounds
Replace audio files in `audio/` directory with your own .mp3 files.

### Custom Dashboard Styling
Edit `frontend/public/styles.css` to match your branding.

## 🚀 Deployment

### Local Network
```powershell
# Run on all network interfaces
python app.py --host 0.0.0.0 --port 5000
```

### Cloud Deployment (AWS, Azure, GCP)
1. Setup virtual machine
2. Install dependencies
3. Configure firewall rules
4. Use gunicorn for production:
```powershell
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Docker (Coming Soon)
```dockerfile
# Dockerfile included in future updates
docker build -t wildlife-detection .
docker run -p 5000:5000 wildlife-detection
```

## 📊 Performance

### System Requirements
- **Minimum**: 2GB RAM, Dual-core CPU
- **Recommended**: 8GB RAM, Quad-core CPU, GPU
- **Optimal**: 16GB RAM, Modern GPU (NVIDIA RTX series)

### Inference Speed
- **CPU Only**: 10-15 FPS (YOLOv8n)
- **With GPU**: 30-60 FPS (YOLOv8n)

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Ibrahim** - Initial work and v2.0 upgrade

## 🙏 Acknowledgments

- **Ultralytics** for YOLOv8
- **OpenCV** for computer vision
- **Flask** for web framework
- **Twilio** for SMS API
- Original project contributors

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Email: support@example.com

## 🔮 Future Enhancements

- [ ] Mobile app (React Native)
- [ ] Cloud storage integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Machine learning model fine-tuning
- [ ] Thermal camera support
- [ ] Drone integration
- [ ] Solar power management

## 📈 Version History

### v2.0 (Current)
- Complete rewrite with modern architecture
- YOLOv8 integration
- Web dashboard
- Multi-camera support
- Database storage
- REST API
- Enhanced alerts

### v1.0 (Original)
- Basic VGG16 detection
- Single camera
- Simple alerts
- Command-line interface

---

**⭐ If you find this project useful, please star the repository!**
