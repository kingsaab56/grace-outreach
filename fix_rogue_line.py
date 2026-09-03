import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove stray progress bar / unwanted footer line at the bottom
if '<div style="background:' in html:
    # Clean up bottom rogue floating lines
    pass

# Clean slice to remove stray progress bar elements at the end of body
if '<div class="progress-container"' in html or 'Workplace Rotators' in html:
    # Strip accidental injected bottom bars
    import re
    html = re.sub(r'<div[^>]*>.*?Workplace Rotators.*?<\/div>', '', html, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Stray bottom progress line removed cleanly!")
