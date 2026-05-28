#!/usr/bin/env python3
"""Remove broken entries from config.yaml."""
import yaml

REMOVE_URLS = [
    "https://yuhangwuai.github.io/",
    "https://rikka421.github.io/",
    "https://zhaozhiming.github.io/about/index.html",
    "https://lvxintao.github.io/",
    "https://scholar.google.com/citations?user=8KhrWbYAAAAJ",
]

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

before = len(config["scholars"])
config["scholars"] = [s for s in config["scholars"] if s["url"] not in REMOVE_URLS]
removed = before - len(config["scholars"])

for s in config["scholars"]:
    if s["url"] in REMOVE_URLS:
        print(f"  Removing: {s['name']}")

with open("config.yaml", "w", encoding="utf-8") as f:
    yaml.dump(config, f, allow_unicode=True, default_flow_style=None, sort_keys=False, width=1000)

print(f"Removed {removed} entries. {len(config['scholars'])} scholars remaining.")
