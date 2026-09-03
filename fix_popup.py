import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove alert popup entirely from module opening functions
html = html.replace('alert("✔ Opening Module 1: Dashboard Overview");', '')
html = html.replace("alert('✔ Opening Module 1: Dashboard Overview');", '')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Popup alert permanently removed!")
