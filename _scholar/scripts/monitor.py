#!/usr/bin/env python3
"""Scholar Monitor - Check for updates on scholar websites.

Strategy per site (by watch type):
  watch=blog       -> RSS preferred, content-diff fallback
  watch=news/publications/general -> content-diff authoritative; RSS supplemental only
  google_scholar   -> SerpApi when SERPAPI_KEY set, else direct fetch + captcha detection
  zhihu            -> cookie API preferred, RSSHub fallback (RSSHUB_BASE)
"""
import os
import re
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import xml.etree.ElementTree as ET
import time
import warnings
from collections import Counter
from datetime import datetime, timedelta, timezone
from difflib import unified_diff
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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
        status_forcelist=[429, 500, 502, 503, 504],
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
RSS_SUPPLEMENTAL_PATH = SNAPSHOT_DIR / "rss_supplemental.yaml"
REPORT_PATH = SNAPSHOT_DIR / "latest_report.md"
LAST_CHECKED_PATH = SNAPSHOT_DIR / "last_checked.txt"
HTML_PATH = BASE_DIR.parent / "scholar" / "index.html"

RSSHUB_BASE = (os.environ.get("RSSHUB_BASE") or "https://rsshub.app").rstrip("/")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/",
}

BLOCKED_SNIPPETS = [
    "请进行人机身份验证", "人机身份验证", "unusual traffic", "enable javascript",
    "enable JavaScript", "captcha", "recaptcha", "verify you are human",
    "There isn't a GitHub Pages site here", "登录后查看", "安全验证",
    "系统目前无法执行此操作", "正在加载...",
]

PAPER_KEYWORDS = {
    "arxiv", "proceedings", "conference", "transactions", "journal",
    "ieee", "iclr", "neurips", "icml", "aaai", "acl", "emnlp", "cvpr", "iccv",
}


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


def fetch(url: str, timeout: int = 30, retries: int = 2):
    if "scholar.google" in url or "google.com" in url:
        timeout = min(timeout, 10)
    last_exc = None
    for attempt in range(retries):
        try:
            resp = SESSION.get(url, headers=REQUEST_HEADERS, timeout=timeout, verify=True)
            if resp.encoding == 'ISO-8859-1' or not resp.encoding:
                resp.encoding = resp.apparent_encoding or 'utf-8'
            resp.raise_for_status()
            return resp
        except requests.exceptions.SSLError as e:
            last_exc = e
            if attempt == retries - 1:
                warnings.warn(f"SSL verification failed for {url}; retrying with verify=False: {e}")
                resp = SESSION.get(url, headers=REQUEST_HEADERS, timeout=timeout, verify=False)
                if resp.encoding == 'ISO-8859-1' or not resp.encoding:
                    resp.encoding = resp.apparent_encoding or 'utf-8'
                resp.raise_for_status()
                return resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
        except requests.exceptions.HTTPError:
            raise
        if attempt < retries - 1:
            time.sleep(1.5 ** attempt)
    raise last_exc


def _looks_blocked(content: str, url: str = "") -> str | None:
    """Return a short reason if content looks like a captcha/login/dead-page shell."""
    if not content:
        return "Empty page content"
    lower = content.lower()
    hits = [s for s in BLOCKED_SNIPPETS if s.lower() in lower]
    if "scholar.google" in url and any(
        x in lower for x in ("人机身份验证", "enable javascript", "unusual traffic", "captcha")
    ):
        return "Google Scholar captcha / bot block"
    if "there isn't a github pages site here" in lower:
        return "GitHub Pages site not found (dead URL)"
    if "zhihu.com" in url and any(x in lower for x in ("登录后查看", "安全验证", "40362", "unhuman")):
        return "Zhihu login wall or security check"
    if any(x in lower for x in ("login required", "please log in", "sign in to continue")):
        return "Login wall"
    if hits and len(content) < 5000:
        return f"Blocked or placeholder page ({hits[0][:40]})"
    return None


def _norm_str(val, default: str = "") -> str:
    return val if val else default


def _scholar_base_result(scholar: dict) -> dict:
    return {
        "name": scholar["name"],
        "url": scholar["url"],
        "affiliation": _norm_str(scholar.get("affiliation")),
        "research_areas": scholar.get("research_areas") or [],
        "labels": scholar.get("labels") or [],
        "watch": scholar.get("watch", "general"),
    }


def _is_blog_watch(scholar: dict) -> bool:
    return scholar.get("watch", "general") == "blog"


# RSS
def _parse_rss_date(date_str: str):
    if not date_str:
        return None
    cleaned = date_str.strip()
    try:
        dt = parsedate_to_datetime(cleaned)
        if dt is not None:
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, IndexError):
        pass
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


def check_rss(name: str, rss_url: str, since: datetime | None) -> dict:
    try:
        resp = fetch(rss_url)
        entries = parse_rss(resp.text)
        valid_entries = []
        for e in entries:
            if _is_placeholder_entry(e):
                continue
            parsed = e.get("_parsed")
            ts = parsed.timestamp() if parsed else 0.0
            valid_entries.append({
                "title": e["title"], "link": e["link"],
                "published": e["published"], "timestamp": ts,
            })
        valid_entries.sort(key=lambda x: x["timestamp"], reverse=True)

        new = []
        for e in valid_entries:
            if since:
                try:
                    since_ts = since.timestamp()
                except Exception:
                    since_ts = 0.0
                if e["timestamp"] == 0.0 or e["timestamp"] <= since_ts:
                    continue
            new.append(dict(e))
            if len(new) >= 20:
                break

        latest = [dict(e) for e in valid_entries[:3]]
        return {"new_entries": new, "latest_entries": latest}
    except Exception as e:
        return {"error": str(e)}


def _merge_rss_into_result(result: dict, rr: dict, since: datetime | None) -> dict:
    if "error" in rr:
        result.setdefault("rss_error", rr["error"])
        return result
    result["latest_entries"] = rr.get("latest_entries", [])
    if since and rr.get("new_entries"):
        existing = {e.get("link") or e.get("title") for e in result.get("entries", [])}
        supplemental = [e for e in rr["new_entries"]
                        if (e.get("link") or e.get("title")) not in existing]
        if supplemental:
            if result.get("type") in ("unchanged", "rss_no_change", None):
                result["type"] = "rss"
                result["entries"] = supplemental
            elif result.get("type") == "rss":
                result.setdefault("entries", []).extend(supplemental)
            elif result.get("type") == "changed":
                result.setdefault("supplemental_entries", []).extend(supplemental)
    return result


# Content extraction
def get_clean_text_custom(element) -> str:
    from bs4 import NavigableString
    chunks = []

    def walk(node):
        if isinstance(node, NavigableString):
            text = node.strip()
            if text:
                chunks.append(text)
            return
        is_block = node.name in {
            "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6",
            "section", "article", "tr", "table", "ul", "ol", "br",
            "aside", "header", "footer", "nav"
        }
        if is_block and chunks and chunks[-1] != "\n":
            chunks.append("\n")
        for child in node.children:
            walk(child)
        if is_block and chunks and chunks[-1] != "\n":
            chunks.append("\n")

    walk(element)
    text_parts = []
    current_line = []
    for c in chunks:
        if c == "\n":
            if current_line:
                text_parts.append(" ".join(current_line))
                current_line = []
            text_parts.append("\n")
        else:
            current_line.append(c)
    if current_line:
        text_parts.append(" ".join(current_line))
    raw_text = "".join(text_parts)
    return "\n".join(l.strip() for l in raw_text.splitlines() if l.strip())


DEFAULT_REMOVE_SELECTORS = [
    "script", "style", "noscript", "iframe", "svg",
    "[class*='visit']", "[class*='counter']", "[id*='busuanzi']",
    "time", ".timeago", "[datetime]",
    "[data-analytics]", "[data-track]", "[data-pid]",
    ".giscus", "#disqus_thread",
]

_NOISE_LINE_DATE = re.compile(r"^\d{4}[-/.]\d{1,2}([-/.]\d{1,2})?\s*$")
_NOISE_LINE_NUM = re.compile(r"^\d+(\.\d+)?\s*$")
_NOISE_LINE_HEX = re.compile(r"^[a-f0-9]{16,}\s*$", re.IGNORECASE)

NEWS_SELECTORS = [
    "#news", ".news", "#recent-news", ".recent-news", ".news-section", "#news-section",
    "#updates", ".updates", "#announcements", ".announcements",
    "#activities", ".activities", "#recent-activity", ".recent-activity",
    "#whats-new", ".whats-new", "[id*='news']", "[class*='news']",
    ".post-list", "#post-list", ".latest-news",
]

PUB_SELECTORS = [
    "#publications", ".publications", "#selected-publications", ".selected-publications",
    "#papers", ".papers", "#research", ".research", "#selected-papers", ".selected-papers",
    ".publication-list", "#publication-list", "table.publications",
    "#gsc_a_b", "#gsc_art",
]


def _normalize_for_diff(text: str) -> str:
    out = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            out.append(line)
            continue
        if _NOISE_LINE_DATE.match(s) or _NOISE_LINE_NUM.match(s) or _NOISE_LINE_HEX.match(s):
            continue
        out.append(line)
    return "\n".join(out)


def extract_content(html: str, selectors: list = None, remove_selectors: list = None, watch: str = "general") -> str:
    soup = BeautifulSoup(html, "html.parser")
    for sel in (DEFAULT_REMOVE_SELECTORS + (remove_selectors or [])):
        for el in soup.select(sel):
            el.decompose()

    targeted = NEWS_SELECTORS if watch == "news" else PUB_SELECTORS if watch == "publications" else []
    for sel in targeted:
        el = soup.select_one(sel)
        if el:
            t = get_clean_text_custom(el)
            if len(t) >= 20:
                return t

    if selectors:
        for sel in selectors:
            el = soup.select_one(sel)
            if el:
                t = get_clean_text_custom(el)
                if len(t) >= 10:
                    return t
    for tag in ["article", "main", ".post", ".content", "#content", ".entry-content"]:
        el = soup.select_one(tag)
        if el:
            return get_clean_text_custom(el)
    body = soup.find("body")
    if body:
        t = get_clean_text_custom(body)
        if len(t) >= 20:
            return t
        return get_clean_text_custom(soup)
    return ""


def _clean(text: str) -> str:
    return "\n".join(l.strip() for l in text.splitlines() if l.strip())


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


def _zhihu_user_id(url: str) -> str | None:
    m = re.search(r"people/([^/?]+)", url)
    return m.group(1) if m else None


def _zhihu_rsshub_url(zid: str) -> str:
    return f"{RSSHUB_BASE}/zhihu/people/activities/{zid}"


def check_zhihu_api(name: str, url: str, since: datetime | None) -> dict | None:
    session = _zhihu_session()
    if session is None:
        return None
    zid = _zhihu_user_id(url)
    if not zid:
        return None
    entries = []
    auth_failed = False
    request_err = None
    try:
        r = session.get(f"https://www.zhihu.com/api/v4/members/{zid}/answers",
                        params={"limit": 10, "order_by": "created"}, timeout=15)
        if r.status_code in (401, 403):
            auth_failed = True
        elif r.status_code == 200:
            for item in r.json().get("data", []):
                created = datetime.fromtimestamp(item["created_time"], tz=timezone.utc)
                if since and created <= since:
                    continue
                entries.append({
                    "title": f"[Answer] {item['question']['title']}",
                    "link": f"https://www.zhihu.com/question/{item['question']['id']}/answer/{item['id']}",
                    "published": created.strftime("%Y-%m-%d"),
                    "timestamp": created.timestamp(),
                })
    except Exception as e:
        request_err = f"Zhihu answers request failed: {e}"
    try:
        r = session.get(f"https://www.zhihu.com/api/v4/members/{zid}/articles",
                        params={"limit": 10, "order_by": "created"}, timeout=15)
        if r.status_code in (401, 403):
            auth_failed = True
        elif r.status_code == 200:
            for item in r.json().get("data", []):
                created = datetime.fromtimestamp(item["created"], tz=timezone.utc)
                if since and created <= since:
                    continue
                entries.append({
                    "title": f"[Article] {item['title']}",
                    "link": f"https://zhuanlan.zhihu.com/p/{item['id']}",
                    "published": created.strftime("%Y-%m-%d"),
                    "timestamp": created.timestamp(),
                })
    except Exception as e:
        request_err = f"Zhihu articles request failed: {e}"
    if auth_failed:
        return {"error": "Zhihu auth failed (cookies expired or invalid — refresh ZHIHU_COOKIES_B64)"}
    if request_err and not entries:
        return {"error": request_err}
    entries.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    if entries:
        return {"new_entries": entries, "latest_entries": entries[:3]}
    return {"new_entries": [], "latest_entries": []}


def check_zhihu_scholar(scholar: dict, since: datetime | None) -> dict:
    result = _scholar_base_result(scholar)
    name, url = scholar["name"], scholar["url"]
    zid = _zhihu_user_id(url)
    if not zid:
        result["type"] = "error"
        result["error"] = "Invalid Zhihu URL"
        return result

    api_rr = check_zhihu_api(name, url, since)
    if api_rr and "error" not in api_rr:
        result["latest_entries"] = api_rr.get("latest_entries", [])
        if since and api_rr.get("new_entries"):
            result["type"] = "rss"
            result["entries"] = api_rr["new_entries"]
        else:
            result["type"] = "rss_no_change"
        return result

    # RSSHub fallback
    rr = check_rss(name, _zhihu_rsshub_url(zid), since)
    if "error" not in rr:
        result["latest_entries"] = rr.get("latest_entries", [])
        if since and rr.get("new_entries"):
            result["type"] = "rss"
            result["entries"] = rr["new_entries"]
        else:
            result["type"] = "rss_no_change"
        return result

    err = (api_rr or {}).get("error") or "Zhihu cookies not configured"
    rss_err = rr.get("error", "RSSHub failed")
    result["type"] = "error"
    result["error"] = f"{err}; RSSHub fallback failed via {RSSHUB_BASE} ({rss_err})"
    return result


# Google Scholar via SerpApi
def _google_scholar_author_id(url: str) -> str | None:
    qs = parse_qs(urlparse(url).query)
    user = qs.get("user", [None])[0]
    return user


def _publications_to_text(pubs: list) -> str:
    lines = []
    for p in pubs:
        title = p.get("title", "")
        raw_authors = p.get("authors", [])
        if isinstance(raw_authors, str):
            authors = raw_authors
        elif isinstance(raw_authors, list):
            authors = ", ".join(
                a.get("name", "") if isinstance(a, dict) else str(a)
                for a in raw_authors[:6]
            )
        else:
            authors = ""
        year = str(p.get("year") or p.get("article_year") or "")
        venue = p.get("publication", "") or ""
        lines.append(title)
        if authors:
            lines.append(authors)
        if venue or year:
            lines.append(f"{venue} {year}".strip())
    return "\n".join(lines)


def check_google_scholar(scholar: dict, since: datetime | None) -> dict:
    result = _scholar_base_result(scholar)
    url = scholar["url"]
    author_id = _google_scholar_author_id(url)
    if not author_id:
        result["type"] = "error"
        result["error"] = "Cannot parse Google Scholar author ID from URL"
        return result

    if SERPAPI_KEY:
        try:
            resp = SESSION.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_scholar_author",
                    "author_id": author_id,
                    "api_key": SERPAPI_KEY,
                    "num": 20,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = data.get("articles", [])
            if not articles:
                result["type"] = "error"
                result["error"] = "SerpApi returned no articles"
                return result
            content = _publications_to_text(articles)
            blocked = _looks_blocked(content, url)
            if blocked:
                result["type"] = "error"
                result["error"] = blocked
                return result
            result["preview"] = [a.get("title", "") for a in articles[:3] if a.get("title")]
            prev = load_snapshot(scholar["name"])
            if prev is None:
                save_snapshot(scholar["name"], content)
                result["type"] = "first_check"
                return result
            prev_norm = _normalize_for_diff(prev)
            content_norm = _normalize_for_diff(content)
            if prev_norm == content_norm:
                result["type"] = "unchanged"
                result["latest_entries"] = [
                    {"title": a.get("title", ""), "link": a.get("link", url),
                     "published": str(a.get("year", "?")), "timestamp": 0.0}
                    for a in articles[:3]
                ]
                return result
            diff = list(unified_diff(
                prev_norm.split("\n"), content_norm.split("\n"),
                fromfile=f"{_safe_name(scholar['name'])} (previous)",
                tofile=f"{_safe_name(scholar['name'])} (current)", lineterm=""))
            save_snapshot(scholar["name"], content)
            result["type"] = "changed"
            result["diff"] = "\n".join(diff[:150])
            result["diff_truncated"] = len(diff) > 150
            return result
        except Exception as e:
            log(f"      ↳ SerpApi failed, falling back to direct fetch: {e}")

    # Direct fetch fallback
    return _content_diff_check(scholar, since, result)


def extract_smart_preview(content: str) -> list:
    lines = content.split("\n")
    boilerplate_words = {
        "搜索此网站", "嵌入的文件", "跳至主要内容", "调至导航栏", "Google 网站", "举报不良行为",
        "skip to content", "toggle navigation", "navigation", "search this site",
        "many thanks", "designed by", "theme by", "powered by", "hosted on", "copyright",
        "all rights reserved", "visitor count", "last updated", "home", "about", "contact",
        "menu", "links", "cv", "biography", "bio", "google scholar", "github", "linkedin",
    }
    clean_lines = []
    for l in lines:
        cl = l.strip()
        if not cl or len(cl) < 5:
            continue
        lower_cl = cl.lower()
        if any(lower_cl == bp or lower_cl.startswith(bp) for bp in boilerplate_words):
            continue
        if re.match(r'^[0-9\s\-\.\,\:\/\\\|\[\]\(\)\*#]+$', cl):
            continue
        clean_lines.append(cl)

    scored_lines = []
    for cl in clean_lines:
        score = 0
        lower_cl = cl.lower()
        if re.search(r'\b(202\d)[-\./](\d{1,2})[-\./]?(\d{1,2})?\b', lower_cl):
            score += 5
        elif any(yr in lower_cl for yr in ["2024", "2025", "2026", "2027"]):
            score += 3
        if any(kw in lower_cl for kw in PAPER_KEYWORDS):
            score += 4
        if re.match(r'^[\*\-\+•⚫📢🎓🔥✨]|\b\d{1,2}\b|\[\d+\]', cl):
            score += 2
        bio_keywords = {"i am a", "currently i", "my research", "postdoctoral", "ph.d", "professor"}
        if any(bkw in lower_cl for bkw in bio_keywords):
            score -= 3
        if 15 < len(cl) < 150:
            score += 1
        scored_lines.append((score, cl))

    for threshold in [3, 1, 0]:
        selected = [cl for score, cl in scored_lines if score >= threshold]
        if len(selected) >= 3:
            return selected[:3]
    return clean_lines[:3]


def _content_diff_check(scholar: dict, since: datetime | None, result: dict) -> dict:
    url = scholar["url"]
    watch = scholar.get("watch", "general")
    try:
        resp = fetch(url)
        content = extract_content(
            resp.text, scholar.get("selectors"), scholar.get("remove_selectors"), watch=watch)
    except requests.exceptions.HTTPError as e:
        resp = getattr(e, "response", None)
        if resp is not None and resp.status_code in (403, 404):
            blocked = _looks_blocked(resp.text or "", url)
            result["type"] = "error"
            result["error"] = blocked or f"HTTP {resp.status_code} for {url}"
            return result
        result["type"] = "error"
        result["error"] = f"Fetch/extract failed: {e}"
        return result
    except Exception as e:
        result["type"] = "error"
        result["error"] = f"Fetch/extract failed: {e}"
        return result
    if not content:
        result["type"] = "error"
        result["error"] = "No content could be extracted"
        return result

    blocked = _looks_blocked(content, url)
    if blocked:
        result["type"] = "error"
        result["error"] = blocked
        return result

    result["preview"] = extract_smart_preview(content)
    prev = load_snapshot(scholar["name"])
    if prev is None:
        save_snapshot(scholar["name"], content)
        result["type"] = "first_check"
        return result

    prev_blocked = _looks_blocked(prev, url)
    if prev_blocked:
        save_snapshot(scholar["name"], content)
        result["type"] = "first_check"
        return result

    prev_norm = _normalize_for_diff(prev)
    content_norm = _normalize_for_diff(content)
    if prev_norm == content_norm:
        result["type"] = "unchanged"
        return result

    diff = list(unified_diff(
        prev_norm.split("\n"), content_norm.split("\n"),
        fromfile=f"{_safe_name(scholar['name'])} (previous)",
        tofile=f"{_safe_name(scholar['name'])} (current)", lineterm=""))
    MAX_DIFF = 150
    truncated = len(diff) > MAX_DIFF
    save_snapshot(scholar["name"], content)
    result["type"] = "changed"
    result["diff"] = "\n".join(diff[:MAX_DIFF])
    result["diff_truncated"] = truncated
    return result


def check_scholar(scholar: dict, rss_cache: dict, rss_supplemental: dict, since: datetime | None) -> dict:
    name = scholar["name"]
    url = scholar["url"]
    watch = scholar.get("watch", "general")
    site_type = scholar.get("site_type", "")

    if site_type == "google_scholar" or "scholar.google.com/citations" in url:
        return check_google_scholar(scholar, since)

    if "zhihu.com" in url:
        return check_zhihu_scholar(scholar, since)

    result = _scholar_base_result(scholar)
    blog_mode = _is_blog_watch(scholar)

    if blog_mode:
        rss_url = rss_cache.get(name)
        if rss_url:
            rr = check_rss(name, rss_url, since)
            if "error" in rr:
                print(f"      ↳ RSS error, falling back to content-diff: {rr['error']}", flush=True)
            else:
                result["latest_entries"] = rr.get("latest_entries", [])
                if since and rr.get("new_entries"):
                    result["type"] = "rss"
                    result["entries"] = rr["new_entries"]
                    return result
                result["type"] = "rss_no_change"
                return result
        return _content_diff_check(scholar, since, result)

    # Homepage / news / publications: content-diff is authoritative
    result = _content_diff_check(scholar, since, result)
    sup_url = rss_supplemental.get(name)
    if sup_url:
        rr = check_rss(name, sup_url, since)
        result = _merge_rss_into_result(result, rr, since)
    return result


# Reports & events
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


def _extract_new_additions(diff_text: str) -> list:
    if not diff_text:
        return []
    lines = diff_text.split("\n")
    deleted_lines = [l[1:].strip() for l in lines if l.startswith("-") and not l.startswith("---") and len(l[1:].strip()) > 5]
    added_raw = [l[1:].strip() for l in lines if l.startswith("+") and not l.startswith("+++")]
    filtered = []
    noise_keywords = {
        "举报不良行为", "google 网站", "many thanks", "great theme",
        "template", "jekyll", "designed by", "last updated",
        "power by", "hosted on", "github pages", "copyright",
        "人机身份验证", "enable javascript",
    }
    for l in added_raw:
        if not l or len(l) < 4:
            continue
        if re.match(r'^[0-9\s\-\.\,\:\/\\\|]+$', l):
            continue
        lower_l = l.lower()
        if any(noise in lower_l for noise in noise_keywords):
            continue
        is_edit = False
        w_added = set(lower_l.split())
        for dl in deleted_lines:
            w_deleted = set(dl.lower().split())
            if not w_added or not w_deleted:
                continue
            similarity = len(w_added.intersection(w_deleted)) / len(w_added.union(w_deleted))
            if similarity > 0.35 or dl.lower() in lower_l or lower_l in dl.lower():
                is_edit = True
                break
        if is_edit:
            continue
        if l not in filtered:
            filtered.append(l)
    return filtered


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


def _kind_from_watch(watch: str, text: str = "") -> str:
    lower = text.lower()
    if watch == "publications" or any(k in lower for k in PAPER_KEYWORDS):
        return "paper"
    if watch == "news":
        return "news"
    if watch == "blog":
        return "post"
    return "update"


def build_events(results: list) -> list:
    events = []
    now_ts = datetime.now(timezone.utc).timestamp()

    def _add_event(r, text, link, date_str, ts, kind=None, diff_text=None):
        if not text or len(text.strip()) < 4:
            return
        events.append({
            "scholar": r["name"],
            "scholar_url": r["url"],
            "affiliation": r.get("affiliation", ""),
            "areas": r.get("research_areas", []),
            "watch": r.get("watch", "general"),
            "kind": kind or _kind_from_watch(r.get("watch", "general"), text),
            "text": text.strip(),
            "link": link or r["url"],
            "date_str": date_str or "",
            "timestamp": ts or now_ts,
            "result_type": r.get("type", ""),
            "diff": diff_text,
        })

    for r in results:
        if r["type"] == "rss":
            for e in r.get("entries", []):
                _add_event(r, e.get("title", ""), e.get("link", r["url"]),
                           e.get("published", ""), e.get("timestamp", 0.0))
        if r.get("supplemental_entries"):
            for e in r["supplemental_entries"]:
                _add_event(r, e.get("title", ""), e.get("link", r["url"]),
                           e.get("published", ""), e.get("timestamp", 0.0), kind="post")
        if r["type"] == "changed":
            additions = _extract_new_additions(r.get("diff", ""))
            if additions:
                for add in additions[:12]:
                    _add_event(r, add, r["url"], "", _extract_timestamp_from_text(add),
                               diff_text=r.get("diff"))
            else:
                _add_event(r, "Page content updated", r["url"], "",
                           now_ts, diff_text=r.get("diff"))

    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events


def generate_report(results: list, total: int, events: list):
    updated = [r for r in results if r["type"] == "changed"]
    rss_new = [r for r in results if r["type"] == "rss"]
    first = [r for r in results if r["type"] == "first_check"]
    unchanged = [r for r in results if r["type"] in ("unchanged", "rss_no_change")]
    errors = [r for r in results if r["type"] == "error"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Scholar Monitor Report", "",
        f"**Run:** {now}  |  **Total:** {total}  |  "
        f"Events {len(events)}  |  RSS {len(rss_new)}  |  CHG {len(updated)}  |  "
        f"FIRST {len(first)}  |  OK {len(unchanged)}  |  ERR {len(errors)}", "",
    ]
    if events:
        lines += ["---", f"## Activity Feed ({len(events)})", ""]
        for ev in events[:40]:
            aff = f" [{ev['affiliation']}]" if ev.get("affiliation") else ""
            lines.append(f"- **{ev['scholar']}**{aff}: {ev['text'][:120]}")
        lines.append("")
    if errors:
        lines += ["---", f"## Needs Attention ({len(errors)})", ""]
        for r in errors:
            lines.append(f"- [{r['name']}]({r['url']}): `{r['error']}`")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return "\n".join(lines)


def _esc(text: str) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _diff_to_html(diff_text: str) -> str:
    hl = []
    for line in (diff_text or "").split("\n"):
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
    if "captcha" in ml or "人机" in msg or "bot block" in ml:
        return "Bot Blocked", "high", "🛡", "Use SerpApi or retry later"
    if "zhihu" in ml and ("auth" in ml or "cookie" in ml):
        return "Zhihu Auth", "high", "🔑", "Refresh ZHIHU_COOKIES_B64 secret"
    if "403" in msg:
        return "Access Denied", "high", "✕", "Cookie expired or blocked"
    if "404" in msg or "dead url" in ml or "not found" in ml:
        return "Dead URL", "high", "404", "Update URL in config.yaml"
    if "ssl" in ml or "certificate" in ml:
        return "SSL Error", "medium", "SSL", "Cert issue - retry next run"
    if "eof" in ml or "timeout" in ml or "connection" in ml:
        return "Network Error", "medium", "NET", "Transient - retry next run"
    if "no content" in ml or "extract" in ml:
        return "Extraction Failed", "low", "!", "Check CSS selectors"
    return "Other", "low", "?", "Check URL and config"


def _watch_icon(w: str) -> str:
    return {"blog": "📝", "news": "📢", "publications": "🎓", "general": "🌐"}.get(w, "🌐")


def _kind_label(kind: str) -> str:
    return {"paper": "论文", "post": "博客", "news": "动态", "update": "更新"}.get(kind, "更新")


def _format_event_date(ts: float, date_str: str) -> str:
    if date_str and date_str != "?":
        return date_str[:24]
    if ts and ts > 0:
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        except (OSError, ValueError):
            pass
    return ""


def _timeline_bucket(ts: float) -> str:
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).timestamp()
    month_ago = (now - timedelta(days=30)).timestamp()
    if ts >= week_ago:
        return "week"
    if ts >= month_ago:
        return "month"
    return "earlier"


def _scholar_status_summary(r: dict) -> str:
    t = r.get("type", "")
    if t == "rss":
        n = len(r.get("entries", []))
        return f"{n} new item(s)"
    if t == "changed":
        adds = _extract_new_additions(r.get("diff", ""))
        return adds[0][:80] if adds else "Content changed"
    if t == "error":
        return (r.get("error") or "Error")[:60]
    if t == "first_check":
        return "Baseline snapshot taken"
    latest = r.get("latest_entries") or []
    if latest:
        return latest[0].get("title", "")[:80]
    preview = r.get("preview") or []
    if preview:
        return preview[0][:80]
    return "No recent activity"


def generate_html_report(results: list, total: int, events: list):
    errors = [r for r in results if r["type"] == "error"]
    ok_count = sum(1 for r in results if r["type"] in ("unchanged", "rss_no_change", "first_check"))
    new_count = len(events)
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    all_affiliations = sorted({r.get("affiliation", "") for r in results if r.get("affiliation")})
    all_areas = sorted({a for r in results for a in r.get("research_areas", []) if a})

    stats_html = f"""<div class="sm-stats">
      <span class="sm-stat sm-stat-new">动态 {new_count}</span>
      <span class="sm-stat sm-stat-warn">需关注 {len(errors)}</span>
      <span class="sm-stat">学者 {total}</span>
      <span class="sm-stat sm-stat-muted">正常 {ok_count}</span>
    </div>"""

    # Filter bar
    filter_html = '<div class="sm-filters" id="filterBar">'
    filter_html += '<input type="search" id="searchInput" placeholder="搜索学者、单位、动态内容…" class="sm-search" oninput="applyFilters()">'
    filter_html += '<div class="sm-filter-row">'
    filter_html += '<span class="sm-filter-label">类型</span>'
    for k, lb in [("paper", "论文"), ("post", "博客"), ("news", "动态"), ("update", "更新")]:
        filter_html += f'<label class="sm-chip"><input type="checkbox" class="fl-kind" value="{k}" checked onchange="applyFilters()">{lb}</label>'
    filter_html += '</div>'
    if all_areas:
        filter_html += '<details class="sm-filter-more"><summary>研究方向</summary><div class="sm-filter-row">'
        for area in all_areas:
            filter_html += (
                f'<label class="sm-chip"><input type="checkbox" class="fl-area" '
                f'value="{_esc(area.lower())}" checked onchange="applyFilters()">{_esc(area)}</label>'
            )
        filter_html += '</div></details>'
    if all_affiliations:
        filter_html += '<details class="sm-filter-more"><summary>单位</summary><div class="sm-filter-row">'
        for aff in all_affiliations:
            filter_html += (
                f'<label class="sm-chip"><input type="checkbox" class="fl-aff" '
                f'value="{_esc(aff.lower())}" checked onchange="applyFilters()">{_esc(aff)}</label>'
            )
        filter_html += '</div></details>'
    filter_html += '<div class="sm-filter-count">显示 <span id="visibleCount">0</span> / <span id="totalCount">0</span> 条</div>'
    filter_html += '</div>'

    # Timeline
    buckets = {"week": [], "month": [], "earlier": []}
    bucket_labels = {"week": "本周", "month": "本月", "earlier": "更早"}
    for ev in events:
        buckets[_timeline_bucket(ev["timestamp"])].append(ev)

    timeline_html = '<section class="sm-timeline" id="timelineSection"><h2 class="sm-section-title">最近在做什么</h2>'
    if not events:
        timeline_html += (
            '<div class="sm-empty"><div class="sm-empty-title">暂无新动态</div>'
            '<div class="sm-empty-sub">上次同步以来没有检测到新的论文、博客或主页更新。</div></div>'
        )
    else:
        for key in ("week", "month", "earlier"):
            group = buckets[key]
            if not group:
                continue
            timeline_html += f'<div class="sm-tl-group" data-bucket="{key}">'
            timeline_html += f'<h3 class="sm-tl-heading">{bucket_labels[key]} <span class="sm-tl-count">{len(group)}</span></h3>'
            timeline_html += '<div class="sm-tl-list">'
            for ev in group:
                areas = ",".join(ev.get("areas", []))
                aff = _norm_str(ev.get("affiliation"))
                date_disp = _format_event_date(ev["timestamp"], ev.get("date_str", ""))
                diff_block = ""
                if ev.get("diff"):
                    diff_block = (
                        f'<details class="sm-tl-diff"><summary>查看原始 diff</summary>'
                        f'<div class="sm-diff">{_diff_to_html(ev["diff"])}</div></details>'
                    )
                timeline_html += (
                    f'<article class="sm-tl-item" data-filterable '
                    f'data-name="{_esc(ev["scholar"].lower())}" '
                    f'data-affiliation="{_esc(aff.lower())}" '
                    f'data-areas="{_esc(areas.lower())}" '
                    f'data-kind="{_esc(ev.get("kind", "update"))}" '
                    f'data-text="{_esc(ev.get("text", "").lower())}">'
                    f'<div class="sm-tl-meta">'
                    f'<span class="sm-kind sm-kind-{_esc(ev.get("kind", "update"))}">{_kind_label(ev.get("kind", "update"))}</span>'
                    f'<a href="{_esc(ev["scholar_url"])}" target="_blank" class="sm-tl-scholar">{_esc(ev["scholar"])}</a>'
                )
                if aff:
                    timeline_html += f'<span class="sm-tag sm-tag-aff">{_esc(aff)}</span>'
                for a in ev.get("areas", [])[:2]:
                    timeline_html += f'<span class="sm-tag sm-tag-area">{_esc(a)}</span>'
                if date_disp:
                    timeline_html += f'<time class="sm-tl-date">{_esc(date_disp)}</time>'
                timeline_html += '</div>'
                link = ev.get("link") or ev["scholar_url"]
                if link and link != ev["scholar_url"]:
                    timeline_html += f'<a href="{_esc(link)}" target="_blank" class="sm-tl-text">{_esc(ev["text"])}</a>'
                else:
                    timeline_html += f'<p class="sm-tl-text">{_esc(ev["text"])}</p>'
                timeline_html += diff_block + '</article>'
            timeline_html += '</div></div>'
    timeline_html += '</section>'

    # Attention section
    attention_html = ""
    if errors:
        attention_html = (
            f'<details class="sm-panel sm-panel-warn" id="attentionSection">'
            f'<summary class="sm-panel-title">需关注 ({len(errors)})</summary><ul class="sm-attn-list">'
        )
        for r in errors:
            em = r.get("error", "")
            _, _, icon, suggestion = _classify_error(em)
            aff = _norm_str(r.get("affiliation"))
            attention_html += (
                f'<li class="sm-attn-item" data-filterable data-name="{_esc(r["name"].lower())}" '
                f'data-affiliation="{_esc(aff.lower())}" '
                f'data-areas="{_esc(",".join(r.get("research_areas", [])).lower())}" '
                f'data-kind="update" data-text="{_esc(em.lower())}">'
                f'<span class="sm-attn-icon">{icon}</span>'
                f'<a href="{_esc(r["url"])}" target="_blank" class="sm-attn-name">{_esc(r["name"])}</a>'
                f'<code class="sm-attn-err">{_esc(em[:140])}</code>'
                f'<span class="sm-attn-hint">{_esc(suggestion)}</span></li>'
            )
        attention_html += '</ul></details>'

    # Directory
    dir_rows = []
    for r in sorted(results, key=lambda x: x["name"].lower()):
        status = _scholar_status_summary(r)
        st = r.get("type", "")
        st_label = {"rss": "NEW", "changed": "CHG", "error": "ERR",
                    "first_check": "INIT", "unchanged": "OK", "rss_no_change": "OK"}.get(st, st)
        areas = ",".join(r.get("research_areas") or [])
        aff = _norm_str(r.get("affiliation"))
        dir_rows.append(
            f'<tr class="sm-dir-row" data-filterable '
            f'data-name="{_esc(r["name"].lower())}" '
            f'data-affiliation="{_esc(aff.lower())}" '
            f'data-areas="{_esc(areas.lower())}" '
            f'data-kind="update" data-text="{_esc(status.lower())}">'
            f'<td><a href="{_esc(r["url"])}" target="_blank">{_esc(r["name"])}</a></td>'
            f'<td>{_esc(aff or "—")}</td>'
            f'<td>{_esc(areas.replace(",", ", ") or "—")}</td>'
            f'<td class="sm-dir-status sm-st-{st}">{st_label}</td>'
            f'<td class="sm-dir-latest">{_esc(status)}</td></tr>'
        )

    directory_html = (
        '<details class="sm-panel" id="directorySection">'
        '<summary class="sm-panel-title">全部学者目录</summary>'
        '<div class="sm-dir-wrap"><table class="sm-dir-table">'
        '<thead><tr><th>学者</th><th>单位</th><th>方向</th><th>状态</th><th>最近动态</th></tr></thead>'
        f'<tbody>{"".join(dir_rows)}</tbody></table></div></details>'
    )

    body = "\n".join([filter_html, timeline_html, attention_html, directory_html])

    template_path = Path(__file__).parent / "_report_template.html"
    if not template_path.exists():
        log("Error: HTML template not found!")
        return
    template = template_path.read_text(encoding="utf-8")
    html = (template.replace("{now}", now).replace("{total}", str(total))
            .replace("{stats_html}", stats_html).replace("{body}", body))
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(html, encoding="utf-8")
    log(f"HTML report saved to: {HTML_PATH}")


def prune_snapshots(scholars, force=False):
    valid = {_safe_name(s["name"]) for s in scholars}
    orphans = [f for f in CONTENT_DIR.glob("*.txt") if f.stem not in valid]
    if not orphans:
        log("No orphaned snapshots to prune.")
        return
    log(f"Found {len(orphans)} orphaned snapshot(s):")
    for f in orphans:
        log(f"  - {f.name}")
    if not force:
        log("(dry-run) re-run with --force to actually delete them.")
        return
    for f in orphans:
        f.unlink()
    log(f"Deleted {len(orphans)} orphaned snapshot(s).")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scholar Monitor - check scholar sites for updates.")
    parser.add_argument("--prune-snapshots", action="store_true",
                        help="Remove snapshots for scholars no longer in config.yaml (dry-run unless --force).")
    parser.add_argument("--force", action="store_true",
                        help="With --prune-snapshots, actually delete the files.")
    args = parser.parse_args()

    config = load_yaml(BASE_DIR / "config.yaml")
    scholars = config.get("scholars", [])
    if not scholars:
        log("Error: No scholars found in config.yaml")
        sys.exit(1)

    if args.prune_snapshots:
        prune_snapshots(scholars, force=args.force)
        return

    run_start = datetime.now(timezone.utc)
    rss_cache = load_yaml(RSS_CACHE_PATH)
    rss_supplemental = load_yaml(RSS_SUPPLEMENTAL_PATH)

    since = None
    if LAST_CHECKED_PATH.exists():
        try:
            since = datetime.fromisoformat(LAST_CHECKED_PATH.read_text().strip())
        except ValueError:
            pass

    log(f"Scholar Monitor - {len(scholars)} scholars to check")
    if SERPAPI_KEY:
        log("SerpApi: configured")
    else:
        log("SerpApi: not configured (Google Scholar will use direct fetch)")
    if since:
        log(f"Last check: {since}")
    else:
        log("First run - taking snapshots; no comparisons yet")
    log("")

    results = []
    for i, s in enumerate(scholars, 1):
        name = s["name"]
        print(f"  [{i:3d}/{len(scholars)}] {name:<30s}", end=" ", flush=True)
        r = check_scholar(s, rss_cache, rss_supplemental, since)
        results.append(r)
        label = {"rss": "[RSS]", "rss_no_change": "[OK]", "changed": "[CHG]",
                 "unchanged": "[OK]", "first_check": "[NEW]", "error": "[ERR]"}.get(r["type"], "?")
        print(f"{label}", flush=True)
        if r["type"] == "error":
            print(f"          -> Error: {r.get('error')}", flush=True)
        elif r["type"] == "rss":
            for e in r.get("entries", []):
                print(f"          -> {e['title']}", flush=True)

    events = build_events(results)
    report = generate_report(results, len(scholars), events)
    generate_html_report(results, len(scholars), events)

    total = len(scholars)
    errors = sum(1 for r in results if r["type"] == "error")
    if total and (errors / total) < 0.2:
        LAST_CHECKED_PATH.write_text(run_start.isoformat())
    else:
        log(f"::warning::Run had {errors}/{total} errors — NOT advancing since watermark")

    log(f"\n{'='*50}")
    log("Report:")
    log(f"{'='*50}")
    log(report)
    log(f"\nSaved to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
