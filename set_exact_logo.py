import os
import base64

img_file = "grace_logo.png"

if not os.path.exists(img_file):
    print("❌ 'grace_logo.png' nahi mili! Pehle image ko save karein E:\Grace Outreach Assistant folder mein.")
    exit(1)

with open(img_file, "rb") as f:
    b64_data = base64.b64encode(f.read()).decode("utf-8")

with open("web_portal.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace any previous favicon handler
import re
code = re.sub(r"if self\.path == '/favicon\.ico':.*?(?=if self\.path|def do_POST)", "", code, flags=re.DOTALL)

favicon_handler = f"""        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            import base64
            self.wfile.write(base64.b64decode('{b64_data}'))
            return\n\n"""

code = code.replace("def do_GET(self):", f"def do_GET(self):\n{favicon_handler}")

# Remove old favicon tags and insert fresh one
code = re.sub(r'<link rel="icon"[^>]*>', '', code)
code = re.sub(r'<link rel="shortcut icon"[^>]*>', '', code)

head_tag = f"""<head>
    <link rel="icon" type="image/png" href="data:image/png;base64,{b64_data}">
    <link rel="shortcut icon" type="image/png" href="data:image/png;base64,{b64_data}">"""

code = code.replace("<head>", head_tag)

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✔ Exact Emerald & Gold 'Developed by King Saab' logo successfully injected!")
