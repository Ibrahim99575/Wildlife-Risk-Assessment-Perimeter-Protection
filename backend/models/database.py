"""
Database Models - SQLite database for storing detection history and configuration
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'database/wildlife_system.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Detections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            camera_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            species TEXT,
            yolo_class TEXT,
            confidence REAL,
            danger_level TEXT,
            distance_cm INTEGER,
            bbox TEXT,
            image_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            camera_id INTEGER,
            message TEXT,
            recipients TEXT,
            status TEXT DEFAULT 'sent',
            data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cameras table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT,
            status TEXT DEFAULT 'inactive',
            last_active TEXT,
            config TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # System logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_level TEXT,
            module TEXT,
            message TEXT,
            data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def save_detection(camera_id, detection_data):
    """Save a detection to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO detections (camera_id, timestamp, species, yolo_class, 
                               confidence, danger_level, distance_cm, bbox)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        camera_id,
        datetime.now().isoformat(),
        detection_data.get('species'),
        detection_data.get('yolo_class'),
        detection_data.get('confidence'),
        detection_data.get('danger_level'),
        detection_data.get('distance_cm'),
        json.dumps(detection_data.get('bbox'))
    ))
    
    conn.commit()
    detection_id = cursor.lastrowid
    conn.close()
    return detection_id

def save_alert(alert_type, camera_id, message, recipients, data=None):
    """Save an alert to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO alerts (alert_type, camera_id, message, recipients, data)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        alert_type,
        camera_id,
        message,
        json.dumps(recipients),
        json.dumps(data) if data else None
    ))
    
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def get_recent_detections(camera_id=None, limit=100):
    """Get recent detections"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if camera_id is not None:
        cursor.execute('''
            SELECT * FROM detections 
            WHERE camera_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (camera_id, limit))
    else:
        cursor.execute('''
            SELECT * FROM detections 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    detections = []
    for row in rows:
        detections.append(dict(row))
    
    return detections

def get_alert_history(limit=100):
    """Get alert history"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM alerts 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append(dict(row))
    
    return alerts

def log_system_event(level, module, message, data=None):
    """Log a system event"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO system_logs (log_level, module, message, data)
        VALUES (?, ?, ?, ?)
    ''', (
        level,
        module,
        message,
        json.dumps(data) if data else None
    ))
    
    conn.commit()
    conn.close()

def get_statistics(days=7):
    """Get system statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total detections
    cursor.execute('SELECT COUNT(*) as count FROM detections')
    total_detections = cursor.fetchone()['count']
    
    # Detections by danger level
    cursor.execute('''
        SELECT danger_level, COUNT(*) as count 
        FROM detections 
        GROUP BY danger_level
    ''')
    danger_stats = {row['danger_level']: row['count'] for row in cursor.fetchall()}
    
    # Total alerts
    cursor.execute('SELECT COUNT(*) as count FROM alerts')
    total_alerts = cursor.fetchone()['count']
    
    # Most detected species
    cursor.execute('''
        SELECT yolo_class, COUNT(*) as count 
        FROM detections 
        GROUP BY yolo_class 
        ORDER BY count DESC 
        LIMIT 10
    ''')
    top_species = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'total_detections': total_detections,
        'danger_stats': danger_stats,
        'total_alerts': total_alerts,
        'top_species': top_species
    }
