"""Build clubs, brands, and discounts from the three saved club pages.

Each club parser can also be run on its own. This script is the one that
writes discounts-data JSON, and the website seed copies when that folder
is present.

    python3 scripts/parse_behatsdaa.py --limit 5
    python3 scripts/parse_hever.py --limit 5
    python3 scripts/parse_buyme.py --limit 5
    python3 scripts/build_dataset.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import DEFAULT_DUMP, NEW_CATEGORIES, SNAPSHOT_DATE, normalize_name, slugify
from parse_behatsdaa import parse as parse_behatsdaa
from parse_buyme import parse as parse_buyme
from parse_hever import parse as parse_hever

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT.parent / "discounts-website" / "src" / "data" / "seed"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(limit: int | None, dump: Path) -> dict:
    listings = []
    listings.extend(parse_behatsdaa(dump / "Beazdaa.html", limit))
    listings.extend(parse_hever(dump / "Hever.html", limit))
    buyme_rows, advertised = parse_buyme(dump / "BuyMe.html", limit)
    listings.extend(buyme_rows)

    clubs = load_json(ROOT / "clubs.json")
    for club in clubs:
        if club["id"] == "buyme":
            club["name"] = "ביימי אול"
            club["nameEn"] = "BuyMe All"
            club["url"] = "https://buyme.co.il/supplier/13438757"

    categories = load_json(ROOT / "categories.json")
    known = {item["id"] for item in categories}
    for item in NEW_CATEGORIES:
        if item["id"] not in known:
            categories.append(item)
            known.add(item["id"])

    brands_by_key: dict[str, dict] = {}
    brand_ids: dict[str, str] = {}
    discounts = []

    for row in listings:
        key = normalize_name(row["name"])
        if not key:
            continue
        if key not in brands_by_key:
            slug = slugify(row["name"], key)
            base = slug
            taken = set(brand_ids.values())
            n = 2
            while slug in taken:
                slug = f"{base}-{n}"
                n += 1
            brand_ids[key] = slug
            brands_by_key[key] = {
                "id": slug,
                "name": row["name"],
                "categories": [],
                "logoUrl": row["logoUrl"],
                "website": None,
            }
        brand = brands_by_key[key]
        if brand["logoUrl"] is None and row["logoUrl"]:
            brand["logoUrl"] = row["logoUrl"]
        for category_id in row["categories"]:
            if category_id not in brand["categories"]:
                brand["categories"].append(category_id)
        if not brand["categories"]:
            brand["categories"] = ["other"]

        percent = row["discountPercentage"]
        discount_id = f"{row['clubId']}-{brand['id']}-001"
        if any(item["id"] == discount_id for item in discounts):
            continue
        discounts.append(
            {
                "id": discount_id,
                "brandId": brand["id"],
                "clubId": row["clubId"],
                "type": "percentage",
                "discountPercentage": percent,
                "originalPrice": None,
                "discountedPrice": None,
                "redemptionUrl": row["redemptionUrl"],
                "onlineRedemption": row["onlineRedemption"],
                "mobileRedemption": None,
                "sourceUrl": row["sourceUrl"],
                "lastVerified": SNAPSHOT_DATE,
                "verificationStatus": "verified",
                "_meta": {
                    "source": f"saved-page:{row['clubId']}",
                    "note": row["note"],
                },
            }
        )

    brands = sorted(brands_by_key.values(), key=lambda item: item["id"])
    discounts.sort(key=lambda item: item["id"])
    return {
        "clubs": clubs,
        "categories": categories,
        "brands": brands,
        "discounts": discounts,
        "buymeAdvertised": advertised,
        "buymeParsed": len(buyme_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
    parser.add_argument("--limit", type=int, default=None, help="Keep the first N rows per club")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    data = build(args.limit, args.dump)
    counts = {
        club["id"]: sum(1 for row in data["discounts"] if row["clubId"] == club["id"])
        for club in data["clubs"]
    }
    print(
        f"brands={len(data['brands'])} discounts={len(data['discounts'])} "
        f"by club={counts} buyme_rendered={data['buymeParsed']} "
        f"buyme_counter={data['buymeAdvertised']}"
    )
    if args.dry_run:
        return
    write_json(ROOT / "clubs.json", data["clubs"])
    write_json(ROOT / "categories.json", data["categories"])
    write_json(ROOT / "brands.json", data["brands"])
    write_json(ROOT / "discounts.json", data["discounts"])
    if SEED.exists():
        write_json(SEED / "clubs.json", data["clubs"])
        write_json(SEED / "categories.json", data["categories"])
        write_json(SEED / "brands.json", data["brands"])
        write_json(SEED / "discounts.json", data["discounts"])
        print(f"synced seed {SEED}")


if __name__ == "__main__":
    main()
