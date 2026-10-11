#!/usr/bin/env python3
"""
Quick Client Assessment
Interactive tool to assess client needs
"""

# Automation options with details
AUTOMATIONS = {
    "1": {
        "name": "Lead Capture",
        "description": "Capture website/form leads → Google Sheets → Welcome email",
        "price": 147,
        "tools": "Zapier/n8n + Google Sheets",
        "setup_time": "2-3 hours",
        "client_value": "Never miss a lead again"
    },
    "2": {
        "name": "Email Follow-up",
        "description": "Automated email sequences to nurture leads",
        "price": 197,
        "tools": "Mailchimp/ActiveCampaign + Zapier",
        "setup_time": "3-4 hours",
        "client_value": "Recover 20-30% of cold leads"
    },
    "3": {
        "name": "Appointment Booking",
        "description": "Online booking + reminders + follow-ups",
        "price": 197,
        "tools": "Calendly + Google Calendar + Zapier",
        "setup_time": "2-3 hours",
        "client_value": "Reduce no-shows by 50%"
    },
    "4": {
        "name": "Invoice Reminders",
        "description": "Auto-send payment reminders",
        "price": 147,
        "tools": "QuickBooks + Zapier",
        "setup_time": "2-3 hours",
        "client_value": "Get paid 40% faster"
    },
    "5": {
        "name": "Review Requests",
        "description": "Auto-request reviews after service",
        "price": 147,
        "tools": "Calendly + Gmail + Zapier",
        "setup_time": "1-2 hours",
        "client_value": "2x more reviews"
    },
    "6": {
        "name": "Social Media Scheduling",
        "description": "Auto-post across platforms",
        "price": 197,
        "tools": "Buffer/Hootsuite + Zapier",
        "setup_time": "2-3 hours",
        "client_value": "Consistent posting"
    }
}


def print_header():
    print("\n" + "="*50)
    print("     AUTOMATION SERVICE - CLIENT ASSESSMENT")
    print("="*50)


def get_business_info():
    print("\n--- BUSINESS INFO ---")
    name = input("Business name: ")
    industry = input("Industry: ")
    employees = input("Number of employees: ")
    return {"name": name, "industry": industry, "employees": employees}


def get_pain_points():
    print("\n--- PAIN POINTS ---")
    print("What wastes your time most?")
    print("1. Manual data entry")
    print("2. Following up with leads")
    print("3. Appointment scheduling")
    print("4. Sending invoices/reminders")
    print("5. Requesting reviews")
    print("6. Social media posting")
    
    choices = input("\nEnter numbers (comma-separated): ").split(",")
    return [c.strip() for c in choices]


def get_budget():
    print("\n--- BUDGET ---")
    print("1. Under $300")
    print("2. $300-500")
    print("3. $500-1000")
    print("4. $1000+")
    choice = input("Select: ")
    
    budgets = {"1": "low", "2": "medium", "3": "high", "4": "premium"}
    return budgets.get(choice, "medium")


def generate_recommendation(business, pain_points, budget):
    print("\n" + "="*50)
    print("     RECOMMENDATION")
    print("="*50)
    
    print(f"\nBusiness: {business['name']}")
    print(f"Industry: {business['industry']}")
    
    # Map pain points to automations
    pain_to_auto = {
        "1": "1",  # data entry -> lead capture
        "2": "2",  # follow-up -> email follow-up
        "3": "3",  # scheduling -> appointment booking
        "4": "4",  # invoices -> invoice reminders
        "5": "5",  # reviews -> review requests
        "6": "6"   # social media -> scheduling
    }
    
    recommended = []
    total_price = 0
    
    print("\nRECOMMENDED AUTOMATIONS:")
    print("-" * 40)
    
    for pain in pain_points:
        if pain in pain_to_auto:
            auto = AUTOMATIONS[pain_to_auto[pain]]
            recommended.append(auto)
            total_price += auto["price"]
            print(f"\n✓ {auto['name']}")
            print(f"  {auto['description']}")
            print(f"  Setup: {auto['setup_time']}")
            print(f"  Price: ${auto['price']}")
    
    print("\n" + "-" * 40)
    print(f"\nTOTAL SETUP: ${total_price}")
    
    # Package recommendation
    if len(recommended) >= 3:
        package_price = total_price * 0.8  # 20% discount
        print(f"PACKAGE DEAL (20% off): ${package_price:.0f}")
    
    print(f"\nMonthly tools cost: $0-20 (free tiers)")
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("1. Send proposal to client")
    print("2. Get 50% payment upfront")
    print("3. Build automation (1-3 days)")
    print("4. Train client + deliver")
    print("5. Get remaining payment")
    print("="*50)


def main():
    print_header()
    
    business = get_business_info()
    pain_points = get_pain_points()
    budget = get_budget()
    
    generate_recommendation(business, pain_points, budget)


if __name__ == "__main__":
    main()
