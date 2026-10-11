#!/usr/bin/env python3
"""
Email Follow-up Sequence Automation
Sends automated email sequences based on triggers
"""

import smtplib
import time
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


class EmailSequence:
    """Manages an email follow-up sequence"""
    
    def __init__(self, name: str, emails: List[Dict[str, Any]]):
        self.name = name
        self.emails = emails  # List of {delay_days, subject, body}
    
    
class FollowUpAutomation:
    """Automates email follow-up sequences"""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.sequences = {}
        self.subscribers = {}  # email -> {sequence_name, current_step, last_sent}
        
    def add_sequence(self, sequence: EmailSequence):
        """Add a new email sequence"""
        self.sequences[sequence.name] = sequence
    
    def subscribe(self, email: str, name: str, sequence_name: str) -> bool:
        """Subscribe someone to a sequence"""
        
        if sequence_name not in self.sequences:
            print(f"Sequence '{sequence_name}' not found")
            return False
        
        self.subscribers[email] = {
            "name": name,
            "sequence": sequence_name,
            "current_step": 0,
            "subscribed_at": datetime.now().isoformat(),
            "last_sent": None,
            "status": "active"
        }
        
        # Send first email immediately
        self._send_email(email, 0)
        
        return True
    
    def unsubscribe(self, email: str):
        """Unsubscribe from sequences"""
        if email in self.subscribers:
            self.subscribers[email]["status"] = "unsubscribed"
    
    def process_queue(self):
        """Process pending emails (run daily via cron/scheduler)"""
        
        now = datetime.now()
        
        for email, subscriber in self.subscribers.items():
            if subscriber["status"] != "active":
                continue
            
            sequence = self.sequences.get(subscriber["sequence"])
            if not sequence:
                continue
            
            current_step = subscriber["current_step"]
            if current_step >= len(sequence.emails):
                subscriber["status"] = "completed"
                continue
            
            email_config = sequence.emails[current_step]
            delay_days = email_config.get("delay_days", 0)
            
            # Check if enough time has passed
            if subscriber["last_sent"]:
                last_sent = datetime.fromisoformat(subscriber["last_sent"])
                if (now - last_sent).days < delay_days:
                    continue
            
            # Send the email
            self._send_email(email, current_step)
    
    def _send_email(self, to_email: str, step: int):
        """Send a specific email in the sequence"""
        
        subscriber = self.subscribers[to_email]
        sequence = self.sequences[subscriber["sequence"]]
        email_config = sequence.emails[step]
        
        # Personalize
        name = subscriber["name"].split()[0] if subscriber["name"] else "there"
        subject = email_config["subject"].replace("{name}", name)
        body = email_config["body"].replace("{name}", name)
        
        # Send
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
            
            # Update subscriber
            subscriber["current_step"] += 1
            subscriber["last_sent"] = datetime.now().isoformat()
            
            print(f"Sent email to {to_email}: {subject}")
            
        except Exception as e:
            print(f"Failed to send to {to_email}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sequence statistics"""
        
        stats = {
            "total_subscribers": len(self.subscribers),
            "active": sum(1 for s in self.subscribers.values() if s["status"] == "active"),
            "completed": sum(1 for s in self.subscribers.values() if s["status"] == "completed"),
            "unsubscribed": sum(1 for s in self.subscribers.values() if s["status"] == "unsubscribed")
        }
        
        return stats


# Pre-built sequence templates
WELCOME_SEQUENCE = EmailSequence(
    name="welcome",
    emails=[
        {
            "delay_days": 0,
            "subject": "Welcome {name}!",
            "body": """
Hi {name},

Thanks for joining us! We're excited to have you.

Here's what you can expect:
- Helpful tips and resources
- Exclusive offers
- Updates on what's new

Stay tuned for our next email!

Best,
The Team
"""
        },
        {
            "delay_days": 2,
            "subject": "Quick question for you",
            "body": """
Hi {name},

Just checking in - do you have any questions about [product/service]?

We're here to help!

Reply to this email anytime.

Best,
The Team
"""
        },
        {
            "delay_days": 5,
            "subject": "A little something for you",
            "body": """
Hi {name},

As a thank you for joining, here's a special offer:

[INSERT DISCOUNT CODE OR FREEBIE]

Enjoy!

Best,
The Team
"""
        }
    ]
)

LEAD_NURTURE_SEQUENCE = EmailSequence(
    name="lead_nurture",
    emails=[
        {
            "delay_days": 0,
            "subject": "Thanks for your interest!",
            "body": """
Hi {name},

Thanks for reaching out about our services.

I'd love to learn more about your needs. Would you be open to a quick 15-minute call this week?

Just reply with a time that works for you.

Best,
The Team
"""
        },
        {
            "delay_days": 3,
            "subject": "How we've helped others",
            "body": """
Hi {name},

I wanted to share a quick success story:

"[Client testimonial here]"

Would you like similar results? Let's talk.

Best,
The Team
"""
        },
        {
            "delay_days": 7,
            "subject": "Still interested?",
            "body": """
Hi {name},

Just following up on my last email.

I know you're busy, so I'll keep this short:

If you're still interested in [service], I have a few spots open this month.

No pressure - just let me know!

Best,
The Team
"""
        }
    ]
)

REVIEW_REQUEST_SEQUENCE = EmailSequence(
    name="review_request",
    emails=[
        {
            "delay_days": 3,
            "subject": "How was your experience?",
            "body": """
Hi {name},

Thanks for working with us! We hope you had a great experience.

Would you mind taking 2 minutes to leave us a review? It really helps us out:

[REVIEW LINK]

Thanks so much!

Best,
The Team
"""
        },
        {
            "delay_days": 7,
            "subject": "Quick favor?",
            "body": """
Hi {name},

I know I asked before, but if you haven't had a chance yet, we'd really appreciate your review.

It only takes 2 minutes and helps other people find us.

[REVIEW LINK]

Thanks!

Best,
The Team
"""
        }
    ]
)


# Example usage
if __name__ == "__main__":
    smtp_config = {
        "host": "smtp.gmail.com",
        "port": 587,
        "username": "your-email@gmail.com",
        "password": "your-app-password",
        "from_email": "your-email@gmail.com"
    }
    
    automation = FollowUpAutomation(smtp_config)
    
    # Add sequences
    automation.add_sequence(WELCOME_SEQUENCE)
    automation.add_sequence(LEAD_NURTURE_SEQUENCE)
    
    # Subscribe a lead
    automation.subscribe("john@example.com", "John Doe", "welcome")
    
    # Check stats
    print("Stats:", automation.get_stats())
    
    # Process queue (would run daily)
    # automation.process_queue()
