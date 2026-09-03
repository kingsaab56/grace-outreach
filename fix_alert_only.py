import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace only the alert inside openModule with a clean tab switcher to avoid breaking anything else
old_alert = 'alert("✔ Opening Module " + modId + ": " + modTitle);'
new_view = 'switchTab("tab-dash", document.querySelectorAll(".ribbon-btn")[0]);'

if old_alert in html:
    html = html.replace(old_alert, new_view)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✔ Alert replaced with direct view switcher safely!")
else:
    print("⚠ Alert statement not found.")
