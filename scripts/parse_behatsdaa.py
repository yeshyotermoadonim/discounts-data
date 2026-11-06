"""Parse a saved בהצדעה wallet page (Beazdaa.html).

The saved page is one wallet. The percentage comes from the page heading
(for example "ארנק רשתות 20%"). Shop cards do not carry a separate rate.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import DEFAULT_DUMP, apply_limit, clean_text

CARD_RE = re.compile(
    r'<div class="shop-card"><div class="shop-icon-border">'
    r'<img src="[^"]*" class="shop-logo" alt="[^"]*"></div>'
    r'<div class="shop-details"><div class="shop-name">([^<]*)</div>'
    r'<div class="link-branches"><a href="([^"]*)">',
    re.S,
)
HEADING_RE = re.compile(r'class="custom-header-text[^"]*"[^>]*>([^<]+)')
PERCENT_RE = re.compile(r"(\d{1,2})\s*%")


def parse(html_path: Path, limit: int | None = None) -> list[dict]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    headings = [clean_text(value) for value in HEADING_RE.findall(html)]
    if not headings:
        raise SystemExit(f"No wallet heading in {html_path}")
    percent_match = PERCENT_RE.search(headings[0])
    if not percent_match:
        raise SystemExit(f"No percentage in בהצדעה heading: {headings[0]!r}")
    percent = int(percent_match.group(1))
    source = "https://www.behatsdaa.org.il/card/shops?walletId=2809"

    rows = []
    seen = set()
    for name, href in CARD_RE.findall(html):
        name = clean_text(name)
        if not name or name in seen:
            continue
        seen.add(name)
        url = href.replace("&amp;", "&")
        rows.append(
            {
                "clubId": "behatsdaa",
                "name": name,
                "categories": ["other"],
                "logoUrl": None,
                "redemptionUrl": url,
                "onlineRedemption": "אונליין" in name.casefold() or "online" in name.casefold(),
                "sourceUrl": source,
                "discountPercentage": percent,
                "note": f"Listed on בהצדעה wallet “{headings[0]}”. Saved page {html_path.name}.",
            }
        )
    return apply_limit(rows, limit)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_DUMP / "Beazdaa.html")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    rows = parse(args.html, args.limit)
    print(f"behatsdaa {len(rows)} shops, sample: {rows[0]['name']} {rows[0]['discountPercentage']}%")


if __name__ == "__main__":
    main()
