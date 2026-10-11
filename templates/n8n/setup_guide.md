# n8n Setup & Workflow Guide

## What is n8n?
Free, open-source automation tool. Self-hosted = unlimited executions.

## Installation Options

### Option 1: Docker (Recommended)
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### Option 2: npm
```bash
npm install n8n -g
n8n start
```

### Option 3: Cloud (Paid)
- https://n8n.io/cloud
- Free trial available

---

## Quick Start

1. Open http://localhost:5678
2. Create account
3. Import workflow JSON
4. Add credentials (Google, SMTP, etc.)
5. Activate workflow

---

## Common Workflows

### 1. Form Submission → Sheets + Email

```
Webhook (POST) → IF (email exists) → Google Sheets + Send Email
```

**Webhook URL:** http://localhost:5678/webhook/lead-capture

**Test with curl:**
```bash
curl -X POST http://localhost:5678/webhook/lead-capture \
  -H "Content-Type: application/json" \
  -d '{"name":"John","email":"john@test.com","phone":"555-1234"}'
```

### 2. Daily Report Generator

```
Cron (9am daily) → Google Sheets (read data) → Format → Send Email
```

### 3. Appointment Reminders

```
Cron (daily 8am) → Google Sheets (read tomorrow's appointments) → Send Emails
```

---

## Credentials Setup

### Google Sheets
1. Go to Google Cloud Console
2. Create service account
3. Download JSON key
4. In n8n: Credentials → Google Sheets → Service Account
5. Upload JSON file

### SMTP (Gmail)
1. Enable 2FA on Gmail
2. Generate App Password
3. In n8n: Credentials → SMTP
   - Host: smtp.gmail.com
   - Port: 587
   - User: your-email@gmail.com
   - Password: your-app-password

### Slack
1. Create Slack App
2. Add OAuth scopes
3. Install to workspace
4. In n8n: Credentials → Slack API

---

## Workflow JSON Templates

See files in this directory:
- `lead_capture_workflow.json`
- `email_sequence_workflow.json`
- `daily_report_workflow.json`

---

## Deployment (Free Options)

### 1. Railway.app
- Free tier available
- Deploy from GitHub
- Custom domain support

### 2. Render.com
- Free tier
- Auto-deploy from GitHub

### 3. Fly.io
- Free tier (limited)
- Docker deployment

### 4. Your Own VPS
- DigitalOcean: $5/month
- Vultr: $3.50/month
- Hetzner: €4/month

---

## Client Setup Checklist

- [ ] n8n installed and running
- [ ] Credentials configured
- [ ] Workflow imported
- [ ] Webhook URLs tested
- [ ] Client trained on basics
- [ ] Documentation provided
