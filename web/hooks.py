"""ryanalynporter.com on Papyrus's standard Markus front end.

Settings, URLs, head, feeds, sitemap and tag pages come from ``projection.json`` and Papyrus core. This module is the
site's look: the masthead and footer, the home, Writing, Building and Background pages, the article page, and the
cards that mix Ryan's own posts with articles syndicated from the Anthus publications (``scripts/syndicate.py``).
"""

import re
from datetime import date
from html import escape

from papyrus_content.projection.standard.fragments import article_body
from papyrus_content.projection.standard.urls import slugify_tag

import site_data as data

NAVIGATION = (("Writing", "/writing/"), ("Building", "/building/"), ("Background", "/background/"))
PERSONAL = {"key": "personal", "label": "This site", "domain": "ryanalynporter.com"}
PUBLICATION_ORDER = ("anthus", "threat", "shipped", "distinctive", "personal")
FEED_CARD_COUNT = 6
FEED_CARDS_PER_PUBLICATION = 2
FEED_ROW_COUNT = 6
FEED_OWN_ROW_COUNT = 4
WRITING_CARD_COUNT = 12
WRITING_CARDS_PER_PUBLICATION = 3
RELATED_COUNT = 3

FILE_CAPTION_PATTERN = re.compile(r"<p><strong>File:</strong> <code>(?P<name>[^<]+)</code></p>\s*(?P<pre><pre>.*?</pre>)", re.S)
DEMO_PATTERN = re.compile(r'<p><a href="(?P<src>/super-minimal-ads/banner\.html[^"]*)">Live demo:[^<]*</a></p>')


# ---------------------------------------------------------------- entries


def _publication(entry):
    if entry.section is not None and entry.section.name == "syndicated":
        return {"key": entry.data.get("publication", "anthus"), "label": entry.data.get("publicationName", ""), "domain": entry.data.get("domain", "")}
    return PERSONAL


def _href(entry):
    return entry.url or entry.link or "#"


def _is_external(entry):
    return entry.url is None


def _date(entry):
    try:
        return date.fromisoformat(entry.date[:10])
    except ValueError:
        return None


def _month(entry):
    published = _date(entry)
    return published.strftime("%b %Y") if published else ""


def _day(entry):
    published = _date(entry)
    return published.strftime("%b %-d") if published else ""


def _long_date(entry):
    published = _date(entry)
    return published.strftime("%B %-d, %Y") if published else ""


def _articles(page):
    return tuple(entry for entry in page.entries if entry.type == "article")


def _balanced(entries, count, per_publication):
    """The newest ``count`` entries, at most ``per_publication`` from any one publication, so no burst of posts takes over."""
    chosen = []
    taken = {}
    for entry in entries:
        key = _publication(entry)["key"]
        if len(chosen) < count and taken.get(key, 0) < per_publication:
            chosen.append(entry)
            taken[key] = taken.get(key, 0) + 1
    return chosen


def _link_attributes(entry):
    return f' href="{escape(_href(entry), quote=True)}"' + (' rel="noopener"' if _is_external(entry) else "")


# ---------------------------------------------------------------- cards and rows


def _preview(entry, publication):
    if entry.image:
        return f'<img class="rap-preview" src="{escape(entry.image, quote=True)}" alt="" loading="lazy">'
    return f'<div class="rap-preview rap-preview--blank" aria-hidden="true">{escape(publication["domain"])}</div>'


def _card(entry, heading="h3"):
    publication = _publication(entry)
    blurb = f'<p class="rap-card-blurb">{escape(entry.summary_text)}</p>' if entry.summary_text else ""
    return (
        f'<a class="rap-card rap-pub--{publication["key"]}" data-publication="{publication["key"]}"{_link_attributes(entry)}>'
        f"{_preview(entry, publication)}"
        f'<span class="rap-card-meta"><span class="rap-source">{escape(publication["label"])}</span>'
        f'<span>{escape(publication["domain"])} · {_month(entry)}</span></span>'
        f'<{heading} class="rap-card-title">{escape(entry.title)}</{heading}>{blurb}</a>'
    )


def _feature(entry):
    publication = _publication(entry)
    return (
        f'<a class="rap-feature rap-pub--{publication["key"]}"{_link_attributes(entry)}>'
        f"{_preview(entry, publication)}"
        '<span class="rap-feature-text">'
        f'<span class="rap-feature-meta"><span class="rap-badge">{escape(publication["label"])}</span>'
        f'<span>{escape(publication["domain"])} · {_month(entry)}</span></span>'
        f'<h2 class="rap-feature-title">{escape(entry.title)}</h2>'
        + (f'<p class="rap-feature-blurb">{escape(entry.summary_text)}</p>' if entry.summary_text else "")
        + f'<span class="rap-feature-cta">Read on {escape(publication["domain"])}{" ↗" if _is_external(entry) else " →"}</span>'
        "</span></a>"
    )


def _row(entry, date_text):
    publication = _publication(entry)
    return (
        f'<a class="rap-row" data-publication="{publication["key"]}"{_link_attributes(entry)}>'
        f'<span class="rap-row-date">{escape(date_text)}</span>'
        f'<span class="rap-row-title">{escape(entry.title)}</span>'
        f'<span class="rap-row-domain">{escape(publication["domain"])}</span></a>'
    )


def _grid(cards, class_name="rap-grid"):
    return f'<div class="{class_name}">{"".join(cards)}</div>'


# ---------------------------------------------------------------- chrome


def _stripe():
    return '<div class="rap-stripe" aria-hidden="true"><i></i><i></i><i></i><i></i></div>'


def _current(page, href):
    return ' aria-current="page"' if page.path.strip("/") == href.strip("/") else ""


def _navigation(page, pills):
    links = "".join(f'<a href="{href}"{_current(page, href)}>{label}</a>' for label, href in NAVIGATION)
    return (
        f'<nav class="rap-nav{" rap-nav--pills" if pills else ""}" aria-label="Site">{links}'
        f'<a class="rap-nav-external" href="{data.ANTHUS_PROFILE_URL}">Anthus ↗</a></nav>'
    )


def _is_home(page):
    return page.kind == "custom" and page.custom_id == "home"


def masthead(page):
    if _is_home(page):
        return (
            f'<header class="rap-masthead rap-masthead--home">{_stripe()}<div class="rap-wrap rap-hero">'
            f'<div class="rap-hero-top"><h1 class="rap-hero-name">Ryan Alyn Porter</h1>{_navigation(page, pills=False)}</div>'
            '<div class="rap-hero-bottom">'
            '<p class="rap-hero-tagline">Systems that improve themselves, <em>and the safeguards that keep them honest.</em></p>'
            '<div class="rap-hero-intro"><p class="rap-eyebrow">CTO · Applied AI · Miami Beach</p>'
            f"<p>{escape(data.HOME_INTRODUCTION)}</p></div></div></div></header>"
        )
    return (
        f'<header class="rap-masthead">{_stripe()}<div class="rap-wrap rap-masthead-bar">'
        f'<a class="rap-wordmark" href="/">Ryan Alyn Porter</a>{_navigation(page, pills=True)}</div></header>'
    )


def footer(page):
    return (
        '<div class="rap-wrap rap-footer"><span>© 2009–2026 Ryan Alyn Porter · Miami Beach</span>'
        f'<span class="rap-footer-links"><a href="{data.GITHUB_URL}">GitHub</a><a href="{data.LINKEDIN_URL}">LinkedIn</a>'
        '<a href="/atom.xml">RSS</a></span></div>'
    )


def body_class(page):
    if page.kind == "custom":
        return f"rap-page--{page.custom_id}"
    return f"rap-page--{page.kind.replace('_', '-')}"


# ---------------------------------------------------------------- pages


def _section_heading(title, link_label=None, href=None):
    link = f'<a class="rap-section-link" href="{href}">{escape(link_label)}</a>' if href else ""
    return f'<div class="rap-section-heading"><h2>{escape(title)}</h2>{link}</div>'


def _pill_links(links):
    return '<p class="rap-pills">' + "".join(f'<a class="{class_name}" href="{href}">{escape(label)}</a>' for label, href, class_name in links) + "</p>"


def _stats(stats):
    items = "".join(f'<div class="rap-stat"><span class="rap-stat-value">{escape(value)}</span><span>{escape(label)}</span></div>' for value, label in stats)
    return f'<div class="rap-stats">{items}</div>'


def _home(page):
    articles = _articles(page)
    with_images = [entry for entry in articles if entry.image]
    feature = with_images[0] if with_images else None
    syndicated = [entry for entry in articles if entry is not feature and _publication(entry)["key"] != PERSONAL["key"]]
    cards = _balanced(syndicated, FEED_CARD_COUNT, FEED_CARDS_PER_PUBLICATION)
    shown = {entry.item_id for entry in cards} | ({feature.item_id} if feature else set())
    remaining = [entry for entry in articles if entry.item_id not in shown]
    own = [entry for entry in remaining if _publication(entry)["key"] == PERSONAL["key"]][:FEED_OWN_ROW_COUNT]
    others = [entry for entry in remaining if _publication(entry)["key"] != PERSONAL["key"]][: FEED_ROW_COUNT - len(own)]
    rows = sorted(others + own, key=lambda entry: entry.sort_key, reverse=True)

    groups = "".join(
        f'<div class="rap-panel"><p class="rap-eyebrow">{escape(label)}</p>'
        + "".join(f'<a class="rap-entry" href="/building/"><span class="rap-entry-name">{escape(name)}</span><span>{escape(blurb)}</span></a>' for name, blurb in items)
        + "</div>"
        for label, items in data.HOME_GROUPS
    )
    roles = "".join(
        f'<div class="rap-role"><span class="rap-role-years">{escape(years)}</span><span><strong>{escape(org)}</strong><span>{escape(title)}</span></span></div>'
        for years, org, title in data.HOME_ROLES
    )
    background = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in data.HOME_BACKGROUND)
    links = _pill_links((
        ("GitHub", data.GITHUB_URL, "rap-pill"),
        ("LinkedIn", data.LINKEDIN_URL, "rap-pill"),
        ("anth.us/ryan", data.ANTHUS_PROFILE_URL, "rap-pill"),
        ("Résumé (PDF)", data.RESUME_URL, "rap-pill rap-pill--yellow"),
    ))
    return (
        '<section id="writing" class="rap-band"><div class="rap-wrap rap-stack">'
        + (_feature(feature) if feature else "")
        + _grid(_card(entry) for entry in cards)
        + '<div class="rap-rows">' + "".join(_row(entry, _month(entry)) for entry in rows)
        + '<a class="rap-rows-more" href="/writing/">All writing →</a></div></div></section>'
        '<section id="building" class="rap-band rap-band--green"><div class="rap-wrap rap-stack">'
        + _section_heading("What I’m building", "Everything I’m building →", "/building/")
        + f'<div class="rap-columns">{groups}</div></div></section>'
        '<section id="background" class="rap-band rap-band--dark"><div class="rap-wrap rap-stack">'
        + _section_heading("Background", "Full background →", "/background/")
        + _stats(data.HOME_STATS)
        + f'<div class="rap-split"><div class="rap-prose">{background}{links}</div><div class="rap-roles">{roles}</div></div></div></section>'
    )


def _page_title(title, introduction):
    return f'<div class="rap-page-title"><h1>{escape(title)}</h1><p>{escape(introduction)}</p></div>'


def _writing(page):
    articles = _articles(page)
    cards = _balanced([entry for entry in articles if _publication(entry)["key"] != PERSONAL["key"]], WRITING_CARD_COUNT, WRITING_CARDS_PER_PUBLICATION)
    shown = {entry.item_id for entry in cards}
    listed = [entry for entry in articles if entry.item_id not in shown]

    counts = {}
    labels = {}
    for entry in articles:
        publication = _publication(entry)
        counts[publication["key"]] = counts.get(publication["key"], 0) + 1
        labels[publication["key"]] = publication["label"]
    filters = [("all", "All", len(articles))] + [(key, labels[key], counts[key]) for key in PUBLICATION_ORDER if counts.get(key)]
    buttons = "".join(
        f'<button type="button" data-filter="{key}" aria-pressed="{"true" if key == "all" else "false"}">{escape(label)} · {count}</button>'
        for key, label, count in filters
    )

    years = {}
    for entry in listed:
        years.setdefault(entry.date[:4], []).append(entry)
    year_groups = "".join(
        f'<div class="rap-year" data-year="{year}"><p class="rap-year-label">{year}</p><div class="rap-year-rows">'
        + "".join(_row(entry, _day(entry)) for entry in entries)
        + "</div></div>"
        for year, entries in years.items()
    )
    return (
        '<div class="rap-wrap rap-stack rap-page">'
        + _page_title("Writing", "Articles from this site and the Anthus publications, newest first. Each one opens where it was published.")
        + f'<div class="rap-filters" role="group" aria-label="Filter by publication" hidden>{buttons}</div>'
        + _grid((_card(entry, heading="h2") for entry in cards), "rap-grid rap-writing-cards")
        + '<p class="rap-empty" hidden>No recent articles from this publication yet.</p>'
        + f'<div class="rap-years">{year_groups}</div></div>'
    )


def _building(page):
    products = "".join(
        f'<a class="rap-product rap-pub--{product["tint"]}" href="{product["url"]}">'
        f'<div class="rap-preview rap-preview--blank" aria-hidden="true">{escape(product["name"])}</div>'
        f'<span class="rap-tags"><span class="rap-tag rap-tag--yellow">{escape(product["status"])}</span><span class="rap-tag">{escape(product["role"])}</span></span>'
        f'<h2>{escape(product["name"])}</h2><p>{escape(product["description"])}</p>'
        f'<span class="rap-product-link">{escape(product["link_label"])} ↗</span></a>'
        for product in data.PRODUCTS
    )
    solutions = "".join(
        f'<a class="rap-tile" href="https://anth.us/"><span class="rap-tile-name">{escape(name)}</span><span>{escape(blurb)}</span></a>'
        for name, blurb in data.SOLUTIONS
    )
    repositories = "".join(
        f'<a class="rap-tile rap-tile--dark" href="{data.GITHUB_URL}/{name}">'
        f'<span class="rap-tile-heading"><span class="rap-tile-name">{escape(name)}</span>'
        + ('<span class="rap-tag rap-tag--yellow">In production</span>' if in_production else "")
        + f'</span><span>{escape(blurb)}</span><span class="rap-tile-foot">AnthusAI/{escape(name)}</span></a>'
        for name, in_production, blurb in data.OPEN_SOURCE
    )
    systems = "".join(
        f'<div class="rap-system"><span class="rap-muted">{escape(years)}</span><span class="rap-tile-name">{escape(name)}</span>'
        f'<span>{escape(description)}</span><span class="rap-tag rap-tag--green">{escape(figure)}</span></div>'
        for years, name, figure, description in data.PRODUCTION_SYSTEMS
    )
    return (
        '<div class="rap-wrap rap-stack rap-page">'
        + _page_title("Building", "Products, AI solutions and open-source platforms out of the lab. Plexus, Tactus and Biblicus run in commercial production.")
        + f'<p class="rap-eyebrow">Products</p><div class="rap-products">{products}</div></div>'
        '<section class="rap-band rap-band--green"><div class="rap-wrap rap-stack">'
        + _section_heading("AI solutions", "From Anthus AI Solutions ↗", "https://anth.us/")
        + f'<div class="rap-tiles">{solutions}</div></div></section>'
        '<section class="rap-band rap-band--dark"><div class="rap-wrap rap-stack">'
        + _section_heading("Open source", "github.com/AnthusAI ↗", data.GITHUB_URL)
        + f'<div class="rap-tiles">{repositories}</div></div></section>'
        '<section class="rap-band rap-band--mint"><div class="rap-wrap rap-stack">'
        + _section_heading("Systems I’ve run in production")
        + f'<div class="rap-systems">{systems}</div></div></section>'
    )


def _background(page):
    roles = "".join(
        f'<div class="rap-experience"><div class="rap-experience-head"><span class="rap-tag rap-tag--mint">{escape(years)}</span>'
        f'<span class="rap-tile-name">{escape(org)}</span><span class="rap-muted rap-strong">{escape(title)}</span></div>'
        f'<ul>{"".join(f"<li>{escape(highlight)}</li>" for highlight in highlights)}</ul></div>'
        for years, org, title, highlights in data.EXPERIENCE
    )
    education = "".join(f'<div class="rap-tile rap-tile--static"><span class="rap-tile-name">{escape(title)}</span><span>{escape(detail)}</span></div>' for title, detail in data.EDUCATION)
    expertise = "".join(
        f'<div class="rap-panel"><p class="rap-eyebrow">{escape(label)}</p><p class="rap-skills">{"".join(f"<span>{escape(skill)}</span>" for skill in skills)}</p></div>'
        for label, skills in data.EXPERTISE
    )
    links = _pill_links((
        ("Download résumé (PDF)", data.RESUME_URL, "rap-pill rap-pill--yellow"),
        ("LinkedIn", data.LINKEDIN_URL, "rap-pill rap-pill--mint"),
        ("GitHub", data.GITHUB_URL, "rap-pill rap-pill--mint"),
    ))
    return (
        '<div class="rap-wrap rap-page rap-background-intro">'
        f'<div><p class="rap-eyebrow">{escape(data.BACKGROUND_EYEBROW)}</p><h1>Background</h1></div>'
        f'<div class="rap-prose"><p>{escape(data.BACKGROUND_SUMMARY)}</p>{links}</div></div>'
        f'<section class="rap-band rap-band--dark" aria-label="By the numbers"><div class="rap-wrap">{_stats(data.BACKGROUND_STATS)}</div></section>'
        f'<section class="rap-band"><div class="rap-wrap rap-stack"><h2 class="rap-h2">Experience</h2>{roles}</div></section>'
        f'<section class="rap-band rap-band--green"><div class="rap-wrap rap-stack"><h2 class="rap-h2">Education and early research</h2><div class="rap-tiles">{education}</div></div></section>'
        f'<section class="rap-band rap-band--mint"><div class="rap-wrap rap-stack"><h2 class="rap-h2">Expertise</h2><div class="rap-columns">{expertise}</div></div></section>'
    )


def _post(page):
    entry = page.entry
    tags = "".join(f'<a class="rap-tag rap-tag--green" href="/tags/{slugify_tag(tag)}/">{escape(tag)}</a>' for tag in entry.tags)
    lede = f'<p class="rap-lede">{escape(entry.summary_text)}</p>' if entry.summary_text else ""
    related = [other for other in _articles(page) if other.image and other.item_id != entry.item_id][:RELATED_COUNT]
    author_links = _pill_links((
        ("Background", "/background/", "rap-pill"),
        ("What I’m building", "/building/", "rap-pill"),
        ("GitHub", data.GITHUB_URL, "rap-pill"),
    ))
    return (
        '<article class="rap-article">'
        '<a class="rap-back" href="/writing/">← All writing</a>'
        f'<p class="rap-tags"><time class="rap-tag rap-tag--white" datetime="{escape(entry.date[:10], quote=True)}">{_long_date(entry)}</time>{tags}</p>'
        f'<h1 class="rap-article-title">{escape(entry.title)}</h1>{lede}{page.page_actions}'
        f'<div class="rap-article-body">{article_body(page.fragment)}</div></article>'
        '<section class="rap-band rap-band--dark" aria-label="About the author"><div class="rap-narrow rap-stack">'
        f'<p class="rap-author-name">Ryan Alyn Porter</p><p class="rap-dark-muted">{escape(data.AUTHOR_BLURB)}</p>{author_links}</div></section>'
        '<section class="rap-band rap-band--mint" aria-label="More writing"><div class="rap-wrap rap-stack">'
        f'<h2 class="rap-h2">More writing</h2>{_grid(_card(other) for other in related)}</div></section>'
    )


def _tag(page):
    view = page.listing
    rows = "".join(_row(entry, _month(entry)) for entry in view.entries)
    return (
        '<div class="rap-wrap rap-stack rap-page">'
        + _page_title(page.title, "Posts from this site with this tag.")
        + f'<div class="rap-rows">{rows}<a class="rap-rows-more" href="/tags/">All tags →</a></div></div>'
    )


def _tags(page):
    links = "".join(f'<a class="rap-tag rap-tag--white" href="/tags/{slugify_tag(tag)}/">{escape(tag)} · {len(found)}</a>' for tag, found in sorted(page.tags.items(), key=lambda pair: pair[0].casefold()))
    return f'<div class="rap-wrap rap-stack rap-page">{_page_title("Tags", "Topics of the posts on this site.")}<p class="rap-tags">{links}</p></div>'


def _not_found(page):
    return (
        '<div class="rap-wrap rap-stack rap-page">'
        + _page_title("Page not found", "That page is not here. It may have moved when the site was rebuilt.")
        + _pill_links((("Home", "/", "rap-pill rap-pill--dark"), ("All writing", "/writing/", "rap-pill rap-pill--mint")))
        + "</div>"
    )


CUSTOM_PAGES = {"home": _home, "writing": _writing, "building": _building, "background": _background}


def main(page):
    if page.kind == "custom" and page.custom_id in CUSTOM_PAGES:
        return CUSTOM_PAGES[page.custom_id](page)
    if page.kind == "item" and page.entry is not None:
        return _post(page)
    if page.kind == "tag":
        return _tag(page)
    if page.kind == "tags":
        return _tags(page)
    if page.kind == "not_found":
        return _not_found(page)
    return None


# ---------------------------------------------------------------- article bodies


def item_decorator(html, summary):
    """Octopress file captions become a code-block header; the super-minimal demo becomes its live iframe."""
    html = FILE_CAPTION_PATTERN.sub(
        lambda match: f'<figure class="rap-code"><figcaption>{match.group("name")}</figcaption>{match.group("pre")}</figure>', html
    )
    return DEMO_PATTERN.sub(
        lambda match: f'<iframe class="rap-demo" title="Super Minimal Ads demo banner" src="{match.group("src")}" width="640" height="79"></iframe>', html
    )
