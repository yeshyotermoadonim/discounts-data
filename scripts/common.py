"""Shared helpers for turning a saved club page into listing records."""

from __future__ import annotations

import hashlib
import re
from html import unescape
from pathlib import Path

SNAPSHOT_DATE = "2026-11-01"
DEFAULT_DUMP = Path.home() / "Downloads" / "Moadonim" / "2026-11-6"

HEVER_CATEGORY_IDS = {
    "ביגוד והנעלה": "clothing-footwear",
    "לבית ולחצר": "home",
    "טיפוח וקוסמטיקה": "beauty",
    "שינה וטקסטיל": "sleep-textile",
    "ספורט": "sport",
    "חשמל ואלקטרוניקה": "electronics",
    "מתנות ופנאי": "gifts-leisure",
    "ילדים ותינוקות": "children",
    "תכשיטים ואקססוריז": "jewelry",
    "נסיעות ומחנאות": "travel-camping",
    "אופטיקה": "optics",
    "שונה": "other",
    "אטרקציות": "attractions",
    "חיות מחמד": "pets",
    "לימודים וספרים": "education",
    "אביזרי מטבח": "home",
    "הלבשה תחתונה": "clothing",
    "יודאיקה": "judaica",
}

NEW_CATEGORIES = [
    {"id": "sleep-textile", "name": "שינה וטקסטיל"},
    {"id": "travel-camping", "name": "נסיעות ומחנאות"},
    {"id": "optics", "name": "אופטיקה"},
    {"id": "attractions", "name": "אטרקציות"},
    {"id": "pets", "name": "חיות מחמד"},
    {"id": "education", "name": "לימודים וספרים"},
    {"id": "judaica", "name": "יודאיקה"},
    {"id": "other", "name": "אחר"},
]

BUYME_KEYWORDS = [
    (["תינוק", "ילדים"], "children"),
    (["משקפ", "אופטיק"], "optics"),
    (["ספא", "טיפוח", "איפור", "קוסמט"], "beauty"),
    (["מלון", "נופש", "צימר"], "tourism"),
    (["מסעד", "קפה", "גליד", "קולינר", "אוכל", "בר"], "food"),
    (["חשמל", "אלקטרון"], "electronics"),
    (["תכשיט"], "jewelry"),
    (["ספורט", "כושר"], "sport"),
    (["ספר", "לימוד"], "education"),
    (["חיות", "כלב", "חתול"], "pets"),
    (["אופנה", "הלבשה", "נעל", "ביגוד"], "clothing-footwear"),
    (["בית", "מטבח", "טקסטיל", "רהיט"], "home"),
]


def clean_text(value: str) -> str:
    text = unescape(value).replace("\xa0", " ").strip()
    return re.sub(r"\s+", " ", text)


def normalize_name(name: str) -> str:
    text = clean_text(name).casefold()
    text = text.replace("׳", "").replace("'", "").replace("`", "").replace('"', "").replace("״", "")
    text = re.sub(r"\b(online|אונליין|אונלין)\b", " ", text)
    text = re.sub(r"^רשת\s+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def slugify(name: str, normalized: str) -> str:
    latin = clean_text(name).casefold()
    latin = re.sub(r"[^a-z0-9]+", "-", latin).strip("-")
    if re.search(r"[a-z]", latin) and len(re.sub(r"[^a-z0-9]", "", latin)) >= 2:
        return latin[:64]
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
    return f"b-{digest}"


def buyme_category(description: str) -> str:
    text = clean_text(description)
    for words, category_id in BUYME_KEYWORDS:
        if any(word in text for word in words):
            return category_id
    return "other"


def apply_limit(rows: list, limit: int | None) -> list:
    if limit is None:
        return rows
    return rows[:limit]
