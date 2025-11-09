"""
Alert Service - Manages SMS, email, and push notifications
"""

import os
from datetime import datetime
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class AlertService:
    """Service for managing alerts and notifications"""
    
    def __init__(self):
        """Initialize alert service"""
        # Twilio configuration
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.twilio_number = os.getenv('TWILIO_NUMBER', '')
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        
        # Contact lists
        self.farmer_numbers = self._load_contacts('farmer_numbers')
        self.farmer_emails = self._load_contacts('farmer_emails')
        self.forest_numbers = self._load_contacts('forest_numbers')
        self.forest_emails = self._load_contacts('forest_emails')
        
        # Alert history
        self.alert_history = []
        self.max_history = 1000
        
        # Rate limiting
        self.last_alert_time = {}
        self.min_alert_interval = 60  # seconds
    
    def _load_contacts(self, contact_type):
        """Load contact list from environment or config"""
        contacts_str = os.getenv(contact_type.upper(), '')
        if contacts_str:
            return [c.strip() for c in contacts_str.split(',')]
        return []
    
    def is_configured(self):
        """Check if alert service is properly configured"""
        return bool(self.twilio_sid and self.twilio_token)
    
    def _check_rate_limit(self, alert_type):
        """Check if enough time has passed since last alert of this type"""
        if alert_type in self.last_alert_time:
            elapsed = (datetime.now() - self.last_alert_time[alert_type]).total_seconds()
            if elapsed < self.min_alert_interval:
                return False
        return True
    
    def send_sms(self, to_number, message):
        """
        Send SMS via Twilio
        
        Args:
            to_number: Recipient phone number
            message: SMS message content
            
        Returns:
            Success status
        """
        if not self.is_configured():
            print("Alert service not configured. Simulating SMS...")
            print(f"SMS to {to_number}: {message}")
            return True
        
        try:
            client = Client(self.twilio_sid, self.twilio_token)
            message_obj = client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=to_number
            )
            print(f"SMS sent: {message_obj.sid}")
            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_email(self, to_email, subject, body):
        """
        Send email notification
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            Success status
        """
        if not self.sender_email or not self.sender_password:
            print("Email not configured. Simulating email...")
            print(f"Email to {to_email}: {subject}")
            return True
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_danger_alert(self, danger_level, species, distance, camera_id=0):
        """
        Send danger alert based on detection
        
        Args:
            danger_level: 'high', 'medium', 'low'
            species: Detected species
            distance: Distance in cm
            camera_id: Camera identifier
        """
        alert_type = f"danger_{danger_level}"
        
        if not self._check_rate_limit(alert_type):
            print(f"Rate limit: Skipping {alert_type} alert")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Compose message based on danger level
        if danger_level == 'high':
            sms_message = f"ALERT! Dangerous wildlife detected: {species} at {distance}cm from Camera {camera_id}. Stay away and contact forest authorities. [{timestamp}]"
            email_subject = "⚠️ HIGH DANGER: Wildlife Alert"
            email_body = f"""
            <html>
            <body>
            <h2 style="color: red;">⚠️ DANGER ALERT</h2>
            <p><strong>Time:</strong> {timestamp}</p>
            <p><strong>Species:</strong> {species}</p>
            <p><strong>Distance:</strong> {distance} cm</p>
            <p><strong>Camera:</strong> {camera_id}</p>
            <p><strong>Danger Level:</strong> HIGH</p>
            <p style="color: red;"><strong>Action Required:</strong> Stay away from the area. Forest authorities have been notified.</p>
            </body>
            </html>
            """
            
            # Alert farmer
            for number in self.farmer_numbers:
                self.send_sms(number, sms_message)
            for email in self.farmer_emails:
                self.send_email(email, email_subject, email_body)
            
            # Alert forest officials
            forest_message = f"Wildlife alert: {species} detected at farm (Camera {camera_id}). Distance: {distance}cm. Farmer contact: {self.farmer_numbers[0] if self.farmer_numbers else 'N/A'}. [{timestamp}]"
            for number in self.forest_numbers:
                self.send_sms(number, forest_message)
            for email in self.forest_emails:
                self.send_email(email, email_subject, email_body)
        
        elif danger_level == 'medium':
            sms_message = f"Alert: Wildlife detected - {species} at {distance}cm from Camera {camera_id}. Monitor the situation. [{timestamp}]"
            email_subject = "⚠️ Wildlife Alert - Medium Risk"
            
            for number in self.farmer_numbers:
                self.send_sms(number, sms_message)
        
        # Log alert
        self.log_alert(alert_type, {
            'danger_level': danger_level,
            'species': species,
            'distance': distance,
            'camera_id': camera_id,
            'timestamp': timestamp
        })
        
        self.last_alert_time[alert_type] = datetime.now()
    
    def send_proximity_alert(self, distance, camera_id=0):
        """Send alert when someone is too close to camera"""
        alert_type = "proximity"
        
        if not self._check_rate_limit(alert_type):
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"SECURITY ALERT! Person detected very close ({distance}cm) to Camera {camera_id}. Possible tampering. [{timestamp}]"
        
        for number in self.farmer_numbers:
            self.send_sms(number, message)
        
        self.log_alert(alert_type, {
            'distance': distance,
            'camera_id': camera_id,
            'timestamp': timestamp
        })
        
        self.last_alert_time[alert_type] = datetime.now()
    
    def send_system_alert(self, message, camera_id=0):
        """Send system-level alert"""
        alert_type = "system"
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"SYSTEM ALERT (Camera {camera_id}): {message} [{timestamp}]"
        
        for number in self.farmer_numbers:
            self.send_sms(number, full_message)
        
        self.log_alert(alert_type, {
            'message': message,
            'camera_id': camera_id,
            'timestamp': timestamp
        })
    
    def log_alert(self, alert_type, data):
        """Log alert to history"""
        alert_record = {
            'type': alert_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        self.alert_history.append(alert_record)
        
        # Keep history size manageable
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
    
    def get_alert_history(self, limit=100):
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history = []
