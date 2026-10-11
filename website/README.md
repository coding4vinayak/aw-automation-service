# AutoFlow Website

Complete business website for selling automation services.

## Pages

| Page | File | Description |
|------|------|-------------|
| Home | `index.html` | Main landing page with hero, services, pricing, FAQ |
| Booking | `booking.html` | Discovery call booking page |
| Portfolio | `portfolio.html` | Example automations and results |
| Thank You | `thank-you.html` | Post-form submission page |
| 404 | `404.html` | Error page |

## Features

- ✅ Mobile-responsive design
- ✅ Tailwind CSS (CDN)
- ✅ ROI Calculator
- ✅ FAQ accordion
- ✅ Contact form
- ✅ Booking system
- ✅ Portfolio showcase
- ✅ Smooth animations
- ✅ SEO meta tags

## Deployment (Free Options)

### GitHub Pages (Recommended)
```bash
# Push to GitHub
git add .
git commit -m "Add website"
git push

# Enable GitHub Pages
# Settings → Pages → Source: master branch → /website
```

### Netlify (Free)
1. Drag & drop `website/` folder to Netlify
2. Custom domain support

### Vercel (Free)
```bash
vercel --prod
```

## Where enquiries go

There is no form backend, and there does not need to be one. All three forms —
`index.html`, `booking.html`, `audit.html` — compose the visitor's answer into a
message and open it in the visitor's own WhatsApp or mail app. Nothing is stored,
no server is involved, and no account has to be created to take a lead.

The single place to configure it is `js/enquiry.js`:

```js
var ROUTING = {
  email: "hello@abetworks.in",
  whatsapp: "",                      // "919812345678" — country code, digits only
  phone: "",                         // click-to-call link
  replyPromise: "within 1 working day",
};
```

Put your business WhatsApp number in `whatsapp` and it becomes the primary channel:
the panel leads with a `wa.me` deep link that already contains the enquiry text, and
mail stays underneath for desktop visitors.

**Do not put `+91 98765 43210` here.** It is the dummy that seeds every template in
this kit, it is a well-formed Indian mobile, and an enquiry sent to it reaches a
stranger. `enquiry.js` refuses it by name, along with any number too short to be
real and any `@example.com`-style address — a channel that is not genuinely
configured is switched off rather than guessed at.

### Why the panel says "one more tap" and not "thanks, we'll be in touch"

Before this existed, all three forms printed the submission to the browser console
and then told the visitor it had worked. `booking.html` went as far as a
"Booking Confirmed! Check your email for a calendar invite" modal for a meeting
nobody could ever see, and `index.html` had a green "✓ We'll get back to you within
24 hours" box. A prospect who believes they are booked does not try again — they
wait for an invite that is not coming. A browser cannot know whether a deep link was
followed, so the panel shows the composed enquiry, offers every channel again, and
has a copy button. It claims exactly what it can guarantee.

### If you want submissions stored rather than relayed

The transports above need nothing but a phone. If you later want leads captured on a
server — so nothing depends on the visitor pressing send in the app that opened — the
endpoint is `abetConnect`'s `POST /api/v1/messages`, authenticated with a workspace API
key as `Authorization: Bearer <key>` (or `x-api-key`), using the `WEBFORM` channel:

```json
{
  "channel": "WEBFORM",
  "payload": {
    "name": "Sneha Rao", "email": "sneha@brightbay.test", "phone": "+91 98123 45678",
    "company": "Bright Bay Café", "subject": "Lead capture for a 4-person team",
    "message": "We chase payments on WhatsApp every single day."
  }
}
```

Those are the field names this site's forms already collect — `message` also accepts
`notes`, `comments`, `body` or `text`, and `company` is derived from the email domain if
you omit it. The reply is `201` with
`{ threadId, messageId, contactId, duplicate, draftId, triage: { score, bucket, intent,
reason, signals } }`.

Include a stable `submissionId` in the payload. Replays are detected on the
`(threadId, externalId)` pair, so a re-post of the same submission returns `200` with
`duplicate: true` and leaves the score untouched — but with no `submissionId` there is
nothing to compare, and a double-clicked submit button becomes two messages in the
thread and two rounds of engagement signals. A form has no provider message id to lean
on, so mint one when the page renders and send it unchanged.

This is **not wired up here, deliberately**. `abetConnect` is not deployed, so pointing
the forms at it would trade a working `mailto:` for a 404 — which is the fake success
state this whole page exists to prevent, just with a real backend behind it that nobody
installed. When it goes live the change is one `fetch` inside `submit` in
`js/enquiry.js`, keeping the panel as the fallback for when the request fails rather
than replacing it.

`thank-you.html` exists for that future and for nothing else. No form redirects to it
any more, because a page that says "Thanks for Reaching Out!" is a claim this site
still cannot make: it would be reached whether or not the visitor pressed send in the
app that opened. Leave it as the destination of a server-backed flow.

## Customization

### Change Branding
1. Edit colors in `tailwind.config` (index.html)
2. Update logo text: "⚡ AutoFlow"
3. Replace placeholder testimonials

### Update Content
- Services: Edit services section in `index.html`
- Pricing: Edit pricing section
- Contact: Update email/phone in footer

### Add Real Testimonials
Replace placeholder testimonials in `index.html` with real client quotes.

## Quick Start

```bash
# Local development
cd website
python3 -m http.server 8000

# Open http://localhost:8000
```

## File Structure

```
website/
├── index.html          # Main landing page
├── booking.html        # Booking page
├── portfolio.html      # Portfolio page
├── thank-you.html      # Thank you page
├── 404.html            # Error page
├── css/
│   └── (empty - using Tailwind CDN)
├── js/
│   └── main.js         # Interactivity
└── assets/
    └── images/         # Images folder
```
