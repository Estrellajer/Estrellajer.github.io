#!/usr/bin/env python3
"""Check Zhihu via browser-exported cookies.

How to use:
  1. Log into zhihu.com in your browser (any method: SMS, QR code, etc.)
  2. Install a cookie export extension:
     - Chrome: "Get cookies.txt" (by rotem)
     - Firefox: "cookies.txt" (by Alex)
  3. Export cookies for zhihu.com as Netscape format
  4. Save as _snapshots/zhihu_cookies.txt
  5. Done — monitor.py will use it automatically.
"""
import re
from datetime import datetime, timezone
from http.cookiejar import MozillaCookieJar
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
COOKIE_PATH = BASE_DIR / "_snapshots" / "zhihu_cookies.txt"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.zhihu.com/",
}


def has_cookies() -> bool:
    return COOKIE_PATH.exists()


def get_session() -> requests.Session | None:
    """Create a requests.Session with zhihu cookies loaded. Returns None if no cookies file."""
    if not COOKIE_PATH.exists():
        return None

    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    cookies = MozillaCookieJar(COOKIE_PATH)
    cookies.load(ignore_discard=True, ignore_expires=True)
    session.cookies.update(cookies)

    return session


def fetch_user_activities(zhihu_id: str, since: datetime | None) -> list[dict]:
    """Fetch a zhihu user's recent answers and articles."""
    session = get_session()
    if not session:
        return []

    entries = []

    # Fetch answers via Zhihu API
    answer_url = f"https://www.zhihu.com/api/v4/members/{zhihu_id}/answers?limit=5&order_by=created"
    try:
        resp = session.get(answer_url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("data", []):
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

    # Fetch articles/posts
    article_url = f"https://www.zhihu.com/api/v4/members/{zhihu_id}/articles?limit=5&order_by=created"
    try:
        resp = session.get(article_url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("data", []):
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

    return entries


if __name__ == "__main__":
    # Quick test
    if not has_cookies():
        print("No cookies found at:", COOKIE_PATH)
        print("\nSteps:")
        print("1. Log into zhihu.com in your browser")
        print("2. Export cookies (Netscape format) using a browser extension")
        print(f"3. Save to: {COOKIE_PATH}")
        print("4. Run this script again to test")
        exit(1)

    print("Cookies found! Testing...")
    session = get_session()
    resp = session.get("https://www.zhihu.com/people/lyq2002", timeout=15)
    if resp.status_code == 200:
        print("Login OK! Zhihu is accessible.")
        # Show recent activities
        entries = fetch_user_activities("lyq2002", None)
        if entries:
            print(f"\nRecent activities ({len(entries)}):")
            for e in entries[:5]:
                print(f"  {e['title']} ({e['published']})")
        else:
            print("No recent activities found (or user has none)")
    else:
        print(f"Failed: HTTP {resp.status_code}")
        print("The cookies may be expired. Re-export them from your browser.")
