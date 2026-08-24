import urllib.request
import base64
import re
import os

with open("web_portal.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Clean previous /favicon.ico route
code = re.sub(r"if self\.path == '/favicon\.ico':.*?(?=\n\s+if self\.path|\n\s+def do_POST)", "", code, flags=re.DOTALL)

# SVG representation of King Saab 3D Gold & Emerald Grace Architecture Logo for crisp crystal-clear Favicon
logo_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="100%" stop-color="#e8ede9"/>
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#d97706"/>
      <stop offset="100%" stop-color="#b45309"/>
    </linearGradient>
    <linearGradient id="emerald" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#065f46"/>
      <stop offset="50%" stop-color="#047857"/>
      <stop offset="100%" stop-color="#022c22"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="100" fill="url(#bg)" stroke="#047857" stroke-width="12"/>
  <rect x="20" y="20" width="472" height="472" rx="85" fill="none" stroke="url(#gold)" stroke-width="6"/>
  <!-- Towers -->
  <path d="M190 280 L190 180 L230 140 L230 280 Z" fill="url(#emerald)"/>
  <path d="M245 280 L245 100 L285 70 L285 280 Z" fill="url(#emerald)"/>
  <path d="M270 70 L285 70 L285 100 L270 100 Z" fill="url(#gold)"/>
  <path d="M300 130 L350 190 L350 280 L320 280 L320 230 L300 230 Z" fill="url(#gold)"/>
  <!-- Text -->
  <text x="256" y="350" font-family="Arial, sans-serif" font-weight="900" font-size="44" fill="#022c22" text-anchor="middle" letter-spacing="8">GRACE</text>
  <text x="256" y="390" font-family="Arial, sans-serif" font-weight="700" font-size="22" fill="#047857" text-anchor="middle" letter-spacing="10">OUTREACH</text>
  <line x1="120" y1="415" x2="392" y2="415" stroke="url(#gold)" stroke-width="3"/>
  <text x="256" y="445" font-family="Georgia, serif" font-style="italic" font-size="19" fill="#78350f" text-anchor="middle">Developed by King Saab</text>
</svg>"""

b64_svg = base64.b64encode(logo_svg.encode('utf-8')).decode('utf-8')

favicon_handler = f"""        if self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-Type', 'image/svg+xml')
            self.end_headers()
            import base64
            self.wfile.write(base64.b64decode('{b64_svg}'))
            return\n\n"""

code = code.replace("def do_GET(self):", f"def do_GET(self):\n{favicon_handler}")

# Remove old favicons
code = re.sub(r'<link rel="icon"[^>]*>', '', code)
code = re.sub(r'<link rel="shortcut icon"[^>]*>', '', code)

# Add SVG Data URI Favicon
head_tag = f"""<head>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{b64_svg}">
    <link rel="shortcut icon" type="image/svg+xml" href="data:image/svg+xml;base64,{b64_svg}">"""

code = code.replace("<head>", head_tag)

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(code)

print("✔ Official Grace Outreach (Developed by King Saab) Favicon built & injected directly into source code!")
