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


# Same store written in English on one club page and Hebrew on another.
NAME_ALIASES = {
    "billabong": "בילבונג",
}


_HEBREW = {
    "א": "",
    "ב": "b",
    "ג": "g",
    "ד": "d",
    "ה": "h",
    "ו": "v",
    "ז": "z",
    "ח": "h",
    "ט": "t",
    "י": "i",
    "כ": "k",
    "ך": "k",
    "ל": "l",
    "מ": "m",
    "ם": "m",
    "נ": "n",
    "ן": "n",
    "ס": "s",
    "ע": "a",
    "פ": "p",
    "ף": "p",
    "צ": "ts",
    "ץ": "ts",
    "ק": "k",
    "ר": "r",
    "ש": "sh",
    "ת": "t",
}


def normalize_name(name: str) -> str:
    text = clean_text(name)
    if ":" in text:
        right = text.split(":", 1)[1].strip()
        if right:
            text = right
    text = text.casefold()
    text = text.replace("׳", "").replace("'", "").replace("`", "").replace('"', "").replace("״", "")
    text = re.sub(r"\b(online|אונליין|אונלין)\b", " ", text)
    text = re.sub(r"^רשת\s+", "", text)
    text = re.sub(r"[^0-9a-z\u0590-\u05ff]+", "", text)
    return NAME_ALIASES.get(text, text)


def phonetic_key(text: str) -> str:
    chars = list(text)
    out: list[str] = []
    index = 0
    while index < len(chars):
        char = chars[index]
        if char == "א" and index + 1 < len(chars) and chars[index + 1] in "יו":
            out.append("i" if chars[index + 1] == "י" else "o")
            index += 2
            continue
        if char == "ה" and index == len(chars) - 1:
            out.append("a")
            index += 1
            continue
        if "א" <= char <= "ת":
            out.append(_HEBREW.get(char, ""))
        elif char.isascii() and char.isalnum():
            out.append(char)
        index += 1
    return "".join(out)


def script_kind(key: str) -> str:
    hebrew = bool(re.search(r"[\u0590-\u05ff]", key))
    latin = bool(re.search(r"[a-z]", key))
    if hebrew and not latin:
        return "he"
    if latin and not hebrew:
        return "lat"
    return "other"


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
