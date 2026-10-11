// Pricing consistency: this repo's generator vs. this repo's rendered site.
//
// Prices live in scripts/gen-suite.py PRODUCTS (mirroring the public site) and
// are repeated in website/suite.html (generated). A buyer who sees two prices
// stops believing either, so this fails when any price in the generator is
// missing from the rendered page.
//
// The pre-split umbrella also kept a hand-written ../SUITE.md that named every
// Abetworks product; that file was cross-repo marketing, not this app, so it
// is not checked here anymore.
//
// Run: node scripts/check-pricing.mjs — must report 0 failed.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const passes = [];
const failures = [];
const check = (label, ok, detail = "") =>
  (ok ? passes : failures).push(ok ? label : `${label}${detail ? ` — ${detail}` : ""}`);

const generator = readFileSync(join(ROOT, "scripts", "gen-suite.py"), "utf8");
const prices = [...generator.matchAll(/"price":\s*"([^"]+)"/g)].map((m) => m[1]);
check("the generator names prices", prices.length > 0, `${prices.length} found`);

const suiteHtml = readFileSync(join(ROOT, "website", "suite.html"), "utf8");

for (const price of prices) {
  check(`suite.html shows ${price}`, suiteHtml.includes(price));
}

for (const label of failures) console.log(`FAIL  ${label}`);
console.log(`\nPricing check — ${passes.length} passed, ${failures.length} failed`);
if (failures.length) process.exit(1);
