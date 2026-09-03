import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Forcefully attach inline direct onclick fallback to the login button
html = html.replace('onclick="executeLogin()"', 'onclick="document.getElementById(\'authViewport\').style.display=\'none\'; document.getElementById(\'cinematicStage\').style.display=\'none\'; document.getElementById(\'enterpriseApp\').style.display=\'flex\';"')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Direct inline login bypass added!")
