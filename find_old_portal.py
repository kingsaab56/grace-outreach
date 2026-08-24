import os
import re

found_code = None

# Scan files that might contain the original rich HTML/Dashboard template
check_files = ["check_old_main.py", "main.py", "test_end_to_end_v2.py", "scan_modules.py"]

for filename in check_files:
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "<!DOCTYPE html>" in content or "class GraceRequestHandler" in content or "class PortalHandler" in content:
                print(f"✔ Purana UI template mil gaya file: {filename} mein!")
                found_code = content
                break

if found_code:
    # Ensure Railway Cloud host & port compatibility
    found_code = re.sub(r'HOST\s*=\s*["\'].*?["\']', 'HOST = "0.0.0.0"', found_code)
    found_code = re.sub(r'PORT\s*=\s*\d+', 'PORT = int(os.environ.get("PORT", 8080))', found_code)
    found_code = found_code.replace("webbrowser.open(", "# webbrowser.open(")
    
    with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
        f.write(found_code)
    print("✔ Purana original portal code successfully 'web_portal.py' mein restore ho gaya!")
else:
    print("ℹ Files mein embedded HTML nahi mila. Kripya batayein purane dashboard mein kon se main buttons / tables the?")
