"""Parse a saved BuyMe All accepting-businesses page (BuyMe.html).

Cards that were rendered into the saved file are imported. The page counter
can be higher than the number of rendered cards because the rest never
loaded into the HTML. There is no discount percentage on this page.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import DEFAULT_DUMP, apply_limit, buyme_category, clean_text

CARD_RE = re.compile(r'data-testid="brand-result-(\d+)"([\s\S]*?)(?=data-testid="brand-result-|$)')
LOGO_RE = re.compile(r'class="properties logo"[^>]*src="\./BuyMe_files/([^"]+)"')
NAME_RE = re.compile(r"<h2[^>]*>\s*([^<]*?)\s*</h2>")
DESC_RE = re.compile(r"<h3[^>]*>\s*([^<]*?)\s*</h3>")
COUNTER_RE = re.compile(
    r'class="brands-page__results-count[\s\S]*?<span[^>]*>\s*(\d+)\s*</span>'
)
SOURCE = "https://buyme.co.il/brands/13438757"
LOGO_BASE = "https://buyme.co.il/files/"


def parse(html_path: Path, limit: int | None = None) -> tuple[list[dict], int | None]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    counter = COUNTER_RE.search(html)
    advertised = int(counter.group(1)) if counter else None
    rows = []
    seen = set()
    for brand_id, chunk in CARD_RE.findall(html):
        if brand_id in seen:
            continue
        seen.add(brand_id)
        logo = LOGO_RE.search(chunk)
        name_match = NAME_RE.search(chunk)
        desc_match = DESC_RE.search(chunk)
        if not logo or not name_match:
            continue
        name = clean_text(name_match.group(1))
        description = clean_text(desc_match.group(1)) if desc_match else ""
        if not name:
            continue
        logo_file = logo.group(1)
        rows.append(
            {
                "clubId": "buyme",
                "name": name,
                "categories": [buyme_category(description)],
                "logoUrl": f"{LOGO_BASE}{logo_file}",
                "redemptionUrl": SOURCE,
                "onlineRedemption": "online-redeem" in chunk,
                "sourceUrl": SOURCE,
                "discountPercentage": None,
                "note": (
                    "Accepts BUYME ALL. "
                    f"Card description: {description or '—'}. "
                    "No percentage on this page."
                ),
            }
        )
    return apply_limit(rows, limit), advertised


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_DUMP / "BuyMe.html")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    rows, advertised = parse(args.html, args.limit)
    print(
        f"buyme {len(rows)} rendered businesses"
        + (f" (page counter {advertised})" if advertised else "")
        + f", sample: {rows[0]['name']}"
    )


if __name__ == "__main__":
    main()
