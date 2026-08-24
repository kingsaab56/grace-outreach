import os
import re

with open("web_portal.py", "r", encoding="utf-8", errors="ignore") as f:
    code = f.read()

# Remove the overlapping ambient-controls from the root layout
code = code.replace('<div class="ambient-controls">', '<div class="ambient-controls" style="display:none !important;">')

# Ensure navbar buttons are positioned cleanly side-by-side
nav_fix = """
        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .ambient-controls { display: none !important; }
"""
code = code.replace('.nav-actions { display: flex;', nav_fix + '\n        .nav-actions { display: flex;')

with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write(code)

print("✔ Overlap permanently removed from web_portal.py!")
