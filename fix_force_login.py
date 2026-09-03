import os

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace auth button inline script to force display none on authViewport and flex on enterpriseApp with high priority
new_onclick = 'onclick="document.getElementById(\'authViewport\').style.cssText=\'display:none !important;\'; document.getElementById(\'cinematicStage\').style.cssText=\'display:none !important;\'; document.getElementById(\'enterpriseApp\').style.cssText=\'display:flex !important;\';"'

import re
html = re.sub(r'onclick="[^"]*?"', new_onclick, html)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✔ Force display override applied to login button!")
