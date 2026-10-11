// Buy-path check for the AutoFlow site.
//
// This exists because the site shipped for months with three forms that collected
// a customer's details, threw them into the browser console, and then told the
// visitor the enquiry had been sent — including a "Booking Confirmed!" modal for
// appointments nobody could ever see. Nothing about that state is detectable by
// opening the site and clicking around: it looks exactly like working software.
//
// So this asserts the properties that actually matter, in one pass:
//   1. no placeholder transport is configured or lurking in a comment
//   2. every page that can take a lead routes it through js/enquiry.js
//   3. every page quoting a price can reach a form
//   4. no relative link in the site resolves to a file that does not exist
//   5. the enquiry composer encodes WhatsApp and mailto links correctly
//
// Run: node scripts/check-buy-path.mjs   (exit 1 on any failure)

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, relative, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(HERE, "..");
const SITE = join(ROOT, "website");

const failures = [];
const passes = [];

function check(label, ok, detail = "") {
  (ok ? passes : failures).push(ok ? label : `${label}${detail ? ` — ${detail}` : ""}`);
}

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

const files = walk(SITE);
const text = (f) => readFileSync(f, "utf8");
const pages = files.filter((f) => f.endsWith(".html"));
const rel = (f) => relative(SITE, f);

// ── 1. no placeholder transports ──────────────────────────────────────────────
// Matching on the whole site rather than just live code is deliberate: the
// commented-out Formspree block is what made the real bug easy to walk past.
const PLACEHOLDERS = [
  "YOUR_FORM_ID",
  "YOUR_PUBLIC_KEY",
  "YOUR_SERVICE_ID",
  "your-email@",
  "formspree.io/f/",
  "example.com",
];

// js/enquiry.js is allowed to name these things because its whole job is refusing
// them: it lists the dummy number and the placeholder domains in order to reject
// them as routing targets. Asserting that refusal is rule 5 below.
const SELF = fileURLToPath(import.meta.url);
const GUARD_FILES = new Set([join(SITE, "js", "enquiry.js"), SELF]);

for (const page of [...pages, ...files.filter((f) => /\.(js|json)$/.test(f))]) {
  if (GUARD_FILES.has(page)) continue;
  const body = text(page);
  for (const needle of PLACEHOLDERS) {
    check(
      `${rel(page)} has no "${needle}"`,
      !body.includes(needle),
      `found "${needle}"`,
    );
  }
}

// The dummy mobile number that seeds every template in this kit. It is a real,
// working-shaped Indian number, so an enquiry sent there reaches a stranger.
// Only code and pages are scanned: website/README.md names the dummy on purpose, to
// tell whoever configures ROUTING not to use it.
const SCANNABLE = files.filter((f) => /\.(html|js|json|css)$/.test(f));
for (const page of SCANNABLE) {
  if (GUARD_FILES.has(page)) continue;
  const body = text(page);
  check(
    `${rel(page)} does not route enquiries to the template dummy number`,
    !/919876543210|98765\s?43210/.test(body) || !/wa\.me|whatsapp|tel:|ROUTING/.test(body),
    "dummy +91 98765 43210 appears next to a contact route",
  );
}

// ── 2. every page that can take a lead routes it through enquiry.js ───────────
const mainJs = text(join(SITE, "js", "main.js"));

for (const page of pages) {
  const body = text(page);
  const takesLeads = /<form[\s>]/i.test(body) && /type=["']submit["']/.test(body);
  if (!takesLeads) continue;

  const name = rel(page);
  const loadsMain = /js\/main\.js/.test(body);
  check(`${name} loads js/enquiry.js`, /js\/enquiry\.js/.test(body), "form present but no enquiry router");
  const code = body + (loadsMain ? mainJs : "");
  check(`${name} routes its form through enquiry.js`, /AutoFlowEnquiry\.wire/.test(code), "no wire() call reachable");

  // A wire() pointing at a panel id that is not on the page fails silently —
  // reveal() returns early and the visitor is left with a form that did nothing.
  for (const match of code.matchAll(/panelId:\s*["']([^"']+)["']/g)) {
    check(`${name} has the enquiry panel #${match[1]}`, body.includes(`id="${match[1]}"`));
  }

  // The signature of the original bug: collected data whose only destination is
  // the developer console.
  check(
    `${name} does not swallow a submission into the console`,
    !/console\.log\(\s*["'](?:Form submitted|Booking|Audit submitted)/.test(code),
  );
  check(
    `${name} does not claim a send it cannot perform`,
    !/alert\(\s*["'`][^"']*(?:has been sent|would send|Form submitted|Booking Confirmed)/i.test(code),
  );
}

// ── 3. a page that quotes a price must be able to reach a sales conversation ──
// terms.html and privacy.html mention money ($50/hour over-runs, $297/month
// support) without offering anything, and are not supposed to carry a "buy" link.
const NOT_AN_OFFER = new Set(["terms.html", "privacy.html"]);
for (const page of pages) {
  const body = text(page);
  if (NOT_AN_OFFER.has(rel(page))) continue;
  const priced = /\$\s?\d{2,4}(?:\s?\/\s?mo)?/.test(body);
  if (!priced) continue;
  const name = rel(page);
  const reachesForm =
    /booking\.html/.test(body) || /id="contact-form"/.test(body) || /js\/main\.js/.test(body);
  check(`${name} quotes a price and offers a way to buy`, reachesForm, "price shown, no route to a form");
}

// ── 4. no link may resolve to a file that is not there ────────────────────────
// Two of the six priced service pages had CTAs pointing at services/booking.html
// and website/../index.html, so the button on a paying customer's page was a 404.
for (const page of pages) {
  const body = text(page);
  for (const match of body.matchAll(/href="([^"#][^"]*)"/g)) {
    const url = match[1];
    if (/^(https?:|mailto:|tel:|\/\/|data:)/.test(url)) continue;
    const target = url.split(/[?#]/)[0];
    if (!target.endsWith(".html")) continue;
    check(
      `${rel(page)} link resolves: ${url}`,
      existsSync(resolve(page, "..", target)),
      "no such file",
    );
  }
}

// ── 5. the composer itself ────────────────────────────────────────────────────
const { default: enquiry } = await import(join(SITE, "js", "enquiry.js"));
const R = enquiry.ROUTING;

check("routing has a real inbox", enquiry.normaliseEmailAddress(R.email) !== "", `email is "${R.email}"`);
check(
  "routing has no half-typed WhatsApp number",
  R.whatsapp === "" || enquiry.normaliseWhatsAppNumber(R.whatsapp) !== "",
  `whatsapp is "${R.whatsapp}" — blank, or a full number with country code`,
);

check("the template dummy number can never become a WhatsApp route", enquiry.normaliseWhatsAppNumber("+91 98765 43210") === "");
check("a bare Indian mobile gets its country code", enquiry.normaliseWhatsAppNumber("9812345678") === "919812345678");
check("a too-short number is refused rather than guessed", enquiry.normaliseWhatsAppNumber("1234") === "");
check("a non-inbox address is refused", enquiry.normaliseEmailAddress("support@example.com") === "");

const composed = enquiry.build({
  title: "AutoFlow test",
  subject: "AutoFlow test",
  rows: [["Name", "Sneha Café"], ["Skipped", ""], ["Phone", "+91 98123 45678"]],
});
check("an email channel exists", composed.primary?.kind === "email");
check("blank optional fields are left out of the message", !composed.text.includes("Skipped"));
check("the message carries the customer's name", composed.text.includes("Name: Sneha Café"));
check("mailto bodies use CRLF and full percent-encoding", enquiry.mailtoHref("a@b.co", "S", "l1\nl2").endsWith("body=l1%0D%0Al2"));
check("whatsapp text is percent-encoded, not raw", enquiry.whatsappHref("919812345678", "héllo").includes("text=h%C3%A9llo"));
check("wa.me links carry the number in the path", enquiry.whatsappHref("919812345678", "x").startsWith("https://wa.me/919812345678?text="));

const withWa = enquiry.build({
  routing: { email: R.email, whatsapp: "919812345678", phone: "+91 98765 43210" },
  title: "AutoFlow test",
  rows: [["A", "b"]],
});
check("a configured WhatsApp number becomes the primary channel", withWa.primary?.kind === "whatsapp");
check("the dummy number never becomes a click-to-call link", !withWa.channels.some((c) => c.kind === "call"));

// ── 6. every ?service= deep link must name a real option ──────────────────────
// booking.html preselects its topic from the query string and, by design, ignores a
// value it does not recognise. So a typo or a rename leaves the customer looking at
// "General consultation" having clicked "Invoice automation" — silently, on the way
// to sending a message that quotes the wrong thing.
const bookingPage = text(join(SITE, "booking.html"));
const topicValues = new Set(
  [...bookingPage.matchAll(/<option value="([^"]*)"/g)].map((m) => m[1]),
);
check("booking.html exposes its topic options", topicValues.size > 1, [...topicValues].join(","));

for (const page of pages) {
  for (const match of text(page).matchAll(/booking\.html\?service=([\w-]+)/g)) {
    check(
      `${rel(page)} → ?service=${match[1]} is a real booking topic`,
      topicValues.has(match[1]),
      `booking.html has no option with value "${match[1]}"`,
    );
  }
}
// The calculator builds its link in JavaScript, so the loop above cannot see it — in
// the file the href is a bare "booking.html" until updatePricing() fills it in. That
// is a real blind spot, so the mapping the page relies on is checked as data instead:
// every card on the page must have a topic, every topic named must exist in
// booking.html, and a mapping left behind for a card someone deleted fails too.
// Adding a ninth service without extending the map now fails here instead of
// preselecting the wrong service and quietly quoting the wrong thing.
const calculatorPage = text(join(SITE, "calculator.html"));
const cardSlugs = [...new Set([...calculatorPage.matchAll(/data-service="([\w-]+)"/g)].map((m) => m[1]))];
const mapBlock = calculatorPage.match(/const TOPIC_BY_SERVICE = \{([\s\S]*?)\};/);
check("the calculator declares a topic map for its cards", Boolean(mapBlock));
if (mapBlock) {
  const topicMap = new Map([...mapBlock[1].matchAll(/'([\w-]+)':\s*'([\w-]+)'/g)].map((m) => [m[1], m[2]]));
  check("the calculator offers packages worth mapping", cardSlugs.length > 1, cardSlugs.join(","));
  for (const slug of cardSlugs) {
    const mapped = topicMap.get(slug);
    check(
      `calculator card "${slug}" maps to a booking topic`,
      Boolean(mapped),
      "TOPIC_BY_SERVICE has no entry, so the link preselects nothing",
    );
    if (mapped) {
      check(`calculator "${slug}" → "${mapped}" exists in booking.html`, topicValues.has(mapped));
    }
  }
  for (const slug of topicMap.keys()) {
    check(
      `TOPIC_BY_SERVICE entry "${slug}" is still offered on the page`,
      cardSlugs.includes(slug),
      "stale mapping for a card that no longer exists",
    );
  }
}



// ── 7. every page must load the router, from a path that resolves ─────────────
// The contact strip is injected by js/enquiry.js. A page that does not load it has
// no contact route at all, which is what 16 of these pages looked like before.
for (const page of pages) {
  const body = text(page);
  const match = body.match(/<script src="([^"]*js\/enquiry\.js)"/);
  check(`${rel(page)} loads the enquiry router`, Boolean(match), "no <script src=...js/enquiry.js>");
  if (match) {
    check(
      `${rel(page)} router path resolves`,
      existsSync(resolve(page, "..", match[1])),
      match[1],
    );
  }
}

// ── summary ───────────────────────────────────────────────────────────────────
console.log(`\nAutoFlow buy-path check — ${passes.length} passed, ${failures.length} failed`);
if (failures.length) {
  console.log("\nFAILURES:");
  for (const f of failures) console.log("  ✗ " + f);
  process.exit(1);
}
console.log(`pages scanned: ${pages.length}   assets: ${files.length}`);
console.log("route today:", R.whatsapp ? "WhatsApp + email" : "email only", "→", R.email || "(none)");
console.log("✓ every form on this site has somewhere for an enquiry to go\n");


