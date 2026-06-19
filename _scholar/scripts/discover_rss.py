#!/usr/bin/env python3
"""Batch RSS discovery - probe all scholars for RSS/Atom feeds.

Uses requests.Session for connection reuse and stops early once RSS is found per site.

The cache (`_snapshots/rss_sources.yaml`) is MERGED, not overwritten: a previously
discovered feed is preserved when a probe fails transiently, so a single network
blip can never demote a scholar from clean RSS to lossy content-diff (which would
cause a one-time false "changed").
"""
import sys
from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup


def main():
    config_path = Path("config.yaml")
    if not config_path.exists():
        print("Error: config.yaml not found. Run generate_config.py first.")
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    scholars = config.get("scholars", [])
    scholar_names = {s["name"] for s in scholars}
    print(f"Probing {len(scholars)} sites for RSS feeds...\n")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    # Don't verify SSL for problematic certs
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Start from the existing cache so transient failures never drop a feed.
    rss_path = Path("_snapshots") / "rss_sources.yaml"
    rss_sources = {}
    if rss_path.exists():
        try:
            with open(rss_path, encoding="utf-8") as f:
                rss_sources = yaml.safe_load(f) or {}
        except Exception:
            rss_sources = {}

    no_rss = []
    errors = []

    # Common RSS paths (ordered by likelihood)
    common_paths = [
        "/feed.xml", "/index.xml", "/rss.xml", "/atom.xml",
        "/feed/",
    ]

    for i, s in enumerate(scholars):
        name = s["name"]
        url = s["url"]
        print(f"  [{i+1}/{len(scholars)}] {name:<30s}", end=" ", flush=True)

        found_rss = None
        last_err = None

        # Method 0: For zhihu, try RSSHub
        if "zhihu.com" in url:
            import re
            zhihu_id = re.search(r"people/([^/?]+)", url)
            if zhihu_id:
                rsshub_url = f"https://rsshub.app/zhihu/people/activities/{zhihu_id.group(1)}"
                try:
                    resp = session.get(rsshub_url, timeout=10)
                    if resp.status_code == 200 and ("<rss" in resp.text[:500] or "<feed" in resp.text[:500]):
                        found_rss = rsshub_url
                except Exception as e:
                    last_err = f"RSSHub probe: {e}"
                if found_rss:
                    print(f"[RSSHub] {rsshub_url}")
                    rss_sources[name] = found_rss
                    continue

        # Method 1: Check HTML for <link> tags (one request)
        try:
            resp = session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for link in soup.find_all("link", type=lambda t: t and ("rss" in t or "atom" in t)):
                href = link.get("href")
                if href:
                    found_rss = urljoin(url, href)
                    break
        except Exception as e:
            last_err = f"page fetch: {e}"

        # Method 2: Try common RSS paths (stop on first hit)
        if not found_rss:
            base = url.rstrip("/")
            for path in common_paths:
                try:
                    rss_url = urljoin(base, path)
                    resp = session.get(rss_url, timeout=8)
                    if resp.status_code == 200:
                        text = resp.text.lower()
                        if "<?xml" in text[:200] or "<rss" in text[:500] or "<feed" in text[:500]:
                            found_rss = rss_url
                            break
                except Exception as e:
                    last_err = f"probe {path}: {e}"
                    continue

        if found_rss:
            rss_sources[name] = found_rss
            print(f"[RSS] {found_rss}")
        elif last_err:
            # Probe failed — keep the previously cached feed (if any) and record the error.
            cached = rss_sources.get(name)
            print(f"[ERR] (cached feed preserved: {cached})" if cached else "[ERR]")
            errors.append({"name": name, "url": url, "error": last_err})
        else:
            # Requests succeeded but no feed found — genuinely no RSS.
            print("[-]")
            no_rss.append({"name": name, "url": url})

    # Save merged cache
    rss_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rss_path, "w", encoding="utf-8") as f:
        yaml.dump(rss_sources, f, allow_unicode=True)

    # Summary
    found_count = sum(1 for n in rss_sources if n in scholar_names)
    print(f"\n{'='*50}")
    print(f"RSS Discovery Complete (merged with existing cache)")
    print(f"{'='*50}")
    print(f"  [OK] RSS Found:   {found_count}/{len(scholars)}")
    print(f"  [-] No RSS:       {len(no_rss)}")
    print(f"  [!] Errors:       {len(errors)}")
    print(f"\nResults saved to: {rss_path}")

    if no_rss:
        print(f"\nSites without RSS (will use content-diff monitoring):")
        for item in no_rss:
            print(f"  - {item['name']}: {item['url']}")

    if errors:
        print(f"\nRequest errors (cached feeds preserved where available):")
        for item in errors:
            print(f"  - {item['name']}: {item['error']}")


if __name__ == "__main__":
    main()
