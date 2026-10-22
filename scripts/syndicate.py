"""Write link-only items for articles published on the other Anthus publications.

Reads each source's Atom feed (scripts/syndication.json), fetches every article's og:image, and writes
content/syndicated/<source>/<slug>.md. The `syndicated` section in web/projection.json has `pages: false`, so these
items are cards that link out to the original article; they get no page here and stay out of the feeds and sitemap.

A source that cannot be read is skipped with a warning, so one publication being down never breaks the build.
"""

import json
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ElementTree
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scripts" / "syndication.json"
OUTPUT = ROOT / "content" / "syndicated"
ATOM = "{http://www.w3.org/2005/Atom}"
USER_AGENT = "ryanalynporter.com syndication (+https://www.ryanalynporter.com/)"
TIMEOUT_SECONDS = 20

META_TAG_PATTERN = re.compile(r"<meta\s[^>]*>", re.I)
ATTRIBUTE_PATTERN = re.compile(r'([a-zA-Z:_-]+)\s*=\s*"([^"]*)"')
SLUG_UNSAFE_PATTERN = re.compile(r"[^a-z0-9-]+")
TAG_PATTERN = re.compile(r"<[^>]+>")


def _fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def _og_image(article_url):
    try:
        html = _fetch(article_url).decode("utf-8", "replace")
    except Exception as error:  # noqa: BLE001 - a missing image is not worth failing the build over
        print(f"  no og:image for {article_url}: {error}", file=sys.stderr)
        return None
    for tag in META_TAG_PATTERN.findall(html):
        attributes = {name.lower(): value for name, value in ATTRIBUTE_PATTERN.findall(tag)}
        if attributes.get("property") == "og:image" and attributes.get("content"):
            return urljoin(article_url, unescape(attributes["content"]))
    return None


def _slug(url):
    path = urlparse(url).path.strip("/") or "index"
    return SLUG_UNSAFE_PATTERN.sub("-", path.lower().replace("/", "--")).strip("-")


def _text(element, name):
    value = element.findtext(ATOM + name)
    return unescape(TAG_PATTERN.sub("", value)).strip() if value else ""


def _entries(source):
    feed = ElementTree.fromstring(_fetch(source["feed"]))
    for entry in feed.findall(ATOM + "entry")[: source["limit"]]:
        link = next((element.get("href") for element in entry.findall(ATOM + "link") if element.get("rel", "alternate") == "alternate"), None)
        if not link:
            continue
        yield {
            "title": _text(entry, "title"),
            "url": urljoin(source["feed"], link),
            "date": (_text(entry, "published") or _text(entry, "updated"))[:10],
            "description": _text(entry, "summary"),
        }


def _write(source, article, image):
    front_matter = {
        "title": article["title"],
        "url": article["url"],
        "date": article["date"],
        "description": article["description"] if article["description"] != article["title"] else "",
        "image": image,
        "publication": source["key"],
        "publicationName": source["name"],
        "domain": source["domain"],
    }
    lines = [f"{name}: {json.dumps(value, ensure_ascii=False)}" for name, value in front_matter.items() if value]
    target = OUTPUT / source["key"] / f"{_slug(article['url'])}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\n" + "\n".join(lines) + "\n---\n", encoding="utf-8")


def main():
    sources = json.loads(CONFIG.read_text())["sources"]
    shutil.rmtree(OUTPUT, ignore_errors=True)
    for source in sources:
        try:
            articles = list(_entries(source))
        except Exception as error:  # noqa: BLE001 - see the module docstring
            print(f"warning: skipped {source['name']} ({source['feed']}): {error}", file=sys.stderr)
            continue
        for article in articles:
            _write(source, article, _og_image(article["url"]))
        print(f"{source['name']}: {len(articles)} articles")


if __name__ == "__main__":
    main()
