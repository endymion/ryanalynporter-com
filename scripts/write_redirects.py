"""Write the `redirects.exact` of web/projection.json into the built site as meta-refresh pages.

Papyrus applies redirects at a CloudFront edge, and GitHub Pages has none, so each old path (the Octopress archive and
category pages) gets an index.html that sends the reader, and search engines through rel=canonical, to its new home.

Usage: python scripts/write_redirects.py <built site directory>
"""

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved</title>
<link rel="canonical" href="{url}">
<meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={target}">
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


def main(site_directory):
    settings = json.loads((ROOT / "web" / "projection.json").read_text())
    origin = settings["site"]["productionUrl"].rstrip("/")
    for source, target in settings.get("redirects", {}).get("exact", {}).items():
        page = site_directory / source.strip("/") / "index.html"
        if page.exists():
            raise SystemExit(f"{source} is a real page; refusing to replace it with a redirect")
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(PAGE.format(url=escape(origin + target, quote=True), target=escape(target, quote=True)))
        print(f"{source} -> {target}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
