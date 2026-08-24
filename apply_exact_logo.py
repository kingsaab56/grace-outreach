import os
import re
import base64

# Check available files in directory
target_file = None
candidates = ["App logo .png", "App logo.png", "grace_logo.png", "logo.png"]

for f in candidates:
    if os.path.exists(f):
        target_file = f
        break

if not target_file:
    # If not found by specific name, find any .png file in the folder
    pngs = [f for f in os.listdir(".") if f.lower().endswith(".png")]
    if pngs:
        target_file = pngs[0]

if not target_file:
    print("❌ Koi PNG image nahi mili folder mein.")
    exit(1)

print(f"✔ Using image file: {target_file}")

with open(target_file, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

with open("web_portal.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Clean previous /favicon.ico route
code = re.sub(r"if self\.path == '/favicon\.ico':.*?(?=\n\s+if self\.path|\n\s+def do_POST)", "", code, flags=re.DOTALL)

# 2. Add fresh favicon handler
favicon_handler = f"""        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            import base64
            self.wfile.write(base64.b64decode('{b64_data}'))
            return\n\n"""

code = code.replace("def do_GET(self):", f"def do_GET(self):\n{favicon_handler}")

# 3. Clean and inject <link rel="icon">
code = re.sub(r'<link rel="icon"[^>]*>', '', code)
code = re.sub(r'<link rel="shortcut icon"[^>]*>', '', code)

head_tag = f"""<head>
    <link rel="icon" type="image/png" href="data:image/png;base64,{b64_data}">
    <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{b64_data}">"""

code = code.replace("<head>", head_tag)

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✔ Developed by King Saab logo successfully embedded into web_portal.py!")
