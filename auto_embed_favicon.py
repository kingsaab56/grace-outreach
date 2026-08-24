import os
import glob
import base64

# Automatically find any png or jpg logo in current directory
candidates = glob.glob("*.png") + glob.glob("*.jpg") + glob.glob("*.jpeg") + glob.glob("*.ico")

if not candidates:
    print("❌ Koi image file folder mein nahi mili! Pehle apni logo image folder mein paste karein.")
    exit(1)

img_file = candidates[0]
print(f"✔ Found image: {img_file}")

with open(img_file, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

with open("web_portal.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Ensure /favicon.ico route exists in do_GET
favicon_handler = f"""        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            import base64
            self.wfile.write(base64.b64decode('{b64_data}'))
            return\n"""

if "self.path == '/favicon.ico'" not in code:
    code = code.replace("def do_GET(self):", f"def do_GET(self):\n{favicon_handler}")

# 2. Add Favicon Tag directly to HTML Head templates
head_replacement = f"""<head>
    <link rel="icon" type="image/png" href="data:image/png;base64,{b64_data}">
    <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{b64_data}">"""

code = code.replace("<head>", head_replacement)

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✔ Favicon & Route successfully embedded into web_portal.py!")
