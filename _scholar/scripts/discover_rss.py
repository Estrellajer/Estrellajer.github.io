#!/usr/bin/env python3
"""Batch RSS discovery - probe scholars for RSS/Atom feeds.

Blog watchers (watch=blog): feeds stored in rss_sources.yaml (primary).
Other watchers: feeds stored in rss_supplemental.yaml (supplemental only).
"""
import os
import re
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
    scholar_by_name = {s["name"]: s for s in scholars}
    print(f"Probing {len(scholars)} sites for RSS feeds...\n")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    session.verify = False
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    rss_path = Path("_snapshots") / "rss_sources.yaml"
    sup_path = Path("_snapshots") / "rss_supplemental.yaml"
    rss_sources = load_merged(rss_path)
    rss_supplemental = load_merged(sup_path)

    rsshub_base = (os.environ.get("RSSHUB_BASE") or "https://rsshub.app").rstrip("/")
    no_rss = []
    errors = []
    common_paths = ["/feed.xml", "/index.xml", "/rss.xml", "/atom.xml", "/feed/"]

    for i, s in enumerate(scholars):
        name = s["name"]
        url = s["url"]
        watch = s.get("watch", "general")
        is_blog = watch == "blog"
        target = rss_sources if is_blog else rss_supplemental
        print(f"  [{i+1}/{len(scholars)}] {name:<30s}", end=" ", flush=True)

        found_rss = None
        last_err = None

        if "zhihu.com" in url:
            zhihu_id = re.search(r"people/([^/?]+)", url)
            if zhihu_id:
                rsshub_url = f"{rsshub_base}/zhihu/people/activities/{zhihu_id.group(1)}"
                try:
                    resp = session.get(rsshub_url, timeout=10)
                    if resp.status_code == 200 and ("<rss" in resp.text[:500] or "<feed" in resp.text[:500]):
                        found_rss = rsshub_url
                except Exception as e:
                    last_err = f"RSSHub probe: {e}"
                if found_rss:
                    print(f"[RSSHub] {rsshub_url}")
                    if is_blog:
                        rss_sources[name] = found_rss
                    else:
                        rss_supplemental[name] = found_rss
                    continue

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

        if found_rss:
            target[name] = found_rss
            tag = "RSS" if is_blog else "SUP"
            print(f"[{tag}] {found_rss}")
        elif last_err:
            cached = target.get(name)
            print(f"[ERR] (cached: {cached})" if cached else "[ERR]")
            errors.append({"name": name, "url": url, "error": last_err})
        else:
            print("[-]")
            no_rss.append({"name": name, "url": url})
            if name in target and name not in scholar_by_name:
                pass

    # Drop feeds for scholars no longer in config and keep primary/supplemental
    # split authoritative by current watch type.
    valid = set(scholar_by_name)
    blog_names = {s["name"] for s in scholars if s.get("watch", "general") == "blog"}
    supplemental_names = valid - blog_names
    rss_sources = {k: v for k, v in rss_sources.items() if k in blog_names}
    rss_supplemental = {k: v for k, v in rss_supplemental.items() if k in supplemental_names}

    rss_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rss_path, "w", encoding="utf-8") as f:
        yaml.dump(rss_sources, f, allow_unicode=True)
    with open(sup_path, "w", encoding="utf-8") as f:
        yaml.dump(rss_supplemental, f, allow_unicode=True)

    blog_count = sum(1 for n in rss_sources if n in valid)
    sup_count = sum(1 for n in rss_supplemental if n in valid)
    print(f"\n{'='*50}")
    print("RSS Discovery Complete")
    print(f"{'='*50}")
    print(f"  [blog primary]  {blog_count}")
    print(f"  [supplemental]  {sup_count}")
    print(f"  [-] no RSS      {len(no_rss)}")
    print(f"  [!] errors      {len(errors)}")


def load_merged(path: Path) -> dict:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    return {}


if __name__ == "__main__":
    main()
