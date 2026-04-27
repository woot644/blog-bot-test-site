"""Regenerate the auto-managed cards block inside src/results.html.

Reads every JSON in scripts/scraped/results/, sorts newest-first, and rewrites
the section between the sentinel comments:

    <!-- bot:results:start -->
    <!-- bot:results:end -->

Hand-crafted cards above/below the sentinels are untouched.

This file is a deployment artefact owned by the blog-bot repo. To update it,
edit blog-bot/site-scripts/build_results_index.py and redeploy to all site
repos (FP Brisbane, blog-bot-test-site).
"""
from __future__ import annotations

import html
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRAPED_DIR = REPO_ROOT / "scripts" / "scraped" / "results"
INDEX_PATH = REPO_ROOT / "src" / "results.html"

START_SENTINEL = "<!-- bot:results:start -->"
END_SENTINEL = "<!-- bot:results:end -->"


def main() -> int:
    if not INDEX_PATH.exists():
        print(f"[build_results_index] Index not found: {INDEX_PATH} — skipping.")
        return 0
    if not SCRAPED_DIR.exists():
        print(f"[build_results_index] No scraped dir: {SCRAPED_DIR} — skipping.")
        return 0

    cards = _load_cards(SCRAPED_DIR)
    block = _render_cards_block(cards)
    original = INDEX_PATH.read_text(encoding="utf-8")
    updated = _replace_block(original, block)
    if updated == original:
        print("[build_results_index] No change.")
        return 0
    INDEX_PATH.write_text(updated, encoding="utf-8")
    print(f"[build_results_index] Wrote {len(cards)} card(s) into {INDEX_PATH}.")
    return 0


def _load_cards(scraped_dir: Path) -> list[dict]:
    cards: list[dict] = []
    for p in scraped_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"[build_results_index] skip {p.name}: {exc}")
            continue
        if data.get("slug") and data.get("url") and data.get("client_name"):
            cards.append(data)
    cards.sort(key=lambda d: d.get("date_published", ""), reverse=True)
    return cards


def _render_cards_block(cards: list[dict]) -> str:
    if not cards:
        return ""
    return "\n".join(_render_card(c) for c in cards)


def _render_card(card: dict) -> str:
    title = f"{card['client_name']} — {card['heading_text']}"
    desc = card.get("description") or ""
    url = card["url"]
    hero = card.get("hero_image") or ""
    hero_webp = hero.replace(".jpg", ".webp") if hero else ""
    alt = f"{card['client_name']} {card['heading_text']}"

    img_block = ""
    if hero:
        img_block = (
            f'<picture>'
            f'<source type="image/webp" srcset="{html.escape(hero_webp)}">'
            f'<img src="{html.escape(hero)}" alt="{html.escape(alt)}" '
            f'loading="lazy" class="w-full aspect-[4/3] object-cover">'
            f'</picture>'
        )

    return (
        f'        <a href="{html.escape(url)}" '
        f'class="block bg-white rounded-xl overflow-hidden shadow-sm '
        f'border border-gray-100 hover:shadow-md hover:border-accent-500/30 '
        f'hover:-translate-y-0.5 transition-all">\n'
        f'          {img_block}\n'
        f'          <div class="p-6">\n'
        f'            <h3 class="font-semibold text-dark-900 text-lg mb-1">'
        f'{html.escape(title)}</h3>\n'
        f'            <p class="text-gray-600 text-sm leading-relaxed">'
        f'{html.escape(desc)}</p>\n'
        f'          </div>\n'
        f'        </a>'
    )


def _replace_block(content: str, block: str) -> str:
    """Replace the content between the start/end sentinels. If either sentinel
    is missing, return content unchanged (no-op rather than fail)."""
    i = content.find(START_SENTINEL)
    j = content.find(END_SENTINEL)
    if i < 0 or j < 0 or j < i:
        return content
    prefix = content[: i + len(START_SENTINEL)]
    suffix = content[j:]
    inner = f"\n{block}\n" if block else "\n"
    return f"{prefix}{inner}{suffix}"


if __name__ == "__main__":
    raise SystemExit(main())
