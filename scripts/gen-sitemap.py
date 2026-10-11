#!/usr/bin/env python3
"""Generate sitemap.xml and robots.txt for the AutoFlow static site.

Usage: python3 scripts/gen-sitemap.py [--base-url URL] [--out-dir DIR]
"""
import argparse
import datetime
import sys
from pathlib import Path

PAGES = [
    ("", "daily", "1.0"),
    ("about.html", "weekly", "0.8"),
    ("audit.html", "weekly", "0.8"),
    ("booking.html", "weekly", "0.8"),
    ("calculator.html", "weekly", "0.8"),
    ("case-studies.html", "weekly", "0.7"),
    ("dashboard.html", "monthly", "0.5"),
    ("invoice.html", "monthly", "0.5"),
    ("portfolio.html", "weekly", "0.7"),
    ("privacy.html", "yearly", "0.3"),
    ("terms.html", "yearly", "0.3"),
    ("thank-you.html", "yearly", "0.3"),
    ("suite.html", "daily", "0.9"),
    ("services/lead-capture.html", "weekly", "0.8"),
    ("services/email-automation.html", "weekly", "0.8"),
    ("services/appointment-booking.html", "weekly", "0.8"),
    ("services/ai-chatbot.html", "weekly", "0.8"),
    ("services/multi-channel.html", "weekly", "0.7"),
    ("services/waitlist-builder.html", "weekly", "0.7"),
]

ROBOTS = """# AutoFlow robots.txt
User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True, help="e.g. https://abetworks.in")
    ap.add_argument("--out-dir", default="website", help="directory containing HTML files")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    out = Path(args.out_dir)

    today = datetime.date.today().isoformat()
    urls = []
    for rel, freq, pri in PAGES:
        urls.append(
            f"  <url>\n"
            f"    <loc>{base}/{rel}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{pri}</priority>\n"
            f"  </url>"
        )

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )

    (out / "sitemap.xml").write_text(sitemap)
    (out / "robots.txt").write_text(ROBOTS.format(base_url=base))
    print(f"Wrote {out}/sitemap.xml ({len(urls)} URLs) and {out}/robots.txt")


if __name__ == "__main__":
    main()