import os
import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Strip any alert containing "Opening Module" across all scripts
html = re.sub(r'alert\s*\(\s*["\']\s*✔?\s*Opening Module.*?["\']\s*\)\s*;?', '', html, flags=re.IGNORECASE)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ All module opening alert popups stripped completely!")
