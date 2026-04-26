# blog-bot-test-site

Sandbox site for testing the blog-bot auto-publish pipeline end-to-end.

Mirrors the structure of a real client site (FP Brisbane) at the minimum
needed to validate publishes:

- `src/blog-page/` — individual blog post HTML files land here
- `src/images/blog/<slug>/` — webp + jpg pair per image
- `scripts/scraped/<slug>.json` — per-post metadata, written by the bot
- `scripts/build_blog_index.py` — regenerates `src/blog-page/index.html`
- `src/llms.txt` — sentinel-wrapped Latest articles block, refreshed on publish

No real content. Vercel auto-deploys `master` to a preview URL — that's the
sandbox visitors hit when iterating on the bot.

To target the bot at this site:

```
SITE_CONFIG=config/test-site.yaml python -m blog_bot
```
