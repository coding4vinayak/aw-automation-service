# AutoFlow - Complete Automation Business

Ready-to-sell automation service business with website, templates, and marketing materials.

## Quick Start

```bash
# 1. Deploy website (free)
cd website && python3 -m http.server 8000

# 2. Open http://localhost:8000
```

## 🌐 Website Pages (20 pages)

| Page | File | Purpose |
|------|------|---------|
| Home | `index.html` | Landing page with services, pricing, FAQ |
| About | `about.html` | Company story and team |
| Lead Capture | `services/lead-capture.html` | Detailed service page |
| Email Automation | `services/email-automation.html` | Detailed service page |
| Appointment Booking | `services/appointment-booking.html` | Detailed service page |
| Case Studies | `case-studies.html` | Client success stories |
| Booking | `booking.html` | Discovery call booking |
| Calculator | `calculator.html` | Interactive pricing calculator |
| Free Audit | `audit.html` | Lead magnet (checklist) |
| Portfolio | `portfolio.html` | Example automations |
| Invoice | `invoice.html` | Printable invoice template |
| Dashboard | `dashboard.html` | Client dashboard template |
| Terms | `terms.html` | Terms of service |
| Privacy | `privacy.html` | Privacy policy |
| Thank You | `thank-you.html` | Post-form confirmation |
| Suite Status | `suite.html` | Live status of all 8 products (generated) |
| 404 | `404.html` | Error page |

## 💰 Service Packages

| Package | Price | Includes |
|---------|-------|----------|
| Starter | $297 | 1 automation + training |
| Growth | $697 | 3 automations + support |
| Premium | $1,497 | 5 automations + dashboard |
| Retainer | $297/mo | Ongoing maintenance |

## 🛠️ Automation Templates

### Python (`templates/python/`)
- `lead_capture.py` - Form → Google Sheets → Email
- `email_followup.py` - Email sequence automation
- `appointment_booking.py` - Booking + reminders
- `invoice_automation.py` - Invoice + payment reminders
- `social_media.py` - Content scheduling
- `reporting.py` - Auto-generate reports

### n8n (`templates/n8n/`)
- `lead_capture_workflow.json`
- `email_sequence_workflow.json`
- `invoice_workflow.json`
- `setup_guide.md`

### Zapier/Make
- `templates/zapier/workflow_templates.md`
- `templates/make/workflow_templates.md`

## 📋 Marketing Materials

| File | Purpose |
|------|---------|
| `marketing/email-templates.md` | 8 cold email templates |
| `marketing/social-media-templates.md` | 8 social posts + schedule |
| `marketing/client-onboarding-sequence.md` | 10-email onboarding sequence |
| `marketing/referral-program.md` | Referral program details |
| `marketing/upsell-templates.md` | Upsell/cross-sell scripts |
| `marketing/webinar-kit.md` | Free workshop kit |
| `marketing/blog-templates.md` | 8 blog post templates |

## 📄 Business Documents

| File | Purpose |
|------|---------|
| `docs/service_packages.md` | Full pricing guide |
| `docs/outreach_templates.md` | Cold DM/email scripts |
| `docs/proposal_template.md` | Client proposal |
| `docs/service_agreement.md` | Contract template |
| `onboarding/questionnaire.md` | Client intake form |

## 🚀 Deploy Website (Free)

### GitHub Pages
1. Push to GitHub
2. Settings → Pages → Source: `master`, folder: `/website`
3. Done!

### Netlify
1. Drag & drop `website/` folder to netlify.com
2. Done!

## 📝 Setup Checklist

1. [ ] Put your business email + WhatsApp number in `website/js/enquiry.js` → `ROUTING`
2. [ ] Run `node scripts/check-buy-path.mjs` (must report 0 failed)
3. [ ] Deploy website — it is static, any host works, see `website/README.md`
4. [ ] Add your name/email to templates
5. [ ] Update social media links in footer
6. [ ] Customize testimonials with real clients
7. [ ] Start outreach using templates

## 🎯 Find Clients

1. LinkedIn DMs (see `docs/outreach_templates.md`)
2. Facebook Groups (local business owners)
3. Google Maps (find businesses without automation)
4. Cold Email (use `marketing/email-templates.md`)
5. Referrals (offer $100 credit - see `marketing/referral-program.md`)
6. Free Audit (use `website/audit.html` as lead magnet)
7. Webinars (use `marketing/webinar-kit.md`)

## 📈 Revenue Targets

| Month | Clients | Revenue |
|-------|---------|---------|
| 1 | 2 | $594 |
| 2 | 3 | $891-2,091 |
| 3 | 5 | $1,485-7,485 |
| 6 | 10 + retainers | $2,970-14,970/mo |

## 📁 Full Structure

```
automation-service/
├── website/                    # Deploy-ready website (20 pages)
├── templates/                  # Automation templates
│   ├── python/                 # 6 Python scripts
│   ├── n8n/                    # 3 workflows + guide
│   ├── zapier/                 # Step-by-step guides
│   └── make/                   # Make.com guides
├── marketing/                  # Sales & marketing
│   ├── email-templates.md
│   ├── social-media-templates.md
│   ├── client-onboarding-sequence.md
│   ├── referral-program.md
│   ├── upsell-templates.md
│   ├── webinar-kit.md
│   └── blog-templates.md
├── docs/                       # Business documents
│   ├── service_packages.md
│   ├── outreach_templates.md
│   ├── proposal_template.md
│   └── service_agreement.md
├── onboarding/
│   └── questionnaire.md
├── scripts/
│   ├── assessment.py
│   └── quick_assessment.py
├── CHECKLIST.md
└── README.md
```

## Ready to Launch!

1. Configure `ROUTING` in `website/js/enquiry.js` (email + WhatsApp number)
2. Run the three checks below — all must exit 0
3. Deploy website (GitHub Pages or Netlify — it is static)
4. Add your info to all templates
5. Start outreach
6. Close first client
7. Deliver using templates
8. Scale!

## Checking the buy path

Two scripts in `scripts/`, no dependencies for the first one:

```bash
node scripts/check-buy-path.mjs                      # static, no dependencies
AUTOFLOW_JSDOM=/path/to/jsdom node scripts/check-buy-path.dom.mjs   # drives real pages
node scripts/check-ui.mjs                            # static, no dependencies
```

(The DOM probe needs jsdom, which this repository does not carry because it is a
static site; point it at any copy that exists nearby.)

The static check asserts that no placeholder transport is configured anywhere, that
every page taking a lead routes it through `js/enquiry.js`, that every page quoting a
price can reach a form, that no link resolves to a missing file, that every
`booking.html?service=` deep link names an option that exists, and that the enquiry
composer encodes `wa.me` and `mailto:` links correctly.

The static check has a blind spot worth naming: it reads markup, so a link that
JavaScript assembles at runtime looks like whatever the file says. `calculator.html`
kept its `href` as a bare `booking.html` and filled it in on click — which meant the
package a visitor built, and the discounted total printed on the button, were both
discarded, and 300-odd static assertions saw nothing. Two things close it now: the DOM
probe drives the real clicks and decodes the resulting enquiry, and the static check
verifies the calculator's card-to-topic map as data, so a service added without a
mapping fails there too.

If you change either check, confirm it can still fail — delete a line the assertion
claims to protect and watch it go red. An assertion that has never been seen to fail
is decoration.

That matters more here than in most projects: for months this site had three forms
that collected a customer's details, printed them to the browser console, and then
told the visitor the enquiry had been sent. It looked exactly like working software.
The DOM probe is what closes that gap — it loads each real page, fills the real
fields, presses submit, and decodes the link that came out.

## Checking the interface

`node scripts/check-ui.mjs` asserts the WCAG basics across all 20 pages, with no
dependencies: every page declares `lang`, carries a unique non-empty title, keeps
viewport zoom enabled, gives every image `alt` text, associates every form
control with its label (`for`/`id`, wrapping, or `aria-label`), and keeps exactly
one `h1` with no skipped heading levels. It has been seen to fail — remove one
`for` and it goes red.
