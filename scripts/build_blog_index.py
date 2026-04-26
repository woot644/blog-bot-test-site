"""Regenerate src/blog-page/index.html from scripts/scraped/*.json.

Reads every JSON, sorts by date_published descending, and rewrites the
block between the `<!-- card-list:start -->` and `<!-- card-list:end -->`
sentinels in the existing index.html. The surrounding chrome is left alone.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRAPED = ROOT / "scripts" / "scraped"
INDEX = ROOT / "src" / "blog-page" / "index.html"
IMG_DIR = ROOT / "src" / "images" / "blog"

CARD_START = "<!-- card-list:start -->"
CARD_END = "<!-- card-list:end -->"


def load_posts() -> list[dict]:
    posts: list[dict] = []
    for p in SCRAPED.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("title"):
            posts.append(data)
    posts.sort(key=lambda d: d.get("date_published") or "0000", reverse=True)
    return posts


def format_date(iso: str) -> str:
    if not iso:
        return ""
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")
    except Exception:
        return iso


def shorten(text: str, n: int = 160) -> str:
    text = (text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1].rsplit(" ", 1)[0] + "\u2026"


def esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def hero_files(slug: str) -> tuple[str, str] | None:
    post_dir = IMG_DIR / slug
    if not post_dir.exists():
        return None
    jpgs = sorted(post_dir.glob("*.jpg"))
    if not jpgs:
        return None
    jpg = jpgs[0]
    webp = jpg.with_suffix(".webp")
    if not webp.exists():
        return None
    return jpg.name, webp.name


def render_card(post: dict) -> str:
    slug = post["slug"]
    title = esc(post["title"])
    description = esc(shorten(post.get("description", ""), 180))
    date_display = format_date(post.get("date_published", ""))

    files = hero_files(slug)
    if files:
        jpg, webp = files
        img = (
            f'<picture>'
            f'<source type="image/webp" srcset="../images/blog/{slug}/{webp}">'
            f'<img src="../images/blog/{slug}/{jpg}" alt="{title}" loading="lazy" '
            f'class="w-full h-48 object-cover">'
            f'</picture>'
        )
    else:
        img = '<div class="w-full h-48 bg-dark-800"></div>'

    date_html = (
        f'<time class="text-xs text-gray-500 uppercase tracking-wider">{date_display}</time>'
        if date_display
        else ""
    )

    return (
        f'<a href="/blog-page/{slug}" class="card-dark overflow-hidden hover:border-accent-500/40 transition-all">'
        f'<div class="overflow-hidden">{img}</div>'
        f'<div class="p-6">'
        f'{date_html}'
        f'<h3 class="text-white font-bold text-lg leading-tight mt-2 mb-3">{title}</h3>'
        f'<p class="text-gray-400 text-sm leading-relaxed">{description}</p>'
        f'</div>'
        f'</a>'
    )


def main() -> None:
    posts = load_posts()
    cards = "\n".join(render_card(p) for p in posts)

    content = INDEX.read_text(encoding="utf-8")
    i = content.find(CARD_START)
    j = content.find(CARD_END)
    if i < 0 or j < 0:
        raise SystemExit("Card-list sentinels missing from index.html")
    prefix = content[: i + len(CARD_START)]
    suffix = content[j:]
    new = f"{prefix}\n{cards}\n{suffix}"
    INDEX.write_text(new, encoding="utf-8")
    print(f"Wrote {INDEX} ({len(posts)} posts)")


if __name__ == "__main__":
    main()
