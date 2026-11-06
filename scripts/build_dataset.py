"""Build clubs, brands, and listings from the three saved club pages.

A listing means the brand is available in that club. Online is stored on
the listing, because the same brand can be online in one club and not in
another. There is no percentage: these pages do not publish one.

Each club parser can also be run on its own. This script writes the JSON
files, and the website seed copies when that folder is present.

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

from common import DEFAULT_DUMP, NEW_CATEGORIES, normalize_name, slugify
from parse_behatsdaa import parse as parse_behatsdaa
from parse_buyme import parse as parse_buyme
from parse_hever import parse as parse_hever

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT.parent / "discounts-website" / "src" / "data" / "seed"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prefer_name(current: str, incoming: str) -> str:
    def score(name: str) -> tuple:
        folded = name.casefold()
        return (
            "אונליין" in folded or "online" in folded,
            folded.startswith("רשת"),
            len(name),
        )

    return incoming if score(incoming) < score(current) else current


def build(limit: int | None, dump: Path, buyme: Path | None = None) -> dict:
    listings = []
    listings.extend(parse_behatsdaa(dump / "Beazdaa.html", limit))
    listings.extend(parse_hever(dump / "Hever.html", limit))
    buyme_path = buyme or (dump / "BuyMe.html")
    buyme_rows, advertised = parse_buyme(buyme_path, limit)
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
    listings_by_pair: dict[tuple[str, str], dict] = {}

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
            }
        brand = brands_by_key[key]
        brand["name"] = prefer_name(brand["name"], row["name"])
        if brand["logoUrl"] is None and row["logoUrl"]:
            brand["logoUrl"] = row["logoUrl"]
        for category_id in row["categories"]:
            if category_id not in brand["categories"]:
                brand["categories"].append(category_id)

        pair = (row["clubId"], brand["id"])
        current = listings_by_pair.get(pair)
        if current is None:
            listings_by_pair[pair] = {
                "brandId": brand["id"],
                "clubId": row["clubId"],
                "online": bool(row["online"]),
                "url": row["url"],
            }
        else:
            current["online"] = current["online"] or bool(row["online"])

    for brand in brands_by_key.values():
        specific = [category_id for category_id in brand["categories"] if category_id != "other"]
        brand["categories"] = specific or brand["categories"]

    brands = sorted(brands_by_key.values(), key=lambda item: item["id"])
    used_categories = {category_id for brand in brands for category_id in brand["categories"]}
    categories = [item for item in categories if item["id"] in used_categories]
    availability = sorted(listings_by_pair.values(), key=lambda item: (item["clubId"], item["brandId"]))
    return {
        "clubs": clubs,
        "categories": categories,
        "brands": brands,
        "listings": availability,
        "buymeAdvertised": advertised,
        "buymeParsed": len(buyme_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
    parser.add_argument("--buyme", type=Path, default=None, help="BuyMe.html, when it lives in a newer folder")
    parser.add_argument("--limit", type=int, default=None, help="Keep the first N rows per club")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    data = build(args.limit, args.dump, args.buyme)
    counts = {
        club["id"]: sum(1 for row in data["listings"] if row["clubId"] == club["id"])
        for club in data["clubs"]
    }
    print(
        f"brands={len(data['brands'])} listings={len(data['listings'])} "
        f"by club={counts} buyme_rendered={data['buymeParsed']} "
        f"buyme_counter={data['buymeAdvertised']}"
    )
    if args.dry_run:
        return
    for folder in (ROOT, SEED):
        if not folder.exists():
            continue
        write_json(folder / "clubs.json", data["clubs"])
        write_json(folder / "categories.json", data["categories"])
        write_json(folder / "brands.json", data["brands"])
        write_json(folder / "listings.json", data["listings"])
        old = folder / "discounts.json"
        if old.exists():
            old.unlink()
    print(f"synced seed {SEED}")


if __name__ == "__main__":
    main()
