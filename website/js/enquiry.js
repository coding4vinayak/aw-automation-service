// AutoFlow — the enquiry router.
//
// Why this file exists
// --------------------
// Until now every form on this site collected a prospect's name, email, phone and
// problem, printed it to the browser console, and then told the visitor it had
// worked. `booking.html` went furthest: it showed a modal reading "Booking
// Confirmed! Check your email for a calendar invite" for a meeting that was never
// sent, never stored and never going to happen. A prospect who believes they are
// booked does not try again somewhere else — they wait for an invite that is not
// coming, which is worse than a form that visibly fails.
//
// There is no backend here and no account to sign up to, so the transports are the
// two the visitor already carries on their phone: WhatsApp and their mail app. Both
// are built from a message this page composes, both are opened by the browser, and
// neither needs a server, a key or a monthly fee. The composed text is always shown
// on the page with a copy button, so if a deep link is blocked or dismissed the
// enquiry is still in the visitor's hands and can be pasted anywhere.
//
// Nothing in here claims a message was delivered, because from the browser there is
// no way to know. The copy says what actually happened: it opened something.

(function (root, factory) {
  var api = factory();
  // Classic script, no build step, because this site is plain HTML on a static
  // host. The module.exports half is what lets scripts/check-buy-path.mjs assert
  // the encoding rules without a browser.
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (root) root.AutoFlowEnquiry = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  "use strict";

  // ── The only block anyone has to edit to go live ────────────────────────────
  //
  // `email` is the brand address already used across the AbetWorks pages, so
  // enquiries land somewhere that exists today.
  //
  // `whatsapp` and `phone` are deliberately EMPTY and must stay that way until a
  // real business number goes in. The rest of this kit is seeded with
  // +91 98765 43210, which is the dummy number Indian tutorials use — it is not
  // yours, it formats as a valid number, and sending a customer's sales enquiry
  // to a stranger's WhatsApp is a worse failure than not offering the channel at
  // all. So a blank or malformed value turns WhatsApp off completely rather than
  // guessing, which is why `normaliseWhatsAppNumber` rejects anything that does
  // not look like a real subscriber number.
  var ROUTING = {
    email: "hello@abetworks.in",
    whatsapp: "", // e.g. "919812345678" — 10-13 digits, country code, no '+'
    phone: "", // shown as a click-to-call link once it is a real number
    replyPromise: "within 1 working day",
  };

  // Numbers that appear in templates and examples all over this repository.
  // Refusing them by name is a cheap guard against the dummy shipping for real.
  var BLOCKED_NUMBERS = ["919876543210", "15551234567", "919999999999"];

  function normaliseWhatsAppNumber(raw) {
    if (!raw || typeof raw !== "string") return "";
    var digits = raw.replace(/[^\d]/g, "");
    if (!digits) return "";
    if (digits.length < 10 || digits.length > 15) return "";
    // An Indian mobile is 10 digits starting 6-9; prefix the country code rather
    // than silently sending a 10-digit number to whatever account holds it.
    if (digits.length === 10) {
      if (!/^[6-9]/.test(digits)) return "";
      digits = "91" + digits;
    }
    if (BLOCKED_NUMBERS.indexOf(digits) !== -1) return "";
    return digits;
  }

  function normaliseEmailAddress(raw) {
    if (!raw || typeof raw !== "string") return "";
    var address = raw.trim();
    // The example.com / your-email@ addresses scattered through the kit are not
    // inboxes. An enquiry posted there is gone either way.
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(address)) return "";
    if (/(example\.(com|org)|yourdomain|your-email|test\.)/.test(address)) return "";
    return address;
  }

  function present(value) {
    if (value === null || value === undefined) return "";
    return String(value).trim();
  }

  // The body is written so it reads correctly in a WhatsApp thread: one field per
  // line, label before colon, no markdown that WhatsApp will not draw.
  function composeMessage(options) {
    var lines = [options.title, ""];
    var rows = options.rows || [];
    for (var i = 0; i < rows.length; i++) {
      var label = present(rows[i][0]);
      var value = present(rows[i][1]);
      if (!value) continue; // A blank optional field is noise in a thread.
      lines.push(label + ": " + value);
    }
    lines.push("");
    lines.push("Reply " + (options.replyPromise || "shortly") + ".");
    if (options.source) lines.push("(" + options.source + ")");
    return lines.join("\n");
  }

  function mailtoHref(address, subject, body) {
    // CRLF is the line break mail clients honour inside a mailto body, and
    // everything has to pass through encodeURIComponent or a name like
    // "Sneha Café" truncates the link at the first byte that is not URL safe.
    var normalised = body.replace(/\r?\n/g, "\r\n");
    return (
      "mailto:" +
      encodeURIComponent(address) +
      "?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(normalised)
    );
  }

  function whatsappHref(number, text) {
    return "https://wa.me/" + number + "?text=" + encodeURIComponent(text);
  }

  // Channels in the order a visitor should be offered them. WhatsApp leads when
  // configured because it is installed on almost every phone in the market this
  // kit targets; mail is the fallback that works on a desktop with no WhatsApp.
  function build(options) {
    var routing = options.routing || ROUTING;
    var email = normaliseEmailAddress(routing.email);
    var whatsapp = normaliseWhatsAppNumber(routing.whatsapp);
    var callDigits = present(routing.phone).replace(/[^\d]/g, "");

    var text = composeMessage({
      title: options.title,
      rows: options.rows,
      replyPromise: routing.replyPromise,
      source: options.source,
    });

    var channels = [];
    if (whatsapp) {
      channels.push({
        kind: "whatsapp",
        label: "Send on WhatsApp",
        href: whatsappHref(whatsapp, text),
      });
    }
    if (email) {
      channels.push({
        kind: "email",
        label: "Send by email",
        href: mailtoHref(email, options.subject || options.title, text),
      });
    }
    // A call is never opened automatically — that would be the browser dialling
    // somebody. It is offered as a link, and only if the number is real.
    if (callDigits.length >= 10 && BLOCKED_NUMBERS.indexOf(callDigits) === -1) {
      channels.push({
        kind: "call",
        label: "Or call " + present(routing.phone),
        href: "tel:" + present(routing.phone).replace(/[^\d+]/g, ""),
      });
    }

    var writeChannels = channels.filter(function (channel) {
      return channel.kind === "whatsapp" || channel.kind === "email";
    });

    return {
      text: text,
      channels: channels,
      primary: writeChannels[0],
      email: email,
      whatsapp: whatsapp,
    };
  }

  function isLocalPreview() {
    var host = typeof location !== "undefined" ? location.hostname : "";
    return host === "" || host === "localhost" || host === "127.0.0.1";
  }

  // The panel is drawn here rather than pasted as markup into three pages, so the
  // honest wording exists once and cannot drift between them. Each page already
  // carries an empty container with the right id; this fills it.
  function reveal(panel, prepared, options) {
    if (!panel) return;
    panel.innerHTML = "";

    var heading = document.createElement("h3");
    heading.textContent = "One more tap and it is on its way";
    panel.appendChild(heading);

    var note = document.createElement("p");
    note.className = "text-sm opacity-90 mt-2";
    note.textContent = prepared.primary
      ? "Your own WhatsApp or email app has just been opened with everything below filled in. " +
        "Press send there and we will reply " +
        (options.replyPromise || "shortly") +
        ". Nothing has been sent yet — this page cannot send anything for you."
      : "This page has not been given a contact address to send to, so nothing has left your browser. " +
        "The text below is your enquiry — copy it and send it to whoever should be reading it.";
    panel.appendChild(note);

    var body = document.createElement("pre");
    body.className = "mt-4 text-left text-xs whitespace-pre-wrap font-mono opacity-95";
    body.textContent = prepared.text;
    panel.appendChild(body);

    var row = document.createElement("div");
    row.className = "mt-4 flex flex-wrap gap-3";

    prepared.channels.forEach(function (channel) {
      var link = document.createElement("a");
      link.href = channel.href;
      link.textContent = channel.label;
      link.className =
        "inline-block bg-white text-indigo-700 px-5 py-2 rounded-full font-semibold text-sm";
      row.appendChild(link);
    });

    var copy = document.createElement("button");
    copy.type = "button";
    copy.textContent = "Copy enquiry text";
    copy.className =
      "inline-block border border-white/70 text-white px-5 py-2 rounded-full font-semibold text-sm";
    copy.addEventListener("click", function () {
      copyToClipboard(prepared.text, copy);
    });
    row.appendChild(copy);
    panel.appendChild(row);

    // Invisible to a customer on a deployed site and loud enough that whoever is
    // running the preview cannot miss an unconfigured storefront.
    if (!prepared.channels.length && isLocalPreview()) {
      var warning = document.createElement("p");
      warning.className = "mt-3 text-xs font-semibold text-amber-200";
      warning.textContent =
        "js/enquiry.js → ROUTING has no usable email or WhatsApp number yet.";
      panel.appendChild(warning);
    }

    panel.classList.remove("hidden");
    panel.setAttribute("data-enquiry-ready", "true");
    // The form hides itself the moment this appears, so on a long page the panel
    // can land where the form used to be — well below whatever was in view.
    if (panel.scrollIntoView) {
      try {
        panel.scrollIntoView({ behavior: "smooth", block: "center" });
      } catch (unsupported) {
        /* older engines just leave it where it is */
      }
    }
  }

  function copyToClipboard(text, button) {
    function done() {
      button.textContent = "Copied ✓";
    }
    // navigator.clipboard exists only in a secure context, which rules out the
    // plain-http LAN preview, so the old path stays.
    if (
      typeof navigator !== "undefined" &&
      navigator.clipboard &&
      navigator.clipboard.writeText
    ) {
      navigator.clipboard.writeText(text).then(done, function () {
        legacyCopy(text);
        done();
      });
      return;
    }
    legacyCopy(text);
    done();
  }

  function legacyCopy(text) {
    var scratch = document.createElement("textarea");
    scratch.value = text;
    scratch.setAttribute("readonly", "");
    scratch.style.position = "fixed";
    scratch.style.top = "-1000px";
    document.body.appendChild(scratch);
    scratch.select();
    try {
      document.execCommand("copy");
    } catch (ignored) {
      /* the text is on screen either way */
    }
    document.body.removeChild(scratch);
  }

  // Reading a control through form.elements rather than a global query selector,
  // because two of these pages reuse field names inside different forms and a
  // document-wide '[name="email"]' picks whichever the DOM happens to yield first.
  function field(form, name) {
    var control = form && form.elements ? form.elements[name] : null;
    if (!control) return "";
    if (control.type === "checkbox") return control.checked ? control.value || "yes" : "";
    return present(control.value);
  }

  function wire(options) {
    var form = document.getElementById(options.formId);
    if (!form) return { wired: false, reason: "no form with id " + options.formId };
    var panel = document.getElementById(options.panelId);
    var routing = options.routing || ROUTING;
    var settings = {
      formId: options.formId,
      subject: options.subject,
      title: options.title,
      replyPromise: options.replyPromise || routing.replyPromise,
    };

    form.addEventListener("submit", function (event) {
      // The browser default for a form with no action is a GET to the page itself,
      // which is part of why these forms looked alive: the address bar changed and
      // whatever had been typed went into a query string that nothing read.
      event.preventDefault();

      var prepared = build({
        routing: routing,
        title: options.title,
        subject: options.subject,
        rows: options.rows(form, field) || [],
        source: typeof location !== "undefined" ? location.href : "",
      });

      // Drawn before anything is opened: launching a mail app can leave the page
      // unpainted, and the visitor is then staring at the form they just filled in.
      reveal(panel, prepared, settings);
      form.classList.add("hidden");

      if (prepared.primary) {
        try {
          // assign() rather than setting href, so the browser's own back button
          // returns to a page that still shows the panel.
          location.assign(prepared.primary.href);
        } catch (blocked) {
          /* a popup rule ate the deep link; the panel still holds every route */
        }
      }
      return prepared;
    });

    return { wired: true };
  }

  // ── the contact strip ───────────────────────────────────────────────────────
  // 18 of the 19 pages on this site have no footer, so a visitor who would rather
  // write than fill in a form had no address to write to. Injected here, once,
  // rather than pasted into every page, because hand-copied contact details are how
  // a site ends up with four different phone numbers.
  function siteRoot() {
    var script = document.querySelector('script[src*="enquiry.js"]');
    if (script && script.src) {
      // The script lives at <root>/js/enquiry.js, so its own URL is the one
      // reference that stays correct from services/* as well as from the root.
      return script.src.replace(/js\/enquiry\.js.*$/, "");
    }
    return typeof location !== "undefined" ? location.href.replace(/[^/]*$/, "") : "";
  }

  function mountContactStrip() {
    var body = document.body;
    if (!body) return;
    if (document.getElementById("autoflow-contact-strip")) return;

    // Pages that already carry a form, or already print an address, are left alone
    // so the strip cannot compete with a call-to-action that works.
    if (/mailto:/.test(body.innerHTML)) return;
    if (document.getElementById("contact-form") || document.getElementById("booking-form") ||
        document.getElementById("audit-form")) return;

    var routing = ROUTING;
    var email = normaliseEmailAddress(routing.email);
    var whatsapp = normaliseWhatsAppNumber(routing.whatsapp);
    if (!email && !whatsapp) return;

    var strip = document.createElement("section");
    strip.id = "autoflow-contact-strip";
    strip.className = "bg-gray-900 text-white py-8 px-4";

    var inner = document.createElement("div");
    inner.className = "max-w-4xl mx-auto flex flex-wrap items-center justify-between gap-4";

    var copy = document.createElement("div");
    var headline = document.createElement("p");
    headline.className = "font-semibold";
    headline.textContent = "Want this set up for you?";
    var sub = document.createElement("p");
    sub.className = "text-gray-400 text-sm mt-1";
    sub.textContent = "One-off price, no monthly fee. We reply " + routing.replyPromise + ".";
    copy.appendChild(headline);
    copy.appendChild(sub);
    inner.appendChild(copy);

    var actions = document.createElement("div");
    actions.className = "flex flex-wrap gap-3";

    var book = document.createElement("a");
    book.href = siteRoot() + "booking.html";
    book.textContent = "Book a free 15-minute call →";
    book.className =
      "inline-block gradient-bg text-white px-5 py-2.5 rounded-full font-semibold text-sm";
    actions.appendChild(book);

    if (email) {
      var mail = document.createElement("a");
      mail.href = "mailto:" + email + "?subject=" + encodeURIComponent("AutoFlow enquiry");
      mail.textContent = email;
      mail.className =
        "inline-block border border-gray-600 text-gray-200 px-5 py-2.5 rounded-full text-sm hover:border-gray-400";
      actions.appendChild(mail);
    }
    if (whatsapp) {
      var wa = document.createElement("a");
      wa.href = whatsappHref(whatsapp, "Hi AutoFlow — I have a question about automation for my business.");
      wa.textContent = "Message us on WhatsApp";
      wa.className =
        "inline-block border border-gray-600 text-gray-200 px-5 py-2.5 rounded-full text-sm hover:border-gray-400";
      actions.appendChild(wa);
    }

    inner.appendChild(actions);
    strip.appendChild(inner);
    body.appendChild(strip);
  }

  if (typeof document !== "undefined" && document.addEventListener) {
    document.addEventListener("DOMContentLoaded", mountContactStrip);
  }

  return {
    ROUTING: ROUTING,
    BLOCKED_NUMBERS: BLOCKED_NUMBERS,
    build: build,
    field: field,
    wire: wire,
    reveal: reveal,
    mountContactStrip: mountContactStrip,
    composeMessage: composeMessage,
    mailtoHref: mailtoHref,
    whatsappHref: whatsappHref,
    normaliseWhatsAppNumber: normaliseWhatsAppNumber,
    normaliseEmailAddress: normaliseEmailAddress,
  };
});




