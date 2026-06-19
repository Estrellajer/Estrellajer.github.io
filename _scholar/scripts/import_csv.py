#!/usr/bin/env python3
"""Import edited CSV back into config.yaml.

URLs are matched after normalization (lowercase scheme/host, trailing slash and
fragment removed, tracking params dropped), so cosmetic differences don't cause
silent no-ops. CSV rows that match no config entry are reported for manual review.
"""
import csv
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlencode, urlunsplit

import yaml

CONFIG_PATH = Path("config.yaml")
CSV_PATH = Path("scholars_metadata.csv")

# Query params to ignore when normalizing URLs for comparison.
_TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
                    "fbclid", "gclid", "ref", "ref_src", "mc_cid", "mc_eid"}


def _normalize_url(u: str) -> str:
    """Normalize a URL for robust matching: lowercase scheme/host, drop fragment,
    strip trailing slash (except root), drop tracking params, sort the rest."""
    try:
        parts = urlsplit((u or "").strip())
    except Exception:
        return (u or "").strip().lower()
    scheme = (parts.scheme or "").lower()
    netloc = (parts.netloc or "").lower()
    path = parts.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    query_pairs = sorted((k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                         if k.lower() not in _TRACKING_PARAMS)
    query = urlencode(query_pairs)
    return urlunsplit((scheme, netloc, path, query, ""))


def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found. Run scripts/add_metadata.py first.")
        return

    # Read CSV keyed by normalized URL
    rows = {}
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[_normalize_url(row["url"])] = (row["url"], row)

    # Read config
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Apply metadata
    updated = 0
    matched_csv_urls = set()
    for s in config["scholars"]:
        norm = _normalize_url(s["url"])
        if norm in rows:
            matched_csv_urls.add(norm)
            row = rows[norm][1]
            if row.get("labels"):
                s["labels"] = [x.strip() for x in row["labels"].split(",") if x.strip()]
            if row.get("research_areas"):
                s["research_areas"] = [x.strip() for x in row["research_areas"].split(",") if x.strip()]
            if row.get("affiliation"):
                s["affiliation"] = row["affiliation"].strip()
            if row.get("watch"):
                s["watch"] = row["watch"].strip()
            updated += 1

    # Save
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=None, sort_keys=False, width=1000)
    print(f"Imported metadata for {updated}/{len(config['scholars'])} scholars")

    # Report CSV rows that matched no config entry (likely path/version drift to reconcile)
    unmatched = [rows[n][0] for n in rows if n not in matched_csv_urls]
    if unmatched:
        print(f"\n{len(unmatched)} CSV row(s) did not match any config.yaml URL (reconcile manually):")
        for u in unmatched:
            print(f"  - {u}")


if __name__ == "__main__":
    main()
