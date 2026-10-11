// UI-basics check for the AutoFlow static site.
//
// Why this file exists: the buy-path check proves an enquiry can leave the
// page; this one proves everyone can use the page. Every assertion is a WCAG
// 2.x rule with a stable, mechanical test — lang (3.1.1), page titled (2.4.2),
// zoomable viewport (1.4.4), img alt (1.1.1), labelled controls (3.3.2/4.1.2),
// one h1 and unskipped heading levels (1.3.1/2.4.6).
//
// Run: node scripts/check-ui.mjs
// Must report 0 failed. If you change this file, prove it can still fail:
// break one label and watch it go red.

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(fileURLToPath(import.meta.url), "..", "..", "website");

function pages(dir, acc = []) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (statSync(full).isDirectory()) pages(full, acc);
    else if (entry.endsWith(".html")) acc.push(full);
  }
  return acc;
}

const passes = [];
const failures = [];
const check = (label, ok, detail = "") =>
  (ok ? passes : failures).push(ok ? label : `${label}${detail ? ` — ${detail}` : ""}`);

const FILES = pages(ROOT);
check("pages were found", FILES.length > 0, `${FILES.length} pages`);

const titles = new Map();
for (const file of FILES) {
  const rel = relative(ROOT, file);
  const raw = readFileSync(file, "utf8");
  // Markup only: example code inside <script> (e.g. "<select>" in a comment)
  // is not a control anyone tabs to.
  const html = raw
    .replace(/<script\b[\s\S]*?<\/script\s*>/gi, "")
    .replace(/<style\b[\s\S]*?<\/style\s*>/gi, "");

  const lang = html.match(/<html[^>]*\blang="([a-zA-Z-]+)"/);
  check(`${rel} declares a page language`, Boolean(lang), "no lang on <html>");

  const title = html.match(/<title>([\s\S]*?)<\/title>/i);
  const text = (title?.[1] ?? "").trim();
  check(`${rel} has a non-empty title`, text.length > 0);
  if (text) {
    check(`${rel} title is unique`, !titles.has(text), `also on ${titles.get(text)}`);
    titles.set(text, rel);
  }

  const vp = html.match(/<meta[^>]*name="viewport"[^>]*content="([^"]*)"/i);
  check(`${rel} has a viewport meta`, Boolean(vp), "no viewport, mobile users suffer");
  if (vp) {
    const zoomable = !/maximum-scale\s*=\s*1(\.0)?\b|user-scalable\s*=\s*no/i.test(vp[1]);
    check(`${rel} viewport keeps zoom enabled`, zoomable, vp[1]);
  }

  for (const img of html.match(/<img\b[^>]*>/gi) ?? []) {
    check(`${rel} image has alt text`, /\balt=/.test(img), img.slice(0, 80));
  }

  const labelRanges = [...html.matchAll(/<label\b[^>]*>[\s\S]*?<\/label>/gi)].map((m) => [
    m.index,
    m.index + m[0].length,
  ]);
  const inLabel = (pos) => labelRanges.some(([s, e]) => s <= pos && pos < e);
  for (const m of html.matchAll(/<(input|select|textarea)\b([^>]*)>/gi)) {
    const attrs = m[2];
    if (/type="(hidden|submit|button|image|reset)"/i.test(attrs)) continue;
    if (/\baria-label="[^"]+"|\baria-labelledby="[^"]+"/.test(attrs)) continue;
    const id = attrs.match(/\bid="([^"]+)"/)?.[1];
    if (id && new RegExp(`<label\\b[^>]*for="${id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`).test(html))
      continue;
    if (inLabel(m.index)) continue;
    check(`${rel} control is labelled`, false, m[0].slice(0, 80));
  }

  const h1s = html.match(/<h1\b/gi) ?? [];
  check(`${rel} has exactly one h1`, h1s.length === 1, `found ${h1s.length}`);

  const levels = [...html.matchAll(/<h([1-6])\b/gi)].map((m) => Number(m[1]));
  const skip = levels.find((lv, i) => i > 0 && lv > levels[i - 1] + 1);
  check(`${rel} never skips a heading level`, skip === undefined, `jump to h${skip}`);
}

for (const label of failures) console.log(`FAIL  ${label}`);
console.log(`\nAutoFlow UI check — ${passes.length} passed, ${failures.length} failed`);
console.log(`pages scanned: ${FILES.length}`);
if (failures.length) process.exit(1);
