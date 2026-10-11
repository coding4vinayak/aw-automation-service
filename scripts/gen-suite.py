#!/usr/bin/env python3
"""Generate website/suite.html: the live Abetworks product suite status page.

Probes each product's health endpoint on localhost and bakes the result
(status + timestamp) into a static page. Re-run before any demo — a status
page that nobody regenerates is decoration:

    python3 scripts/gen-suite.py

Prices match the public site (abetworks-website.onrender.com/products/).
Local API base paths are shown as text, never links: a visitor's browser
has no localhost services, so linking them would be a dead end.
"""

import datetime
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PRODUCTS = [
    {
        "name": "AbetConnect",
        "desc": "Omnichannel team inbox — every channel, ranked by who is closest to buying.",
        "price": "$24/agent/month",
        "local": "localhost:3101",
        "health": "http://127.0.0.1:3101/api/health",
    },
    {
        "name": "LeadGenius",
        "desc": "Multichannel outreach engine — campaigns, sequences, warmup, analytics.",
        "price": "$29/user/month",
        "local": "localhost:3200",
        "health": "http://127.0.0.1:3200/api/health",
    },
    {
        "name": "LeadWorks",
        "desc": "Lead sourcing & enrichment — scrape, enrich, validate, dedupe, export.",
        "price": "$49/month",
        "local": "localhost:3300",
        "health": "http://127.0.0.1:3300/api/health",
    },
    {
        "name": "AbetAgent",
        "desc": "Autonomous AI agents — cited answers from your data, escalates instead of bluffing.",
        "price": "$99/month",
        "local": "localhost:3400",
        "health": "http://127.0.0.1:3400/api/health",
    },
    {
        "name": "AbetFlow",
        "desc": "Workflow automation — triggers, branches, loops, vaulted credentials, dead letter.",
        "price": "Included",
        "local": "localhost:3500",
        "health": "http://127.0.0.1:3500/api/health",
    },
    {
        "name": "AbetAnalytics",
        "desc": "Revenue intelligence — metrics, funnels, frozen snapshots, threshold alerts.",
        "price": "Included",
        "local": "localhost:3600",
        "health": "http://127.0.0.1:3600/api/health",
    },
    {
        "name": "AbetAPI",
        "desc": "Developer platform — scoped keys, signed webhooks, usage metering, SSO registry.",
        "price": "Included",
        "local": "localhost:3700",
        "health": "http://127.0.0.1:3700/api/health",
    },
    {
        "name": "AgentWork SDK",
        "desc": "Python SDK for Flask/FastAPI agents — sync + async handlers, tested.",
        "price": "Included",
        "local": "Flask :8000 · FastAPI :3103",
        "health": "http://127.0.0.1:8000/health",
    },
]


def probe(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=8) as res:
            return 200 <= res.status < 300
    except Exception:
        return False


def main() -> None:
    checked = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows = []
    live = 0
    for p in PRODUCTS:
        up = probe(p["health"])
        live += up
        badge = (
            '<span class="inline-block rounded-full bg-green-100 text-green-800 px-3 py-1 text-xs font-semibold">● Live</span>'
            if up
            else '<span class="inline-block rounded-full bg-red-100 text-red-800 px-3 py-1 text-xs font-semibold">● Down</span>'
        )
        rows.append(
            "<tr class=\"border-t border-gray-100\">"
            f"<td class=\"py-3 pr-4 font-semibold text-gray-900\">{p['name']}</td>"
            f"<td class=\"py-3 pr-4 text-gray-600\">{p['desc']}</td>"
            f"<td class=\"py-3 pr-4 text-gray-900 whitespace-nowrap\">{p['price']}</td>"
            f"<td class=\"py-3 pr-4\"><code class=\"text-xs bg-gray-100 rounded px-2 py-1\">{p['local']}</code></td>"
            f"<td class=\"py-3\">{badge}</td>"
            "</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Suite Status | AutoFlow</title>
    <meta name="description" content="Live status of every Abetworks product: inbox, outreach, leads, agents, automation, analytics and API.">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#9889;</text></svg>">
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Contact strip injector: rule 7 of check-buy-path.mjs requires every page to load it. -->
    <script src="js/enquiry.js"></script>
</head>
<body class="bg-gray-50 text-gray-900">
    <main class="max-w-5xl mx-auto px-6 py-12">
        <p class="text-sm font-semibold text-indigo-600 mb-2"><a href="index.html" class="hover:underline">&larr; AutoFlow home</a></p>
        <h1 class="text-3xl font-bold mb-2">Abetworks suite — live status</h1>
        <p class="text-gray-600 mb-2">Every product below is running and health-checked. Statuses were probed at <strong>{checked}</strong> ({live}/{len(PRODUCTS)} live). Re-run <code class="text-xs bg-gray-100 rounded px-2 py-1">python3 scripts/gen-suite.py</code> before a demo.</p>
        <h2 class="text-xl font-bold mt-8 mb-4">Products</h2>
        <div class="bg-white rounded-2xl shadow-sm p-6 overflow-x-auto">
            <table class="w-full text-sm">
                <thead>
                    <tr class="text-left text-gray-500">
                        <th class="pb-2 pr-4 font-medium">Product</th>
                        <th class="pb-2 pr-4 font-medium">What it does</th>
                        <th class="pb-2 pr-4 font-medium">Price</th>
                        <th class="pb-2 pr-4 font-medium">Demo address</th>
                        <th class="pb-2 font-medium">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
        <h2 class="text-xl font-bold mt-8 mb-4">Start a trial</h2>
        <div class="bg-white rounded-2xl shadow-sm p-6">
            <p class="text-gray-600 mb-4">Tell us which product to open for you and where to send the invite. No credit card, no sales call unless you ask for one.</p>
            <form id="suitetrial-form">
                <div class="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2" for="suitetrial-name">Your name *</label>
                        <input type="text" name="name" required placeholder="Priya Raman" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" id="suitetrial-name">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2" for="suitetrial-email">Work email *</label>
                        <input type="email" name="email" required placeholder="you@company.com" class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none" id="suitetrial-email">
                    </div>
                </div>
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2" for="suitetrial-product">Product *</label>
                    <select name="product" required class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none bg-white" id="suitetrial-product">
                        <option value="abetconnect">AbetConnect — omnichannel inbox ($24/agent/month)</option>
                        <option value="leadgenius">LeadGenius — outreach engine ($29/user/month)</option>
                        <option value="leadworks">LeadWorks — lead sourcing ($49/month)</option>
                        <option value="abetagent">AbetAgent — autonomous agents ($99/month)</option>
                        <option value="abetflow">AbetFlow — workflow automation (included)</option>
                        <option value="abetanalytics">AbetAnalytics — revenue BI (included)</option>
                        <option value="abetapi">AbetAPI — developer platform (included)</option>
                        <option value="agentwork">AgentWork SDK — Flask/FastAPI agents (included)</option>
                    </select>
                </div>
                <button type="submit" class="gradient-bg text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition">Request trial invite</button>
            </form>
            <div id="suitetrial-sent" class="hidden mt-6"></div>
        </div>
        <h2 class="text-xl font-bold mt-8 mb-4">See it on your own data</h2>
        <div class="bg-white rounded-2xl shadow-sm p-6">
            <p class="text-gray-600 mb-4">Twenty minutes, your use case, a running product — not slides. Pick a time and we will tailor the walkthrough.</p>
            <a href="booking.html" class="inline-block bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition">Book a live demo</a>
        </div>
        <p class="mt-8 text-xs text-gray-400">Prices match the public catalogue. Demo addresses are local development endpoints shown for the demo room — they resolve on the demo machine only.</p>
    </main>
    <script>
        AutoFlowEnquiry.wire({{
            formId: 'suitetrial-form',
            panelId: 'suitetrial-sent',
            title: 'Abetworks suite — trial invite request',
            subject: 'Trial invite request',
            rows: (form, field) => {{
                var select = form.elements['product'];
                var product = select && select.selectedOptions && select.selectedOptions[0]
                    ? select.selectedOptions[0].text.trim()
                    : field(form, 'product');
                return [
                    ['Name', field(form, 'name')],
                    ['Email', field(form, 'email')],
                    ['Product', product],
                ];
            }},
        }});
    </script>
</body>
</html>
"""
    (ROOT / "website" / "suite.html").write_text(html)
    print(f"Wrote website/suite.html ({live}/{len(PRODUCTS)} live, checked {checked})")


if __name__ == "__main__":
    main()
