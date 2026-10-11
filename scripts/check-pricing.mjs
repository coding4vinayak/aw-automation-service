// Pricing consistency: one catalogue, three places.
//
// Prices live in scripts/gen-suite.py PRODUCTS (mirroring the public site).
// They are repeated in website/suite.html (generated) and products/SUITE.md
// (hand-written). A buyer who sees two prices stops believing either, so this
// fails when any price in the generator is missing from both documents.
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
const portfolio = readFileSync(join(ROOT, "..", "SUITE.md"), "utf8");

for (const price of prices) {
  check(`suite.html shows ${price}`, suiteHtml.includes(price));
  check(`SUITE.md shows ${price}`, portfolio.includes(price));
}

for (const label of failures) console.log(`FAIL  ${label}`);
console.log(`\nPricing check — ${passes.length} passed, ${failures.length} failed`);
if (failures.length) process.exit(1);
