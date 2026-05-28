#!/usr/bin/env python3
"""Rebuild monitor.py with corrected encoding."""
from pathlib import Path

monitor_path = Path("scripts/monitor.py")
body_path = Path("scripts/_new_html_body.txt")

# Read the original file up to line 574
with open(monitor_path, "r", encoding="utf-8", errors="replace") as f:
    all_lines = f.readlines()

# Keep header (lines 0-573, 0-indexed) and footer (lines 913+)
header = "".join(all_lines[:574])
footer = "".join(all_lines[913:])

# Read the new body
with open(body_path, "r", encoding="utf-8") as f:
    new_body = f.read()

# Write the result
with open(monitor_path, "w", encoding="utf-8") as f:
    f.write(header + "\n" + new_body + "\n" + footer)

# Verify syntax
import py_compile
try:
    py_compile.compile(monitor_path, doraise=True)
    print("Syntax OK!")
except py_compile.PyCompileError as e:
    print(f"Syntax error: {e}")
