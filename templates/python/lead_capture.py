#!/usr/bin/env python3
"""
Lead Capture Automation
Captures form submissions and adds to Google Sheets + sends welcome email
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any

# Try to import optional dependencies
try:
    import requests
except ImportError:
    requests = None

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    service_account = None
    build = None


class LeadCaptureAutomation:
    """Captures leads from various sources and processes them"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_config = config.get("smtp", {})
        self.sheets_config = config.get("google_sheets", {})
        
    def capture_from_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming webhook data (from Typeform, JotForm, etc.)"""
        
        lead = {
            "name": webhook_data.get("name", webhook_data.get("Name", "")),
            "email": webhook_data.get("email", webhook_data.get("Email", "")),
            "phone": webhook_data.get("phone", webhook_data.get("Phone", "")),
            "source": webhook_data.get("source", "website_form"),
            "message": webhook_data.get("message", webhook_data.get("Message", "")),
            "captured_at": datetime.now().isoformat(),
            "status": "new"
        }
        
        # Process the lead
        result = self.process_lead(lead)
        return result
    
    def capture_from_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract lead info from incoming email"""
        
        lead = {
            "name": email_data.get("from_name", ""),
            "email": email_data.get("from_email", ""),
            "phone": "",
            "source": "email_inquiry",
            "message": email_data.get("subject", "") + " - " + email_data.get("body", "")[:200],
            "captured_at": datetime.now().isoformat(),
            "status": "new"
        }
        
        return self.process_lead(lead)
    
    def capture_manual(self, name: str, email: str, phone: str = "", 
                      source: str = "manual_entry", message: str = "") -> Dict[str, Any]:
        """Manually capture a lead"""
        
        lead = {
            "name": name,
            "email": email,
            "phone": phone,
            "source": source,
            "message": message,
            "captured_at": datetime.now().isoformat(),
            "status": "new"
        }
        
        return self.process_lead(lead)
    
    def process_lead(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Process a lead: save to sheets + send welcome email"""
        
        result = {
            "lead": lead,
            "sheets_added": False,
            "welcome_sent": False,
            "errors": []
        }
        
        # Add to Google Sheets
        if self.sheets_config.get("spreadsheet_id"):
            try:
                self._add_to_sheets(lead)
                result["sheets_added"] = True
            except Exception as e:
                result["errors"].append(f"Sheets error: {str(e)}")
        
        # Send welcome email
        if self.smtp_config.get("host"):
            try:
                self._send_welcome_email(lead)
                result["welcome_sent"] = True
            except Exception as e:
                result["errors"].append(f"Email error: {str(e)}")
        
        return result
    
    def _add_to_sheets(self, lead: Dict[str, Any]):
        """Add lead to Google Sheets"""
        
        if not build or not service_account:
            # Fallback: save to local CSV
            self._save_to_csv(lead)
            return
            
        credentials = service_account.Credentials.from_service_account_file(
            self.sheets_config["credentials_file"],
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        
        values = [[
            lead["captured_at"],
            lead["name"],
            lead["email"],
            lead["phone"],
            lead["source"],
            lead["message"],
            lead["status"]
        ]]
        
        body = {'values': values}
        
        service.spreadsheets().values().append(
            spreadsheetId=self.sheets_config["spreadsheet_id"],
            range="Leads!A:G",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
    
    def _save_to_csv(self, lead: Dict[str, Any]):
        """Fallback: save to local CSV file"""
        import csv
        
        filename = "leads.csv"
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "captured_at", "name", "email", "phone", "source", "message", "status"
            ])
            if not file_exists:
                writer.writeheader()
            writer.writerow(lead)
    
    def _send_welcome_email(self, lead: Dict[str, Any]):
        """Send welcome email to new lead"""
        
        if not self.smtp_config.get("host"):
            print("SMTP not configured, skipping email")
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config["from_email"]
        msg['To'] = lead["email"]
        msg['Subject'] = self.smtp_config.get("subject", "Thanks for reaching out!")
        
        # Personalize message
        body = self.smtp_config.get("body", """
        Hi {name},
        
        Thanks for reaching out! We'll get back to you within 24 hours.
        
        Best regards,
        The Team
        """).format(name=lead["name"].split()[0] if lead["name"] else "there")
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"]) as server:
            server.starttls()
            server.login(self.smtp_config["username"], self.smtp_config["password"])
            server.send_message(msg)


# Flask webhook endpoint (optional)
def create_webhook_app(automation: LeadCaptureAutomation):
    """Create a Flask app for webhook endpoints"""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("Flask not installed. Run: pip install flask")
        return None
    
    app = Flask(__name__)
    
    @app.route('/webhook/lead', methods=['POST'])
    def lead_webhook():
        data = request.json
        result = automation.capture_from_webhook(data)
        return jsonify(result)
    
    return app


# Example configuration
EXAMPLE_CONFIG = {
    "smtp": {
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "your-email@gmail.com",
        "password": "your-app-password",
        "from_email": "your-email@gmail.com",
        "subject": "Thanks for contacting us!",
        "body": """
        Hi {name},
        
        Thanks for reaching out! We've received your inquiry and will get back to you within 24 hours.
        
        In the meantime, feel free to reply to this email with any questions.
        
        Best regards,
        The Team
        """
    },
    "google_sheets": {
        "credentials_file": "credentials.json",
        "spreadsheet_id": "your-spreadsheet-id"
    }
}


if __name__ == "__main__":
    # Quick test
    automation = LeadCaptureAutomation(EXAMPLE_CONFIG)
    
    # Simulate a form submission
    test_lead = automation.capture_manual(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        source="website",
        message="Interested in your services"
    )
    
    print("Lead captured:", test_lead["lead"]["name"])
    print("Email:", test_lead["lead"]["email"])
