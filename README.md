# ryanalynporter.com

Ryan Alyn Porter's site, built with [Papyrus](https://github.com/AnthusAI/Papyrus) as a static Markus site and
published to GitHub Pages by `.github/workflows/pages.yml` on every push to `master` and once a day.

## Layout

| Path | What it is |
|---|---|
| `content/<yyyy>/<mm>/<dd>/<slug>.md` | Posts written for this site. The path is the URL: `/2012/06/12/simple-redis-caching-in-ruby/`, as it was under Octopress. |
| `content/syndicated/` | Generated at build time by `scripts/syndicate.py` (not committed): link-only cards for articles on the Anthus publications listed in `scripts/syndication.json`. |
| `web/projection.json` | Papyrus settings: sections, pages, feeds, legacy redirects. |
| `web/hooks.py`, `web/site_data.py` | The look of every page, and the standing copy of the Building and Background pages. |
| `web/css/site-theme.css`, `web/assets/site.js` | The theme and the Writing page's publication filter. |
| `web/public/` | Files published as they are at the site root: post images, the résumé, the Super Minimal Ads demo, the favicon. |

## Writing a post

Add `content/<yyyy>/<mm>/<dd>/<slug>.md` with front matter `title`, `description`, `date` and `tags`. A post in a new
year needs that year added to `urls.sections` in `web/projection.json` (Papyrus ignores items in undeclared sections).

## Building locally

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
PATH=.venv/bin:$PATH scripts/build.sh
python3 -m http.server 8642 --directory dist
```

`scripts/write_redirects.py` turns `redirects.exact` into meta-refresh pages, because GitHub Pages has no edge to
redirect at (the old `/archives/` and `/categories/<name>/` pages).
