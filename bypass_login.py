import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Auto-hide login overlay and show dashboard immediately
html = html.replace('id="login-overlay" style="display: flex;"', 'id="login-overlay" style="display: none;"')
html = html.replace("document.getElementById('login-overlay').style.display = 'flex';", "document.getElementById('login-overlay').style.display = 'none';")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Login overlay bypassed successfully!")
