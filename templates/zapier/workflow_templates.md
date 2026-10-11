# Zapier Automation Templates

## 1. Lead Capture: Form → Google Sheets + Email

### Steps:
1. **Trigger:** Typeform / JotForm / Google Forms submission
2. **Action 1:** Google Sheets - Add Row
3. **Action 2:** Gmail - Send Email

### Zapier Instructions:
```
TRIGGER: Typeform
- Select form: "Contact Us"
- Test trigger to get sample data

ACTION 1: Google Sheets
- Spreadsheet: "Leads"
- Worksheet: "Sheet1"
- Map fields:
  - Name: {{form_data.name}}
  - Email: {{form_data.email}}
  - Phone: {{form_data.phone}}
  - Message: {{form_data.message}}

ACTION 2: Gmail
- To: {{form_data.email}}
- Subject: "Thanks for reaching out!"
- Body: "Hi {{form_data.name}}, Thanks for your interest..."
```

---

## 2. Appointment Reminders: Google Calendar → Email

### Steps:
1. **Trigger:** Google Calendar - Event in 24 hours
2. **Action:** Gmail - Send Reminder

### Zapier Instructions:
```
TRIGGER: Google Calendar
- Calendar: "Appointments"
- Time before event: 24 hours

ACTION: Gmail
- To: {{calendar_event.attendees.email}}
- Subject: "Reminder: Appointment Tomorrow"
- Body: "Hi {{calendar_event.attendees.name}}, This is a reminder..."
```

---

## 3. New Lead → CRM + Welcome Sequence

### Steps:
1. **Trigger:** HubSpot / Pipedrive - New Contact
2. **Action 1:** Mailchimp - Add Subscriber
3. **Action 2:** Slack - Notify Team

### Zapier Instructions:
```
TRIGGER: HubSpot
- Event: New Contact Created

ACTION 1: Mailchimp
- List: "New Leads"
- Email: {{hubspot_contact.email}}
- Name: {{hubspot_contact.firstname}}

ACTION 2: Slack
- Channel: #sales
- Message: "New lead: {{hubspot_contact.firstname}} {{hubspot_contact.lastname}}"
```

---

## 4. Invoice Follow-up: QuickBooks → Email

### Steps:
1. **Trigger:** QuickBooks - Invoice Overdue
2. **Action:** Gmail - Send Reminder

### Zapier Instructions:
```
TRIGGER: QuickBooks
- Event: Invoice Overdue

ACTION: Gmail
- To: {{invoice.customer_email}}
- Subject: "Payment Reminder - Invoice #{{invoice.id}}"
- Body: "Hi {{invoice.customer_name}}, This is a friendly reminder..."
```

---

## 5. Review Request: Appointment Complete → Email

### Steps:
1. **Trigger:** Calendly / Acuity - Appointment Complete
2. **Action:** Gmail - Send Review Request (delay 3 days)

### Zapier Instructions:
```
TRIGGER: Calendly
- Event: Invitee Created
- Wait: 3 days

ACTION: Gmail
- To: {{calendly_invitee.email}}
- Subject: "Thanks for visiting!"
- Body: "Hi {{calendly_invitee.name}}, Thanks for your appointment..."
```

---

## Free Zapier Tier Limits
- 100 tasks/month
- 5 Zaps
- 15-minute update time

## Paid Plans
- Starter: $19.99/month (750 tasks)
- Professional: $49/month (2,000 tasks)
