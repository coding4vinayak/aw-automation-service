#!/usr/bin/env python3
"""
Automation Assessment Tool
Analyzes client questionnaire and recommends automations
"""

import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ClientProfile:
    business_name: str
    industry: str
    employees: int
    tools_used: List[str]
    daily_tasks: List[str]
    time_wasters: Dict[str, int]
    pain_points: List[str]
    budget: str
    timeline: str

# Pain point -> Automation mapping
AUTOMATION_MAP = {
    "website_visitors": {
        "name": "Lead Capture Automation",
        "description": "Capture website visitors and add to CRM/email list",
        "tools": ["Zapier", "Make.com", "Python"],
        "setup_time": "2-4 hours",
        "one_time_price": 300,
        "monthly_price": 50,
        "roi": "Convert 5-15% more visitors to leads"
    },
    "leads_cold": {
        "name": "Email Follow-up Sequence",
        "description": "Automated email sequences to nurture leads",
        "tools": ["Mailchimp", "ActiveCampaign", "Python"],
        "setup_time": "3-5 hours",
        "one_time_price": 400,
        "monthly_price": 75,
        "roi": "Recover 20-30% of cold leads"
    },
    "customers_dont_return": {
        "name": "Customer Retention Automation",
        "description": "Post-purchase emails, loyalty rewards, review requests",
        "tools": ["Mailchimp", "Zapier", "Python"],
        "setup_time": "4-6 hours",
        "one_time_price": 500,
        "monthly_price": 100,
        "roi": "Increase repeat purchases by 25-40%"
    },
    "missed_invoices": {
        "name": "Invoice & Payment Automation",
        "description": "Auto-send invoices, track payments, send reminders",
        "tools": ["QuickBooks API", "Python", "Zapier"],
        "setup_time": "3-4 hours",
        "one_time_price": 350,
        "monthly_price": 50,
        "roi": "Reduce late payments by 60%"
    },
    "missed_appointments": {
        "name": "Appointment Booking System",
        "description": "Online booking with reminders and follow-ups",
        "tools": ["Calendly", "Google Calendar", "Zapier"],
        "setup_time": "2-3 hours",
        "one_time_price": 250,
        "monthly_price": 25,
        "roi": "Reduce no-shows by 50%"
    },
    "data_entry": {
        "name": "Data Entry Automation",
        "description": "Auto-populate spreadsheets from forms/emails",
        "tools": ["Python", "Google Sheets API", "n8n"],
        "setup_time": "4-8 hours",
        "one_time_price": 600,
        "monthly_price": 75,
        "roi": "Save 5-10 hours/week"
    },
    "sending_emails": {
        "name": "Email Automation",
        "description": "Triggered emails based on events/conditions",
        "tools": ["Python", "SMTP", "Zapier"],
        "setup_time": "3-5 hours",
        "one_time_price": 400,
        "monthly_price": 50,
        "roi": "Save 3-5 hours/week"
    },
    "follow_ups": {
        "name": "Follow-up Automation",
        "description": "Auto-follow-up sequences for leads/customers",
        "tools": ["Python", "CRM API", "Zapier"],
        "setup_time": "3-4 hours",
        "one_time_price": 350,
        "monthly_price": 50,
        "roi": "Never miss a follow-up again"
    },
    "reporting": {
        "name": "Reporting Dashboard",
        "description": "Auto-generate and send reports",
        "tools": ["Python", "Google Sheets", "Email"],
        "setup_time": "5-8 hours",
        "one_time_price": 700,
        "monthly_price": 100,
        "roi": "Save 3-5 hours/week on reporting"
    },
    "scheduling": {
        "name": "Social Media Scheduling",
        "description": "Auto-post across platforms",
        "tools": ["Buffer", "Hootsuite", "Python"],
        "setup_time": "2-3 hours",
        "one_time_price": 250,
        "monthly_price": 50,
        "roi": "Consistent posting without daily effort"
    }
}

# Industry-specific recommendations
INDUSTRY_AUTOMATIONS = {
    "restaurant": ["appointment_booking", "customer_retention", "reporting"],
    "retail": ["data_entry", "customer_retention", "reporting"],
    "services": ["leads_cold", "follow_ups", "appointment_booking"],
    "real_estate": ["leads_cold", "follow_ups", "scheduling"],
    "healthcare": ["appointment_booking", "follow_ups", "data_entry"],
    "education": ["leads_cold", "follow_ups", "scheduling"],
    "consulting": ["leads_cold", "reporting", "follow_ups"],
    "ecommerce": ["customer_retention", "data_entry", "reporting"]
}

def assess_client(profile: ClientProfile) -> dict:
    """Analyze client profile and recommend automations"""
    
    recommendations = []
    
    # Map pain points to automations
    pain_point_map = {
        "website_visitors": "website_visitors",
        "leads_go_cold": "leads_cold",
        "customers_dont_come_back": "customers_dont_return",
        "forget_to_send_invoices": "missed_invoices",
        "missed_appointments": "missed_appointments"
    }
    
    for pain in profile.pain_points:
        if pain in pain_point_map:
            auto_key = pain_point_map[pain]
            if auto_key in AUTOMATION_MAP:
                recommendations.append(AUTOMATION_MAP[auto_key])
    
    # Add industry-specific automations
    industry_lower = profile.industry.lower()
    for industry_key, auto_keys in INDUSTRY_AUTOMATIONS.items():
        if industry_key in industry_lower:
            for auto_key in auto_keys:
                if auto_key in AUTOMATION_MAP:
                    auto = AUTOMATION_MAP[auto_key]
                    if auto not in recommendations:
                        recommendations.append(auto)
    
    # Add time-waster based recommendations
    if profile.time_wasters.get("data_entry", 0) > 5:
        if AUTOMATION_MAP["data_entry"] not in recommendations:
            recommendations.append(AUTOMATION_MAP["data_entry"])
    
    if profile.time_wasters.get("sending_emails", 0) > 5:
        if AUTOMATION_MAP["sending_emails"] not in recommendations:
            recommendations.append(AUTOMATION_MAP["sending_emails"])
    
    if profile.time_wasters.get("follow_ups", 0) > 5:
        if AUTOMATION_MAP["follow_ups"] not in recommendations:
            recommendations.append(AUTOMATION_MAP["follow_ups"])
    
    if profile.time_wasters.get("reporting", 0) > 5:
        if AUTOMATION_MAP["reporting"] not in recommendations:
            recommendations.append(AUTOMATION_MAP["reporting"])
    
    # Calculate totals
    total_setup = sum(r["one_time_price"] for r in recommendations)
    total_monthly = sum(r["monthly_price"] for r in recommendations)
    total_hours_saved = sum(r["roi"].count("hours") for r in recommendations)
    
    return {
        "client": profile.business_name,
        "industry": profile.industry,
        "recommended_automations": recommendations,
        "pricing": {
            "one_time_total": total_setup,
            "monthly_total": total_monthly,
            "package_discount_10": total_setup * 0.9,
            "package_discount_20": total_setup * 0.8
        },
        "estimated_roi": {
            "hours_saved_per_week": total_hours_saved * 3,
            "potential_revenue_increase": "15-30%"
        }
    }

def format_proposal(assessment: dict) -> str:
    """Format assessment into a client proposal"""
    
    proposal = f"""
═══════════════════════════════════════════════════════════════
                    AUTOMATION PROPOSAL
                    {assessment['client'].upper()}
═══════════════════════════════════════════════════════════════

Business: {assessment['client']}
Industry: {assessment['industry']}

───────────────────────────────────────────────────────────────
RECOMMENDED AUTOMATIONS
───────────────────────────────────────────────────────────────
"""
    
    for i, auto in enumerate(assessment['recommended_automations'], 1):
        proposal += f"""
{i}. {auto['name']}
   {auto['description']}
   Tools: {', '.join(auto['tools'])}
   Setup Time: {auto['setup_time']}
   One-time: ${auto['one_time_price']}
   Monthly: ${auto['monthly_price']}/month
   Expected ROI: {auto['roi']}
"""
    
    pricing = assessment['pricing']
    proposal += f"""
───────────────────────────────────────────────────────────────
PRICING OPTIONS
───────────────────────────────────────────────────────────────

Option A: Pay Per Automation
  Total Setup: ${pricing['one_time_total']}
  Monthly: ${pricing['monthly_total']}/month

Option B: Package Deal (10% off)
  Total Setup: ${pricing['package_discount_10']:.0f}
  Monthly: ${pricing['monthly_total']}/month

Option C: Premium Package (20% off)
  Total Setup: ${pricing['package_discount_20']:.0f}
  Monthly: ${pricing['monthly_total']}/month
  + Priority support
  + 1 free automation/month

───────────────────────────────────────────────────────────────
EXPECTED RESULTS
───────────────────────────────────────────────────────────────

  Hours Saved: ~{assessment['estimated_roi']['hours_saved_per_week']} hours/week
  Revenue Increase: {assessment['estimated_roi']['potential_revenue_increase']}
  Payback Period: 1-2 months

───────────────────────────────────────────────────────────────
NEXT STEPS
───────────────────────────────────────────────────────────────

1. Choose your package
2. I'll start building within 24 hours
3. First draft in 3-5 days
4. Training + go-live in 1 week

═══════════════════════════════════════════════════════════════
"""
    
    return proposal

# Example usage
if __name__ == "__main__":
    # Sample client
    client = ClientProfile(
        business_name="Smith's Dental Clinic",
        industry="healthcare",
        employees=5,
        tools_used=["google_sheets", "email", "phone"],
        daily_tasks=["data_entry", "sending_emails", "follow_ups"],
        time_wasters={"data_entry": 10, "sending_emails": 8, "follow_ups": 6},
        pain_points=["missed_appointments", "leads_go_cold"],
        budget="one_time_and_monthly",
        timeline="within_2_weeks"
    )
    
    assessment = assess_client(client)
    print(format_proposal(assessment))
