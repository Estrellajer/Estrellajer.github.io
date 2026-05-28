#!/usr/bin/env python3
"""Add metadata (labels, research_areas, affiliation) to existing config.yaml and
export a CSV template for bulk editing."""

import csv
import re
from pathlib import Path

import yaml

CONFIG_PATH = Path("config.yaml")
CSV_PATH = Path("scholars_metadata.csv")

# watch value based on scholar type
WATCH_DEFAULTS = {
    "github_pages": None,  # depends on labels
    "kexuefm": "blog",
    "zhihu": "blog",
    "substack": "blog",
    "cnblogs": "blog",
    "csdn": "blog",
    "google_scholar": "publications",
    "google_sites": "general",
    "openreview": "publications",
    "huggingface": "blog",
    "google_blog": "blog",
    "personal_website": "general",
}


def guess_affiliation(url: str) -> str:
    """Guess institution from URL patterns."""
    url_lower = url.lower()
    patterns = [
        (r"lamda\.nju\.edu\.cn", "NJU LAMDA"),
        (r"nju\.edu\.cn", "NJU"),
        (r"tsinghua\.edu\.cn", "Tsinghua University"),
        (r"pku\.edu\.cn", "Peking University"),
        (r"riken", "RIKEN AIP"),
        (r"mit\.edu", "MIT"),
        (r"stanford\.edu", "Stanford"),
        (r"berkeley\.edu", "UC Berkeley"),
        (r"cmu\.edu", "CMU"),
        (r"google\.com", "Google"),
        (r"research\.google", "Google Research"),
        (r"microsoft\.com", "Microsoft"),
        (r"openai\.com", "OpenAI"),
        (r"deepmind\.com", "DeepMind"),
        (r"iiis\.tsinghua", "Tsinghua IIIS"),
        (r"github\.io", ""),  # Can't guess from GitHub Pages
        (r"zhihu\.com", "Zhihu"),
        (r"scholar\.google", ""),
    ]
    for regex, aff in patterns:
        if re.search(regex, url_lower):
            return aff
    return ""


def main():
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Add metadata to each scholar
    for s in config["scholars"]:
        cat = s.get("category", "")

        # Label: derive from original bookmark category
        labels = []
        if "blog" in cat.lower():
            labels.append("blog")
        if "homepage" in cat.lower() or "home" in cat.lower():
            labels.append("homepage")
        if not labels:
            labels.append("homepage")

        s["labels"] = labels
        s["research_areas"] = s.get("research_areas", [])
        s["affiliation"] = s.get("affiliation", guess_affiliation(s["url"]))

        # Watch field: what to monitor this scholar for
        site_type = s.get("site_type", "")
        watch_default = WATCH_DEFAULTS.get(site_type)
        if watch_default is None:
            if "blog" in labels:
                watch_default = "blog"
            else:
                watch_default = "general"
        s["watch"] = s.get("watch", watch_default)

    # Save updated config
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=None, sort_keys=False, width=1000)
    print(f"Updated {CONFIG_PATH} with metadata fields")

    # Export CSV template
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "url", "labels", "watch", "research_areas", "affiliation"])
        for s in config["scholars"]:
            writer.writerow([
                s["name"],
                s["url"],
                ", ".join(s.get("labels", [])),
                s.get("watch", "general"),
                ", ".join(s.get("research_areas", [])),
                s.get("affiliation", ""),
            ])
    print(f"Exported CSV template: {CSV_PATH}")
    print(f"\nEdit {CSV_PATH} in Excel/Google Sheets to fill in:")
    print(f"  - watch: 'blog', 'vlog', 'news', 'publications', or 'general'")
    print(f"  - research_areas: e.g. 'reinforcement learning, LLM, continual learning'")
    print(f"  - affiliation: e.g. 'NJU LAMDA'")
    print(f"\nThen run: python scripts/import_csv.py")


if __name__ == "__main__":
    main()
