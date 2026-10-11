#!/usr/bin/env python3
"""
Appointment Booking Automation
Online booking with reminders and follow-ups
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    service_account = None
    build = None


class AppointmentBooking:
    """Manages appointment booking with reminders"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.appointments = []
        self.available_slots = []
        self.smtp_config = config.get("smtp", {})
        
    def set_availability(self, slots: List[Dict[str, Any]]):
        """Set available time slots"""
        self.available_slots = slots
        
    def get_available_slots(self, date: str) -> List[Dict[str, Any]]:
        """Get available slots for a specific date"""
        return [s for s in self.available_slots if s["date"] == date and s["available"]]
    
    def book_appointment(self, customer: Dict[str, str], slot: Dict[str, Any]) -> Dict[str, Any]:
        """Book an appointment"""
        
        appointment = {
            "id": len(self.appointments) + 1,
            "customer": customer,
            "slot": slot,
            "status": "confirmed",
            "booked_at": datetime.now().isoformat(),
            "reminders_sent": []
        }
        
        self.appointments.append(appointment)
        
        # Mark slot as unavailable
        slot["available"] = False
        
        # Send confirmation
        self._send_confirmation(appointment)
        
        return appointment
    
    def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel an appointment"""
        
        for apt in self.appointments:
            if apt["id"] == appointment_id:
                apt["status"] = "cancelled"
                apt["slot"]["available"] = True
                self._send_cancellation(apt)
                return True
        
        return False
    
    def send_reminders(self):
        """Send reminders for upcoming appointments (run daily)"""
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        for apt in self.appointments:
            if apt["status"] != "confirmed":
                continue
            
            if apt["slot"]["date"] == tomorrow:
                if "24h" not in apt["reminders_sent"]:
                    self._send_reminder(apt, "24h")
                    apt["reminders_sent"].append("24h")
    
    def send_followups(self):
        """Send follow-up emails after appointments (run daily)"""
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        for apt in self.appointments:
            if apt["status"] != "confirmed":
                continue
            
            if apt["slot"]["date"] == yesterday:
                if "followup" not in apt["reminders_sent"]:
                    self._send_followup(apt)
                    apt["reminders_sent"].append("followup")
    
    def _send_confirmation(self, appointment: Dict[str, Any]):
        """Send booking confirmation"""
        
        customer = appointment["customer"]
        slot = appointment["slot"]
        
        subject = "Appointment Confirmed!"
        body = f"""
Hi {customer['name']},

Your appointment has been confirmed!

Date: {slot['date']}
Time: {slot['time']}
Service: {slot.get('service', 'Consultation')}

We'll send you a reminder 24 hours before.

If you need to reschedule, please reply to this email.

Best,
The Team
"""
        
        self._send_email(customer["email"], subject, body)
    
    def _send_reminder(self, appointment: Dict[str, Any], timing: str):
        """Send appointment reminder"""
        
        customer = appointment["customer"]
        slot = appointment["slot"]
        
        subject = f"Reminder: Appointment Tomorrow at {slot['time']}"
        body = f"""
Hi {customer['name']},

This is a friendly reminder about your appointment tomorrow.

Date: {slot['date']}
Time: {slot['time']}
Service: {slot.get('service', 'Consultation')}

See you soon!

Best,
The Team
"""
        
        self._send_email(customer["email"], subject, body)
    
    def _send_followup(self, appointment: Dict[str, Any]):
        """Send post-appointment follow-up"""
        
        customer = appointment["customer"]
        slot = appointment["slot"]
        
        subject = "Thanks for visiting!"
        body = f"""
Hi {customer['name']},

Thanks for coming in today! We hope you had a great experience.

If you have any questions, feel free to reply to this email.

We'd also appreciate it if you could leave us a review:
[REVIEW LINK]

See you next time!

Best,
The Team
"""
        
        self._send_email(customer["email"], subject, body)
    
    def _send_cancellation(self, appointment: Dict[str, Any]):
        """Send cancellation confirmation"""
        
        customer = appointment["customer"]
        slot = appointment["slot"]
        
        subject = "Appointment Cancelled"
        body = f"""
Hi {customer['name']},

Your appointment has been cancelled.

Date: {slot['date']}
Time: {slot['time']}

If you'd like to rebook, please visit our booking page or reply to this email.

Best,
The Team
"""
        
        self._send_email(customer["email"], subject, body)
    
    def _send_email(self, to_email: str, subject: str, body: str):
        """Send an email"""
        
        if not self.smtp_config.get("host"):
            print(f"SMTP not configured. Would send to {to_email}: {subject}")
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config["from_email"]
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)
            print(f"Sent: {subject} to {to_email}")
        except Exception as e:
            print(f"Failed to send: {e}")


# Example usage
if __name__ == "__main__":
    config = {
        "smtp": {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "from_email": "your-email@gmail.com"
        }
    }
    
    booking = AppointmentBooking(config)
    
    # Set availability
    booking.set_availability([
        {"date": "2024-01-15", "time": "10:00", "available": True},
        {"date": "2024-01-15", "time": "11:00", "available": True},
        {"date": "2024-01-15", "time": "14:00", "available": True},
    ])
    
    # Book an appointment
    result = booking.book_appointment(
        customer={"name": "Jane Smith", "email": "jane@example.com"},
        slot={"date": "2024-01-15", "time": "10:00", "service": "Consultation"}
    )
    
    print(f"Booked: Appointment #{result['id']}")
