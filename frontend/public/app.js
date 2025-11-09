// Wildlife Risk Assessment System - Frontend JavaScript

const API_BASE = 'http://localhost:5000/api';
let socket;
let currentCamera = 0;
let isRecording = false;
let startTime = Date.now();
let isCameraActive = false;

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Wildlife Risk Assessment System...');
    
    // Initialize WebSocket connection
    initializeWebSocket();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    loadStatistics();
    loadAlertHistory();
    
    // Start periodic updates
    setInterval(updateUptime, 1000);
    setInterval(loadStatistics, 5000);
    setInterval(loadAlertHistory, 10000);
    
    // Check system health
    checkSystemHealth();
    
    // Initialize button states
    updateCameraButtonStates();
});

// WebSocket Connection
function initializeWebSocket() {
    socket = io('http://localhost:5000');
    
    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateStatus('Connected', true);
    });
    
    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateStatus('Disconnected', false);
    });
    
    socket.on('detection_update', (data) => {
        handleDetectionUpdate(data);
    });
    
    socket.on('alert', (data) => {
        showAlert(data);
    });
}

// Event Listeners
function setupEventListeners() {
    // Camera controls
    document.getElementById('startBtn').addEventListener('click', startCamera);
    document.getElementById('stopBtn').addEventListener('click', stopCamera);
    document.getElementById('recordBtn').addEventListener('click', toggleRecording);
    document.getElementById('cameraSelect').addEventListener('change', (e) => {
        currentCamera = parseInt(e.target.value);
    });
    
    // Settings
    document.getElementById('confidenceThreshold').addEventListener('input', (e) => {
        document.getElementById('confidenceValue').textContent = e.target.value + '%';
    });
    
    document.getElementById('saveSettings').addEventListener('click', saveSettings);
}

// System Health Check
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        console.log('System Health:', data);
        
        if (data.status === 'healthy') {
            updateStatus('System Ready', true);
        } else {
            updateStatus('System Issues Detected', false);
        }
    } catch (error) {
        console.error('Health check failed:', error);
        updateStatus('Backend Offline', false);
    }
}

// Camera Controls
async function startCamera() {
    try {
        const response = await fetch(`${API_BASE}/cameras/${currentCamera}/start`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Camera started');
            isCameraActive = true;
            updateCameraButtonStates();
            startVideoStream();
            socket.emit('start_detection', { camera_id: currentCamera });
        }
    } catch (error) {
        console.error('Failed to start camera:', error);
        alert('Failed to start camera. Make sure the backend is running.');
    }
}

async function stopCamera() {
    try {
        const response = await fetch(`${API_BASE}/cameras/${currentCamera}/stop`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Camera stopped');
            isCameraActive = false;
            updateCameraButtonStates();
            stopVideoStream();
            socket.emit('stop_detection', { camera_id: currentCamera });
            
            // Reset recording state
            if (isRecording) {
                isRecording = false;
                const recordBtn = document.getElementById('recordBtn');
                recordBtn.textContent = 'Record';
                recordBtn.classList.remove('btn-danger');
                recordBtn.classList.add('btn-warning');
            }
        }
    } catch (error) {
        console.error('Failed to stop camera:', error);
    }
}

// Update button states based on camera status
function updateCameraButtonStates() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const recordBtn = document.getElementById('recordBtn');
    
    if (isCameraActive) {
        startBtn.disabled = true;
        startBtn.style.opacity = '0.5';
        startBtn.style.cursor = 'not-allowed';
        
        stopBtn.disabled = false;
        stopBtn.style.opacity = '1';
        stopBtn.style.cursor = 'pointer';
        
        recordBtn.disabled = false;
        recordBtn.style.opacity = '1';
        recordBtn.style.cursor = 'pointer';
    } else {
        startBtn.disabled = false;
        startBtn.style.opacity = '1';
        startBtn.style.cursor = 'pointer';
        
        stopBtn.disabled = true;
        stopBtn.style.opacity = '0.5';
        stopBtn.style.cursor = 'not-allowed';
        
        recordBtn.disabled = true;
        recordBtn.style.opacity = '0.5';
        recordBtn.style.cursor = 'not-allowed';
    }
}

async function toggleRecording() {
    const recordBtn = document.getElementById('recordBtn');
    
    try {
        if (!isRecording) {
            const response = await fetch(`${API_BASE}/cameras/${currentCamera}/recording/start`, {
                method: 'POST'
            });
            
            if (response.ok) {
                isRecording = true;
                recordBtn.textContent = 'Stop Recording';
                recordBtn.classList.remove('btn-warning');
                recordBtn.classList.add('btn-danger');
            }
        } else {
            const response = await fetch(`${API_BASE}/cameras/${currentCamera}/recording/stop`, {
                method: 'POST'
            });
            
            if (response.ok) {
                isRecording = false;
                recordBtn.textContent = 'Record';
                recordBtn.classList.remove('btn-danger');
                recordBtn.classList.add('btn-warning');
            }
        }
    } catch (error) {
        console.error('Failed to toggle recording:', error);
    }
}

// Video Stream
function startVideoStream() {
    const videoFeed = document.getElementById('videoFeed');
    const placeholder = document.getElementById('videoPlaceholder');
    
    videoFeed.src = `${API_BASE}/cameras/${currentCamera}/stream?t=${Date.now()}`;
    videoFeed.style.display = 'block';
    if (placeholder) placeholder.style.display = 'none';
}

function stopVideoStream() {
    const videoFeed = document.getElementById('videoFeed');
    const placeholder = document.getElementById('videoPlaceholder');
    
    videoFeed.src = '';
    videoFeed.style.display = 'none';
    if (placeholder) placeholder.style.display = 'flex';
}

// Statistics
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/statistics`);
        const data = await response.json();
        
        document.getElementById('totalDetections').textContent = data.total_alerts || 0;
        document.getElementById('dangerAlerts').textContent = data.danger_alerts || 0;
        document.getElementById('activeCameras').textContent = data.cameras_active || 0;
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

// Alerts
async function loadAlertHistory() {
    try {
        const response = await fetch(`${API_BASE}/alerts/history?limit=10`);
        const data = await response.json();
        
        const alertsList = document.getElementById('alertsList');
        alertsList.innerHTML = '';
        
        if (data.alerts.length === 0) {
            alertsList.innerHTML = '<p style="color: #6b7280;">No alerts yet</p>';
            return;
        }
        
        data.alerts.forEach(alert => {
            const alertItem = createAlertElement(alert);
            alertsList.appendChild(alertItem);
        });
    } catch (error) {
        console.error('Failed to load alerts:', error);
    }
}

function createAlertElement(alert) {
    const div = document.createElement('div');
    const dangerLevel = alert.data?.danger_level || 'low';
    div.className = `alert-item ${dangerLevel}`;
    
    const time = new Date(alert.timestamp).toLocaleTimeString();
    const message = alert.data?.species || alert.type;
    
    div.innerHTML = `
        <div class="alert-time">${time}</div>
        <div><strong>${message}</strong></div>
        <div style="font-size: 12px; color: #6b7280;">
            Distance: ${alert.data?.distance || 'N/A'}cm | 
            Camera: ${alert.data?.camera_id || 0}
        </div>
    `;
    
    return div;
}

function showAlert(alertData) {
    // Add new alert to the top of the list
    const alertsList = document.getElementById('alertsList');
    const alertItem = createAlertElement(alertData);
    alertsList.insertBefore(alertItem, alertsList.firstChild);
    
    // Play sound if available
    try {
        const audio = new Audio('../audio/ok.mp3');
        audio.play().catch(e => console.log('Could not play alert sound'));
    } catch (e) {
        console.log('Alert sound not available');
    }
    
    // Keep only last 10 alerts
    while (alertsList.children.length > 10) {
        alertsList.removeChild(alertsList.lastChild);
    }
}

// Detection Updates
function handleDetectionUpdate(data) {
    console.log('Detection update:', data);
    
    // Update overlay
    const overlay = document.getElementById('detectionOverlay');
    
    if (data.detections && data.detections.length > 0) {
        const detection = data.detections[0];
        overlay.innerHTML = `
            Species: ${detection.species}<br>
            Danger: ${detection.danger_level}<br>
            Distance: ${detection.distance_cm}cm
        `;
    } else {
        overlay.innerHTML = 'No detections';
    }
}

// Settings
async function saveSettings() {
    const settings = {
        alerts_enabled: document.getElementById('alertsEnabled').checked,
        confidence_threshold: document.getElementById('confidenceThreshold').value,
        min_distance: document.getElementById('minDistance').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            alert('Settings saved successfully!');
        }
    } catch (error) {
        console.error('Failed to save settings:', error);
        alert('Failed to save settings');
    }
}

// UI Updates
function updateStatus(message, isHealthy) {
    const statusElement = document.getElementById('status');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('span:last-child');
    
    statusText.textContent = `System Status: ${message}`;
    statusDot.style.background = isHealthy ? '#10b981' : '#ef4444';
}

function updateUptime() {
    const elapsed = Date.now() - startTime;
    const hours = Math.floor(elapsed / 3600000);
    const minutes = Math.floor((elapsed % 3600000) / 60000);
    const seconds = Math.floor((elapsed % 60000) / 1000);
    
    document.getElementById('uptime').textContent = 
        `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
}

function pad(num) {
    return num.toString().padStart(2, '0');
}

// Utility Functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function getDangerLevelColor(level) {
    const colors = {
        'high': '#ef4444',
        'medium': '#f59e0b',
        'low': '#10b981',
        'human': '#8b5cf6'
    };
    return colors[level] || '#6b7280';
}

// Recordings Management
async function loadRecordings() {
    try {
        const response = await fetch(`${API_BASE}/recordings`);
        const data = await response.json();
        
        const recordingsList = document.getElementById('recordingsList');
        recordingsList.innerHTML = '';
        
        if (data.recordings.length === 0) {
            recordingsList.innerHTML = '<p style="color: #6b7280;">No recordings yet. Click "Record" while camera is active.</p>';
            return;
        }
        
        data.recordings.forEach(recording => {
            const card = createRecordingCard(recording);
            recordingsList.appendChild(card);
        });
    } catch (error) {
        console.error('Failed to load recordings:', error);
    }
}

function createRecordingCard(recording) {
    const card = document.createElement('div');
    card.className = 'recording-card';
    
    const date = new Date(recording.created);
    const formattedDate = date.toLocaleString();
    
    card.innerHTML = `
        <h4>🎥 ${recording.filename}</h4>
        <div class="recording-info">
            <span>📅 ${formattedDate}</span>
            <span>💾 ${recording.size_mb} MB</span>
        </div>
        <div class="recording-actions">
            <button class="btn btn-info" onclick="playRecording('${recording.filename}')">▶️ Play</button>
            <button class="btn btn-danger" onclick="deleteRecording('${recording.filename}')">🗑️ Delete</button>
        </div>
    `;
    
    return card;
}

// Video.js player instance
let videoJsPlayer = null;

function playRecording(filename) {
    const modal = document.getElementById('videoPlayerModal');
    const videoTitle = document.getElementById('videoTitle');
    
    // Determine MIME type based on file extension
    let mimeType = 'video/mp4';
    if (filename.endsWith('.webm')) {
        mimeType = 'video/webm';
    } else if (filename.endsWith('.avi')) {
        mimeType = 'video/avi';
    }
    
    // Update title
    videoTitle.textContent = `Playing: ${filename}`;
    
    // Show modal first
    modal.classList.add('active');
    
    // Initialize or update Video.js player
    if (!videoJsPlayer) {
        videoJsPlayer = videojs('videoPlayer', {
            controls: true,
            preload: 'auto',
            fluid: true,
            responsive: true,
            playbackRates: [0.5, 1, 1.5, 2],
            html5: {
                vhs: {
                    overrideNative: true
                },
                nativeAudioTracks: false,
                nativeVideoTracks: false
            },
            techOrder: ['html5'],
            sources: []
        });
    }
    
    // Set source with proper type
    videoJsPlayer.src({
        src: `${API_BASE}/recordings/${filename}/stream`,
        type: mimeType
    });
    
    // Load and play
    videoJsPlayer.load();
    videoJsPlayer.ready(function() {
        videoJsPlayer.play().catch(e => {
            console.log('Autoplay prevented or codec not supported:', e);
            // Show error message in Video.js player
            videoJsPlayer.error({code: 4, message: 'This video format may not be supported. Try recording a new video with WebM format.'});
        });
    });
}

function closeVideoPlayer() {
    const modal = document.getElementById('videoPlayerModal');
    
    // Stop video using Video.js API
    if (videoJsPlayer) {
        videoJsPlayer.pause();
        videoJsPlayer.currentTime(0);
    }
    
    // Hide modal
    modal.classList.remove('active');
}

async function deleteRecording(filename) {
    showDeleteConfirm(filename);
}

function showDeleteConfirm(filename) {
    const modal = document.getElementById('deleteConfirmModal');
    const message = document.getElementById('deleteConfirmMessage');
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    message.textContent = `Are you sure you want to delete "${filename}"?`;
    
    // Remove any existing event listeners by cloning the button
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    
    // Add new event listener for this specific deletion
    newConfirmBtn.addEventListener('click', async () => {
        await performDelete(filename);
        closeDeleteConfirm();
    });
    
    // Show modal
    modal.classList.add('active');
}

function closeDeleteConfirm() {
    const modal = document.getElementById('deleteConfirmModal');
    modal.classList.remove('active');
}

async function performDelete(filename) {
    try {
        const response = await fetch(`${API_BASE}/recordings/${filename}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('Recording deleted:', filename);
            showSuccessMessage('Recording deleted successfully!');
            loadRecordings(); // Refresh list
        } else {
            // Show the specific error message from the server
            showErrorMessage(`Failed to delete recording: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Failed to delete recording:', error);
        showErrorMessage('Error deleting recording. Make sure recording is stopped first.');
    }
}

function showSuccessMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #10b981;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}

function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ef4444;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const videoModal = document.getElementById('videoPlayerModal');
    const deleteModal = document.getElementById('deleteConfirmModal');
    
    if (event.target === videoModal) {
        closeVideoPlayer();
    }
    if (event.target === deleteModal) {
        closeDeleteConfirm();
    }
}

// Load recordings on page load
document.addEventListener('DOMContentLoaded', () => {
    // ... existing code ...
    loadRecordings();
    
    // Refresh recordings every 30 seconds
    setInterval(loadRecordings, 30000);
});

