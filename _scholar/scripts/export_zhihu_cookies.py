#!/usr/bin/env python3
"""Export zhihu cookies.txt as base64 for GitHub Actions secret.

Usage:
  1. Export zhihu.com cookies from browser as Netscape format
  2. Save to _snapshots/zhihu_cookies.txt
  3. Run: python scripts/export_zhihu_cookies.py
  4. Add the secret: gh secret set ZHIHU_COOKIES_B64 < zhihu_cookies.b64.txt
"""
import base64
from pathlib import Path

COOKIE_PATH = Path("_snapshots/zhihu_cookies.txt")


def main():
    if not COOKIE_PATH.exists():
        print(f"Error: Cookies not found at {COOKIE_PATH}")
        print("1. Log into zhihu.com in your browser")
        print("2. Install 'Get cookies.txt' extension")
        print("3. Export zhihu.com cookies as Netscape format")
        print(f"4. Save to {COOKIE_PATH}")
        print("5. Run this script again")
        return

    size = COOKIE_PATH.stat().st_size
    with open(COOKIE_PATH, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    output_path = Path("zhihu_cookies.b64.txt")
    output_path.write_text(b64)
    print(f"Exported {size} bytes from {COOKIE_PATH} -> {output_path}")
    print(f"\nAdd as GitHub secret:")
    print(f"  gh secret set ZHIHU_COOKIES_B64 < {output_path}")


if __name__ == "__main__":
    main()
