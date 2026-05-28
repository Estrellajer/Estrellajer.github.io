#!/usr/bin/env python3
"""Scholar Monitor - Check for updates on scholar websites.

Strategy per site:
  1. RSS preferred: parse feed for new entries since last check
  2. Content diff: extract text with per-site CSS selectors, compare with last snapshot
  3. Zhihu: use zhihu-oauth if token available
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from difflib import unified_diff
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup


# 鈹€鈹€ Paths 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
BASE_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BASE_DIR / "_snapshots"
CONTENT_DIR = SNAPSHOT_DIR / "content"
RSS_CACHE_PATH = SNAPSHOT_DIR / "rss_sources.yaml"
REPORT_PATH = SNAPSHOT_DIR / "latest_report.md"
LAST_CHECKED_PATH = SNAPSHOT_DIR / "last_checked.txt"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
}

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 鈹€鈹€ Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def log(msg: str):
    print(msg, flush=True)


def load_yaml(path: Path):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def save_yaml(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)


def fetch(url: str, timeout: int = 30):
    try:
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp
    except requests.exceptions.SSLError:
        # Retry without SSL verification
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp


# 鈹€鈹€ RSS (no feedparser needed, uses lxml) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _parse_rss_date(date_str: str):
    """Try to parse common RSS date formats, including non-standard abbreviations."""
    if not date_str:
        return None
    # Strip non-standard weekday abbreviations like "Thurs" -> "Thu"
    cleaned = date_str.strip()
    # Remove leading weekday name (any language) before the comma
    if "," in cleaned[:8]:
        parts = cleaned.split(",", 1)
        cleaned = parts[1].strip()

    for fmt in [
        "%d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d %b %Y",
    ]:
        try:
            dt = datetime.strptime(cleaned, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
    return None


def _is_placeholder_entry(entry: dict) -> bool:
    """Check if an RSS entry is a placeholder/dummy post."""
    title = entry.get("title", "")
    if "future blog post" in title.lower():
        return True
    pub = entry.get("_parsed")
    if pub and pub.year > 2100:
        return True
    return False


def parse_rss(xml_text: str) -> list:
    """Parse RSS 2.0 or Atom XML, return list of {title, link, published}."""
    entries = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return entries

    # RSS 2.0: <rss><channel><item><title>...
    # Atom: <feed><entry><title>...
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    if root.tag == "rss":
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link_el = item.find("link")
            link = link_el.text if link_el is not None else ""
            pub = item.findtext("pubDate") or item.findtext("dc:date")
            entries.append({
                "title": title.strip(),
                "link": link.strip(),
                "published": pub.strip() if pub else "?",
                "_parsed": _parse_rss_date(pub) if pub else None,
            })
    elif root.tag == "{http://www.w3.org/2005/Atom}feed" or root.tag == "feed":
        for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
            title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href", "") if link_el is not None else ""
            pub = entry.findtext("{http://www.w3.org/2005/Atom}published") or \
                  entry.findtext("{http://www.w3.org/2005/Atom}updated")
            entries.append({
                "title": title.strip(),
                "link": link.strip(),
                "published": pub.strip() if pub else "?",
                "_parsed": _parse_rss_date(pub) if pub else None,
            })

    return entries


def check_rss(name: str, rss_url: str, since: datetime) -> dict:
    """Check RSS feed for new entries since `since`."""
    try:
        resp = fetch(rss_url)
        entries = parse_rss(resp.text)
        new_entries = []
        for e in entries:
            if _is_placeholder_entry(e):
                continue
            if since and e.get("_parsed") and e["_parsed"] <= since:
                continue
            new_entries.append({
                "title": e["title"],
                "link": e["link"],
                "published": e["published"],
            })
            if len(new_entries) >= 20:
                break
        return {"new_entries": new_entries}
    except Exception as e:
        return {"error": str(e)}


# 鈹€鈹€ Content extraction 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def extract_content(html: str, selectors: list = None, remove_selectors: list = None) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for sel in remove_selectors or []:
        for el in soup.select(sel):
            el.decompose()

    if selectors:
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                return _clean_text(el.get_text(separator="\n"))

    for tag in ["article", "main", ".post", ".content", "#content",
                 ".entry-content", ".post-content", ".page-content"]:
        el = soup.select_one(tag)
        if el:
            return _clean_text(el.get_text(separator="\n"))

    # Aggressive fallback: grab all visible text from body
    body = soup.find("body")
    if body:
        text = _clean_text(body.get_text(separator="\n"))
        # If the body text is very short, try the whole HTML
        if len(text) < 20:
            text = _clean_text(soup.get_text(separator="\n"))
        return text

    return ""


def _clean_text(text: str) -> str:
    return "\n".join(l.strip() for l in text.splitlines() if l.strip())


# 鈹€鈹€ Snapshot mgmt 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
def _safe_name(name: str) -> str:
    return re.sub(r'[^\w\-_]', '_', name).strip('_').lower() or "unnamed"


def snapshot_path(name: str) -> Path:
    return CONTENT_DIR / f"{_safe_name(name)}.txt"


def load_snapshot(name: str):
    p = snapshot_path(name)
    return p.read_text(encoding="utf-8") if p.exists() else None


def save_snapshot(name: str, content: str):
    p = snapshot_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _scholar_tag(scholar: dict) -> str:
    """Build a compact metadata tag like '[NJU-LAMDA, continual-learning]'."""
    parts = []
    aff = scholar.get("affiliation", "")
    if aff:
        parts.append(aff)
    areas = scholar.get("research_areas", [])
    if areas:
        parts.append(", ".join(areas[:3]))
    return f" `[{', '.join(parts)}]`" if parts else ""


# 鈹€鈹€ Zhihu 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def _zhihu_session():
    """Create an authenticated requests session for zhihu using cookies."""
    cookie_file = SNAPSHOT_DIR / "zhihu_cookies.txt"
    if not cookie_file.exists():
        return None
    try:
        from http.cookiejar import MozillaCookieJar
        session = requests.Session()
        session.headers.update(REQUEST_HEADERS)
        session.headers["Referer"] = "https://www.zhihu.com/"
        cookies = MozillaCookieJar(cookie_file)
        cookies.load(ignore_discard=True, ignore_expires=True)
        session.cookies.update(cookies)
        return session
    except Exception:
        return None


def check_zhihu(name: str, url: str, since: datetime | None) -> dict | None:
    """Check a Zhihu user's recent answers/articles via API. Returns None if no cookies."""
    session = _zhihu_session()
    if session is None:
        return None

    m = re.search(r"people/([^/?]+)", url)
    if not m:
        return None
    zhihu_id = m.group(1)

    entries = []

    # Fetch answers
    try:
        resp = session.get(
            f"https://www.zhihu.com/api/v4/members/{zhihu_id}/answers",
            params={"limit": 10, "order_by": "created"},
            timeout=15,
        )
        if resp.status_code == 200:
            for item in resp.json().get("data", []):
                created = datetime.fromtimestamp(item["created_time"], tz=timezone.utc)
                if since and created <= since:
                    continue
                entries.append({
                    "title": f"[Answer] {item['question']['title']}",
                    "link": f"https://www.zhihu.com/question/{item['question']['id']}/answer/{item['id']}",
                    "published": created.strftime("%Y-%m-%d"),
                })
    except Exception:
        pass

    # Fetch articles
    try:
        resp = session.get(
            f"https://www.zhihu.com/api/v4/members/{zhihu_id}/articles",
            params={"limit": 10, "order_by": "created"},
            timeout=15,
        )
        if resp.status_code == 200:
            for item in resp.json().get("data", []):
                created = datetime.fromtimestamp(item["created"], tz=timezone.utc)
                if since and created <= since:
                    continue
                entries.append({
                    "title": f"[Article] {item['title']}",
                    "link": f"https://zhuanlan.zhihu.com/p/{item['id']}",
                    "published": created.strftime("%Y-%m-%d"),
                })
    except Exception:
        pass

    if entries:
        return {"type": "rss", "name": name, "url": url, "entries": entries}
    return {"type": "rss_no_change", "name": name, "url": url}


# 鈹€鈹€ Scholar check 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def check_scholar(scholar: dict, rss_cache: dict, since: datetime | None) -> dict:
    name = scholar["name"]
    url = scholar["url"]
    result = {"name": name, "url": url,
              "affiliation": scholar.get("affiliation", ""),
              "research_areas": scholar.get("research_areas", []),
              "labels": scholar.get("labels", []),
              "watch": scholar.get("watch", "general")}

    # Phase 1: RSS
    rss_url = rss_cache.get(name)
    if rss_url and since:
        rss_result = check_rss(name, rss_url, since)
        if rss_result.get("new_entries"):
            result["type"] = "rss"
            result["entries"] = rss_result["new_entries"]
            return result
        elif not rss_result.get("error"):
            result["type"] = "rss_no_change"
            return result

    # Phase 1.5: Zhihu special handling
    if "zhihu.com" in url:
        zhihu_result = check_zhihu(name, url, since)
        if zhihu_result is not None:
            return zhihu_result

    # Phase 2: Content diff
    try:
        resp = fetch(url)
        content = extract_content(
            resp.text,
            scholar.get("selectors"),
            scholar.get("remove_selectors"),
        )
    except Exception as e:
        result["type"] = "error"
        result["error"] = f"Fetch/extract failed: {e}"
        return result

    if not content:
        result["type"] = "error"
        result["error"] = "No content could be extracted"
        return result

    prev = load_snapshot(name)
    if prev is None:
        save_snapshot(name, content)
        result["type"] = "first_check"
        return result

    if prev == content:
        result["type"] = "unchanged"
        return result

    prev_lines, curr_lines = prev.split("\n"), content.split("\n")
    diff = list(unified_diff(
        prev_lines, curr_lines,
        fromfile=f"{_safe_name(name)} (previous)",
        tofile=f"{_safe_name(name)} (current)",
        lineterm="",
    ))

    MAX_DIFF = 150
    truncated = len(diff) > MAX_DIFF
    save_snapshot(name, content)

    result["type"] = "changed"
    result["diff"] = "\n".join(diff[:MAX_DIFF])
    result["diff_truncated"] = truncated
    return result


# 鈹€鈹€ Report 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

def _group_by_area(results: list) -> dict:
    """Group results by research area. Results without areas go to 'Other'."""
    groups = {}
    for r in results:
        areas = r.get("research_areas", [])
        if not areas:
            groups.setdefault("Other", []).append(r)
        else:
            for area in areas:
                groups.setdefault(area, []).append(r)
    # Deduplicate within each group
    for area in groups:
        seen = set()
        groups[area] = [r for r in groups[area]
                        if r["name"] not in seen and not seen.add(r["name"])]
    return groups


def generate_report(results: list, total: int):
    updated = [r for r in results if r["type"] == "changed"]
    rss_new = [r for r in results if r["type"] == "rss"]
    first = [r for r in results if r["type"] == "first_check"]
    unchanged = [r for r in results if r["type"] in ("unchanged", "rss_no_change")]
    errors = [r for r in results if r["type"] == "error"]

    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Scholar Monitor Report",
        f"",
        f"**Run:** {now}  |  **Total:** {total}  |  "
        f"馃摗 {len(rss_new)} RSS  |  馃敂 {len(updated)} changed  |  "
        f"馃搵 {len(first)} first  |  鉁?{len(unchanged)} ok  |  鉂?{len(errors)} errors",
        f"",
    ]

    # 鈹€鈹€ RSS: group by research area 鈹€鈹€
    if rss_new:
        lines.append(f"---")
        lines.append(f"## 馃摗 New Publications & Blog Posts ({len(rss_new)})")
        lines.append(f"")
        rss_by_area = _group_by_area(rss_new)
        for area in sorted(rss_by_area):
            if area != "Other":
                lines.append(f"### {area}")
            for r in rss_by_area[area]:
                aff = r.get("affiliation", "")
                tag = f" `[{aff}]`" if aff else ""
                lines.append(f"**[{r['name']}]({r['url']})**{tag}")
                for e in r["entries"]:
                    lines.append(f"- [{e['title']}]({e['link']}) 鈥?{e['published']}")
                lines.append(f"")
        lines.append("")

    # 鈹€鈹€ Content changes: group by research area 鈹€鈹€
    if updated:
        lines.append(f"---")
        lines.append(f"## 馃敂 Pages with Changes ({len(updated)})")
        lines.append(f"")
        chg_by_area = _group_by_area(updated)
        for area in sorted(chg_by_area):
            if area != "Other":
                lines.append(f"### {area}")
            for r in chg_by_area[area]:
                aff = r.get("affiliation", "")
                tag = f" `[{aff}]`" if aff else ""
                lines.append(f"**[{r['name']}]({r['url']})**{tag}")
                lines.append(f"```diff")
                lines.append(r.get("diff", ""))
                if r.get("diff_truncated"):
                    lines.append("# ... diff truncated (150 lines max)")
                lines.append("```")
                lines.append(f"")
        lines.append("")

    if errors:
        lines.append(f"---")
        lines.append(f"## 鉂?Errors ({len(errors)})")
        lines.append(f"")
        for r in errors:
            tag = _scholar_tag(r)
            lines.append(f"- [{r['name']}]({r['url']}){tag}: `{r['error']}`")

    if first:
        lines.append(f"---")
        lines.append(f"## 馃搵 First-time Snapshots Saved ({len(first)})")
        lines.append(f"")
        for r in first:
            tag = _scholar_tag(r)
            lines.append(f"- {r['name']}{tag}")
        lines.append(f"")

    # Stats table
    lines.append(f"---")
    lines.append(f"## 馃搳 Quick Stats")
    lines.append(f"")
    lines.append(f"| Label | Count |")
    lines.append(f"|-------|-------|")
    from collections import Counter
    label_counts = Counter()
    for r in results:
        for label in r.get("labels", []):
            label_counts[label] += 1
    for label, cnt in sorted(label_counts.items()):
        lines.append(f"| {label} | {cnt} |")

    # Area summary
    area_counts = Counter()
    for r in results:
        for area in r.get("research_areas", []):
            area_counts[area] += 1
    if area_counts:
        lines.append(f"")
        lines.append(f"| Research Area | Count |")
        lines.append(f"|--------------|-------|")
        for area, cnt in sorted(area_counts.items()):
            lines.append(f"| {area} | {cnt} |")

    if updated or rss_new:
        lines.append(f"")
        lines.append(f"*Report auto-generated by Scholar Monitor*")

    text = "\n".join(lines)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(text, encoding="utf-8")
    return text


# 鈹€鈹€ HTML Report 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€
HTML_PATH = BASE_DIR / "docs" / "index.html"


def _esc(text: str) -> str:
    """HTML-escape a string."""
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def _diff_to_html(diff_text: str) -> str:
    """Render a unified diff as HTML with color-coded lines."""
    lines = []
    for line in diff_text.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(f'<span class="diff-add">{_esc(line)}</span>')
        elif line.startswith("-") and not line.startswith("---"):
            lines.append(f'<span class="diff-del">{_esc(line)}</span>')
        elif line.startswith("@@"):
            lines.append(f'<span class="diff-header">{_esc(line)}</span>')
        else:
            lines.append(f'<span>{_esc(line)}</span>')
    return "\n".join(lines)


def _classify_error(msg: str) -> tuple:
    """Classify an error message into (category, severity, icon, suggestion)."""
    msg_lower = msg.lower()
    if "403" in msg:
        return "Access Denied", "high", "馃敀", "Cookie may be expired 鈥?re-export from browser"
    if "404" in msg:
        return "Page Not Found", "high", "馃拃", "URL is dead 鈥?remove from config"
    if "ssl" in msg_lower or "certificate" in msg_lower:
        return "SSL Error", "medium", "馃攼", "Certificate issue 鈥?add verify=false in config"
    if "eof" in msg_lower or "timeout" in msg_lower or "connection" in msg_lower:
        return "Network Error", "medium", "馃寪", "Transient network issue 鈥?will retry next run"
    if "no content" in msg_lower:
        return "Extraction Failed", "low", "鈿狅笍", "CSS selector mismatch 鈥?update selectors in config"
    return "Other Error", "low", "鉂?, "Check URL and config"



def main():
    config = load_yaml(BASE_DIR / "config.yaml")
    scholars = config.get("scholars", [])
    if not scholars:
        log("Error: No scholars found in config.yaml")
        sys.exit(1)

    rss_cache = load_yaml(RSS_CACHE_PATH)

    since = None
    if LAST_CHECKED_PATH.exists():
        try:
            since = datetime.fromisoformat(LAST_CHECKED_PATH.read_text().strip())
        except ValueError:
            pass

    log(f"Scholar Monitor 鈥?{len(scholars)} scholars to check")
    if since:
        log(f"Last check: {since}")
    else:
        log("First run 鈥?taking snapshots; no comparisons yet")
    log("")

    results = []
    for i, s in enumerate(scholars, 1):
        name = s["name"]
        print(f"  [{i:3d}/{len(scholars)}] {name:<30s}", end=" ", flush=True)
        r = check_scholar(s, rss_cache, since)
        results.append(r)

        emoji = {
            "rss": "[RSS]", "rss_no_change": "[OK]",
            "changed": "[CHG]", "unchanged": "[OK]",
            "first_check": "[NEW]", "error": "[ERR]",
        }.get(r["type"], "?")
        print(f"{emoji}", flush=True)

        if r["type"] == "error":
            print(f"          -> Error: {r.get('error')}", flush=True)
        elif r["type"] == "rss":
            for e in r.get("entries", []):
                print(f"          -> {e['title']}", flush=True)

    report = generate_report(results, len(scholars))
    generate_html_report(results, len(scholars))
    LAST_CHECKED_PATH.write_text(datetime.now(timezone.utc).isoformat())

    log(f"\n{'='*50}")
    log("Report:")
    log(f"{'='*50}")
    log(report)
    log(f"\nSaved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
