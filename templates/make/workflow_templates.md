# Make.com (Integromat) Automation Templates

## 1. Lead Capture Multi-Step

### Scenario:
```
Webhook → Filter → Google Sheets → Router → Email + Slack
```

### Make.com Instructions:
```
MODULE 1: Webhook
- Create custom webhook
- URL: https://hook.make.com/your-unique-id
- Expected data: name, email, phone, message

MODULE 2: Filter
- Condition: Email is not empty

MODULE 3: Google Sheets
- Connection: Your Google account
- Spreadsheet: Leads
- Action: Add a Row
- Map: Name, Email, Phone, Message

MODULE 4: Router
- Path A: Send Email
- Path B: Notify Slack

MODULE 5A: Email
- To: {{1.email}}
- Subject: Thanks {{1.name}}!
- Body: Personalized message

MODULE 5B: Slack
- Channel: #leads
- Message: New lead: {{1.name}} ({{1.email}})
```

---

## 2. Appointment Booking Flow

### Scenario:
```
Calendly → Google Calendar → Email Confirmation → Reminder (24h)
```

### Make.com Instructions:
```
MODULE 1: Calendly
- Watch for new events

MODULE 2: Google Sheets
- Add row with booking details

MODULE 3: Email
- Send confirmation to attendee

MODULE 4: Sleep
- Wait 23 hours

MODULE 5: Email
- Send reminder
```

---

## 3. Social Media Auto-Post

### Scenario:
```
RSS Feed / New Blog → Buffer → Post to Social
```

### Make.com Instructions:
```
MODULE 1: RSS
- URL: https://yourblog.com/feed

MODULE 2: Buffer
- Add to queue
- Profile: Your social accounts
- Content: {{1.title}} - {{1.link}}
```

---

## Free Make.com Tier
- 1,000 operations/month
- 2 active scenarios
- 15-minute check interval

## Paid Plans
- Core: $9/month (10,000 ops)
- Pro: $16/month (10,000 ops + faster)
