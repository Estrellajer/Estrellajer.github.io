#!/usr/bin/env python3
"""Parse browser bookmarks HTML file and generate config.yaml."""

import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse
from pathlib import Path


class BookmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.entries = []  # list of (name, url, category)
        self.current_category = None
        self.in_dl = 0
        self.in_h3 = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "h3":
            self.in_h3 = True
        elif tag == "dl":
            self.in_dl += 1
        elif tag == "a" and self.in_dl > 0:
            href = attrs_dict.get("href", "")
            name = ""
            # We'll get the name from handle_data
            self.current_link = {"url": href}

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_h3 = False
        elif tag == "dl":
            self.in_dl -= 1

    def handle_data(self, data):
        if self.in_h3 and data.strip():
            self.current_category = data.strip()
        if hasattr(self, "current_link") and self.current_link:
            name = data.strip()
            if name and self.current_link["url"]:
                # Skip non-http URLs
                if self.current_link["url"].startswith("http"):
                    category = self.current_category or "uncategorized"
                    # Clean category name
                    category = re.sub(r'[^\w\-一-鿿]', '', category)
                    self.entries.append((name, self.current_link["url"], category))
            self.current_link = None


def classify_url(url: str) -> str:
    """Auto-classify a URL to determine extraction strategy."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if "github.io" in domain:
        return "github_pages"
    elif "scholar.google" in domain:
        return "google_scholar"
    elif "zhihu.com" in domain:
        return "zhihu"
    elif "substack.com" in domain or "substack" in domain:
        return "substack"
    elif "cnblogs.com" in domain:
        return "cnblogs"
    elif "csdn.net" in domain:
        return "csdn"
    elif "openreview.net" in domain:
        return "openreview"
    elif "huggingface.co" in domain:
        return "huggingface"
    elif "sites.google.com" in domain:
        return "google_sites"
    elif "research.google" in domain:
        return "google_blog"
    elif "kexue.fm" in domain:
        return "kexuefm"
    else:
        return "personal_website"


def guess_selectors(site_type: str) -> list:
    """Guess CSS selectors for content extraction based on site type."""
    defaults = {
        "github_pages": ["article", "main", ".post-content", ".entry-content", ".content"],
        "google_scholar": ["#gsc_a_b", "#gsc_art", "#gsc_prf", "table"],
        "zhihu": [".RichText", ".ContentItem", ".Post-content", "article"],
        "substack": ["article", ".main", ".post", ".substack"],
        "cnblogs": ["#post_detail", "article", ".post", ".main"],
        "csdn": ["#article_content", "article", ".main"],
        "openreview": [".main", ".profile", ".content"],
        "huggingface": ["main", ".prose", ".content"],
        "google_sites": [".main-content", "#content", ".sites-embed"],
        "google_blog": ["article", ".post", ".main"],
        "kexuefm": ["article", ".entry-content", ".content"],
        "personal_website": ["main", ".content", "#content", "article"],
    }
    return defaults.get(site_type, defaults["personal_website"])


def generate_config(entries, output_path="config.yaml"):
    """Generate config.yaml from parsed bookmark entries."""
    lines = []
    lines.append("# Scholar Monitor Configuration")
    lines.append("# Auto-generated from bookmarks. Edit selectors per-site for best results.")
    lines.append("")
    lines.append("scholars:")

    for name, url, category in entries:
        site_type = classify_url(url)
        selectors = guess_selectors(site_type)

        lines.append(f"")
        lines.append(f"  - name: \"{name}\"")
        lines.append(f"    url: \"{url}\"")
        lines.append(f"    category: \"{category}\"")
        lines.append(f"    site_type: \"{site_type}\"")
        lines.append(f"    selectors:")
        for sel in selectors:
            lines.append(f"      - \"{sel}\"")
        lines.append(f"    remove_selectors:")
        lines.append(f"      - \"script\"")
        lines.append(f"      - \"style\"")
        lines.append(f"      - \"nav\"")
        lines.append(f"      - \"footer\"")
        lines.append(f"      - \"header\"")
        lines.append(f"      - \"aside\"")
        lines.append(f"      - \".sidebar\"")
        lines.append(f"      - \".comments\"")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {output_path} with {len(entries)} scholars")
    return len(entries)


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_config.py <bookmarks.html> [output.yaml]")
        sys.exit(1)

    html_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "config.yaml"

    with open(html_path, encoding="utf-8") as f:
        html = f.read()

    parser = BookmarkParser()
    parser.feed(html)

    # Deduplicate by URL
    seen = set()
    unique_entries = []
    for e in parser.entries:
        if e[1] not in seen:
            seen.add(e[1])
            unique_entries.append(e)

    print(f"Parsed {len(parser.entries)} bookmarks, {len(unique_entries)} unique URLs")
    generate_config(unique_entries, output_path)


if __name__ == "__main__":
    main()
