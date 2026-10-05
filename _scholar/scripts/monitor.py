#!/usr/bin/env python3
"""Scholar Monitor - Check for updates on scholar websites.

Strategy per site (by watch type):
  watch=blog       -> RSS preferred, content-diff fallback
  watch=news/publications/general -> content-diff authoritative; RSS supplemental only
  google_scholar   -> SerpApi when SERPAPI_KEY set, else direct fetch + captcha detection
  zhihu            -> cookie API preferred, RSSHub fallback (RSSHUB_BASE)
"""
import calendar
import json
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
from urllib.parse import parse_qs, urlparse, urljoin

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
EVENTS_HISTORY_PATH = SNAPSHOT_DIR / "events_history.json"
HTML_PATH = BASE_DIR.parent / "scholar" / "index.html"

EVENTS_HISTORY_LIMIT = 200
EVENTS_DISPLAY_LIMIT = 150

MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
MONTH_PAT = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'


def normalize_date(d_str: str, ts: float = 0.0) -> tuple[str, float]:
    """Robust parser that standardizes any RFC 2822, ISO 8601, English or Chinese date to YYYY-MM-DD or YYYY-MM."""
    if not d_str and ts > 0:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d"), ts
    if not d_str:
        return "", ts

    d_str = str(d_str).strip()
    try:
        dt = parsedate_to_datetime(d_str)
        return dt.strftime("%Y-%m-%d"), dt.timestamp()
    except Exception:
        pass

    try:
        clean_iso = d_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_iso)
        return dt.strftime("%Y-%m-%d"), dt.timestamp()
    except Exception:
        pass

    m = re.search(rf'\b({MONTH_PAT})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+\b(202\d)\b', d_str, re.I)
    if m:
        mo = MONTH_MAP[m.group(1).lower().rstrip('.')]
        d = int(m.group(2))
        y = int(m.group(3))
        dt = datetime(y, mo, d, tzinfo=timezone.utc)
        return f"{y:04d}-{mo:02d}-{d:02d}", dt.timestamp()

    m = re.search(rf'\b({MONTH_PAT})\.?,?\s+\b(202\d)\b', d_str, re.I)
    if m:
        mo = MONTH_MAP[m.group(1).lower().rstrip('.')]
        y = int(m.group(2))
        dt = datetime(y, mo, 1, tzinfo=timezone.utc)
        return f"{y:04d}-{mo:02d}", dt.timestamp()

    m = re.search(r'\b(202\d)年(\d{1,2})月(?:(\d{1,2})日)?', d_str)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        d = int(m.group(3)) if m.group(3) else 1
        dt = datetime(y, mo, d, tzinfo=timezone.utc)
        return (f"{y:04d}-{mo:02d}-{d:02d}" if m.group(3) else f"{y:04d}-{mo:02d}"), dt.timestamp()

    m = re.search(r'\b(202\d)[-/\.](\d{1,2})[-/\.](\d{1,2})\b', d_str)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        dt = datetime(y, mo, d, tzinfo=timezone.utc)
        return f"{y:04d}-{mo:02d}-{d:02d}", dt.timestamp()

    m = re.search(r'\b(202\d)[-/\.](\d{1,2})\b', d_str)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        dt = datetime(y, mo, 1, tzinfo=timezone.utc)
        return f"{y:04d}-{mo:02d}", dt.timestamp()

    m = re.search(r'\b(\d{1,2})[-/\.](202\d)\b', d_str)
    if m:
        mo, y = int(m.group(1)), int(m.group(2))
        dt = datetime(y, mo, 1, tzinfo=timezone.utc)
        return f"{y:04d}-{mo:02d}", dt.timestamp()

    m = re.search(r'\b(202\d)\b', d_str)
    if m:
        y = int(m.group(1))
        dt = datetime(y, 6, 1, tzinfo=timezone.utc)
        return f"{y:04d}", dt.timestamp()

    if ts > 0:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d"), ts

    return d_str[:10], ts

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

    # Last resort fallback: try curl if available
    try:
        import subprocess
        cmd = ["curl", "-s", "-L", "--max-time", str(max(timeout, 15)), url]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and len(res.stdout.strip()) > 30:
            class DummyResp:
                def __init__(self, text):
                    self.text = text
                    self.status_code = 200
                def raise_for_status(self):
                    pass
            return DummyResp(res.stdout)
    except Exception:
        pass

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
        "site_type": scholar.get("site_type", ""),
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

        latest = [dict(e) for e in valid_entries[:10]]
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
    from bs4 import Comment, NavigableString
    chunks = []

    def walk(node):
        if isinstance(node, Comment):
            return
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
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if _NOISE_LINE_DATE.match(s) or _NOISE_LINE_NUM.match(s) or _NOISE_LINE_HEX.match(s):
            continue
        out.append(s)
    return "\n".join(out)


SECTION_BLACKLIST_KEYWORDS = [
    'about me', 'about', 'bio', 'biography', 'short bio', 'personal',
    'research interest', 'research focus', 'research statement', 'overview',
    'education', 'educations', 'academic background',
    'experience', 'working experience', 'work experience', 'internship', 'employment',
    'service', 'services', 'academic service', 'professional service', 'activities',
    'teaching', 'current teaching', 'past teaching', 'course', 'courses', 'evaluations',
    'mentoring', 'alumni', 'student', 'students', 'group', 'research group', 'team', 'members',
    'award', 'awards', 'honor', 'honors', 'fellowship', 'scholarship', 'grant', 'grants',
    'invited talk', 'talks', 'recent talks', 'presentation', 'presentations',
    'quote', 'quotes', 'favorite quotes',
    'connect', 'contact', 'contact me', 'links', 'comments', 'visitors',
    'repositories', 'open source', 'misc', 'miscs', 'miscellaneous',
]

SECTION_WHITELIST_KEYWORDS = [
    'news', 'recent news', 'latest news', 'highlights', 'updates',
    'publication', 'publications', 'selected publication', 'selected publications',
    'paper', 'papers', 'selected paper', 'selected papers',
    'preprint', 'preprints', 'conference', 'journal', 'refereed',
    'project', 'projects', 'research project', 'research projects',
    'selected work', 'work',
]


def _is_blacklisted_academic_heading(text: str, tag_id: str = '', tag_cls: str = '') -> bool:
    combined = f"{text} {tag_id} {tag_cls}".lower().strip()
    for w in SECTION_WHITELIST_KEYWORDS:
        if w in combined:
            return False
    for b in SECTION_BLACKLIST_KEYWORDS:
        if re.search(r'\b' + re.escape(b) + r'\b', combined):
            return True
    return False


def _clean_academic_soup(soup: BeautifulSoup) -> None:
    """Decompose non-publication/news sections (Bio, Interests, Teaching, Service, etc.) in-place."""
    from bs4 import Tag
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'heading']
    for h in soup.find_all(heading_tags):
        if not h.parent:
            continue
        txt = h.get_text(strip=True)
        hid = h.get('id', '')
        hcls = ' '.join(h.get('class', [])) if h.get('class') else ''
        if _is_blacklisted_academic_heading(txt, hid, hcls):
            curr = h.next_sibling
            while curr:
                nxt = curr.next_sibling
                if isinstance(curr, Tag):
                    if curr.name in heading_tags:
                        curr_txt = curr.get_text(strip=True)
                        curr_id = curr.get('id', '')
                        curr_cls = ' '.join(curr.get('class', [])) if curr.get('class') else ''
                        if not _is_blacklisted_academic_heading(curr_txt, curr_id, curr_cls):
                            break
                    curr.decompose()
                curr = nxt
            h.decompose()


def extract_content(html: str, selectors: list = None, remove_selectors: list = None, watch: str = "general", scholar: dict = None) -> str:
    soup = BeautifulSoup(html, "html.parser")
    from bs4 import Comment
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    for sel in (DEFAULT_REMOVE_SELECTORS + (remove_selectors or [])):
        for el in soup.select(sel):
            el.decompose()

    url = (scholar.get("url", "") if scholar else "")
    name = (scholar.get("name", "") if scholar else "")
    is_academic = (
        (scholar and scholar.get("category") == "HomePage")
        or (scholar and scholar.get("site_type") in ("github_pages", "personal_website", "google_sites"))
        or any(d in url for d in ("github.io", "sites.google.com", "edu.cn", "berkeley.edu", "tsinghua.edu.cn", "mit.edu"))
    )

    # Special handling for Google Sites
    if "sites.google.com/site/mathshenli" in url or "沈立" in name:
        texts = []
        for h2 in soup.find_all("h2"):
            t = h2.get_text().lower()
            if any(k in t for k in ("conference", "journal", "thesis")):
                parent = h2.parent
                if parent:
                    texts.append(get_clean_text_custom(parent))
        if texts:
            return "\n\n".join(texts)

    if "sites.google.com/view/kesun" in url or "孙科" in name:
        for sec in soup.find_all("section"):
            t = sec.get_text().lower()
            if any(k in t for k in ("selected preprints", "curverl", "selectedpreprint", "publications")):
                return get_clean_text_custom(sec)

    # Multi-element selector matching
    BROAD_FALLBACKS = {"article", "main", ".post", ".content", "#content", ".entry-content", ".page__content", "#main", "body"}

    if selectors:
        specific_sels = [s for s in selectors if s not in BROAD_FALLBACKS]
        fallback_sels = [s for s in selectors if s in BROAD_FALLBACKS]

        extracted_parts = []
        for sel in specific_sels:
            for el in soup.select(sel):
                t = get_clean_text_custom(el)
                if len(t) >= 5 and t not in extracted_parts:
                    extracted_parts.append(t)
        if extracted_parts:
            return "\n\n".join(extracted_parts)

        if is_academic:
            _clean_academic_soup(soup)

        for sel in fallback_sels:
            for el in soup.select(sel):
                t = get_clean_text_custom(el)
                if len(t) >= 15:
                    return t

    targeted = NEWS_SELECTORS if watch == "news" else PUB_SELECTORS if watch == "publications" else []
    for sel in targeted:
        el = soup.select_one(sel)
        if el:
            t = get_clean_text_custom(el)
            if len(t) >= 20:
                return t

    if is_academic:
        _clean_academic_soup(soup)

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


def _publication_title_key(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip().lower())


def _parse_publications_snapshot(text: str) -> list:
    """Parse snapshot text produced by _publications_to_text into publication dicts."""
    lines = [l.strip() for l in (text or "").split("\n") if l.strip()]
    pubs = []
    i = 0
    while i < len(lines):
        title = lines[i]
        i += 1
        authors = ""
        if i < len(lines) and not re.search(r"\b20\d{2}\b", lines[i]):
            authors = lines[i]
            i += 1
        venue, year = "", ""
        if i < len(lines):
            m = re.search(r"^(.+?)\s+(20\d{2})\s*$", lines[i])
            if m:
                venue, year = m.group(1).strip(" ,"), m.group(2)
                i += 1
        pubs.append({"title": title, "authors": authors, "publication": venue, "year": year})
    return pubs


def _normalize_serpapi_article(article: dict) -> dict:
    raw_authors = article.get("authors", "")
    if isinstance(raw_authors, list):
        authors = ", ".join(
            a.get("name", "") if isinstance(a, dict) else str(a)
            for a in raw_authors[:6]
        )
    else:
        authors = str(raw_authors or "")
    year = str(article.get("year") or article.get("article_year") or "")
    link = article.get("link") or ""
    if not link and article.get("citation_id"):
        link = f"https://scholar.google.com/citations?view_op=view_citation&citation_for_view={article['citation_id']}"
    return {
        "title": article.get("title", ""),
        "authors": authors,
        "publication": article.get("publication", "") or "",
        "year": year,
        "link": link,
    }


def _format_publication_event(pub: dict) -> str:
    title = (pub.get("title") or "").strip()
    pub_venue = (pub.get("publication") or "").strip(" ,")
    pub_year = str(pub.get("year") or "").strip()

    if pub_venue:
        # Remove page numbers like ", 122493-122531" or ", 8425-8428"
        pub_venue = re.sub(r',\s*\d+-\d+\b', '', pub_venue)
        # Deduplicate year inside venue like "2026, 2026"
        pub_venue = re.sub(r'(\b202\d\b)(?:[,\s]+\1)+', r'\1', pub_venue)

    meta = []
    if pub_venue:
        meta.append(pub_venue)
    if pub_year and pub_year not in pub_venue:
        meta.append(pub_year)
    if meta:
        return f"{title} · {', '.join(meta)}"
    return title


def _year_to_timestamp(year) -> float:
    now_dt = datetime.now(timezone.utc)
    try:
        y = int(str(year).strip())
        if 1900 <= y <= now_dt.year:
            return min(datetime(y, 6, 1, tzinfo=timezone.utc).timestamp(), now_dt.timestamp())
    except (ValueError, TypeError):
        pass
    return now_dt.timestamp()


def _is_google_scholar_result(result: dict) -> bool:
    if result.get("site_type") == "google_scholar":
        return True
    return "scholar.google.com/citations" in (result.get("url") or "")


def _sort_publications_by_year_desc(pubs: list) -> list:
    def _extract_yr(p):
        for f in (p.get("year"), p.get("publication"), p.get("title")):
            if f:
                m = re.search(r'\b(20\d{2})\b', str(f))
                if m:
                    return int(m.group(1))
        return 0
    return sorted(pubs, key=_extract_yr, reverse=True)


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
                    "sort": "pubdate",
                    "num": 20,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            articles = [_normalize_serpapi_article(a) for a in data.get("articles", [])]
            articles = _sort_publications_by_year_desc(articles)
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
            result["latest_entries"] = [
                {
                    "title": _format_publication_event(a),
                    "link": a.get("link") or url,
                    "published": str(a.get("year") or "2026"),
                    "timestamp": _extract_timestamp_from_text(f"{a.get('publication', '')} {a.get('year', '')}"),
                }
                for a in articles[:10]
            ]
            prev = load_snapshot(scholar["name"])
            if prev is None:
                save_snapshot(scholar["name"], content)
                result["type"] = "first_check"
                return result
            prev_titles = {
                _publication_title_key(p["title"])
                for p in _parse_publications_snapshot(prev)
            }
            new_articles = [
                a for a in articles
                if _publication_title_key(a.get("title", "")) not in prev_titles
            ]
            prev_norm = _normalize_for_diff(prev)
            content_norm = _normalize_for_diff(content)
            if not new_articles and prev_norm == content_norm:
                result["type"] = "unchanged"
                return result
            save_snapshot(scholar["name"], content)
            if new_articles:
                result["type"] = "changed"
                result["new_publications"] = new_articles
            else:
                result["type"] = "unchanged"
            return result
        except Exception as e:
            log(f"      ↳ SerpApi failed, falling back to snapshot / direct fetch: {e}")

    # Snapshot fallback if SerpApi is unavailable or blocked
    prev = load_snapshot(scholar["name"])
    if prev:
        pubs = _parse_publications_snapshot(prev)
        pubs = _sort_publications_by_year_desc(pubs)
        if pubs:
            result["preview"] = [p.get("title", "") for p in pubs[:3] if p.get("title")]
            result["latest_entries"] = [
                {
                    "title": _format_publication_event(p),
                    "link": p.get("link") or url,
                    "published": str(p.get("year") or "2026"),
                    "timestamp": _extract_timestamp_from_text(f"{p.get('publication', '')} {p.get('year', '')}"),
                }
                for p in pubs[:10]
            ]
            result["type"] = "unchanged"
            return result

    # Direct fetch fallback
    return _content_diff_check(scholar, since, result)


def check_zifeng_wang(scholar: dict, since: datetime | None) -> dict:
    result = _scholar_base_result(scholar)
    url = scholar["url"]
    js_url = "https://zifengwang.me/js/publications.js"
    js_text = ""
    try:
        resp = fetch(js_url, timeout=20)
        js_text = resp.text
    except Exception as e:
        log(f"      ↳ Fetch zifeng publications.js failed: {e}")

    prev = load_snapshot(scholar["name"])
    pubs = []
    if js_text:
        entries = re.split(r'\{\s*title:', js_text)[1:]
        for e in entries:
            m_title = re.search(r'^\s*\"([^\"]+)\"', e)
            title = m_title.group(1) if m_title else ''
            m_auth = re.search(r'authors:\s*\"([^\"]+)\"', e)
            authors = m_auth.group(1) if m_auth else ''
            m_abbr = re.search(r'abbreviation:\s*\"([^\"]+)\"', e)
            abbr = m_abbr.group(1) if m_abbr else ''
            m_full = re.search(r'fullName:\s*\"([^\"]+)\"', e)
            full = m_full.group(1) if m_full else ''
            m_year = re.search(r'year:\s*(\d{4})', e)
            year = m_year.group(1) if m_year else ''
            m_link = re.search(r'paperLink:\s*\"([^\"]+)\"', e)
            link = m_link.group(1) if m_link else ''
            venue = abbr or full
            if title:
                pubs.append({
                    'title': title,
                    'authors': authors,
                    'publication': venue,
                    'year': year,
                    'link': link
                })
    elif prev:
        pubs = _parse_publications_snapshot(prev)

    pubs = _sort_publications_by_year_desc(pubs)
    if not pubs:
        result["type"] = "error"
        result["error"] = "Failed to parse publications for 王子峰"
        return result

    content = _publications_to_text(pubs)
    result["preview"] = [p.get("title", "") for p in pubs[:3] if p.get("title")]
    result["latest_entries"] = [
        {
            "title": _format_publication_event(p),
            "link": p.get("link") or url,
            "published": str(p.get("year") or "2026"),
            "timestamp": _extract_timestamp_from_text(f"{p.get('publication', '')} {p.get('year', '')}"),
        }
        for p in pubs[:10]
    ]

    if prev is None:
        save_snapshot(scholar["name"], content)
        result["type"] = "first_check"
        return result

    prev_norm = _normalize_for_diff(prev)
    content_norm = _normalize_for_diff(content)
    if prev_norm == content_norm:
        result["type"] = "unchanged"
        return result

    save_snapshot(scholar["name"], content)
    result["type"] = "changed"
    diff = list(unified_diff(
        prev_norm.split("\n"), content_norm.split("\n"),
        fromfile=f"{_safe_name(scholar['name'])} (previous)",
        tofile=f"{_safe_name(scholar['name'])} (current)", lineterm=""))
    result["diff"] = "\n".join(diff[:150])
    return result


def extract_entries_from_html(html: str, scholar: dict) -> list:
    name = scholar.get("name", "")
    base_url = scholar.get("url", "")
    soup = BeautifulSoup(html, "html.parser")
    entries = []

    # 1. 柠檬CC
    if "柠檬" in name or "limoncc" in base_url:
        for art in soup.select("article"):
            t_el = art.select_one("h2, h3, .post-title")
            l_el = art.select_one("h2 a, h3 a, a[href*='/post/']")
            time_el = art.select_one("time")
            if t_el:
                title = _clean_paper_entry(t_el.get_text(strip=True))
                link = urljoin(base_url, l_el["href"]) if l_el else base_url
                d = time_el.get_text(strip=True) if time_el else ""
                ts, ds = _extract_timestamp_and_date(d)
                entries.append({"title": title, "link": link, "published": ds or d or "2026", "timestamp": ts or 0.0})
        return entries[:10]

    # 2. DaNing Blog
    if "DaNing" in name or "adaning" in base_url:
        for a in soup.select("a[href*='/posts/']"):
            t = a.get_text(strip=True)
            if t and t != "阅读更多" and len(t) > 3:
                link = urljoin(base_url, a["href"])
                entries.append({"title": _clean_paper_entry(t), "link": link, "published": "2026", "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()})
        return entries[:10]

    # 3. A. Weers Blog
    if "aweers" in base_url or "A. Weers" in name:
        for art in soup.select(".post-entry, article"):
            t_el = art.select_one("h2 a, h3 a, h2, h3")
            l_el = art.select_one("h2 a, h3 a, a[href*='/blog/']")
            meta_el = art.select_one(".post-meta, time")
            if t_el:
                title = _clean_paper_entry(t_el.get_text(strip=True))
                link = urljoin(base_url, l_el["href"]) if l_el else base_url
                d = meta_el.get_text(strip=True) if meta_el else ""
                ts, ds = _extract_timestamp_and_date(d)
                entries.append({"title": title, "link": link, "published": ds or "2026", "timestamp": ts})
        return entries[:10]

    # 4. plmblog
    if "plmsmile" in base_url or "plmblog" in name:
        for card in soup.select(".post-card, .archive-item"):
            t_el = card.select_one("a.post-title, .post-title a, a[href*='/posts/']")
            if t_el:
                title = _clean_paper_entry(t_el.get_text(strip=True))
                link = urljoin(base_url, t_el.get("href", ""))
                entries.append({"title": title, "link": link, "published": "2026", "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()})
        return entries[:10]

    # Generic selectors fallback with urljoin
    selectors = scholar.get("selectors", [])
    for sel in selectors:
        if sel in ["article", "main", ".content", "#content", "body"]:
            continue
        for el in soup.select(sel):
            txt = el.get_text(" ", strip=True)
            if not txt or len(txt) < 8 or _is_tag_or_noise_line(txt, name):
                continue
            clean_t = _clean_paper_entry(txt)
            best_link = base_url
            a_el = el.find("a", href=True) if el.name != "a" else el
            if a_el and a_el.get("href"):
                best_link = urljoin(base_url, a_el["href"])
            ts, ds = _extract_timestamp_and_date(txt)
            entries.append({"title": clean_t, "link": best_link, "published": ds or "2026", "timestamp": ts or 0.0})
            if len(entries) >= 10:
                break
        if entries:
            break

    return entries[:10]


def extract_scholar_latest_entries(content: str, scholar: dict) -> list:
    if not content:
        return []
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    scholar_name = scholar.get("name", "")
    url = scholar.get("url", "")
    candidates = []

    for i, line in enumerate(lines):
        clean_l = _clean_html(line)
        clean_l = re.sub(r'202\s*([4567])', r'202\1', clean_l)
        lower_l = clean_l.lower()

        # Check if line contains 2026 (or 2025)
        if re.search(r'\b2026\b', clean_l):
            is_venue = any(v in lower_l for v in ['icml', 'iclr', 'neurips', 'cvpr', 'eccv', 'acl', 'emnlp', 'aaai', 'ijcv', 'tkde', 'published in', 'accepted']) and len(clean_l) < 90
            if is_venue:
                title = None
                for back in range(i - 1, max(-1, i - 5), -1):
                    cand = lines[back].strip()
                    if len(cand) > 10 and not _is_tag_or_noise_line(cand, scholar_name) and not _is_bio_or_profile_line(cand):
                        if not re.search(r'^[A-Z][a-z]+ [A-Z][a-z]+.*,', cand) and not any(k in cand.lower() for k in ['author', 'co-first', 'download paper', '[ paper ]']):
                            title = cand
                            break
                if title:
                    entry_text = f"{title} · {clean_l}"
                    ts, ds = _extract_timestamp_and_date(clean_l)
                    candidates.append((ts, ds, entry_text))
                    continue

            if len(clean_l) >= 15 and not _is_tag_or_noise_line(clean_l, scholar_name) and not _is_bio_or_profile_line(clean_l):
                ts, ds = _extract_timestamp_and_date(clean_l)
                candidates.append((ts, ds, clean_l))

        elif re.search(r'\b2025\b', clean_l):
            is_venue = any(v in lower_l for v in ['icml', 'iclr', 'neurips', 'cvpr', 'eccv', 'acl', 'emnlp', 'aaai', 'ijcv', 'tkde', 'published in', 'accepted']) and len(clean_l) < 90
            if is_venue:
                title = None
                for back in range(i - 1, max(-1, i - 5), -1):
                    cand = lines[back].strip()
                    if len(cand) > 10 and not _is_tag_or_noise_line(cand, scholar_name) and not _is_bio_or_profile_line(cand):
                        if not re.search(r'^[A-Z][a-z]+ [A-Z][a-z]+.*,', cand) and not any(k in cand.lower() for k in ['author', 'co-first', 'download paper', '[ paper ]']):
                            title = cand
                            break
                if title:
                    entry_text = f"{title} · {clean_l}"
                    ts, ds = _extract_timestamp_and_date(clean_l)
                    candidates.append((ts, ds, entry_text))
                    continue

            if len(clean_l) >= 20 and not _is_tag_or_noise_line(clean_l, scholar_name) and not _is_bio_or_profile_line(clean_l):
                ts, ds = _extract_timestamp_and_date(clean_l)
                candidates.append((ts, ds, clean_l))

    seen_texts = set()
    unique_cands = []
    for ts, ds, text in sorted(candidates, key=lambda x: x[0], reverse=True):
        norm_t = re.sub(r'[\W_]+', '', text.lower())[:50]
        if norm_t in seen_texts:
            continue
        seen_texts.add(norm_t)
        unique_cands.append({
            "title": text,
            "link": url,
            "published": ds,
            "timestamp": ts,
        })

    return unique_cands[:10]


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
        cl = re.sub(r'<[^>]+>', '', l).strip()
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
            resp.text, scholar.get("selectors"), scholar.get("remove_selectors"), watch=watch, scholar=scholar)
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
    html_entries = extract_entries_from_html(resp.text, scholar)
    if html_entries:
        result["latest_entries"] = html_entries
    else:
        result["latest_entries"] = extract_scholar_latest_entries(content, scholar)
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

    if site_type == "zifeng_wang" or "zifengwang.me" in url:
        return check_zifeng_wang(scholar, since)

    if site_type == "google_scholar" or "scholar.google.com/citations" in url:
        return check_google_scholar(scholar, since)

    if "zhihu.com" in url:
        return check_zhihu_scholar(scholar, since)

    result = _scholar_base_result(scholar)
    blog_mode = _is_blog_watch(scholar)

    if blog_mode:
        rss_url = scholar.get("rss_url") or rss_cache.get(name) or rss_supplemental.get(name)
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


PAPER_TITLE_WORDS = {
    'learning', 'models', 'model', 'neural', 'deep', 'network', 'networks',
    'reasoning', 'framework', 'approach', 'optimization', 'representations',
    'representation', 'transformers', 'transformer', 'reinforcement',
    'continual', 'multimodal', 'generative', 'adaptation', 'adapter',
    'prompt', 'instruction', 'tuning', 'scaling', 'agent', 'agents',
    'diffusion', 'vision', 'language', 'knowledge', 'retrieval',
    'efficient', 'robust', 'defense', 'attack', 'distillation', 'survey',
    'rethinking', 'reweighting', 'tree', 'anchoring', 'hierarchical',
    'curverl', 'dynaflip', 'reid', 'flexcover', 'rotvla'
}

NEWS_VERBS_REGEX = re.compile(
    r'\b(?:is accepted|are accepted|accepted to|accepted by|organizing|invited to|'
    r'serving as|serve as|released|open-sourced|we propose|we study|we introduce|'
    r'congrats to|congratulations)\b', re.I
)

SECTION_HEADERS = {
    "research interests", "selected papers", "selected publications",
    "publications", "preprints", "conference paper", "conference papers",
    "journal papers", "journal articles", "all papers", "latest news",
    "recent news", "news", "updates", "biography", "short bio", "bio",
    "awards", "honors", "services", "professional activities", "teaching",
    "talks", "invited talks", "experiences", "work experience", "education",
    "patents", "students", "team", "group", "contact", "links",
    "favorite quotes", "open source", "projects", "selected projects",
    "recent updates", "recent activities", "activity", "activities",
    "selected preprints / publications"
}

BUTTON_KEYWORDS = [
    'pdf', 'paper', 'code', 'project', 'project page', 'bib', 'slides',
    'model', 'media', 'demo', 'video', 'website', 'talk', 'poster', 'arxiv',
    'dataset', 'doc', 'docs', 'review', 'github'
]

STATUS_LINE_KEYWORDS = [
    'oral presentation', 'spotlight presentation', 'poster presentation',
    'oral', 'spotlight', 'poster', 'esi highly cited paper', 'esi hot cited paper',
    'top-3 most influential ijcai papers'
]

VENUE_PATTERNS = [
    r'(?:advances in\s+)?neural information processing systems(?:\s*\(\s*neurips\s*\))?',
    r'neurips(?:\'?\d{2,4})?',
    r'international conference on machine learning(?:\s*\(\s*icml\s*\))?',
    r'icml(?:\'?\d{2,4})?',
    r'international conference on learning representations(?:\s*\(\s*iclr\s*\))?',
    r'iclr(?:\'?\d{2,4})?',
    r'(?:ieee\s+)?conference on computer vision and pattern recognition(?:\s*\(\s*cvpr\s*\))?',
    r'cvpr(?:\'?\d{2,4})?',
    r'international conference on computer vision(?:\s*\(\s*iccv\s*\))?',
    r'iccv(?:\'?\d{2,4})?',
    r'european conference on computer vision(?:\s*\(\s*eccv\s*\))?',
    r'eccv(?:\'?\d{2,4})?',
    r'(?:ieee\s+)?transactions on [a-zA-Z\s]+(?:\s*\([a-zA-Z\s]+\))?',
    r'tpami(?:\'?\d{2,4})?',
    r'international joint conference on artificial intelligence(?:\s*\(\s*ijcai\s*\))?',
    r'ijcai(?:\'?\d{2,4})?',
    r'conference on robot learning(?:\s*\(\s*corl\s*\))?',
    r'corl(?:\'?\d{2,4})?',
    r'proceedings of (?:the\s+)?[a-zA-Z0-9\s,\-]+(?:conference|symposium|workshop)',
    r'in proceedings of (?:the\s+)?[a-zA-Z0-9\s,\-]+',
    r'acm multimedia(?:\s*\(\s*acm mm\s*\))?',
    r'acm mm(?:\'?\d{2,4})?',
    r'emnlp(?:\'?\d{2,4})?',
    r'acl(?:\'?\d{2,4})?',
    r'aaai(?:\'?\d{2,4})?',
    r'arxiv(?::\d+|\s+20\d\d)?',
    r'international journal of computer vision(?:\s*\(\s*ijcv\s*\))?',
    r'ijcv(?:\'?\d{2,4})?',
    r'nature\s+(?:communications|machine intelligence|biotechnology|methods|machine learning)',
    r'patterns(?:\s*,\s*cover paper)?',
]


def _clean_html(text: str) -> str:
    clean = re.sub(r'<[^>]+>', '', text).strip()
    clean = re.sub(r'^(?:\"?>|>|\"|<a\b[^>]*>|</a>|</?[a-z0-9]+[^>]*>)', '', clean).strip()
    return clean


def _clean_paper_entry(text: str) -> str:
    if not text:
        return ""
    clean = _clean_html(text).strip()

    # 1. Format "(Venue) ... 'Title'" into "Title · Venue"
    m = re.match(r'^\s*\(([^)]+)\)\s*[-:]?\s*.*?"([^"]{8,})"', clean)
    if m:
        venue_tag = m.group(1).strip()
        title = m.group(2).strip()
        clean = f"{title} · {venue_tag}"

    # 2. Strip BibTeX blocks
    clean = re.sub(r'Bib\s*@article\s*\{.*$', '', clean, flags=re.DOTALL | re.I).strip()

    # 3. Handle multi-event concatenations (e.g. 冯钰捷 or 庄辉平)
    if '!' in clean and re.search(r'!\s*202\d', clean):
        clean = re.split(r'!\s*202\d', clean)[0].strip() + "!"

    # 4. Strip leading date prefixes like [2026-09], 2026.07:, 09.2026,, 2026/09
    clean = re.sub(r'^\s*\[?\s*202\d[-\./]\d{1,2}(?:[-\./]\d{1,2})?\s*\]?\s*[\:\,\-—·]?\s*', '', clean)
    clean = re.sub(r'^\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+202\d\s*[\:\,\-—·]?\s*', '', clean, flags=re.I)
    clean = re.sub(r'^\s*202\d\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}\s*[\:\,\-—·]?\s*', '', clean, flags=re.I)
    clean = re.sub(r'^\s*\d{1,2}[-\./]202\d\s*[\:\,\-—·]?\s*', '', clean)
    clean = re.sub(r'^\s*\d{1,2}\s*[💼😋🎉🔥✨]?\s*(?:Activity|Accepted)?\s*', '', clean)
    clean = re.sub(r'^\s*2025\s*年\s*\d{1,2}\s*月随笔\s*', '随笔', clean)

    # 5. Strip leading citation numbers like [7], [1], 1., 7.
    clean = re.sub(r'^\s*\[\s*\d+\s*\]\s*', '', clean)
    clean = re.sub(r'^\s*\d+\.\s+', '', clean)

    # Normalize verbose Google Scholar / DBLP proceedings titles to standard venue names
    clean = re.sub(r'Proceedings of (?:the )?(?:IEEE/CVF )?(?:Winter )?Conference on Applications of Computer Vision(?:\s*\(WACV\))?', 'WACV', clean, flags=re.I)
    clean = re.sub(r'Advances in Neural Information Processing Systems\s*(?:\d+)?', 'NeurIPS', clean, flags=re.I)
    clean = re.sub(r'International Conference on Learning Representations', 'ICLR', clean, flags=re.I)
    clean = re.sub(r'International Conference on Machine Learning', 'ICML', clean, flags=re.I)
    clean = re.sub(r'IEEE/CVF Conference on Computer Vision and Pattern Recognition', 'CVPR', clean, flags=re.I)
    clean = re.sub(r'International Conference on Computer Vision(?:\s*\(ICCV\s*\d{4}\))?', 'ICCV', clean, flags=re.I)
    clean = re.sub(r'European Conference on Computer Vision(?:\s*\(ECCV\s*\d{4}\))?', 'ECCV', clean, flags=re.I)
    clean = re.sub(r'Annual Meeting of the Association for Computational Linguistics', 'ACL', clean, flags=re.I)
    clean = re.sub(r'Conference on Empirical Methods in Natural Language Processing', 'EMNLP', clean, flags=re.I)
    clean = re.sub(r'(?:\d+(?:st|nd|rd|th)\s+)?(?:ACM\s+)?(?:SIGKDD|KDD)\s+Conference\s+on\s+Knowledge\s+Discovery\s+and\s+Data\s+Mining', 'SIGKDD', clean, flags=re.I)
    clean = re.sub(r'arXiv\s+preprint\s+arXiv:\d+\.\d+', 'arXiv', clean, flags=re.I)

    # 6. Embedded author lists before venue (e.g. 黄家斌, 孙宇, 吴太强, 冯亮)
    clean = re.sub(r'\s*\([^)]*Co-first Author[^)]*\)', '', clean, flags=re.I)
    clean = re.sub(r'\s*\(\*:\s*core contributors\)', '', clean, flags=re.I)
    m_venue = re.search(r'\b(NeurIPS|ICML|ICLR|CVPR|ECCV|ICCV|ACL|EMNLP|COLM|AAAI|KDD|SIGKDD|WACV|IJCV|TPAMI|TKDE|arXiv|Proceedings of|International Conference)\b.*', clean, re.I)
    if m_venue and m_venue.start() > 25:
        prefix = clean[:m_venue.start()].strip()
        venue_suffix = clean[m_venue.start():].strip()
        m_authors = re.search(r'^(.*?)\s+([A-Z][a-z]+ [A-Z][a-z]+[\s\*\,\.\-]+(?:[A-Z][a-z]+ [A-Z][a-z]+|\bet al\b).*)$', prefix)
        if m_authors and len(m_authors.group(1)) > 15:
            clean = f"{m_authors.group(1).strip()} · {venue_suffix}"

    # 7. Strip leading author patterns: "Author1*, Author2 . Paper Title"
    m_auth = re.match(r'^[A-Z][a-zA-Z\s\*\,\.\-]+?\s*[\.\:\-]\s*([A-Z].+)$', clean)
    if m_auth and len(m_auth.group(1)) > 15:
        left = clean[:m_auth.start(1)]
        if any(c in left for c in ["*", "et al", "Sun", "Zhou", "Zhao", "Li", "Wang", "Zhang", "Chen", "Huang"]):
            clean = m_auth.group(1)

    # 8. Strip trailing buttons
    clean = re.sub(r'\s*\[\s*(?:Code|PDF|Project|Zhihu|BibTeX|Paper|Download|HuggingFace|Slide|Slides|Weights|page|Paper \(PDF\)|Project page)\b[^\]]*\]\s*', '', clean, flags=re.I)
    clean = re.sub(r'\bDownload Paper\b', '', clean, flags=re.I)

    # 9. Strip decorative emoji at start or end
    clean = re.sub(r'^[\s🔥✨💡👉🔗🎉📘💼]+', '', clean)
    clean = re.sub(r'[\s🔥✨💡👉🔗🎉📘💼]+$', '', clean)

    # 10. Strip Google Scholar page ranges like ", 122493-122531" or ", 8425-8428"
    clean = re.sub(r',\s*\d+-\d+\b', '', clean)

    # 11. Deduplicate repeated year patterns like ", 2026, 2026" or " 2026 2026"
    clean = re.sub(r'(\b202\d\b)(?:[,\s]+\1)+', r'\1', clean)
    clean = re.sub(r'\b202\d\s+(202\d)\b', r'\1', clean)
    clean = re.sub(r'·\s*([^·]+)\s*,\s*(202\d)\s*,\s*\2', r'· \1, \2', clean)
    clean = clean.replace("↗", "").strip()

    return clean.strip()


def _extract_base_title(text: str) -> str:
    """Extract stripped, normalized semantic core of paper title for deduplication."""
    if not text:
        return ""
    t = _clean_paper_entry(text)
    # Strip common leading announcement prefixes:
    t = re.sub(r'^(?:Our team\s+)?(?:released|open-sourced|published|open-sourced model)\s+', '', t, flags=re.I)
    t = re.sub(r'^(?:One|Two|Three|Several of our)\s+papers?\s+(?:are|have been|is)\s+accepted\s+(?:to|by)\s+[A-Za-z0-9\s]+\.?\s*', '', t, flags=re.I)
    t = re.sub(r'^Our\s+paper\s+on\s+.*?\s+(?:has been|is)\s+accepted\s+(?:by|to)\s+[A-Za-z0-9\s]+\.?\s*', '', t, flags=re.I)
    t = re.sub(r'^Excited that .*? papers were accepted to\s+[A-Za-z0-9\s]+\.?\s*', '', t, flags=re.I)
    t = re.sub(r'^(?:Oral|Spotlight|Highlight|Poster|Paper)\s*[-:·•]\s*', '', t, flags=re.I)

    # Strip venue suffix: " · NeurIPS 2026", " - ICML 2026", " @ CVPR 2026", " in Nature", etc.
    t = re.sub(r'\s*[·•|@-]\s*(?:NeurIPS|ICML|ICLR|CVPR|ECCV|ICCV|ACL|EMNLP|COLM|AAAI|KDD|SIGKDD|WACV|IJCV|TPAMI|TKDE|arXiv|JASA|SIGIR|ACM MM|WWW|TMLR|Nature Communications|Patterns|IEEE TPAMI|Oral|Spotlight|Highlight).*$', '', t, flags=re.I)
    t = re.sub(r'[\s,]+202\d\b.*$', '', t)
    return re.sub(r'[\W_]+', '', t.lower())


def _is_html_or_artifact_noise(text: str) -> bool:
    raw = text.strip()
    if raw.startswith('">') or raw.startswith('="') or raw.startswith("'>") or raw.startswith('href="'):
        return True
    clean = _clean_html(text)
    if not clean or len(clean) < 4:
        return True
    if clean.startswith('">') or clean.startswith('="') or clean.startswith('href="'):
        return True
    if re.match(r'^html\b', clean, re.I):
        return True
    if re.search(r'https?://[^\s]+', clean) and len(clean.split()) <= 2:
        return True
    if re.match(r'^(?:email|e-mail|contact|tel|phone|office|fax|address)\s*:', clean, re.I):
        return True
    if '[at]' in clean.lower() and len(clean.split()) <= 4:
        return True
    return False


def _is_author_list_line(text: str) -> bool:
    clean = _clean_html(text)
    # Negative checks:
    if re.search(r'["“「][^"”」]{8,}["”」]', clean):
        return False
    if NEWS_VERBS_REGEX.search(clean):
        return False
    clean_words = set(re.findall(r'[a-zA-Z]{3,}', clean.lower()))
    if any(w in PAPER_TITLE_WORDS for w in clean_words):
        return False
    if re.match(r'^(?:\[\d{4}[-/.]\d{1,2}\]|\d{1,2}[-/.]\d{4}|\d{4}[-/.]\d{1,2})', clean):
        return False

    simplified = re.sub(r'\$[^$]+?\$', '', clean)
    simplified = re.sub(r'\^\{?[^}]*\}?', '', simplified)
    simplified = re.sub(r'\\(?:ast|dagger|ddagger|star)\b', '', simplified)
    simplified = re.sub(r'\b(?:et al\.?|\(equal contribution\)|\*: core contributors|core contributors|equal advising)\b', '', simplified, flags=re.I)
    simplified = re.sub(r'[\*†‡#\$^\\?0-9\{\}\\]', '', simplified)
    simplified = re.sub(r'\([A-Za-z\s,]+\)', '', simplified)
    simplified = simplified.strip()

    parts = [p.strip().rstrip('.') for p in re.split(r'[,、]|\band\b|&', simplified) if p.strip()]
    if len(parts) >= 2:
        name_count = 0
        for p in parts:
            if re.match(r"^[A-Z][a-zA-Z\.\-']+(?:\s+[A-Z][a-zA-Z\.\-']+){0,3}$", p):
                name_count += 1
            elif re.match(r"^[\u4e00-\u9fa5]{2,4}$", p):
                name_count += 1
        if name_count / len(parts) >= 0.75:
            return True
    return False


def _is_status_or_venue_line(text: str) -> bool:
    clean = _clean_html(text)
    if _is_tag_or_noise_line(text):
        return True
    if re.search(r'["“「][^"”」]{10,}["”」]', clean):
        return False
    if NEWS_VERBS_REGEX.search(clean):
        return False
    for vp in VENUE_PATTERNS:
        m = re.search(vp, clean, re.I)
        if m:
            rem = re.sub(vp, '', clean, flags=re.I)
            rem = re.sub(r'\b(?:202\d|spotlight|oral|poster|dec\.\d+|nov\.\d+|sydney|australia|in|to appear in)\b', '', rem, flags=re.I)
            rem = re.sub(r'[\(\)\[\]\,\.\:\;\-\s#\*\+]+', '', rem)
            if len(rem) < 15:
                return True
    return False


def _is_bio_or_profile_line(text: str) -> bool:
    clean = _clean_html(text)
    bio_regexes = [
        r'\b(?:i am a|i was a|i am an|i am currently|i\'m an?)\s+(?:final-year\s+)?(?:ph\.?d\.?|postdoc|researcher|scientist|assistant\s+professor|associate\s+professor|professor|student|candidate|fellow)\b',
        r'\b(?:under the supervision of|advised by|co-advised by|working with\s+prof)\b',
        r'\b(?:my research focuses on|my research interests? (?:include|lie in|is|are)|my recent work studies|i am interested in)\b',
        r'\b(?:i received my|i obtained my|i earned my|i completed my)\s+(?:ph\.?d\.?|b\.?s\.?|m\.?s\.?|master|bachelor|degree)\b',
        r'\b(?:incoming assistant professor|tenure-track assistant professor)\b',
        r'\b(?:welcome to (?:my|our) (?:homepage|personal website|website))\b',
        r'\b(?:curriculum vitae|full cv|download cv)\b',
        r'\b(?:previously,?\s+he\s+was|he\s+is\s+a|he\s+was\s+a|he\s+received\s+his|he\s+obtained\s+his|his\s+research\s+interests?)\b',
        r'\b(?:our\s+team\s+recruits?|recruiting\s+(?:several\s+)?(?:phd|postdocs?)|博士后招聘|博士生招聘|招聘)\b',
        r'⭐️⭐️⭐️',
        r'\bphd\s+thesis\b',
    ]
    for r in bio_regexes:
        if re.search(r, clean, re.I):
            return True
    return False


def _is_tag_or_noise_line(text: str, scholar_name: str = "") -> bool:
    clean = _clean_html(text)
    if _is_html_or_artifact_noise(text):
        return True
    if re.search(r'\bProf(?:essor)?\.\s+[A-Z]', clean):
        return True
    if re.match(r'^(?:Dr\.|Prof\.|Mr\.|Ms\.)\s+[A-Z]', clean):
        return True
    if re.match(r'^(?:The\s+)?(?:\d+(?:st|nd|rd|th)\s+)?(?:International\s+)?(?:ACM\s+|IEEE\s+)?(?:SIGIR|KDD|SIGKDD|NeurIPS|ICML|ICLR|CVPR|ECCV|ICCV|ACL|EMNLP)\s+Conference\b', clean, re.I):
        return True
    if clean.strip().lower() in ['download paper', 'swe 自进化', 'identification', 'see you in wuhan, valse 2026!']:
        return True
    if scholar_name and (clean.lower() == scholar_name.lower() or clean.lower() in scholar_name.lower()):
        return True
    lower = clean.lower().strip(" :#*-—–")
    if lower in SECTION_HEADERS:
        return True
    if lower in STATUS_LINE_KEYWORDS:
        return True
    if re.match(r'^\*+\s*(?:denotes|equal contribution|core contributors).*', lower):
        return True

    btn_regex = r'^\s*\[\s*(?:' + '|'.join(BUTTON_KEYWORDS) + r')(?:\s*\(.*?\))?\s*\]'
    if re.match(btn_regex, clean, re.I):
        if len(clean) < 60:
            words = clean.lower().split()
            if not any(w in PAPER_TITLE_WORDS for w in words if len(w) > 4):
                return True

    stripped_brackets = re.sub(r'\[\s*(?:' + '|'.join(BUTTON_KEYWORDS) + r')[^\]]*\]', '', clean, flags=re.I)
    stripped_brackets = re.sub(r'\([^\)]*\)', '', stripped_brackets)
    stripped_brackets = re.sub(r'[\s🔥✨💡👉🔗\*\,\.\-—–]+', '', stripped_brackets)
    if len(clean) < 80 and len(stripped_brackets) <= 8 and any(bk in clean.lower() for bk in BUTTON_KEYWORDS):
        return True

    # Noise keywords
    noise_keywords = [
        "最新发布", "公告", "新版本特性", "博文目录", "分享到", "微信扫一扫",
        "上一篇", "下一篇", "未经许可", "版权声明", "点赞", "收藏", "评论", "转载", "免责声明",
        "举报不良行为", "google 网站", "many thanks", "great theme",
        "template", "jekyll", "designed by", "last updated",
        "power by", "hosted on", "github pages", "copyright",
        "人机身份验证", "enable javascript",
        "阅读全文", "最新文章", "历史文章", "时间 热度", "标签", "技术空间",
        "favorite quotes", "practice without theory", "theory without practice",
        "immanuel kant", "selected preprints", "full publications",
        "view all publications", "google scholar",
    ]
    lower_c = clean.lower()
    if any(k in lower_c for k in noise_keywords):
        return True

    # Broken sentence fragments from multi-line descriptions
    if re.match(r'^(?:and|whose|during|synthesized|exploring|with|for|or|to)\s+', clean, re.I):
        return True

    return False


def _extract_new_additions(diff_text: str, scholar_name: str = "") -> list:
    if not diff_text:
        return []
    lines = diff_text.split("\n")
    deleted_lines = [re.sub(r'<[^>]+>', '', l[1:]).strip() for l in lines if l.startswith("-") and not l.startswith("---") and len(l[1:].strip()) > 5]
    added_raw = [re.sub(r'<[^>]+>', '', l[1:]).strip() for l in lines if l.startswith("+") and not l.startswith("+++")]
    filtered = []
    for l in added_raw:
        if not l or len(l) < 4:
            continue
        if re.match(r'^[0-9\s\-\.\,\:\/\\\|\[\]\(\)]+$', l):
            continue
        if _is_tag_or_noise_line(l, scholar_name):
            continue
        if _is_author_list_line(l):
            continue
        if _is_status_or_venue_line(l):
            continue
        if _is_bio_or_profile_line(l):
            continue
        cl = _clean_paper_entry(_clean_html(l))
        lower_l = cl.lower()
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
        if cl not in filtered:
            filtered.append(cl)
    return filtered


def _extract_timestamp_and_date(text: str) -> tuple:
    text = re.sub(r'202\s*([4567])', r'202\1', text or '')
    now_dt = datetime.now(timezone.utc)
    max_valid_ts = (now_dt + timedelta(days=1)).timestamp()

    # 1. YYYY-MM-DD, YYYY.MM.DD, YYYY/MM/DD
    match = re.search(r'\b(202\d)[-\./](\d{1,2})[-\./](\d{1,2})\b', text)
    if match:
        try:
            y, m, d = int(match.group(1)), int(match.group(2)), int(match.group(3))
            dt = datetime(y, m, d, tzinfo=timezone.utc)
            if dt.timestamp() <= max_valid_ts:
                return dt.timestamp(), f"{y:04d}-{m:02d}-{d:02d}"
        except ValueError:
            pass

    # 2. Chinese date format: YYYY年MM月(DD日)?
    match_zh = re.search(r'\b(202\d)年(\d{1,2})月(?:(\d{1,2})日)?', text)
    if match_zh:
        try:
            y, m = int(match_zh.group(1)), int(match_zh.group(2))
            d = int(match_zh.group(3)) if match_zh.group(3) else 1
            dt = datetime(y, m, d, tzinfo=timezone.utc)
            if dt.timestamp() <= max_valid_ts:
                date_str = f"{y:04d}-{m:02d}-{d:02d}" if match_zh.group(3) else f"{y:04d}-{m:02d}"
                return dt.timestamp(), date_str
        except ValueError:
            pass

    # 3. YYYY-MM, YYYY.MM, [YYYY-MM], [YYYY.MM]
    match_month = re.search(r'(?:\[|\(|\b)(202\d)[-\./](\d{1,2})(?:\]|\)|\b)', text)
    if match_month:
        try:
            y, m = int(match_month.group(1)), int(match_month.group(2))
            if 1 <= m <= 12:
                now_utc = datetime.now(timezone.utc)
                if y == now_utc.year and m == now_utc.month:
                    dt = now_utc
                elif y == now_utc.year and (now_utc.month - m == 1 or (now_utc.month == 1 and m == 12)):
                    last_day = calendar.monthrange(y, m)[1]
                    dt = datetime(y, m, last_day, 12, 0, tzinfo=timezone.utc)
                else:
                    dt = datetime(y, m, 1, tzinfo=timezone.utc)
                if dt.timestamp() <= max_valid_ts:
                    return dt.timestamp(), f"{y:04d}-{m:02d}"
        except ValueError:
            pass

    # 4. MM.YYYY e.g. "09.2026, Five papers"
    match_my = re.search(r'\b(\d{1,2})[-\./](202\d)\b', text)
    if match_my:
        try:
            m, y = int(match_my.group(1)), int(match_my.group(2))
            if 1 <= m <= 12:
                now_utc = datetime.now(timezone.utc)
                if y == now_utc.year and m == now_utc.month:
                    dt = now_utc
                elif y == now_utc.year and (now_utc.month - m == 1 or (now_utc.month == 1 and m == 12)):
                    last_day = calendar.monthrange(y, m)[1]
                    dt = datetime(y, m, last_day, 12, 0, tzinfo=timezone.utc)
                else:
                    dt = datetime(y, m, 1, tzinfo=timezone.utc)
                if dt.timestamp() <= max_valid_ts:
                    return dt.timestamp(), f"{y:04d}-{m:02d}"
        except ValueError:
            pass

    # 5. English month names with year (must be whole month word, in date context)
    month_map = {
        "jan": 1, "january": 1, "feb": 2, "february": 2,
        "mar": 3, "march": 3, "apr": 4, "april": 4,
        "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
        "oct": 10, "october": 10, "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }
    month_pattern = r'(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)'

    match_a = re.search(rf'\b({month_pattern})\.?\s+(?:(\d{{1,2}})(?:st|nd|rd|th)?,?\s+)?\b(202\d)\b', text, re.IGNORECASE)
    if match_a:
        m_name = match_a.group(1).lower().rstrip(".")
        m_num = month_map.get(m_name)
        if m_num:
            day = int(match_a.group(2)) if match_a.group(2) else 1
            year = int(match_a.group(3))
            try:
                dt = datetime(year, m_num, day, tzinfo=timezone.utc)
                if dt.timestamp() <= max_valid_ts:
                    date_str = f"{year:04d}-{m_num:02d}-{day:02d}" if match_a.group(2) else f"{year:04d}-{m_num:02d}"
                    return dt.timestamp(), date_str
            except ValueError:
                pass

    match_b = re.search(rf'\b(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({month_pattern})\.?,?\s+\b(202\d)\b', text, re.IGNORECASE)
    if match_b:
        m_name = match_b.group(2).lower().rstrip(".")
        m_num = month_map.get(m_name)
        if m_num:
            day = int(match_b.group(1))
            year = int(match_b.group(3))
            try:
                dt = datetime(year, m_num, day, tzinfo=timezone.utc)
                if dt.timestamp() <= max_valid_ts:
                    return dt.timestamp(), f"{year:04d}-{m_num:02d}-{day:02d}"
            except ValueError:
                pass

    match_c = re.search(rf'\b(202\d)\s+({month_pattern})\b', text, re.IGNORECASE)
    if match_c:
        m_name = match_c.group(2).lower()
        m_num = month_map.get(m_name)
        if m_num:
            year = int(match_c.group(1))
            try:
                dt = datetime(year, m_num, 1, tzinfo=timezone.utc)
                if dt.timestamp() <= max_valid_ts:
                    return dt.timestamp(), f"{year:04d}-{m_num:02d}"
            except ValueError:
                pass

    # 6. Conference venue with year (e.g. ICML 2026, NeurIPS 2026, ICLR 2026)
    conf_months = {
        'aaai': ('02', 2),
        'iclr': ('05', 5),
        'cvpr': ('06', 6),
        'icml': ('07', 7),
        'acl': ('08', 8),
        'eccv': ('09', 9),
        'ijcv': ('09', 9),
        'acm mm': ('10', 10),
        'colm': ('10', 10),
        'emnlp': ('11', 11),
        'neurips': ('09', 9),
        'tkde': ('07', 7),
    }
    lower_text = text.lower()
    m_conf_yr = re.search(r'\b(202[4567])\b', text)
    if m_conf_yr:
        yr = int(m_conf_yr.group(1))
        for conf, (m_str, m_num) in conf_months.items():
            if conf in lower_text:
                dt = datetime(yr, m_num, 1, tzinfo=timezone.utc)
                if dt.timestamp() <= max_valid_ts:
                    return dt.timestamp(), f"{yr:04d}-{m_str}"
        dt = datetime(yr, 6, 1, tzinfo=timezone.utc)
        if dt.timestamp() <= max_valid_ts:
            return dt.timestamp(), f"{yr:04d}"

    return now_dt.timestamp(), ""


def _extract_timestamp_from_text(text: str) -> float:
    ts, _ = _extract_timestamp_and_date(text)
    return ts


NEWS_ANNOUNCEMENT_PATTERNS = [
    r'\b(?:accepted (?:by|to|in|at)|are accepted|is accepted|have been accepted|has been accepted|paper accepted)\b',
    r'\b(?:invited to|serving as|area chair|session chair|action editor)\b',
    r'\b(?:received (?:the|an?)|awarded|fellowship|scholarship|honorary)\b',
    r'\b(?:released|open-sourced|announced|launched|joined|defended|graduated)\b',
    r'\b(?:happy to announce|excited to share|pleased to announce)\b',
]


POST_ANNOUNCEMENT_PATTERNS = [
    r'\[中文版\]', r'\bblog\b', r'\bzhihu\b', r'\bpost\b', r'\bessay\b',
    r'failure modes', r'repair paths', r'agent behavior', r'early stopping',
    r'deep dive into', r'playing to the grader', r'thoughts? on',
]


def _kind_from_watch(watch: str, text: str = "") -> str:
    lower = text.lower()
    for pat in POST_ANNOUNCEMENT_PATTERNS:
        if re.search(pat, lower, re.I):
            return "post"
    for pat in NEWS_ANNOUNCEMENT_PATTERNS:
        if re.search(pat, lower, re.I):
            return "news"
    if watch == "blog":
        return "post"
    if watch == "publications":
        return "paper"
    if any(k in lower for k in PAPER_KEYWORDS):
        return "paper"
    if watch == "news":
        return "news"
    return "update"


def aggregate_events(events: list) -> list:
    """Cluster all events for each scholar into a single parent card.
    The newest event serves as the primary headline, and subsequent events
    (up to 9 items, for a total of up to 10 entries per scholar) become sub_items."""
    if not events:
        return []

    by_scholar = {}
    for ev in events:
        by_scholar.setdefault(ev["scholar"], []).append(ev)

    aggregated = []
    for scholar, items in by_scholar.items():
        all_candidates = []
        for it in items:
            it_date = it.get("date_str") or ""
            it_ts = it.get("timestamp") or 0.0
            clean_date, clean_ts = normalize_date(it_date, it_ts)
            all_candidates.append({
                "text": it.get("text", "").strip(),
                "link": it.get("link", ""),
                "kind": it.get("kind", "update"),
                "date_str": clean_date,
                "timestamp": clean_ts,
                "scholar_url": it.get("scholar_url", ""),
                "affiliation": it.get("affiliation", ""),
                "areas": it.get("areas", []),
                "watch": it.get("watch", "general"),
                "result_type": it.get("result_type", ""),
                "diff": it.get("diff"),
                "first_seen": it.get("first_seen"),
            })
            for sub in it.get("sub_items", []):
                s_date = sub.get("date") or sub.get("date_str") or sub.get("published") or ""
                s_ts = sub.get("timestamp") or it_ts
                s_clean_date, s_clean_ts = normalize_date(s_date, s_ts)
                all_candidates.append({
                    "text": sub.get("text", "").strip(),
                    "link": sub.get("link", "") or it.get("link", ""),
                    "kind": sub.get("kind", it.get("kind", "update")),
                    "date_str": s_clean_date,
                    "timestamp": s_clean_ts,
                    "scholar_url": it.get("scholar_url", ""),
                    "affiliation": it.get("affiliation", ""),
                    "areas": it.get("areas", []),
                    "watch": it.get("watch", "general"),
                    "result_type": it.get("result_type", ""),
                    "diff": None,
                    "first_seen": it.get("first_seen"),
                })

        valid_cands = []
        seen_keys = set()
        for cand in all_candidates:
            raw_txt = cand["text"]
            if not raw_txt or len(raw_txt) < 4:
                continue
            txt = _clean_paper_entry(_clean_html(raw_txt))
            if not txt or len(txt) < 4:
                continue
            if _is_tag_or_noise_line(txt, scholar) or _is_author_list_line(txt) or _is_status_or_venue_line(txt) or _is_bio_or_profile_line(txt):
                continue
            cand["text"] = txt
            dedup_key = re.sub(r'[\W_]+', '', txt.lower())[:60]
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)
            valid_cands.append(cand)

        if not valid_cands:
            continue

        valid_cands.sort(key=lambda x: x["timestamp"], reverse=True)
        top = valid_cands[0]
        top_cleaned_text = _clean_paper_entry(top.get("text", ""))
        top_norm = re.sub(r'[\W_]+', '', top_cleaned_text.lower())
        parent_ev = {
            "scholar": scholar,
            "scholar_url": top.get("scholar_url") or (items[0].get("scholar_url") if items else ""),
            "affiliation": top.get("affiliation") or (items[0].get("affiliation") if items else ""),
            "areas": top.get("areas") or (items[0].get("areas") if items else []),
            "watch": top.get("watch") or (items[0].get("watch") if items else "general"),
            "kind": top.get("kind", "update"),
            "text": top_cleaned_text,
            "link": top.get("link") or top.get("scholar_url"),
            "date_str": top.get("date_str", ""),
            "timestamp": top.get("timestamp") or 0.0,
            "result_type": top.get("result_type", ""),
            "first_seen": top.get("first_seen") or datetime.now(timezone.utc).isoformat(),
        }
        if top.get("diff"):
            parent_ev["diff"] = top["diff"]

        from difflib import SequenceMatcher
        sub_items = []
        top_base = _extract_base_title(top_cleaned_text)
        seen_norms = {top_norm}
        seen_bases = {top_base} if top_base else set()

        for cand in valid_cands[1:]:
            cand_clean = _clean_paper_entry(cand["text"])
            if not cand_clean or len(cand_clean) < 4:
                continue
            cand_norm = re.sub(r'[\W_]+', '', cand_clean.lower())
            cand_base = _extract_base_title(cand_clean)
            if cand_norm in seen_norms or (cand_base and cand_base in seen_bases):
                continue

            # Compare against top headline
            if SequenceMatcher(None, top_norm, cand_norm).ratio() > 0.70:
                continue
            if top_base and cand_base and SequenceMatcher(None, top_base, cand_base).ratio() > 0.70:
                continue
            if len(top_base) > 12 and len(cand_base) > 12 and (cand_base in top_base or top_base in cand_base):
                continue
            if len(cand_norm) > 15 and (cand_norm in top_norm or top_norm in cand_norm):
                continue

            # Compare against previous sub items
            is_dupe = False
            for prev_norm in seen_norms:
                if SequenceMatcher(None, prev_norm, cand_norm).ratio() > 0.75:
                    is_dupe = True
                    break
                if len(cand_norm) > 15 and len(prev_norm) > 15 and (cand_norm in prev_norm or prev_norm in cand_norm):
                    is_dupe = True
                    break
            if is_dupe:
                continue

            for prev_base in seen_bases:
                if SequenceMatcher(None, prev_base, cand_base).ratio() > 0.72:
                    is_dupe = True
                    break
                if len(cand_base) > 12 and len(prev_base) > 12 and (cand_base in prev_base or prev_base in cand_base):
                    is_dupe = True
                    break
            if is_dupe:
                continue

            seen_norms.add(cand_norm)
            if cand_base:
                seen_bases.add(cand_base)
            sub_items.append({
                "text": cand_clean,
                "link": cand["link"],
                "kind": cand["kind"],
                "date": cand["date_str"],
                "timestamp": cand["timestamp"],
            })
            if len(sub_items) >= 9:
                break
        if sub_items:
            parent_ev["sub_items"] = sub_items

        aggregated.append(parent_ev)

    aggregated.sort(key=lambda x: x.get("timestamp") or 0.0, reverse=True)
    return aggregated


def build_events(results: list) -> list:
    events = []
    now_ts = datetime.now(timezone.utc).timestamp()
    now_iso = datetime.now(timezone.utc).isoformat()

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
            "first_seen": now_iso,
        })

    for r in results:
        if r.get("new_publications"):
            for pub in r["new_publications"]:
                year = pub.get("year") or ""
                text = _format_publication_event(pub)
                _add_event(
                    r,
                    text,
                    pub.get("link") or r["url"],
                    str(year) if year else "",
                    _year_to_timestamp(year),
                    kind="paper",
                )
            continue
        if r["type"] == "rss":
            for e in r.get("entries", []):
                _add_event(r, e.get("title", ""), e.get("link", r["url"]),
                           e.get("published", ""), e.get("timestamp", 0.0))
        if r.get("supplemental_entries"):
            for e in r["supplemental_entries"]:
                _add_event(r, e.get("title", ""), e.get("link", r["url"]),
                           e.get("published", ""), e.get("timestamp", 0.0), kind="post")
        if r["type"] == "changed":
            if _is_google_scholar_result(r):
                continue
            additions = _extract_new_additions(r.get("diff", ""), r.get("name", ""))
            if additions:
                for add in additions[:8]:
                    ts, date_str = _extract_timestamp_and_date(add)
                    _add_event(r, add, r["url"], date_str, ts,
                               diff_text=r.get("diff"))

    events = aggregate_events(events)
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events


def _event_dedup_key(ev: dict) -> str:
    text = (ev.get("text") or "")[:120]
    return f"{ev.get('scholar', '')}|{ev.get('kind', 'update')}|{text}"


def _strip_event_for_history(ev: dict) -> dict:
    areas = ev.get("areas") or []
    if not isinstance(areas, list):
        areas = list(areas)
    res = {
        "scholar": ev.get("scholar", ""),
        "scholar_url": ev.get("scholar_url", ""),
        "affiliation": ev.get("affiliation", ""),
        "areas": areas,
        "watch": ev.get("watch", "general"),
        "kind": ev.get("kind", "update"),
        "text": ev.get("text", ""),
        "link": ev.get("link", ""),
        "date_str": ev.get("date_str", ""),
        "timestamp": ev.get("timestamp") or 0.0,
        "result_type": ev.get("result_type", ""),
        "first_seen": ev.get("first_seen") or datetime.now(timezone.utc).isoformat(),
    }
    if ev.get("sub_items"):
        res["sub_items"] = ev["sub_items"]
    return res


def load_events_history() -> list:
    if not EVENTS_HISTORY_PATH.exists():
        return []
    try:
        data = json.loads(EVENTS_HISTORY_PATH.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return []
        now_ts = datetime.now(timezone.utc).timestamp()
        max_valid_ts = now_ts + 86400

        config = load_yaml(BASE_DIR / "config.yaml")
        scholars_cfg = {s["name"]: s for s in config.get("scholars", []) if "name" in s}

        filtered_data = []
        for ev in data:
            s = ev.get("scholar", "")
            t = ev.get("text", "")
            if not s or not t or t.lower() == "page content updated":
                continue

            # Skip scholars not present in current config.yaml to eliminate ghost entries
            if s not in scholars_cfg:
                continue

            # Synchronize canonical metadata directly from config.yaml
            cfg_entry = scholars_cfg[s]
            ev["affiliation"] = _norm_str(cfg_entry.get("affiliation"))
            ev["areas"] = cfg_entry.get("research_areas") or []
            ev["scholar_url"] = cfg_entry.get("url", ev.get("scholar_url", ""))
            ev["watch"] = cfg_entry.get("watch", ev.get("watch", "general"))

            # Filter out stale events prior to 2025
            d_str = ev.get("date_str", "")
            m_yr = re.search(r'\b(202\d)\b', d_str)
            ev_yr = int(m_yr.group(1)) if m_yr else None
            if not ev_yr:
                ts_cand = ev.get("timestamp") or 0.0
                if ts_cand > 0:
                    ev_yr = datetime.fromtimestamp(ts_cand, tz=timezone.utc).year
            if ev_yr and ev_yr < 2025:
                continue

            t_clean = _clean_paper_entry(_clean_html(t))
            if not t_clean or len(t_clean) < 4:
                continue
            if _is_tag_or_noise_line(t_clean, s) or _is_author_list_line(t_clean) or _is_status_or_venue_line(t_clean) or _is_bio_or_profile_line(t_clean):
                continue
            ev["text"] = t_clean

            # Clean and filter sub_items
            if "sub_items" in ev and isinstance(ev["sub_items"], list):
                cleaned_subs = []
                for sub in ev["sub_items"]:
                    sub_txt = sub.get("text", "")
                    sub_clean = _clean_paper_entry(_clean_html(sub_txt))
                    if not sub_clean or len(sub_clean) < 4:
                        continue
                    if _is_tag_or_noise_line(sub_clean, s) or _is_author_list_line(sub_clean) or _is_status_or_venue_line(sub_clean) or _is_bio_or_profile_line(sub_clean):
                        continue
                    sub["text"] = sub_clean
                    cleaned_subs.append(sub)
                ev["sub_items"] = cleaned_subs

            ts = ev.get("timestamp") or 0.0
            fs_ts = _first_seen_to_timestamp(ev.get("first_seen", ""))
            if ts > max_valid_ts:
                ev["timestamp"] = fs_ts if fs_ts > 0 else now_ts
            elif fs_ts > 0 and ts > 0:
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                if dt.day == 1 and dt.hour == 0 and dt.minute == 0:
                    fs_dt = datetime.fromtimestamp(fs_ts, tz=timezone.utc)
                    if fs_dt.year == dt.year and fs_dt.month == dt.month:
                        ev["timestamp"] = fs_ts
                        if ev.get("date_str") == f"{dt.year:04d}-{dt.month:02d}":
                            ev["date_str"] = fs_dt.strftime("%Y-%m-%d")

            filtered_data.append(ev)

        return aggregate_events(filtered_data)
    except (json.JSONDecodeError, OSError):
        return []


def save_events_history(events: list) -> None:
    EVENTS_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    stripped = [_strip_event_for_history(ev) for ev in events[:EVENTS_HISTORY_LIMIT]]
    EVENTS_HISTORY_PATH.write_text(
        json.dumps(stripped, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def merge_events_history(history: list, new_events: list) -> list:
    """Merge current-run events with persisted history; new events win on dedup."""
    merged = []
    seen = set()
    hist_by_key = {_event_dedup_key(h): h for h in history}

    for ev in new_events:
        key = _event_dedup_key(ev)
        if key in seen:
            continue
        seen.add(key)
        out = dict(ev)
        hist_match = hist_by_key.get(key)
        if hist_match and hist_match.get("first_seen"):
            out["first_seen"] = hist_match["first_seen"]
        else:
            out["first_seen"] = datetime.now(timezone.utc).isoformat()
        merged.append(out)

    for h in history:
        key = _event_dedup_key(h)
        if key in seen:
            continue
        seen.add(key)
        merged.append(dict(h))

    merged = aggregate_events(merged)
    merged.sort(key=lambda x: x.get("timestamp") or 0, reverse=True)
    return merged


def build_last_update_map(events: list) -> dict:
    """Map scholar name -> timestamp of most recent detected update (first_seen)."""
    last = {}
    for ev in events:
        name = ev.get("scholar", "")
        if not name:
            continue
        ts = _first_seen_to_timestamp(ev.get("first_seen", ""))
        if ts <= 0:
            ts = ev.get("timestamp") or 0
        if ts >= last.get(name, 0):
            last[name] = ts
    return last


def _first_seen_to_timestamp(first_seen: str) -> float:
    if not first_seen:
        return 0.0
    try:
        return datetime.fromisoformat(first_seen.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def backfill_missing_recent_events(merged: list, results: list, days: int = 30) -> list:
    """Ensure every scholar has their latest activity (up to 10 entries) from results/feeds."""
    scholar_item_counts = {}
    for ev in merged:
        s_name = ev.get("scholar")
        count = 1 + len(ev.get("sub_items", []))
        scholar_item_counts[s_name] = scholar_item_counts.get(s_name, 0) + count

    backfill = []
    for r in results:
        name = r["name"]
        candidates = r.get("entries") or r.get("latest_entries") or []
        if not candidates:
            continue

        existing_count = scholar_item_counts.get(name, 0)
        if existing_count >= 10:
            continue

        cands_to_add = []
        for e in candidates:
            ts = e.get("timestamp") or 0
            d_str = e.get("published", "") or ""
            m_y = re.search(r"\b(202\d)\b", d_str)
            e_year = int(m_y.group(1)) if m_y else None
            if not e_year and ts > 0:
                e_year = datetime.fromtimestamp(ts, tz=timezone.utc).year
            if e_year and e_year < 2025:
                continue
            cands_to_add.append(e)

        if not cands_to_add:
            continue

        needed = max(0, 10 - existing_count)
        top = cands_to_add[0]
        ts = top.get("timestamp") or 0
        first_seen = (
            datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            if ts > 0
            else datetime.now(timezone.utc).isoformat()
        )
        main_ev = {
            "scholar": name,
            "scholar_url": r["url"],
            "affiliation": r.get("affiliation", ""),
            "areas": r.get("research_areas", []),
            "watch": r.get("watch", "general"),
            "kind": _kind_from_watch(r.get("watch", "general"), top.get("title", "")),
            "text": top.get("title", "").strip(),
            "link": top.get("link") or r["url"],
            "date_str": top.get("published", "") or "",
            "timestamp": ts,
            "result_type": r.get("type", ""),
            "first_seen": first_seen,
        }
        if len(cands_to_add) > 1:
            main_ev["sub_items"] = [
                {
                    "text": sub.get("title", "").strip(),
                    "link": sub.get("link") or r["url"],
                    "kind": _kind_from_watch(r.get("watch", "general"), sub.get("title", "")),
                    "date": sub.get("published", "") or "",
                    "timestamp": sub.get("timestamp") or 0.0,
                }
                for sub in cands_to_add[1:needed]
            ]
        backfill.append(main_ev)

    if not backfill:
        return merged
    return merge_events_history(merged, backfill)


def _format_update_date(ts: float) -> str:
    if not ts or ts <= 0:
        return "—"
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
    except (OSError, ValueError):
        return "—"


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
    res, _ = normalize_date(date_str, ts)
    return res


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
        adds = _extract_new_additions(r.get("diff", ""), r.get("name", ""))
        txt = adds[0][:80] if adds else "Content changed"
        return re.sub(r'<[^>]+>', '', txt)
    if t == "error":
        return re.sub(r'<[^>]+>', '', (r.get("error") or "Error")[:60])
    if t == "first_check":
        return "Baseline snapshot taken"
    preview = r.get("preview") or []
    if preview:
        return re.sub(r'<[^>]+>', '', preview[0][:80])
    latest = r.get("latest_entries") or []
    if latest:
        return re.sub(r'<[^>]+>', '', latest[0].get("title", "")[:80])
    return "No recent activity"


def generate_html_report(
    results: list,
    total: int,
    new_events: list,
    display_events: list,
    last_update_map: dict,
):
    errors = [r for r in results if r["type"] == "error"]
    ok_count = sum(1 for r in results if r["type"] in ("unchanged", "rss_no_change", "first_check"))
    new_count = len(new_events)
    now = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    all_affiliations = sorted({r.get("affiliation", "") for r in results if r.get("affiliation")})
    all_areas = sorted({a for r in results for a in r.get("research_areas", []) if a})

    warn_class = "sm-stat-warn" if errors else "sm-stat-muted"
    stats_html = f"""<div class="sm-stats">
      <span class="sm-stat sm-stat-new">动态 {new_count}</span>
      <span class="sm-stat {warn_class}">需关注 {len(errors)}</span>
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
        filter_html += (
            '<details class="sm-filter-more">'
            '<summary class="sm-filter-summary"><span>研究方向</span>'
            '<span class="sm-filter-actions">'
            '<button type="button" class="sm-btn-link" onclick="toggleAllFilters(\'fl-area\', true); event.stopPropagation();">全选</button> / '
            '<button type="button" class="sm-btn-link" onclick="toggleAllFilters(\'fl-area\', false); event.stopPropagation();">清空</button>'
            '</span></summary><div class="sm-filter-row">'
        )
        for area in all_areas:
            filter_html += (
                f'<label class="sm-chip"><input type="checkbox" class="fl-area" '
                f'value="{_esc(area.lower())}" checked onchange="applyFilters()">{_esc(area)}</label>'
            )
        filter_html += '</div></details>'
    if all_affiliations:
        filter_html += (
            '<details class="sm-filter-more">'
            '<summary class="sm-filter-summary"><span>单位</span>'
            '<span class="sm-filter-actions">'
            '<button type="button" class="sm-btn-link" onclick="toggleAllFilters(\'fl-aff\', true); event.stopPropagation();">全选</button> / '
            '<button type="button" class="sm-btn-link" onclick="toggleAllFilters(\'fl-aff\', false); event.stopPropagation();">清空</button>'
            '</span></summary><div class="sm-filter-row">'
        )
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
    bucket_labels = {"week": "🔥 本周动态", "month": "⚡️ 本月动态", "earlier": "📜 更早历史动态"}
    for ev in display_events:
        buckets[_timeline_bucket(ev["timestamp"])].append(ev)

    week_count = len(buckets["week"])
    month_count = len(buckets["month"])
    earlier_count = len(buckets["earlier"])
    recent_count = week_count + month_count
    total_count = len(display_events)

    scope_tabs_html = (
        '<div class="sm-scope-tabs" id="scopeTabs">'
        f'<button type="button" class="sm-scope-btn active" data-scope="recent" onclick="setScope(\'recent\')">⚡️ 近期精选 <span class="sm-scope-count">{recent_count}</span></button>'
        f'<button type="button" class="sm-scope-btn" data-scope="week" onclick="setScope(\'week\')">🔥 本周动态 <span class="sm-scope-count">{week_count}</span></button>'
        f'<button type="button" class="sm-scope-btn" data-scope="month" onclick="setScope(\'month\')">📅 本月动态 <span class="sm-scope-count">{month_count}</span></button>'
        f'<button type="button" class="sm-scope-btn" data-scope="all" onclick="setScope(\'all\')">📜 全部动态 <span class="sm-scope-count">{total_count}</span></button>'
        '</div>'
    )

    timeline_html = (
        '<section class="sm-timeline" id="timelineSection">'
        '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; margin-bottom:1.5rem;">'
        '<h2 class="sm-section-title" style="margin:0;">最近在做什么</h2>'
        f'{scope_tabs_html}'
        '</div>'
    )
    if not display_events:
        timeline_html += (
            '<div class="sm-empty"><div class="sm-empty-title">暂无动态记录</div>'
            '<div class="sm-empty-sub">尚未检测到任何论文、博客或主页更新。</div></div>'
        )
    else:
        for key in ("week", "month", "earlier"):
            group = buckets[key]
            if not group:
                continue
            if key == "earlier":
                timeline_html += f'<details class="sm-tl-group sm-tl-group-earlier" data-bucket="{key}">'
                timeline_html += f'<summary class="sm-tl-heading sm-tl-earlier-summary"><span>📜 更早历史动态 (点击展开剩余 {len(group)} 条)</span> <span class="sm-tl-count">{len(group)}</span></summary>'
            else:
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
                sub_html = ""
                if ev.get("sub_items"):
                    subs = ev["sub_items"]
                    sub_items_li = ""
                    main_kind = ev.get("kind", "update")
                    for s in subs:
                        stext = _esc(s.get("text", ""))
                        slink = s.get("link")
                        skind = s.get("kind", main_kind)
                        sdate = s.get("date") or s.get("date_str") or s.get("published") or ""
                        sdate_disp = ""
                        if sdate:
                            sdate_disp, _ = normalize_date(sdate, s.get("timestamp") or 0.0)
                        date_badge = f'<time class="sm-sub-date">{_esc(sdate_disp)}</time>' if sdate_disp else '<time class="sm-sub-date sm-sub-date-empty">—</time>'

                        # Only show badge if the sub-item type differs from the card's main type
                        if skind != main_kind:
                            skind_badge = f'<span class="sm-kind sm-kind-{_esc(skind)} sm-sub-kind">{_kind_label(skind)}</span>'
                        else:
                            skind_badge = ''

                        if slink and slink != ev.get("scholar_url"):
                            link_html = f'<a href="{_esc(slink)}" target="_blank" class="sm-sub-link">{stext} <span class="sm-link-icon">↗</span></a>'
                        elif slink or ev.get("scholar_url"):
                            target_link = slink or ev.get("scholar_url")
                            link_html = f'<a href="{_esc(target_link)}" target="_blank" class="sm-sub-link sm-sub-link-site">{stext} <span class="sm-link-badge">主页 ↗</span></a>'
                        else:
                            link_html = f'<span class="sm-sub-text">{stext}</span>'

                        sub_items_li += (
                            f'<li class="sm-tl-subpaper-item">'
                            f'{date_badge}{skind_badge}'
                            f'<div class="sm-sub-title-wrap">{link_html}</div>'
                            f'</li>'
                        )

                    sub_kinds = [s.get("kind", main_kind) for s in subs]
                    counts = Counter([main_kind] + sub_kinds)
                    dominant_kind = counts.most_common(1)[0][0]
                    if dominant_kind == "paper":
                        summary_label = "近期发表成果 / 论文"
                    elif dominant_kind == "post":
                        summary_label = "近期技术博文"
                    elif dominant_kind == "news":
                        summary_label = "更多近期动态"
                    else:
                        summary_label = "更多更新记录"

                    sub_html = (
                        f'<details class="sm-tl-subpapers">'
                        f'<summary class="sm-tl-subpapers-summary">'
                        f'<span class="sm-sub-summary-title"><span class="sm-sub-chevron">▸</span> {summary_label}</span>'
                        f'<span class="sm-sub-count-badge">{len(subs)} 项</span>'
                        f'</summary>'
                        f'<div class="sm-tl-subpapers-body">'
                        f'<ul class="sm-tl-subpapers-list">{sub_items_li}</ul>'
                        f'</div>'
                        f'</details>'
                    )
                search_text = ev.get("text", "")
                if ev.get("sub_items"):
                    search_text += " " + " ".join(s.get("text", "") for s in ev["sub_items"])
                timeline_html += (
                    f'<article class="sm-tl-item" data-filterable '
                    f'data-bucket="{key}" '
                    f'data-name="{_esc(ev["scholar"].lower())}" '
                    f'data-affiliation="{_esc(aff.lower())}" '
                    f'data-areas="{_esc(areas.lower())}" '
                    f'data-kind="{_esc(ev.get("kind", "update"))}" '
                    f'data-text="{_esc(search_text.lower())}">'
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
                link = ev.get("link") or ev.get("scholar_url")
                if link and link != ev.get("scholar_url"):
                    timeline_html += f'<a href="{_esc(link)}" target="_blank" class="sm-tl-text">{_esc(ev["text"])} <span class="sm-link-icon">↗</span></a>'
                elif link:
                    timeline_html += f'<a href="{_esc(link)}" target="_blank" class="sm-tl-text sm-tl-text-site">{_esc(ev["text"])} <span class="sm-link-badge">个人主页 ↗</span></a>'
                else:
                    timeline_html += f'<p class="sm-tl-text">{_esc(ev["text"])}</p>'
                timeline_html += sub_html + diff_block + '</article>'
            timeline_html += '</div>'
            if key == "earlier":
                timeline_html += '</details>'
            else:
                timeline_html += '</div>'
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
        update_disp = _format_update_date(last_update_map.get(r["name"], 0))
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
            f'<td class="sm-dir-updated">{_esc(update_disp)}</td>'
            f'<td class="sm-dir-latest">{_esc(status)}</td></tr>'
        )

    directory_html = (
        '<details class="sm-panel" id="directorySection">'
        '<summary class="sm-panel-title">全部学者目录</summary>'
        '<div class="sm-dir-wrap"><table class="sm-dir-table">'
        '<thead><tr><th>学者</th><th>单位</th><th>方向</th><th>状态</th>'
        '<th>更新时间</th><th>最近动态</th></tr></thead>'
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
    parser.add_argument("--report-only", action="store_true",
                        help="Regenerate events_history and HTML report without making external network calls.")
    args = parser.parse_args()

    config = load_yaml(BASE_DIR / "config.yaml")
    scholars = config.get("scholars", [])
    if not scholars:
        log("Error: No scholars found in config.yaml")
        sys.exit(1)

    if args.prune_snapshots:
        prune_snapshots(scholars, force=args.force)
        return

    if args.report_only:
        log("Report-only mode: generating HTML from snapshots and history...")
        events = load_events_history()
        save_events_history(events)
        results = []
        for s in scholars:
            base_r = _scholar_base_result(s)
            base_r["type"] = "unchanged"
            results.append(base_r)
        last_update_map = build_last_update_map(events)
        display_events = events[:EVENTS_DISPLAY_LIMIT]
        generate_html_report(
            results, len(scholars), [], display_events, last_update_map
        )
        log("Report generated successfully.")
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

    new_events = build_events(results)
    history = load_events_history()
    merged_events = merge_events_history(history, new_events)
    merged_events = backfill_missing_recent_events(merged_events, results)
    save_events_history(merged_events)
    last_update_map = build_last_update_map(merged_events)
    display_events = merged_events[:EVENTS_DISPLAY_LIMIT]
    log(f"Events: {len(new_events)} new this run, {len(merged_events)} in history, "
        f"showing {len(display_events)} on timeline")

    report = generate_report(results, len(scholars), new_events)
    generate_html_report(
        results, len(scholars), new_events, display_events, last_update_map,
    )

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
