import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Completely remove the login overlay block from HTML so it never blocks access
if '<div id="login-overlay"' in html:
    start_idx = html.find('<div id="login-overlay"')
    # Find closing div roughly or remove section
    # Let's just set its display to none via CSS injection right inside head
    html = html.replace('<head>', '<head><style>#login-overlay { display: none !important; }</style>')
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✔ Login overlay permanently hidden via CSS!")
else:
    print("⚠ Login overlay not found.")
