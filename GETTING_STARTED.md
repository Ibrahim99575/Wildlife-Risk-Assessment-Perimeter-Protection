# 🚀 Quick Start Guide

## Getting Started in 3 Steps

### Step 1: Install Dependencies
```powershell
python quick_start.py
```
Choose option 1 (Full Setup) and follow the prompts.

### Step 2: Configure Your Settings
Edit the `.env` file with your credentials:
```powershell
notepad .env
```

Add your:
- Twilio credentials (for SMS alerts)
- Email settings (for email alerts)
- Phone numbers and email addresses

### Step 3: Run the Application

**Option A: Standalone Application**
```powershell
python main_v2.py
```
- Best for: Testing, single camera, offline use
- Features: Direct camera access, keyboard controls
- Controls: q=quit, r=record, s=snapshot

**Option B: Web Application**
```powershell
python backend/app.py
```
Then open browser to: `http://localhost:5000`
- Best for: Production, multiple cameras, remote access
- Features: Web dashboard, REST API, multi-camera support

## What You Get

### 1. Advanced AI Detection
- **YOLOv8**: State-of-the-art object detection
- **Multi-species**: Identifies specific animals
- **Danger levels**: High/Medium/Low risk assessment
- **Distance**: Calculates object distance from camera

### 2. Smart Alerts
- **SMS**: Instant text notifications via Twilio
- **Email**: Detailed alerts with images
- **Multi-recipient**: Alerts farmers, forest officials
- **Smart throttling**: Prevents alert spam

### 3. Web Dashboard
- **Live video**: Real-time camera feeds
- **Detection overlay**: Visual bounding boxes
- **Alert history**: All past alerts
- **Statistics**: System metrics and analytics
- **Settings**: Configure thresholds

### 4. Data Management
- **Database**: SQLite stores all detections
- **Video recording**: Auto-record on detection
- **Snapshots**: Manual screenshot capture
- **Export**: Download detection data

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Web Dashboard                      │
│         (Live Feed, Alerts, Statistics)             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              Flask Backend Server                   │
│     REST API + WebSocket (Real-time updates)        │
└─────┬────────────┬──────────────┬───────────────────┘
      │            │              │
      ▼            ▼              ▼
┌──────────┐ ┌──────────┐  ┌────────────┐
│ Camera   │ │Detection │  │   Alert    │
│ Service  │ │ Service  │  │  Service   │
└──────────┘ └────┬─────┘  └────────────┘
                  │
                  ▼
           ┌──────────────┐
           │  YOLOv8 AI   │
           │   Model      │
           └──────────────┘
                  │
                  ▼
           ┌──────────────┐
           │   SQLite     │
           │  Database    │
           └──────────────┘
```

## Key Features

### Detection Pipeline
1. Camera captures frame
2. YOLOv8 detects objects
3. Classifier determines species
4. System calculates danger level
5. Measures distance to object
6. Saves to database
7. Triggers appropriate alerts

### Alert Logic
- **High Danger**: Dangerous animal detected
  - Sends SMS to farmer
  - Sends SMS to forest officials
  - Plays loud deterrent sound
  - Records video

- **Medium Risk**: Normal wildlife
  - Sends SMS to farmer
  - Plays monitoring alert
  - Records video

- **Proximity**: Human too close to camera
  - Sends security alert
  - Possible tampering warning

### Danger Categories

**High Danger Animals:**
- Tiger, Lion, Leopard, Bear, Wolf
- Hyena, Crocodile, Elephant, Rhino, Buffalo

**Medium Risk Animals:**
- Deer, Wild Boar, Monkey, Fox
- Jackal, Wild Dog

**Low Risk:**
- Rabbit, Squirrel, Peacock, Birds
- Domestic animals

## Configuration Options

### Detection Settings
- **Confidence Threshold**: 0-100% (default: 50%)
- **Min Distance Alert**: Distance in cm (default: 50cm)
- **Detection Interval**: Milliseconds between frames

### Alert Settings
- **SMS Enabled**: On/Off
- **Email Enabled**: On/Off
- **Alert Cooldown**: Seconds between alerts (default: 60s)
- **Recipients**: Multiple phone numbers/emails

### Camera Settings
- **Camera ID**: 0 for default, or RTSP URL
- **Resolution**: Width x Height
- **FPS**: Frames per second
- **Recording**: Auto-record on detection

## Troubleshooting

### Camera not detected
```powershell
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Dependencies missing
```powershell
pip install -r requirements.txt --upgrade
```

### SMS not working
- Check Twilio credentials in .env
- Verify phone number format: +1234567890
- Ensure Twilio account has credit

### Slow detection
- Use GPU if available
- Lower camera resolution
- Use YOLOv8n (nano) instead of larger models

## Advanced Usage

### Multiple Cameras
```python
# Add cameras via web interface
# Or programmatically:
camera_service.add_camera(0, "Front Gate")
camera_service.add_camera(1, "Back Fence")
```

### Custom Species
Edit `ai_models/yolo_detector.py`:
```python
self.wildlife_categories = {
    'dangerous': ['your_species_here'],
    # ...
}
```

### API Integration
```python
import requests

# Get detection history
response = requests.get('http://localhost:5000/api/alerts/history')
alerts = response.json()

# Start camera
requests.post('http://localhost:5000/api/cameras/0/start')
```

## Performance Tips

1. **Use GPU**: Install CUDA-enabled PyTorch
2. **Lower Resolution**: Reduce camera resolution for speed
3. **Adjust Confidence**: Higher threshold = fewer detections
4. **Limit Recording**: Only record important events
5. **Clean Database**: Periodically archive old data

## Need Help?

- Check README_V2.md for detailed documentation
- Review backend/services/ for service implementations
- Check logs/ directory for error messages
- Open GitHub issue for bugs

## What's Next?

After basic setup:
1. Calibrate distance measurement for your camera
2. Fine-tune detection thresholds
3. Add custom animal species
4. Set up multiple cameras
5. Configure cloud backup
6. Deploy to production server

---

**Happy Monitoring! 🦁📹**
