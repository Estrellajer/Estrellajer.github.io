#!/usr/bin/env python3
"""Import edited CSV back into config.yaml."""
import csv
from pathlib import Path

import yaml

CONFIG_PATH = Path("config.yaml")
CSV_PATH = Path("scholars_metadata.csv")


def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found. Run scripts/add_metadata.py first.")
        return

    # Read CSV
    rows = {}
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[row["url"]] = row

    # Read config
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Apply metadata
    updated = 0
    for s in config["scholars"]:
        url = s["url"]
        if url in rows:
            row = rows[url]
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


if __name__ == "__main__":
    main()
