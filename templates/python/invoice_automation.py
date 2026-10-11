#!/usr/bin/env python3
"""
Invoice & Payment Automation
Auto-send invoices, track payments, send reminders
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any


class InvoiceAutomation:
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.invoices = []
        
    def create_invoice(self, client: Dict[str, str], items: List[Dict], due_days: int = 30) -> Dict[str, Any]:
        total = sum(item["amount"] for item in items)
        invoice = {
            "id": f"INV-{len(self.invoices) + 1:04d}",
            "client": client,
            "items": items,
            "total": total,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=due_days)).isoformat(),
            "reminders_sent": []
        }
        self.invoices.append(invoice)
        self._send_invoice(invoice)
        return invoice
    
    def mark_paid(self, invoice_id: str) -> bool:
        for inv in self.invoices:
            if inv["id"] == invoice_id:
                inv["status"] = "paid"
                return True
        return False
    
    def send_reminders(self):
        today = datetime.now()
        for inv in self.invoices:
            if inv["status"] != "pending":
                continue
            due_date = datetime.fromisoformat(inv["due_date"])
            days_until_due = (due_date - today).days
            if days_until_due == 3 and "3_days" not in inv["reminders_sent"]:
                self._send_reminder(inv, "3 days before due")
                inv["reminders_sent"].append("3_days")
            elif days_until_due == 0 and "due_today" not in inv["reminders_sent"]:
                self._send_reminder(inv, "due today")
                inv["reminders_sent"].append("due_today")
            elif days_until_due == -3 and "overdue_3" not in inv["reminders_sent"]:
                self._send_reminder(inv, "3 days overdue")
                inv["reminders_sent"].append("overdue_3")
    
    def _send_invoice(self, invoice: Dict[str, Any]):
        client = invoice["client"]
        items_text = "\n".join([f"- {item['description']}: ${item['amount']}" for item in invoice["items"]])
        body = f"""
Hi {client['name']},

Here is your invoice:

Invoice #: {invoice['id']}
Items:
{items_text}

Total: ${invoice['total']}
Due Date: {invoice['due_date'][:10]}

Please submit payment via PayPal or Stripe.

Thank you!
[Your Name]
"""
        self._send_email(client['email'], f"Invoice #{invoice['id']} - ${invoice['total']}", body)
    
    def _send_reminder(self, invoice: Dict[str, Any], message: str):
        client = invoice["client"]
        body = f"""
Hi {client['name']},

This is a reminder that invoice #{invoice['id']} is {message}.

Amount Due: ${invoice['total']}

Please submit payment at your earliest convenience.

Thank you!
[Your Name]
"""
        self._send_email(client['email'], f"Payment Reminder - Invoice #{invoice['id']}", body)
    
    def _send_email(self, to_email: str, subject: str, body: str):
        if not self.smtp_config.get("host"):
            print(f"Would send to {to_email}: {subject}")
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
            print(f"Sent: {subject}")
        except Exception as e:
            print(f"Failed: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        pending = [i for i in self.invoices if i["status"] == "pending"]
        paid = [i for i in self.invoices if i["status"] == "paid"]
        return {
            "total": len(self.invoices),
            "pending": len(pending),
            "paid": len(paid),
            "pending_amount": sum(i["total"] for i in pending),
            "paid_amount": sum(i["total"] for i in paid)
        }


if __name__ == "__main__":
    smtp = {"host": "smtp.gmail.com", "port": 587, "username": "test@gmail.com", "password": "pass", "from_email": "test@gmail.com"}
    auto = InvoiceAutomation(smtp)
    inv = auto.create_invoice(
        client={"name": "John", "email": "john@test.com"},
        items=[{"description": "Lead Capture", "amount": 147}, {"description": "Email Sequence", "amount": 197}]
    )
    print(f"Created: {inv['id']} - ${inv['total']}")
