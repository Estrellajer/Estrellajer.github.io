#!/usr/bin/env python3
"""Replace generate_html_report in monitor.py with new implementation."""
import re
from pathlib import Path

MONITOR_PATH = Path("scripts/monitor.py")

# Read the new function
NEW_FUNC_PATH = Path("scripts/_new_html_report.txt")
new_func = NEW_FUNC_PATH.read_text(encoding="utf-8")

# Read the current monitor.py
code = MONITOR_PATH.read_text(encoding="utf-8")

# Find the function boundaries
pattern = r"^def generate_html_report\(results: list, total: int\):.*?^(?=\ndef main|\ndef _summarize)"
replacement = new_func

new_code = re.sub(pattern, replacement, code, count=1, flags=re.DOTALL | re.MULTILINE)

if new_code == code:
    print("ERROR: Pattern did not match. Printing first 50 chars of function:")
    import re as re2
    m = re2.search(r"def generate_html_report\(results: list, total: int\):", code)
    if m:
        print(f"Found at position {m.start()}")
    else:
        print("Function start not found!")
else:
    MONITOR_PATH.write_text(new_code, encoding="utf-8")
    print("Successfully replaced generate_html_report!")
