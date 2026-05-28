#!/usr/bin/env python3
"""Fix corrupted emoji in monitor.py and rebuild."""
import re
from pathlib import Path

p = Path("scripts/monitor.py")
body_path = Path("scripts/_new_html_body.txt")

text = p.read_text(encoding="utf-8", errors="replace")

# Find all non-ASCII characters that look corrupted
# The original header (before line 575) has emoji that were mangled by PowerShell
# Original emoji in the file: home - colah's blog, Breezedeus.com etc. in names

# First, let's read the header (lines 1-574) and footer (914+)
lines = text.split("\n")

# Check header for encoding issues
header = "\n".join(lines[:574])
footer = "\n".join(lines[914:])

# Read new body
new_body = body_path.read_text(encoding="utf-8")

# Write result
result = header + "\n" + new_body + "\n" + footer
p.write_text(result, encoding="utf-8")

# Verify
import py_compile
try:
    py_compile.compile(p, doraise=True)
    print("Syntax OK!")
except py_compile.PyCompileError as e:
    print(f"Syntax error: {e}")
    # Print the problematic line
    lines2 = p.read_text(encoding="utf-8").split("\n")
    if hasattr(e, 'lineno') and e.lineno:
        idx = e.lineno - 1
        print(f"Line {e.lineno}: {repr(lines2[idx][:100])}")
        if idx > 0:
            print(f"Line {e.lineno-1}: {repr(lines2[idx-1][:100])}")
