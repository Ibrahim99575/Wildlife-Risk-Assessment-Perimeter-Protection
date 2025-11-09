# Installation Guide - Python 3.13 Compatibility

## ✅ Successfully Installed!

Your system is now running with **Python 3.13** compatible packages.

## 📦 What Was Fixed

### Original Issue:
- Some packages (mediapipe, cvzone) don't support Python 3.13 yet
- Specific versions of torch and ultralytics had Python version restrictions

### Solution Applied:
- Updated `requirements.txt` to use Python 3.13 compatible versions
- Removed packages not yet supporting Python 3.13 (mediapipe, cvzone)
- Updated to latest compatible versions:
  - `ultralytics >= 8.3.0`
  - `torch >= 2.6.0`
  - `torchvision >= 0.21.0`

## 🚀 Quick Start

### Option 1: Use the Batch File (Windows)
```powershell
start_server.bat
```
Double-click `start_server.bat` or run it from terminal

### Option 2: Manual Start
```powershell
# Create directories
mkdir logs, recordings, snapshots, database, uploads

# Start backend
$env:PYTHONPATH="backend"
python backend/app.py
```

### Option 3: Use Python Script
```powershell
python quick_start.py
```

## 🌐 Access the Dashboard

Once the server starts, open your browser to:
- **Local:** http://localhost:5000
- **Network:** http://192.168.1.36:5000 (your local IP)

## ⚙️ Configuration

1. **Copy environment template:**
   ```powershell
   copy .env.example .env
   ```

2. **Edit .env with your credentials:**
   ```powershell
   notepad .env
   ```

3. **Add your Twilio and email settings**

## 🔧 What Works Without Mediapipe

The system is fully functional without mediapipe:
- ✅ YOLOv8 object detection
- ✅ Multi-species identification
- ✅ Bounding box visualization
- ✅ Distance estimation (simplified method)
- ✅ Danger level classification
- ✅ SMS and email alerts
- ✅ Video recording
- ✅ Web dashboard
- ✅ Multi-camera support

## 📊 Distance Estimation

Without mediapipe facial landmarks, distance is estimated using:
- Bounding box size (width and height)
- Calibrated focal length
- Known object sizes

**Note:** For precise facial distance measurement, use Python 3.11 or install mediapipe when it supports 3.13.

## 🐛 Troubleshooting

### Server Won't Start
```powershell
# Check Python version
python --version  # Should be 3.13

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check imports
python -c "import flask, ultralytics, opencv-python"
```

### Camera Not Working
```powershell
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"
```

### Port Already in Use
If port 5000 is busy, edit `backend/app.py` and change:
```python
socketio.run(app, host='0.0.0.0', port=5001, debug=True)
```

## 📝 Current Status

✅ **Dependencies Installed:**
- flask 3.1.2
- flask-cors 6.0.1
- flask-socketio 5.5.1
- opencv-python 4.12.0.88
- ultralytics 8.3.226
- torch 2.9.0
- torchvision 0.24.0
- pillow 12.0.0
- twilio 9.8.5
- pygame 2.6.1
- All supporting packages

✅ **Backend Server:** Running on http://localhost:5000

✅ **Database:** SQLite initialized

✅ **Web Dashboard:** Accessible via browser

## 🎯 Next Steps

1. **Configure Alerts:**
   - Edit `.env` file
   - Add Twilio credentials
   - Add email settings

2. **Test Camera:**
   - Click "Start" button in dashboard
   - Allow camera permissions if prompted

3. **Test Detection:**
   - Point camera at objects/animals
   - View real-time detections

4. **Configure Thresholds:**
   - Adjust settings in dashboard
   - Fine-tune detection confidence

## 🔮 Future: Python 3.11 for Full Features

If you need facial recognition features:
1. Install Python 3.11 alongside 3.13
2. Create virtual environment with Python 3.11:
   ```powershell
   py -3.11 -m venv venv311
   venv311\Scripts\activate
   pip install -r requirements_full.txt
   ```
3. Run with full mediapipe support

## 📞 Support

- Check `README_V2.md` for complete documentation
- Review `GETTING_STARTED.md` for guides
- Check `logs/app.log` for error messages

## ✨ You're All Set!

Your Wildlife Risk Assessment System is ready to use!

Start the server and open http://localhost:5000 to begin monitoring.

---
**Version 2.0 - Python 3.13 Compatible**
