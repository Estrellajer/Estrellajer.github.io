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
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from difflib import unified_diff
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import yaml
from bs4 import BeautifulSoup

def _get_session():
    s = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

SESSION = _get_session()


# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = BASE_DIR / "_snapshots"
CONTENT_DIR = SNAPSHOT_DIR / "content"
RSS_CACHE_PATH = SNAPSHOT_DIR / "rss_sources.yaml"
REPORT_PATH = SNAPSHOT_DIR / "latest_report.md"
LAST_CHECKED_PATH = SNAPSHOT_DIR / "last_checked.txt"
HTML_PATH = BASE_DIR.parent / "scholar" / "index.html"

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
}
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    if "scholar.google" in url or "google.com" in url:
        timeout = min(timeout, 10)
    try:
        return SESSION.get(url, headers=REQUEST_HEADERS, timeout=timeout, verify=False)
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError, Exception):
        return SESSION.get(url, headers=REQUEST_HEADERS, timeout=timeout, verify=False)


# RSS
def _parse_rss_date(date_str: str):
    if not date_str:
        return None
    cleaned = date_str.strip()
    if "," in cleaned[:8]:
        cleaned = cleaned.split(",", 1)[1].strip()
    for fmt in [
        "%d %b %Y %H:%M:%S %z", "%d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d %b %Y",
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
    title = entry.get("title", "")
    if "future blog post" in title.lower():
        return True
    pub = entry.get("_parsed")
    if pub and pub.year > 2100:
        return True
    return False


def parse_rss(xml_text: str) -> list:
    entries = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return entries
    if root.tag == "rss":
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link_el = item.find("link")
            link = link_el.text if link_el is not None else ""
            pub = item.findtext("pubDate") or item.findtext("dc:date")
            entries.append({"title": title.strip(), "link": link.strip(),
                            "published": pub.strip() if pub else "?",
                            "_parsed": _parse_rss_date(pub) if pub else None})
    elif "feed" in root.tag:
        ns = "http://www.w3.org/2005/Atom"
        for entry in root.iter(f"{{{ns}}}entry"):
            title = entry.findtext(f"{{{ns}}}title", "")
            link_el = entry.find(f"{{{ns}}}link")
            link = link_el.get("href", "") if link_el is not None else ""
            pub = entry.findtext(f"{{{ns}}}published") or entry.findtext(f"{{{ns}}}updated")
            entries.append({"title": title.strip(), "link": link.strip(),
                            "published": pub.strip() if pub else "?",
                            "_parsed": _parse_rss_date(pub) if pub else None})
    return entries


def check_rss(name: str, rss_url: str, since: datetime) -> dict:
    try:
        resp = fetch(rss_url)
        entries = parse_rss(resp.text)
        
        # Filter placeholders and get timestamps
        valid_entries = []
        for e in entries:
            if _is_placeholder_entry(e):
                continue
            parsed = e.get("_parsed")
            ts = parsed.timestamp() if parsed else 0.0
            valid_entries.append({
                "title": e["title"],
                "link": e["link"],
                "published": e["published"],
                "timestamp": ts
            })
            
        # Sort valid_entries descending by timestamp
        valid_entries.sort(key=lambda x: x["timestamp"], reverse=True)
        
        new = []
        for e in valid_entries:
            if since:
                try:
                    since_ts = since.timestamp()
                except Exception:
                    since_ts = 0.0
                if e["timestamp"] <= since_ts:
                    continue
            new.append({
                "title": e["title"],
                "link": e["link"],
                "published": e["published"],
                "timestamp": e["timestamp"]
            })
            if len(new) >= 20:
                break
                
        latest = []
        for e in valid_entries[:3]:
            latest.append({
                "title": e["title"],
                "link": e["link"],
                "published": e["published"],
                "timestamp": e["timestamp"]
            })
            
        return {"new_entries": new, "latest_entries": latest}
    except Exception as e:
        return {"error": str(e)}


# Content extraction
def extract_content(html: str, selectors: list = None, remove_selectors: list = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for sel in remove_selectors or []:
        for el in soup.select(sel):
            el.decompose()
    if selectors:
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                return _clean(el.get_text(separator="\n"))
    for tag in ["article", "main", ".post", ".content", "#content", ".entry-content"]:
        el = soup.select_one(tag)
        if el:
            return _clean(el.get_text(separator="\n"))
    body = soup.find("body")
    if body:
        t = _clean(body.get_text(separator="\n"))
        if len(t) >= 20:
            return t
        return _clean(soup.get_text(separator="\n"))
    return ""


def _clean(text: str) -> str:
    return "\n".join(l.strip() for l in text.splitlines() if l.strip())


# Snapshots
def _safe_name(name: str) -> str:
    return re.sub(r'[^\w\-_]', '_', name).strip('_').lower() or "unnamed"


def snapshot_path(name: str) -> Path:
    return CONTENT_DIR / f"{_safe_name(name)}.txt"


def load_snapshot(name: str):
    p = snapshot_path(name)
    if p.exists():
        content = p.read_text(encoding="utf-8")
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        return _clean(content)
    return None


def save_snapshot(name: str, content: str):
    p = snapshot_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# Zhihu
def _zhihu_session():
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
    session = _zhihu_session()
    if session is None:
        return None
    m = re.search(r"people/([^/?]+)", url)
    if not m:
        return None
    zid = m.group(1)
    entries = []
    try:
        r = session.get(f"https://www.zhihu.com/api/v4/members/{zid}/answers",
                        params={"limit": 10, "order_by": "created"}, timeout=15)
        if r.status_code == 200:
            for item in r.json().get("data", []):
                created = datetime.fromtimestamp(item["created_time"], tz=timezone.utc)
                if since and created <= since:
                    continue
                entries.append({"title": f"[Answer] {item['question']['title']}",
                                "link": f"https://www.zhihu.com/question/{item['question']['id']}/answer/{item['id']}",
                                "published": created.strftime("%Y-%m-%d")})
    except Exception:
        pass
    try:
        r = session.get(f"https://www.zhihu.com/api/v4/members/{zid}/articles",
                        params={"limit": 10, "order_by": "created"}, timeout=15)
        if r.status_code == 200:
            for item in r.json().get("data", []):
                created = datetime.fromtimestamp(item["created"], tz=timezone.utc)
                if since and created <= since:
                    continue
                entries.append({"title": f"[Article] {item['title']}",
                                "link": f"https://zhuanlan.zhihu.com/p/{item['id']}",
                                "published": created.strftime("%Y-%m-%d")})
    except Exception:
        pass
    if entries:
        return {"type": "rss", "name": name, "url": url, "entries": entries}
    return {"type": "rss_no_change", "name": name, "url": url}


# Scholar check
def check_scholar(scholar: dict, rss_cache: dict, since: datetime | None) -> dict:
    name = scholar["name"]
    url = scholar["url"]
    result = {"name": name, "url": url,
              "affiliation": scholar.get("affiliation", ""),
              "research_areas": scholar.get("research_areas", []),
              "labels": scholar.get("labels", []),
              "watch": scholar.get("watch", "general")}
    rss_url = rss_cache.get(name)
    if rss_url and scholar.get("watch") == "blog":
        rr = check_rss(name, rss_url, since)
        if "error" in rr:
            result["type"] = "error"
            result["error"] = rr["error"]
            return result
        result["latest_entries"] = rr.get("latest_entries", [])
        if since and rr.get("new_entries"):
            result["type"] = "rss"
            result["entries"] = rr["new_entries"]
            return result
        else:
            result["type"] = "rss_no_change"
            return result
    if "zhihu.com" in url:
        zr = check_zhihu(name, url, since)
        if zr is not None:
            return zr
    try:
        resp = fetch(url)
        content = extract_content(resp.text, scholar.get("selectors"), scholar.get("remove_selectors"))
    except Exception as e:
        result["type"] = "error"
        result["error"] = f"Fetch/extract failed: {e}"
        return result
    if not content:
        result["type"] = "error"
        result["error"] = "No content could be extracted"
        return result
        
    # Capture latest 3 non-empty lines as preview
    result["preview"] = [l.strip() for l in content.split("\n") if l.strip()][:3]
    
    prev = load_snapshot(name)
    if prev is None:
        save_snapshot(name, content)
        result["type"] = "first_check"
        return result
    if prev == content:
        result["type"] = "unchanged"
        return result
    diff = list(unified_diff(prev.split("\n"), content.split("\n"),
                             fromfile=f"{_safe_name(name)} (previous)",
                             tofile=f"{_safe_name(name)} (current)", lineterm=""))
    MAX_DIFF = 150
    truncated = len(diff) > MAX_DIFF
    save_snapshot(name, content)
    result["type"] = "changed"
    result["diff"] = "\n".join(diff[:MAX_DIFF])
    result["diff_truncated"] = truncated
    return result


# Markdown report
def _group_by_area(results: list) -> dict:
    groups = {}
    for r in results:
        areas = r.get("research_areas", [])
        if not areas:
            groups.setdefault("Other", []).append(r)
        else:
            for a in areas:
                groups.setdefault(a, []).append(r)
    for a in groups:
        seen = set()
        groups[a] = [r for r in groups[a] if r["name"] not in seen and not seen.add(r["name"])]
    return groups


def generate_report(results: list, total: int):
    updated = [r for r in results if r["type"] == "changed"]
    rss_new = [r for r in results if r["type"] == "rss"]
    first = [r for r in results if r["type"] == "first_check"]
    unchanged = [r for r in results if r["type"] in ("unchanged", "rss_no_change")]
    errors = [r for r in results if r["type"] == "error"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Scholar Monitor Report", "", f"**Run:** {now}  |  **Total:** {total}  |  "
             f"RSS {len(rss_new)}  |  CHG {len(updated)}  |  FIRST {len(first)}  |  OK {len(unchanged)}  |  ERR {len(errors)}", ""]
    if rss_new:
        lines += ["---", f"## New Publications & Blog Posts ({len(rss_new)})", ""]
        for area in sorted(_group_by_area(rss_new)):
            if area != "Other":
                lines.append(f"### {area}")
            for r in _group_by_area(rss_new)[area]:
                tag = f" [{r.get('affiliation', '')}]" if r.get("affiliation") else ""
                lines.append(f"**[{r['name']}]({r['url']})**{tag}")
                for e in r["entries"]:
                    lines.append(f"- [{e['title']}]({e['link']}) - {e['published']}")
                lines.append("")
    if updated:
        lines += ["---", f"## Pages with Changes ({len(updated)})", ""]
        for area in sorted(_group_by_area(updated)):
            if area != "Other":
                lines.append(f"### {area}")
            for r in _group_by_area(updated)[area]:
                tag = f" [{r.get('affiliation', '')}]" if r.get("affiliation") else ""
                lines.append(f"**[{r['name']}]({r['url']})**{tag}")
                lines.append(f"```diff\n{r.get('diff', '')}\n```")
                lines.append("")
    if errors:
        lines += ["---", f"## Errors ({len(errors)})", ""]
        for r in errors:
            lines.append(f"- [{r['name']}]({r['url']}): `{r['error']}`")
    if first:
        lines += ["---", f"## First-time Snapshots ({len(first)})", ""]
        for r in first:
            lines.append(f"- {r['name']}")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return "\n".join(lines)


def _extract_new_additions(diff_text: str) -> list:
    if not diff_text:
        return []
    lines = diff_text.split("\n")
    added_raw = [l[1:].strip() for l in lines if l.startswith("+") and not l.startswith("+++")]
    
    filtered = []
    noise_keywords = {
        "举报不良行为", "google 网站", "many thanks", "great theme", 
        "template", "jekyll", "designed by", "last updated",
        "power by", "hosted on", "github pages", "copyright"
    }
    
    for l in added_raw:
        if not l:
            continue
        # Skip pure numbers, dates or punctuation
        if re.match(r'^[0-9\s\-\.\,\:\/\\\|]+$', l):
            continue
        # Skip standard boilerplate noise
        lower_l = l.lower()
        if any(noise in lower_l for noise in noise_keywords):
            continue
        if len(l) < 4:
            continue
        if l not in filtered:
            filtered.append(l)
    return filtered


# HTML helpers
def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def _diff_to_html(diff_text: str) -> str:
    hl = []
    for line in diff_text.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            hl.append(f'<span class="da2">{_esc(line)}</span>')
        elif line.startswith("-") and not line.startswith("---"):
            hl.append(f'<span class="dd2">{_esc(line)}</span>')
        elif line.startswith("@@"):
            hl.append(f'<span class="dh">{_esc(line)}</span>')
        else:
            hl.append(f'<span>{_esc(line)}</span>')
    return "\n".join(hl)


def _classify_error(msg: str) -> tuple:
    ml = msg.lower()
    if "403" in msg:
        return "Access Denied", "high", "[X]", "Cookie expired - re-export from browser"
    if "404" in msg:
        return "Page Not Found", "high", "[404]", "URL is dead - remove from config"
    if "ssl" in ml or "certificate" in ml:
        return "SSL Error", "medium", "[SSL]", "Cert issue - retry next run"
    if "eof" in ml or "timeout" in ml or "connection" in ml:
        return "Network Error", "medium", "[NET]", "Transient - retry next run"
    if "no content" in ml:
        return "Extraction Failed", "low", "[WARN]", "CSS selector mismatch"
    return "Other", "low", "[?]", "Check URL and config"
def _extract_timestamp_from_text(text: str) -> float:
    match = re.search(r'\b(202\d)[-\./](\d{1,2})[-\./](\d{1,2})\b', text)
    if match:
        try:
            dt = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            pass
    match_month = re.search(r'\b(202\d)[-\./](\d{1,2})\b', text)
    if match_month:
        try:
            dt = datetime(int(match_month.group(1)), int(match_month.group(2)), 1, tzinfo=timezone.utc)
            return dt.timestamp()
        except ValueError:
            pass
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    lower_text = text.lower()
    for i, m in enumerate(months, 1):
        if m in lower_text:
            match_year = re.search(r'\b(202\d)\b', text)
            if match_year:
                try:
                    dt = datetime(int(match_year.group(1)), i, 1, tzinfo=timezone.utc)
                    return dt.timestamp()
                except ValueError:
                    pass
    return datetime.now(timezone.utc).timestamp()


def get_update_timestamp(r: dict) -> float:
    if r["type"] == "rss" and r.get("entries"):
        ts_list = [e.get("timestamp", 0.0) for e in r["entries"] if e.get("timestamp")]
        if ts_list:
            return max(ts_list)
    elif r["type"] == "changed":
        additions = _extract_new_additions(r.get("diff", ""))
        if additions:
            for add in additions[:3]:
                ts = _extract_timestamp_from_text(add)
                if ts < datetime.now(timezone.utc).timestamp() - 10.0:
                    return ts
        return datetime.now(timezone.utc).timestamp()
    return 0.0


def generate_html_report(results: list, total: int):
    rss_new = [r for r in results if r["type"] == "rss"]
    updated = [r for r in results if r["type"] == "changed"]
    first = [r for r in results if r["type"] == "first_check"]
    errors = [r for r in results if r["type"] == "error"]
    ok_list = [r for r in results if r["type"] in ("unchanged", "rss_no_change")]

    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    all_affiliations = sorted(set(r.get("affiliation", "") for r in results if r.get("affiliation")))
    all_areas = sorted(set(area for r in results for area in r.get("research_areas", []) if area))
    all_watches = sorted(set(r.get("watch", "general") for r in results))
    watch_counts = Counter(r.get("watch", "general") for r in results)

    def _watch_icon(w: str) -> str:
        return {"blog": "📝", "news": "📢",
                "publications": "🎓", "general": "🌐"}.get(w, "🌐")

    def _scholar_header(r, extra_tags="") -> str:
        parts = []
        watch = r.get("watch", "general")
        parts.append(f'<span class="wb2 wb2-{watch}">{_watch_icon(watch)} {watch}</span>')
        if r.get("affiliation"):
            parts.append(f'<span class="t ta">{_esc(r["affiliation"])}</span>')
        if r.get("research_areas"):
            for a in r["research_areas"][:2]:
                parts.append(f'<span class="t tr">{_esc(a)}</span>')
        tags = " ".join(parts)
        return f'<a href="{_esc(r["url"])}" target="_blank" class="sn2">{_esc(r["name"])}</a> {tags} {extra_tags}'

    def _status_badge(r) -> str:
        labels = {"rss": "NEW", "changed": "CHG", "error": "ERR",
                  "first_check": "FIRST", "unchanged": "OK", "rss_no_change": "OK"}
        t = r["type"]
        return f'<span class="st2 st-{t}">{labels.get(t, t)}</span>'

    def _data_attrs(r) -> str:
        return (
            f'data-name="{_esc(r.get("name", "").lower())}" '
            f'data-label="{_esc(",".join(r.get("labels", [])))}" '
            f'data-watch="{_esc(r.get("watch", "general"))}" '
            f'data-affiliation="{_esc(r.get("affiliation", "").lower())}" '
            f'data-status="{_esc(r.get("type", ""))}" '
            f'data-areas="{_esc(",".join(r.get("research_areas", [])))}"'
        )

    def _summarize_change(r: dict) -> str:
        diff = r.get("diff", "")
        lines = diff.split("\n")
        added = sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in lines if l.startswith("-") and not l.startswith("---"))
        if added == 0 and removed == 0:
            return "Content updated"
        diff_text = " ".join(lines).lower()
        paper_kw = ["arxiv", "proceedings", "conference", "transactions", "journal", "ieee", "iclr", "neurips", "icml", "aaai", "acl", "emnlp"]
        if any(kw in diff_text for kw in paper_kw) and added >= 2:
            added_lines = [l[1:].strip() for l in lines if l.startswith("+") and not l.startswith("+++") and len(l[1:].strip()) > 15]
            return f'<strong>{max(1, len(added_lines))} new publication(s)</strong> <span class="ds">(+{added}/-{removed})</span>'
        section_markers = ["publications", "papers", "teaching", "research", "bio", "about", "news", "education"]
        added_text = " ".join(l[1:].strip().lower() for l in lines if l.startswith("+") and not l.startswith("+++"))
        for marker in section_markers:
            if marker in added_text:
                return f'<strong>{marker.title()} section</strong> updated <span class="ds">(+{added}/-{removed})</span>'
        return f'Content changed <span class="ds">(+{added}/-{removed} lines)</span>'

    def _build_card(r) -> str:
        watch = r.get("watch", "general")
        card = f'<div class="sb2 sb2-{watch}" {_data_attrs(r)}>'
        card += f'<div class="sh">{_scholar_header(r, _status_badge(r))}</div>'
        if r["type"] == "rss":
            card += '<ul class="el">'
            for e in r["entries"][:10]:
                card += f'<li><a href="{_esc(e["link"])}" target="_blank">{_esc(e["title"])}</a> <span class="da">- {_esc(e["published"])}</span></li>'
            if len(r["entries"]) > 10:
                card += f'<li class="mo">... and {len(r["entries"]) - 10} more</li>'
            card += '</ul>'
        elif r["type"] == "rss_no_change":
            latest = r.get("latest_entries", [])
            if latest:
                card += '<div class="scholar-preview">'
                card += '<span class="sp-title">✨ Latest Posts:</span>'
                card += '<ul class="sp-list">'
                for e in latest[:3]:
                    card += f'<li><a href="{_esc(e["link"])}" target="_blank">{_esc(e["title"])}</a> <span class="da">- {_esc(e["published"])}</span></li>'
                card += '</ul>'
                card += '</div>'
        elif r["type"] == "changed":
            card += f'<div class="cs">{_summarize_change(r)}</div>'
            additions = _extract_new_additions(r.get("diff", ""))
            if additions:
                card += '<div class="new-additions">'
                card += '<span class="na-title">✨ Detected Additions:</span>'
                card += '<ul class="na-list">'
                for add_item in additions[:8]:
                    card += f'<li>{_esc(add_item)}</li>'
                if len(additions) > 8:
                    card += f'<li class="mo">... and {len(additions) - 8} more</li>'
                card += '</ul>'
                card += '</div>'
            card += f'<details class="dd"><summary>Show raw diff</summary><div class="db">{_diff_to_html(r.get("diff", ""))}</div>'
            if r.get("diff_truncated"):
                card += '<p class="tr2">... diff truncated</p>'
            card += '</details>'
        elif r["type"] in ("unchanged", "first_check"):
            preview = r.get("preview", [])
            if preview:
                card += '<div class="scholar-preview">'
                card += '<span class="sp-title">📄 Page Preview (Latest News/Info):</span>'
                card += '<ul class="sp-list">'
                for line in preview:
                    card += f'<li>{_esc(line)}</li>'
                card += '</ul>'
                card += '</div>'
        elif r["type"] == "error":
            err_msg = r.get("error", "")
            cat, sev, icon, suggestion = _classify_error(err_msg)
            card += f'<div class="ei2">{icon} <code>{_esc(err_msg[:120])}</code>'
            card += f'<span class="esg"> {_esc(suggestion)}</span></div>'
        card += '</div>'
        return card

    def _render_label_group(label: str, label_display: str, results_in_label: list) -> str:
        rss = [r for r in results_in_label if r["type"] == "rss"]
        changed = [r for r in results_in_label if r["type"] == "changed"]
        ok_list_local = [r for r in results_in_label if r["type"] in ("unchanged", "rss_no_change")]
        first_local = [r for r in results_in_label if r["type"] == "first_check"]
        errs_local = [r for r in results_in_label if r["type"] == "error"]
        if not any([rss, changed, ok_list_local, first_local, errs_local]):
            return ""
        html = f'<div class="lg" data-label="{label}">'
        html += f'<h2 class="lt">{label_display}</h2>'
        if rss:
            html += f'<div class="g gn"><h3>🎉 New Entries ({len(rss)})</h3>'
            for r in rss: html += _build_card(r)
            html += '</div>'
        if changed:
            html += f'<div class="g gc"><h3>⚡ Changes ({len(changed)})</h3>'
            for r in changed: html += _build_card(r)
            html += '</div>'
        if first_local:
            html += f'<div class="g gf"><h3>🆕 First Snapshots ({len(first_local)})</h3>'
            for r in first_local: html += _build_card(r)
            html += '</div>'
        if errs_local:
            html += f'<div class="g ge"><h3>⚠️ Errors ({len(errs_local)})</h3>'
            for r in errs_local: html += _build_card(r)
            html += '</div>'
        if ok_list_local:
            html += f'<details class="g-details"><summary><h3>🟢 Silent & Safe ({len(ok_list_local)})</h3></summary>'
            html += '<div class="g">'
            for r in ok_list_local: html += _build_card(r)
            html += '</div></details>'
        html += '</div>'
        return html

    sections = []
    
    # 1. Timeline Updates at the Top
    recent_updates = [r for r in results if r["type"] in ("rss", "changed")]
    recent_updates.sort(key=get_update_timestamp, reverse=True)
    recent_html = '<div class="rd-section"><h2>🔥 Recent Discoveries & Updates</h2>'
    if recent_updates:
        recent_html += '<div class="rd-container">'
        for r in recent_updates:
            watch = r.get("watch", "general")
            recent_html += f'<div class="rd-card rd-card-{watch}">'
            recent_html += f'<div class="rd-card-header">'
            recent_html += f'<span class="rd-watch">{_watch_icon(watch)} {watch.upper()}</span>'
            recent_html += f'<a href="{_esc(r["url"])}" target="_blank" class="rd-title">{_esc(r["name"])}</a>'
            if r.get("affiliation"):
                recent_html += f'<span class="rd-aff">{_esc(r["affiliation"])}</span>'
            recent_html += '</div>'
            
            if r["type"] == "rss":
                recent_html += '<ul class="rd-list">'
                for e in r["entries"][:3]:
                    recent_html += f'<li><a href="{_esc(e["link"])}" target="_blank">{_esc(e["title"])}</a> <span class="rd-date">{_esc(e["published"])}</span></li>'
                recent_html += '</ul>'
            elif r["type"] == "changed":
                recent_html += f'<div class="rd-change">{_summarize_change(r)}</div>'
                additions = _extract_new_additions(r.get("diff", ""))
                if additions:
                    recent_html += '<div class="rd-additions">'
                    recent_html += '<ul class="rd-add-list">'
                    for add_item in additions[:3]:
                        recent_html += f'<li>✨ {_esc(add_item)}</li>'
                    if len(additions) > 3:
                        recent_html += f'<li class="mo">... and {len(additions) - 3} more</li>'
                    recent_html += '</ul>'
                    recent_html += '</div>'
                recent_html += f'<details class="rd-details"><summary>View Changes</summary>'
                recent_html += f'<div class="rd-diff">{_diff_to_html(r.get("diff", ""))}</div></details>'
            recent_html += '</div>'
        recent_html += '</div>'
    else:
        recent_html += """
        <div class="rd-empty">
            <span class="rd-empty-icon">✨</span>
            <div class="rd-empty-text">All homepages are currently silent.</div>
            <div class="rd-empty-sub">No new posts or publications detected in the latest sync. Check back tomorrow!</div>
        </div>
        """
    recent_html += '</div>'
    sections.append(recent_html)

    total_new = len([r for r in results if r["type"] in ("rss", "changed")])
    watch_badges = " ".join(
        f'<span class="s">{_watch_icon(w)} {c} {w}</span>'
        for w, c in sorted(watch_counts.items()))
    stats_html = f"""<div class="sb">
      <span class="s sn">NEW {total_new}</span>
      <span class="s sf">FIRST {len(first)}</span>
      <span class="s se2">ERR {len(errors)}</span>
      <span class="s">OK {len(ok_list)}</span>
    </div><div class="wb">{watch_badges}</div>"""

    # Filter bar
    filter_html = '<div class="fb" id="filterBar"><div class="fr">'
    filter_html += '<input type="text" id="searchInput" placeholder="Search scholars..." oninput="applyFilters()" class="si">'
    filter_html += '<span class="flt">Label:</span>'
    for lb in ["blog", "homepage"]:
        filter_html += f'<label class="fc"><input type="checkbox" class="fl-label" value="{lb}" checked onchange="applyFilters()"> {lb}</label>'
    filter_html += '<span class="flt">Watch:</span>'
    for w in ["blog", "news", "publications", "general"]:
        filter_html += f'<label class="fc"><input type="checkbox" class="fl-watch" value="{w}" checked onchange="applyFilters()"> {_watch_icon(w)} {w}</label>'
    filter_html += '<span class="flt">Status:</span>'
    for st, sl in [("rss", "NEW"), ("changed", "CHG"), ("first_check", "FIRST"), ("error", "ERR")]:
        filter_html += f'<label class="fc"><input type="checkbox" class="fl-status" value="{st}" checked onchange="applyFilters()"> {sl}</label>'
    filter_html += '</div>'
    if all_affiliations:
        filter_html += '<div class="fr ar"><span class="flt">Affiliation:</span>'
        for aff in all_affiliations:
            if aff:
                filter_html += f'<label class="fc"><input type="checkbox" class="fl-aff" value="{_esc(aff.lower())}" checked onchange="applyFilters()"> {_esc(aff)}</label>'
        filter_html += '</div>'
    if all_areas:
        filter_html += '<div class="fr ar"><span class="flt">Research Area:</span>'
        for area in all_areas:
            if area:
                filter_html += f'<label class="fc"><input type="checkbox" class="fl-area" value="{_esc(area.lower())}" checked onchange="applyFilters()"> {_esc(area)}</label>'
        filter_html += '</div>'
    filter_html += '<div class="fs">Showing <span id="visibleCount">0</span> of <span id="totalCount">0</span> scholars</div></div>'
    sections.append(filter_html)

    # Errors (always visible, at top)
    if errors:
        err_categories = Counter()
        for r in errors:
            cat, _, _, _ = _classify_error(r.get("error", ""))
            err_categories[cat] += 1
        cat_badges = " ".join(f'<span class="ec">{cat}({c})</span>' for cat, c in err_categories.most_common())
        err_html = f'<div class="se3"><h2>Errors ({len(errors)})</h2><div class="es">{cat_badges}</div><ul class="el2">'
        for r in errors:
            em = r.get("error", ""); cat, sev, icon, suggestion = _classify_error(em)
            sc = {"high": "sh", "medium": "sm", "low": "sl2"}.get(sev, "sl2")
            err_html += f'<li class="ei {sc}"><span class="eic">{icon}</span>{_scholar_header(r)}: <code>{_esc(em[:100])}</code><span class="esg">{_esc(suggestion)}</span></li>'
        err_html += '</ul></div>'
        sections.append(err_html)

    # Blog section
    blog_r = [r for r in results if "blog" in r.get("labels", [])]
    bh = _render_label_group("blog", "📝 Blog Feeds", blog_r)
    if bh: sections.append(bh)

    # Homepage section
    hp_r = [r for r in results if "homepage" in r.get("labels", []) and "blog" not in r.get("labels", [])]
    hh = _render_label_group("homepage", "🌐 Academic Homepages", hp_r)
    if hh: sections.append(hh)

    # Unlabeled & Custom Labels (Other Channels)
    ul_r = [r for r in results if r not in blog_r and r not in hp_r]
    uh = _render_label_group("other", "❓ Other Channels", ul_r)
    if uh: sections.append(uh)

    body = "\n".join(sections)

    template_path = Path(__file__).parent / "_report_template.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
        html = template.replace("{now}", now).replace("{total}", str(total)).replace("{stats_html}", stats_html).replace("{body}", body)
    else:
        log("Error: HTML template not found!")
        return

    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(html, encoding="utf-8")
    log(f"HTML report saved to: {HTML_PATH}")
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

    log(f"Scholar Monitor - {len(scholars)} scholars to check")
    if since:
        log(f"Last check: {since}")
    else:
        log("First run - taking snapshots; no comparisons yet")
    log("")

    results = []
    for i, s in enumerate(scholars, 1):
        name = s["name"]
        print(f"  [{i:3d}/{len(scholars)}] {name:<30s}", end=" ", flush=True)
        r = check_scholar(s, rss_cache, since)
        results.append(r)

        label = {"rss": "[RSS]", "rss_no_change": "[OK]", "changed": "[CHG]",
                 "unchanged": "[OK]", "first_check": "[NEW]", "error": "[ERR]"}.get(r["type"], "?")
        print(f"{label}", flush=True)
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
