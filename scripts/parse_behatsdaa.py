"""Parse a saved בהצדעה wallet page (Beazdaa.html).

Each shop card means the chain is available in that wallet. The page does
not give a per-shop percentage, so none is recorded. "אונליין" in the shop
name is treated as online for this club only.
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
def parse(html_path: Path, limit: int | None = None) -> list[dict]:
    html = html_path.read_text(encoding="utf-8", errors="replace")
    rows = []
    seen = set()
    for name, href in CARD_RE.findall(html):
        name = clean_text(name)
        if not name or name in seen:
            continue
        seen.add(name)
        folded = name.casefold()
        rows.append(
            {
                "clubId": "behatsdaa",
                "name": name,
                "categories": [],
                "logoUrl": None,
                "url": href.replace("&amp;", "&"),
                "online": "אונליין" in folded or "online" in folded,
            }
        )
    return apply_limit(rows, limit)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, default=DEFAULT_DUMP / "Beazdaa.html")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    rows = parse(args.html, args.limit)
    print(f"behatsdaa {len(rows)} shops, sample: {rows[0]['name']} online={rows[0]['online']}")


if __name__ == "__main__":
    main()
