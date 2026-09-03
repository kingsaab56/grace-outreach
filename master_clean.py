import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Strip any accidental rogue bottom progress bars or floating text lines
if "Workplace Rotators" in html:
    import re
    html = re.sub(r'<div[^>]*>.*?Workplace Rotators.*?<\/div>', '', html, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Master codebase stabilized and cleaned successfully!")
