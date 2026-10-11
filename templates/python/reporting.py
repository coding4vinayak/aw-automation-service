#!/usr/bin/env python3
"""
Reporting Automation
Auto-generate and send reports
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json


class ReportAutomation:
    def __init__(self, smtp_config: Dict[str, Any] = None):
        self.smtp_config = smtp_config
        self.reports = []
        
    def generate_lead_report(self, leads: List[Dict]) -> Dict[str, Any]:
        total = len(leads)
        new_today = len([l for l in leads if l.get("date") == datetime.now().strftime("%Y-%m-%d")])
        sources = {}
        for lead in leads:
            source = lead.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        report = {
            "type": "lead_report",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_leads": total,
            "new_today": new_today,
            "by_source": sources,
            "conversion_rate": f"{(len([l for l in leads if l.get('converted')]) / total * 100) if total > 0 else 0:.1f}%"
        }
        self.reports.append(report)
        return report
    
    def generate_email_report(self, emails_sent: int, opened: int, clicked: int) -> Dict[str, Any]:
        report = {
            "type": "email_report",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "sent": emails_sent,
            "opened": opened,
            "clicked": clicked,
            "open_rate": f"{(opened / emails_sent * 100) if emails_sent > 0 else 0:.1f}%",
            "click_rate": f"{(clicked / emails_sent * 100) if emails_sent > 0 else 0:.1f}%"
        }
        self.reports.append(report)
        return report
    
    def generate_appointment_report(self, appointments: List[Dict]) -> Dict[str, Any]:
        total = len(appointments)
        completed = len([a for a in appointments if a.get("status") == "completed"])
        no_show = len([a for a in appointments if a.get("status") == "no_show"])
        
        report = {
            "type": "appointment_report",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total": total,
            "completed": completed,
            "no_show": no_show,
            "no_show_rate": f"{(no_show / total * 100) if total > 0 else 0:.1f}%"
        }
        self.reports.append(report)
        return report
    
    def format_report(self, report: Dict[str, Any]) -> str:
        lines = [f"=== {report['type'].replace('_', ' ').title()} ===", f"Date: {report['date']}", ""]
        for key, value in report.items():
            if key not in ["type", "date"]:
                lines.append(f"{key.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)
    
    def send_report(self, to_email: str, report: Dict[str, Any]):
        if not self.smtp_config or not self.smtp_config.get("host"):
            print(f"Report generated:\n{self.format_report(report)}")
            return
        
        body = self.format_report(report)
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config["from_email"]
        msg['To'] = to_email
        msg['Subject'] = f"Daily Report - {report['date']}"
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_config["host"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["username"], self.smtp_config["password"])
                server.send_message(msg)
            print(f"Report sent to {to_email}")
        except Exception as e:
            print(f"Failed to send: {e}")


if __name__ == "__main__":
    report_auto = ReportAutomation()
    
    leads = [
        {"name": "John", "email": "john@test.com", "source": "website", "date": "2026-01-15"},
        {"name": "Jane", "email": "jane@test.com", "source": "facebook", "date": "2026-01-15"},
        {"name": "Bob", "email": "bob@test.com", "source": "website", "date": "2026-01-14"}
    ]
    
    report = report_auto.generate_lead_report(leads)
    print(report_auto.format_report(report))
