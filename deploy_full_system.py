import os
import re

# Restore full portal features into web_portal.py while maintaining Cloud host/port
with open("portal_app.py" if os.path.exists("portal_app.py") else "web_portal.py", "r", encoding="utf-8", errors="ignore") as f:
    full_code = f.read()

# Ensure dynamic port & 0.0.0.0 bind
full_code = re.sub(r'HOST\s*=\s*["\'].*?["\']', 'HOST = "0.0.0.0"', full_code)
if 'HOST = "0.0.0.0"' not in full_code:
    full_code = 'HOST = "0.0.0.0"\n' + full_code

full_code = re.sub(r'PORT\s*=\s*\d+', 'PORT = int(os.environ.get("PORT", 8080))', full_code)

# Ensure webbrowser doesn't crash cloud
full_code = full_code.replace("webbrowser.open(f\"http://localhost:{PORT}\")", "pass")

with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write(full_code)

print("✔ Full Production Dashboard & System successfully configured!")
