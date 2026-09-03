import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Make Module 1 matrix click directly switch to the main dashboard tab
old_mod1_click = 'onclick="openModule(1, \'Dashboard Overview\')"'
new_mod1_click = 'onclick="switchTab(\'tab-dash\', document.querySelectorAll(\'.ribbon-btn\')[0])"'

if old_mod1_click in html:
    html = html.replace(old_mod1_click, new_mod1_click)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✔ Module 1 click routed directly to main dashboard view!")
else:
    print("⚠ Module 1 click pattern not found.")
