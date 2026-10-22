"""Write link-only items for Ryan's articles on the other Anthus publications.

For each source in scripts/syndication.json this reads the publication's full article list (the Papyrus
`/_data/search-index.json` when it serves one, else its Atom feed), keeps only articles whose byline matches
`authorPattern`, and writes content/syndicated/<source>/<slug>.md with the article's og:image. The `syndicated`
section in web/projection.json has `pages: false`, so these items are cards that link out to the original article;
they get no page here and stay out of the feeds and sitemap.

The byline is read from where Papyrus and other sites put it: the Atom entry's authors, the `By ...` line of the
article's Markdown twin, `<meta name="author">`, JSON-LD `author`, and elements whose class names a byline or author.
Never from the article body, where Ryan may only be mentioned.

A source that cannot be read is skipped with a warning, so one publication being down never breaks the build.
"""

import json
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ElementTree
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scripts" / "syndication.json"
OUTPUT = ROOT / "content" / "syndicated"
ATOM = "{http://www.w3.org/2005/Atom}"
USER_AGENT = "ryanalynporter.com syndication (+https://www.ryanalynporter.com/)"
TIMEOUT_SECONDS = 20
PARALLEL_FETCHES = 8

META_TAG_PATTERN = re.compile(r"<meta\s[^>]*>", re.I)
ATTRIBUTE_PATTERN = re.compile(r'([a-zA-Z:_-]+)\s*=\s*"([^"]*)"')
JSON_LD_PATTERN = re.compile(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', re.I | re.S)
BYLINE_ELEMENT_PATTERN = re.compile(r'<(\w+)[^>]*class="[^"]*\b(?:byline|author)[^"]*"[^>]*>(.*?)</\1>', re.I | re.S)
TWIN_BYLINE_PATTERN = re.compile(r"^By (.+)$", re.M)
SLUG_UNSAFE_PATTERN = re.compile(r"[^a-z0-9-]+")
TAG_PATTERN = re.compile(r"<[^>]+>")


def _fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def _fetch_text(url):
    try:
        return _fetch(url).decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 - a missing page only means less to go on
        return ""


def _plain(markup):
    return unescape(TAG_PATTERN.sub(" ", markup)).strip()


def _twin_url(article_url):
    """The Markdown twin Papyrus publishes beside every page."""
    path = urlparse(article_url).path
    if path.endswith("/"):
        return article_url + "index.md"
    return re.sub(r"\.html$", ".md", article_url) if path.endswith(".html") else article_url + ".md"


def _json_ld_authors(html):
    names = []
    for block in JSON_LD_PATTERN.findall(html):
        try:
            documents = json.loads(block)
        except ValueError:
            continue
        for document in documents if isinstance(documents, list) else [documents]:
            authors = document.get("author") if isinstance(document, dict) else None
            for author in authors if isinstance(authors, list) else [authors]:
                if isinstance(author, dict):
                    names.append(str(author.get("name", "")))
                elif author:
                    names.append(str(author))
    return names


def _page_facts(article_url):
    """The article's og:image and every byline it states, from its HTML page and its Markdown twin."""
    html = _fetch_text(article_url)
    image = None
    bylines = []
    for tag in META_TAG_PATTERN.findall(html):
        attributes = {name.lower(): value for name, value in ATTRIBUTE_PATTERN.findall(tag)}
        if attributes.get("property") == "og:image" and attributes.get("content") and image is None:
            image = urljoin(article_url, unescape(attributes["content"]))
        if attributes.get("name") == "author" and attributes.get("content"):
            bylines.append(unescape(attributes["content"]))
    bylines += _json_ld_authors(html)
    bylines += [_plain(content) for _, content in BYLINE_ELEMENT_PATTERN.findall(html)]
    bylines += TWIN_BYLINE_PATTERN.findall(_fetch_text(_twin_url(article_url)))
    return image, bylines


def _slug(url):
    path = urlparse(url).path.strip("/") or "index"
    return SLUG_UNSAFE_PATTERN.sub("-", path.lower().replace("/", "--")).strip("-")


def _text(element, name):
    value = element.findtext(ATOM + name)
    return _plain(value) if value else ""


def _from_search_index(source):
    entries = json.loads(_fetch(urljoin(source["site"], "/_data/search-index.json")))
    for entry in entries:
        yield {
            "title": entry.get("title", ""),
            "url": urljoin(source["site"], entry["url"]),
            "date": str(entry.get("date", ""))[:10],
            "description": entry.get("summary", ""),
            "authors": [],
        }


def _from_feed(source):
    feed = ElementTree.fromstring(_fetch(urljoin(source["site"], "/atom.xml")))
    for entry in feed.findall(ATOM + "entry"):
        link = next((element.get("href") for element in entry.findall(ATOM + "link") if element.get("rel", "alternate") == "alternate"), None)
        if not link:
            continue
        yield {
            "title": _text(entry, "title"),
            "url": urljoin(source["site"], link),
            "date": (_text(entry, "published") or _text(entry, "updated"))[:10],
            "description": _text(entry, "summary"),
            "authors": [author.findtext(ATOM + "name") or "" for author in entry.findall(ATOM + "author")],
        }


def _articles(source):
    try:
        return list(_from_search_index(source))
    except Exception:  # noqa: BLE001 - not every site publishes the search index; the feed is the fallback
        return list(_from_feed(source))


def _write(source, article, image):
    front_matter = {
        "title": article["title"],
        "url": article["url"],
        "date": article["date"],
        "description": article["description"] if article["description"] != article["title"] else "",
        "image": image,
        "publication": source["key"],
        "publicationName": source["name"],
        "domain": urlparse(source["site"]).netloc,
    }
    lines = [f"{name}: {json.dumps(value, ensure_ascii=False)}" for name, value in front_matter.items() if value]
    target = OUTPUT / source["key"] / f"{_slug(article['url'])}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("---\n" + "\n".join(lines) + "\n---\n", encoding="utf-8")


def main():
    config = json.loads(CONFIG.read_text())
    author_pattern = re.compile(config["authorPattern"], re.I)
    shutil.rmtree(OUTPUT, ignore_errors=True)
    for source in config["sources"]:
        try:
            articles = _articles(source)
        except Exception as error:  # noqa: BLE001 - see the module docstring
            print(f"warning: skipped {source['name']} ({source['site']}): {error}", file=sys.stderr)
            continue
        with ThreadPoolExecutor(PARALLEL_FETCHES) as pool:
            facts = list(pool.map(lambda article: _page_facts(article["url"]), articles))
        kept = 0
        for article, (image, bylines) in zip(articles, facts):
            if author_pattern.search(" | ".join(article["authors"] + bylines)):
                _write(source, article, image)
                kept += 1
        print(f"{source['name']}: {kept} of {len(articles)} articles have Ryan's byline")


if __name__ == "__main__":
    main()
