#!/usr/bin/env python3
"""Build the public wiki into the GitHub Pages site artifact.

Usage: python scripts/build_docs.py WIKI_CHECKOUT SITE_OUTPUT
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


WIKI_URL = "https://github.com/greensh16/hpc_dashboard_public/wiki"
SITE_URL = "https://hpc-dash.au"


def page_url(stem: str) -> str:
    return "/docs/" if stem == "Home" else f"/docs/{stem.lower()}/"


class RewriteWikiLinks(Treeprocessor):
    def __init__(self, md: markdown.Markdown, pages: set[str], assets: set[str]):
        super().__init__(md)
        self.pages = pages
        self.assets = assets

    def run(self, root):
        for element in root.iter():
            if element.tag == "a" and "href" in element.attrib:
                element.set("href", self.rewrite(element.get("href", "")))
            elif element.tag == "img" and "src" in element.attrib:
                element.set("src", self.rewrite(element.get("src", "")))
        return root

    def rewrite(self, address: str) -> str:
        parts = urlsplit(address)
        if parts.scheme or parts.netloc or address.startswith(("/", "#", "mailto:")):
            return address
        path = unquote(parts.path)
        stem = path[:-3] if path.endswith(".md") else path
        match = next((page for page in self.pages if page.casefold() == stem.casefold()), None)
        suffix = f"#{quote(unquote(parts.fragment), safe='-._~')}" if parts.fragment else ""
        if match:
            return page_url(match) + suffix
        if path in self.assets:
            return "/docs/" + quote(path, safe="/-._~") + suffix
        raise ValueError(f"Wiki link target does not exist: {address}")


class WikiLinksExtension(Extension):
    def __init__(self, pages: set[str], assets: set[str]):
        self.pages = pages
        self.assets = assets
        super().__init__()

    def extendMarkdown(self, md):
        md.treeprocessors.register(RewriteWikiLinks(md, self.pages, self.assets), "wiki_links", 15)


def sidebar_entries(sidebar: str, pages: set[str]) -> list[tuple[str, list[tuple[str, str]]]]:
    sections: list[tuple[str, list[tuple[str, str]]]] = [("Overview", [("Home", "Home")])]
    for line in sidebar.splitlines():
        heading = re.fullmatch(r"\*\*([^*\[]+)\*\*", line.strip())
        link = re.fullmatch(r"- \[([^]]+)\]\(([^)]+)\)", line.strip())
        if heading:
            sections.append((heading.group(1), []))
        elif link:
            label, stem = link.groups()
            if stem not in pages:
                raise ValueError(f"Sidebar page does not exist: {stem}")
            sections[-1][1].append((label, stem))
    listed = {stem for _, links in sections for _, stem in links}
    if missing := pages - listed:
        sections.append(("More", [(stem.replace("-", " "), stem) for stem in sorted(missing)]))
    return sections


def render_nav(sections: list[tuple[str, list[tuple[str, str]]]], current: str) -> str:
    chunks = []
    for heading, links in sections:
        items = "".join(
            f'<a href="{page_url(stem)}"{(" aria-current=\"page\"" if stem == current else "")}>{html.escape(label)}</a>'
            for label, stem in links
        )
        chunks.append(f'<div class="docs-nav-group"><h2>{html.escape(heading)}</h2>{items}</div>')
    return "".join(chunks)


def render_page(stem: str, body: str, nav: str, prev_next: str) -> str:
    title = "Documentation" if stem == "Home" else stem.replace("-", " ")
    page_address = SITE_URL + page_url(stem)
    return f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#0a1018" />
    <meta name="description" content="{html.escape(title)} — HPC Dashboard documentation." />
    <link rel="canonical" href="{page_address}" />
    <meta property="og:type" content="article" />
    <meta property="og:title" content="{html.escape(title)} — HPC Dashboard" />
    <meta property="og:url" content="{page_address}" />
    <link rel="icon" href="/favicon.png" type="image/png" />
    <link rel="stylesheet" href="/styles.css" />
    <link rel="stylesheet" href="/docs.css" />
    <title>{html.escape(title)} — HPC Dashboard</title>
  </head>
  <body class="docs-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header"><div class="wrap header-inner">
      <a class="brand" href="/" aria-label="HPC Dashboard home"><img class="brand-icon" src="/logo.png" alt="" aria-hidden="true" /><span>HPC<span class="brand-light"> Dashboard</span></span></a>
      <nav class="nav" aria-label="Main navigation"><a href="/">Overview</a><a href="/docs/" aria-current="page">Docs</a><a href="{WIKI_URL}">GitHub wiki <span aria-hidden="true">↗</span></a></nav>
      <a class="header-cta" href="https://github.com/greensh16/hpc_dashboard_public/releases/latest">Download <span aria-hidden="true">↗</span></a>
    </div></header>
    <main id="main" class="docs-shell wrap">
      <aside class="docs-sidebar"><nav aria-label="Documentation">{nav}</nav><a class="docs-source" href="{WIKI_URL}/{stem}">View source on GitHub ↗</a></aside>
      <div class="docs-content">
        <details class="docs-mobile-nav"><summary>Browse documentation</summary><nav aria-label="Documentation">{nav}</nav></details>
        <p class="docs-breadcrumb"><a href="/">HPC Dashboard</a><span aria-hidden="true">/</span><a href="/docs/">Docs</a>{'' if stem == 'Home' else '<span aria-hidden="true">/</span>' + html.escape(title)}</p>
        <article class="docs-article">{body}</article>
        <nav class="docs-pagination" aria-label="Documentation pages">{prev_next}</nav>
        <p class="docs-edit">Found an error? <a href="{WIKI_URL}/{stem}/_edit">Edit this page on GitHub ↗</a></p>
      </div>
    </main>
    <footer class="footer"><div class="wrap footer-bottom docs-footer"><span>© 2026 Sam Green · Apache 2.0</span><span><a href="/">Home</a> · <a href="{WIKI_URL}">GitHub wiki</a> · <a href="https://github.com/greensh16/hpc_dashboard_public/issues">Report an issue</a></span></div></footer>
  </body>
</html>
'''


def build(wiki_dir: Path, site_dir: Path) -> None:
    source_files = sorted(wiki_dir.glob("*.md"))
    pages = {path.stem for path in source_files if not path.stem.startswith("_")}
    if "Home" not in pages:
        raise ValueError("Wiki has no Home.md")
    asset_files = [path for path in wiki_dir.rglob("*") if path.is_file() and path.suffix != ".md" and ".git" not in path.parts]
    assets = {path.relative_to(wiki_dir).as_posix() for path in asset_files}
    sections = sidebar_entries((wiki_dir / "_Sidebar.md").read_text(encoding="utf-8"), pages)
    order = [stem for _, links in sections for _, stem in links]
    docs_dir = site_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for asset in asset_files:
        target = docs_dir / asset.relative_to(wiki_dir)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(asset, target)
    for index, stem in enumerate(order):
        source = wiki_dir / f"{stem}.md"
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", WikiLinksExtension(pages, assets)])
        body = md.convert(source.read_text(encoding="utf-8"))
        nav = render_nav(sections, stem)
        previous = f'<a href="{page_url(order[index - 1])}"><small>← Previous</small>{html.escape(order[index - 1].replace("-", " "))}</a>' if index else "<span></span>"
        following = f'<a href="{page_url(order[index + 1])}"><small>Next →</small>{html.escape(order[index + 1].replace("-", " "))}</a>' if index + 1 < len(order) else "<span></span>"
        output = docs_dir / ("index.html" if stem == "Home" else f"{stem.lower()}/index.html")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_page(stem, body, nav, previous + following), encoding="utf-8")
    print(f"Built {len(order)} wiki pages in {docs_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: build_docs.py WIKI_CHECKOUT SITE_OUTPUT")
    build(Path(sys.argv[1]), Path(sys.argv[2]))
