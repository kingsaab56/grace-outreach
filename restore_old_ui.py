import os
import re

# Backup se original main portal dhoond kar restore karein
source_file = None
candidates = ["web_portal.py.bak", "web_portal_backup.py", "portal_app.py", "app.py"]

for c in candidates:
    if os.path.exists(c):
        source_file = c
        break

if source_file:
    with open(source_file, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()
    print(f"✔ Restoring original portal UI from {source_file}...")
else:
    print("ℹ Original backup file direct na milne par clean configuration apply ki ja rahi hai...")

# Ensure Cloud host 0.0.0.0 and PORT dynamic binding
code = re.sub(r'HOST\s*=\s*["\'].*?["\']', 'HOST = "0.0.0.0"', code if source_file else "")
if source_file:
    code = re.sub(r'PORT\s*=\s*\d+', 'PORT = int(os.environ.get("PORT", 8080))', code)
    code = code.replace("webbrowser.open(", "# webbrowser.open(")
    
    with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
        f.write(code)
    print("✔ Asal purana dashboard successfully restore ho gaya!")
else:
    print("❌ Purana exact template load karne ke liye batayein konsa feature/layout pehle mojood tha.")
