"""Parse a saved חבר שלי chain list (Hever.html).

The page lists chains on the loaded card. It includes a category and an
online badge, and it does not include a discount percentage.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from common import DEFAULT_DUMP, HEVER_CATEGORY_IDS, apply_limit, clean_text

CHUNK_RE = re.compile(r'javascript:gotoBranches\((\d+)\)">([\s\S]*?)</a>')
SOURCE = "https://www.mcc.co.il/site/pg/shely_card_company"
LOGO_BASE = "https://www.mcc.co.il/pics/giftcard/"


def parse(html_path: Path, limit: int | None = None) -> list[dict]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    rows = []
    seen = set()
    unknown = set()
    for company_id, chunk in CHUNK_RE.findall(html):
        logo = re.search(r'src="\./Hever_files/([^"]+)"', chunk)
        name_match = re.search(r'<p class="h6[^"]*"[^>]*>\s*([^<]+?)\s*</p>', chunk)
        category_match = re.search(
            r'<p class="d-none d-xl-block[^"]*"[^>]*>([\s\S]*?)</p>',
            chunk,
        )
        if not logo or not name_match or not category_match:
            continue
        name = clean_text(name_match.group(1))
        raw_category = category_match.group(1)
        categories = [
            clean_text(part)
            for part in re.split(r"<br\s*/?>|\|", raw_category)
            if clean_text(part)
        ]
        logo_file = logo.group(1)
        if not name or name in seen:
            continue
        seen.add(name)
        category_ids = []
        for category in categories:
            category_id = HEVER_CATEGORY_IDS.get(category)
            if category_id is None:
                unknown.add(category)
                category_id = "other"
            if category_id not in category_ids:
                category_ids.append(category_id)
        category = " | ".join(categories)
        window_start = html.find(f"gotoBranches({company_id})")
        prefix = html[max(0, window_start - 400) : window_start]
        badge = re.search(r'class="online-badge([^"]*)"', prefix)
        online = bool(badge) and "hide" not in badge.group(1)
        rows.append(
            {
                "clubId": "hever-sheli",
                "name": name,
                "categories": category_ids or ["other"],
                "logoUrl": f"{LOGO_BASE}{logo_file}",
                "redemptionUrl": f"https://www.mcc.co.il/site/pg/shely_card_store?sn={company_id}",
                "onlineRedemption": online,
                "sourceUrl": SOURCE,
                "discountPercentage": None,
                "note": (
                    "Listed on חבר שלי chain directory. "
                    f"Category “{category}”. No percentage on this page."
                ),
            }
        )
    if unknown:
        raise SystemExit(f"Unmapped חבר categories: {sorted(unknown)}")
    return apply_limit(rows, limit)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_DUMP / "Hever.html")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    rows = parse(args.html, args.limit)
    print(f"hever {len(rows)} chains, sample: {rows[0]['name']} / {rows[0]['categories']}")


if __name__ == "__main__":
    main()
