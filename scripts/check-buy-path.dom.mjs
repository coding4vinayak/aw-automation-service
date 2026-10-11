// DOM probe for the AutoFlow buy path — the part scripts/check-buy-path.mjs can only
// assert statically: that filling a form and pressing submit actually produces a
// panel with a correct send link.
//
// Needs jsdom. This repository has no package.json (it is a static site), so run it
// against any checkout that has one installed. On this machine NuCRM keeps one:
//
//   NODE_PATH=/srv/work/longhorizon-target/node_modules \
//     node scripts/check-buy-path.dom.mjs
//
// jsdom cannot navigate, so a mailto:/wa.me: open surfaces as
// "Not implemented: navigation" on the virtual console. That is useful rather than a
// nuisance here: it is how we can see the page really did try to open something.

import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";

// jsdom is resolved through require() rather than import because this repository is
// a static site with no node_modules of its own, and NODE_PATH — the usual way to
// point at a neighbouring checkout's — is honoured by CommonJS resolution and
// silently ignored by ESM resolution.
const require = createRequire(import.meta.url);
let JSDOM, VirtualConsole;
try {
  ({ JSDOM, VirtualConsole } = require("jsdom"));
} catch {
  const fallback =
    process.env.AUTOFLOW_JSDOM || "/srv/work/longhorizon-target/node_modules/jsdom";
  try {
    ({ JSDOM, VirtualConsole } = require(fallback));
  } catch {
    console.error(
      `\nThis probe needs jsdom. Install it, or point AUTOFLOW_JSDOM at a copy,\n` +
        `e.g. AUTOFLOW_JSDOM=/path/to/node_modules/jsdom node ${process.argv[1]}\n`,
    );
    process.exit(2);
  }
}

const SITE = join(dirname(fileURLToPath(import.meta.url)), "..", "website");

const passes = [];
const failures = [];
function check(label, ok, detail = "") {
  (ok ? passes : failures).push(ok ? label : `${label}${detail ? ` — ${detail}` : ""}`);
}

async function open(page, query = "") {
  const consoleEvents = [];
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", (error) => consoleEvents.push(String(error.message || error)));

  const file = join(SITE, page);
  // The URL has to stay on file:// because jsdom resolves the pages' relative
  // <script src="js/enquiry.js"> against it — point it at http://localhost and the
  // router silently never loads, which is exactly the class of bug this probe is
  // meant to catch. The query string still rides along, so ?service= works.
  const url = pathToFileURL(file).href + query;

  const dom = await JSDOM.fromFile(file, {
    runScripts: "dangerously",
    resources: "usable",
    url,
    virtualConsole,
  });

  await new Promise((resolve) => {
    if (dom.window.document.readyState === "complete") return resolve();
    dom.window.addEventListener("load", resolve);
  });
  // The pages load enquiry.js as an external resource, so give the fetch a beat to
  // land before asserting anything about what the inline scripts wired up.
  await new Promise((resolve) => setTimeout(resolve, 250));

  return { dom, doc: dom.window.document, consoleEvents };
}

function fill(doc, form, values) {
  for (const [name, value] of Object.entries(values)) {
    const control = form.elements[name];
    if (!control) throw new Error(`${form.id}: no field named "${name}"`);
    control.value = value;
  }
}

function submit(form) {
  const event = new form.ownerDocument.defaultView.Event("submit", { bubbles: true, cancelable: true });
  form.dispatchEvent(event);
  return event;
}

const firstHref = (panel, scheme) =>
  Array.from(panel.querySelectorAll('a[href^="' + scheme + '"]')).map((a) => a.href)[0];

const bodyOf = (mailto) => (mailto ? decodeURIComponent(mailto.split("body=")[1] || "") : "");

// ── booking.html, arriving from a service page ────────────────────────────────
{
  const { doc, consoleEvents } = await open("booking.html", "?service=lead-capture&price=147");
  const form = doc.getElementById("booking-form");
  const button = form.querySelector('button[type="submit"]');
  const panel = doc.getElementById("booking-sent");

  check("booking: submit starts disabled until a slot exists", button.disabled === true);
  check(
    "booking: arriving with ?service= preselects the topic",
    form.elements.topic.value === "lead-capture",
    `topic is "${form.elements.topic.value}"`,
  );
  const note = doc.getElementById("package-note").textContent;
  check("booking: the package and its price are named back to the visitor", /Lead capture automation/.test(note) && /\$147/.test(note), note);

  doc.querySelector(".date-btn")?.click();
  doc.querySelector(".time-slot")?.click();
  check("booking: choosing a slot enables submit", button.disabled === false);

  fill(doc, form, {
    first_name: "Sneha",
    last_name: "Rao",
    email: "sneha@brightbay.test",
    phone: "+91 98123 45678",
    business: "Bright Bay Café",
  });
  const event = submit(form);

  check("booking: the browser default that used to lose everything is prevented", event.defaultPrevented);
  check("booking: the form is replaced rather than left looking untouched", form.classList.contains("hidden"));
  check("booking: an enquiry panel is drawn", panel.getAttribute("data-enquiry-ready") === "true");

  const mailto = firstHref(panel, "mailto:");
  check("booking: panel offers an email link", Boolean(mailto));
  check(
    "booking: the email goes to the configured inbox",
    decodeURIComponent((mailto || "").split("?")[0]) === "mailto:hello@abetworks.in",
    mailto,
  );
  const body = bodyOf(mailto);
  check("booking: enquiry names the customer and the business", /Name: Sneha Rao/.test(body) && /Business: Bright Bay Café/.test(body), body);
  check("booking: enquiry carries the package with its price", /Lead capture automation \(\$147\)/.test(body), body);
  check("booking: enquiry carries the chosen slot", /Preferred slot: \d{4}-\d{2}-\d{2}, \d/.test(body), body);
  check("booking: the page really tried to open a mail client", consoleEvents.some((m) => /navigation/i.test(m)), consoleEvents.join(" | "));
  check("booking: the panel admits nothing has been sent yet", /Nothing has been sent yet/.test(panel.textContent));
  check("booking: the panel has a copy fallback", /Copy enquiry text/.test(panel.textContent));
}

// ── calculator.html: the package the visitor built must survive the click ──────
// The static check is blind to this link by construction. In the file the href is a
// bare "booking.html" and the query string only exists after updatePricing() runs,
// which is how a page that quoted a discounted total on its own button then carried
// none of it slipped past every static assertion.
{
  const { doc } = await open("calculator.html");
  const link = doc.getElementById("book-link");
  const cards = Array.from(doc.querySelectorAll(".service-card"));
  const pick = (slug) => {
    const card = cards.find((c) => c.dataset.service === slug);
    if (!card) throw new Error(`no card with data-service="${slug}"`);
    card.click();
  };
  const sent = () => new URL(link.href).searchParams;

  check("calculator: the offer is inert until something is picked", link.classList.contains("pointer-events-none"));
  check("calculator: an inert offer carries no quote", link.getAttribute("href") === "booking.html", link.getAttribute("href"));

  pick("email-sequence");
  check("calculator: one pick preselects its own topic", sent().get("service") === "email", link.href);
  check("calculator: one pick carries its price", sent().get("price") === "197", link.href);
  check("calculator: one pick needs no itemisation", !sent().has("pkg"), sent().get("pkg"));

  pick("lead-capture");
  const bundle = sent();
  // 197 + 147 = 344, two services = 10% off, so 344 - 34 = 310.
  check("calculator: a bundle carries both items by name and price", /Lead Capture \$147/.test(bundle.get("pkg") || "") && /Email Follow-up \$197/.test(bundle.get("pkg") || ""), bundle.get("pkg"));
  check("calculator: a bundle carries the discounted total, not the subtotal", bundle.get("price") === "310", bundle.get("price"));
  check("calculator: a bundle carries the saving", bundle.get("saved") === "34", bundle.get("saved"));
  check("calculator: a bundle does not pretend to be one service", bundle.get("service") === "other", bundle.get("service"));
  check("calculator: the button and the link quote the same number", /310/.test(link.textContent) && /price=310/.test(link.href), `${link.textContent} | ${link.href}`);

  pick("lead-capture");
  pick("email-sequence");
  check("calculator: emptying the basket retracts the quote", link.getAttribute("href") === "booking.html", link.getAttribute("href"));
  check("calculator: an empty basket is inert again", link.classList.contains("pointer-events-none"));

  // The route has to land, not just launch: booking.html must read the package back
  // and put it in the message the business receives.
  pick("email-sequence");
  pick("lead-capture");
  const { doc: bdoc } = await open("booking.html", "?" + bundle.toString());
  const bnote = bdoc.getElementById("package-note");
  check("booking: a calculator package is shown, not swallowed by the topic select", !bnote.classList.contains("hidden") && /Lead Capture \$147/.test(bnote.textContent) && /\$310/.test(bnote.textContent), bnote.textContent);

  const bform = bdoc.getElementById("booking-form");
  check("booking: a package leaves the topic at Other rather than guessing", bform.elements.topic.value === "other", bform.elements.topic.value);
  bdoc.querySelector(".date-btn")?.click();
  bdoc.querySelector(".time-slot")?.click();
  fill(bdoc, bform, { first_name: "Nadia", email: "nadia@brightbay.test", business: "Bright Bay Café" });
  submit(bform);
  const bpanel = bdoc.getElementById("booking-sent");
  const bbody = bodyOf(firstHref(bpanel, "mailto:"));
  check("booking: the enquiry itemises the package", /Lead Capture \$147 \+ Email Follow-up \$197/.test(bbody), bbody);
  check("booking: the enquiry states the total the visitor was quoted", /= \$310 \(saved \$34\)/.test(bbody), bbody);
  check("booking: a bundle does not reach the business as just 'Other'", !/Wants to discuss: Other/.test(bbody), bbody);
}


// ── the router object the pages actually received ─────────────────────────────
{
  const { dom } = await open("booking.html");
  const E = dom.window.AutoFlowEnquiry;
  check("enquiry.js reached the page and exposes wire()", Boolean(E) && typeof E.wire === "function");
  if (E) {
    const built = E.build({
      routing: { email: E.ROUTING.email, whatsapp: "919812345678", phone: "" },
      title: "t",
      rows: [["Name", "A"]],
    });
    check("a configured number puts WhatsApp ahead of email", built.channels[0].kind === "whatsapp");
    check(
      "WhatsApp link is a wa.me deep link carrying an encoded multi-line body",
      built.channels[0].href.startsWith("https://wa.me/919812345678?text=") &&
        /Name%3A%20A/.test(built.channels[0].href),
      built.channels[0].href,
    );
    check("an absent field leaves no dangling label behind", !/Preferred slot/.test(built.text));
  }
}

// ── index.html contact form, which reaches the router via js/main.js ──────────
{
  const { doc } = await open("index.html");
  const form = doc.getElementById("contact-form");
  check("index: contact form exists", Boolean(form));
  fill(doc, form, {
    name: "Imran Sheikh",
    email: "imran@qissa.test",
    phone: "",
    business: "Qissa Tailors",
    // The value is "email-sequence" here while booking.html's topic select uses
    // "email" for the same service — two forms, two vocabularies. The static check
    // asserts every ?service= link resolves to a real option; this is the shape
    // that drift takes, so the probe uses the page's own value.
    service: "email-sequence",
    message: "We chase payments on WhatsApp every single day.",
  });
  const event = submit(form);
  const panel = doc.getElementById("contact-sent");
  check("index: submission is intercepted", event.defaultPrevented);
  check("index: panel replaces the old green 'thanks' box", panel.getAttribute("data-enquiry-ready") === "true");
  const body = bodyOf(firstHref(panel, "mailto:"));
  check("index: the service travels as the human label, not the option value", /Service asked about: Email Follow-up Sequences/.test(body), body);
  check("index: the chosen value is not leaked as its raw slug", !/email-sequence/.test(body), body);
  check("index: the customer's own words survive the trip", /We chase payments on WhatsApp/.test(body), body);
  check("index: the empty optional phone is not sent as a blank label", !/^Phone:$/m.test(body), body);
}

// ── audit.html: the quiz result is the lead qualifier ─────────────────────────
{
  const { doc } = await open("audit.html");
  const form = doc.getElementById("audit-form");
  fill(doc, form, { first_name: "Priya", last_name: "Nair", email: "priya@kadambar.test", business: "Kadambar Salons" });
  submit(form);
  const panel = doc.getElementById("audit-sent");
  check("audit: the quiz form routes an enquiry now", panel.getAttribute("data-enquiry-ready") === "true");
  const body = bodyOf(firstHref(panel, "mailto:"));
  check("audit: the score the visitor worked for is attached to the lead", /automation score/i.test(body), body);
  // The panel's honest line contains the words "Nothing has been sent yet", so
  // matching on "has been sent" alone flags correct behaviour. Match the claim
  // shape instead: something completed, to the visitor's address.
  check("audit: the panel states plainly that nothing has been sent", /Nothing has been sent yet/.test(panel.textContent));
  check("audit: no claim that a report was delivered remains", !/report has been sent|has been sent to your email/i.test(panel.textContent));
}

// ── the one-line configuration the owner will make ────────────────────────────
// ROUTING is read at submit time, not wire time, so flipping WhatsApp on here
// exercises the same path a real deployment takes: the deep link becomes the
// channel the browser opens, and the panel offers both routes.
{
  const { dom, doc } = await open("booking.html", "?service=invoice&price=197");
  const E = dom.window.AutoFlowEnquiry;
  E.ROUTING.whatsapp = "919812345678";

  const form = doc.getElementById("booking-form");
  doc.querySelector(".date-btn")?.click();
  doc.querySelector(".time-slot")?.click();
  fill(doc, form, { first_name: "Asha", last_name: "V", email: "asha@mill.test", business: "The Mill" });
  submit(form);

  const panel = doc.getElementById("booking-sent");
  const links = Array.from(panel.querySelectorAll("a[href]")).map((a) => a.getAttribute("href"));
  check("with a number configured, WhatsApp is offered", links.some((h) => h.startsWith("https://wa.me/919812345678")));
  check("email stays available for the desktop visitor with no WhatsApp", links.some((h) => h.startsWith("mailto:")));
  check("WhatsApp comes first in the panel", links[0].startsWith("https://wa.me/"));
  const wa = links.find((h) => h.startsWith("https://wa.me/"));
  const waText = decodeURIComponent(wa.split("text=")[1] || "");
  check("the WhatsApp body carries the package and its price", /Invoice & Reminders|Invoice/.test(waText) && /\$197/.test(waText), waText);
  check("the WhatsApp body carries the chosen slot", /Preferred slot: \d{4}-\d{2}-\d{2}/.test(waText), waText);

  E.ROUTING.whatsapp = "";
}

// ── the injected contact strip ────────────────────────────────────────────────
{
  const { doc } = await open("services/lead-capture.html");
  const strip = doc.getElementById("autoflow-contact-strip");
  check("a service page gets the contact strip", Boolean(strip), "no #autoflow-contact-strip after load");
  if (strip) {
    const hrefs = Array.from(strip.querySelectorAll("a[href]")).map((a) => a.getAttribute("href"));
    check(
      "the strip's booking link resolves from one directory down",
      hrefs.some((h) => h.endsWith("/booking.html") && h.includes("website/")),
      hrefs.join(" , "),
    );
    check("the strip prints a real address, not a placeholder", hrefs.some((h) => h.startsWith("mailto:hello@abetworks.in")));
    check("the strip does not invent a WhatsApp button when no number is set", !hrefs.some((h) => h.includes("wa.me")));
  }

  const booking = (await open("booking.html")).doc;
  check(
    "a page that already has a working form is not given a competing strip",
    booking.getElementById("autoflow-contact-strip") === null,
  );
}

// ── suite.html: the trial form is the money path — it must produce a lead ──
{
  const { doc } = await open("suite.html");
  const form = doc.getElementById("suitetrial-form");
  check("suite: trial form exists", Boolean(form));
  fill(doc, form, { name: "Rohan Mehta", email: "rohan@loomcraft.test", product: "leadgenius" });
  const event = submit(form);
  const panel = doc.getElementById("suitetrial-sent");
  check("suite: submission is intercepted", event.defaultPrevented);
  check("suite: panel is marked ready", panel.getAttribute("data-enquiry-ready") === "true");
  const body = bodyOf(firstHref(panel, "mailto:"));
  check("suite: the visitor's name travels", /Rohan Mehta/.test(body), body);
  check("suite: the product travels as its human label, not the slug", /LeadGenius/.test(body) && !/Product: leadgenius/.test(body), body);
  check("suite: the trial intent is in the subject line", /Trial invite request/.test(decodeURIComponent(firstHref(panel, "mailto:") || "")));
}

// ── summary ───────────────────────────────────────────────────────────────────
console.log(`\nAutoFlow DOM probe — ${passes.length} passed, ${failures.length} failed`);
if (failures.length) {
  console.log("\nFAILURES:");
  for (const f of failures) console.log("  ✗ " + f);
  process.exit(1);
}
console.log("✓ all three forms produce a sendable, correctly-encoded enquiry\n");

