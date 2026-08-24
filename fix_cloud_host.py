import re

with open("web_portal.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Bind to 0.0.0.0 for Cloud Container and use dynamic PORT
content = re.sub(r'HOST\s*=\s*["\'].*?["\']', 'HOST = "0.0.0.0"', content)
if 'HOST = "0.0.0.0"' not in content:
    content = 'HOST = "0.0.0.0"\n' + content

content = re.sub(r'PORT\s*=\s*.*', 'PORT = int(os.environ.get("PORT", 8080))', content)

# 2. Update server binding
content = re.sub(r'ThreadingHTTPServer\(\(.*?,\s*PORT\)', 'ThreadingHTTPServer((HOST, PORT)', content)
content = re.sub(r'HTTPServer\(\(.*?,\s*PORT\)', 'HTTPServer((HOST, PORT)', content)

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✔ Server updated to listen on 0.0.0.0 and dynamic cloud PORT!")
