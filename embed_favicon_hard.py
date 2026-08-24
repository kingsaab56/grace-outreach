import os
import base64

# Find image file
img_file = "App logo .png" if os.path.exists("App logo .png") else "logo.png"

with open(img_file, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

with open("web_portal.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Ensure /favicon.ico route exists in do_GET
favicon_handler = f"""        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            with open('{img_file}', 'rb') as f:
                self.wfile.write(f.read())
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

print("✔ Favicon & Route embedded directly into web_portal.py!")
