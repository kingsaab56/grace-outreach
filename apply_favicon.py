import os
import base64

# Locate the logo image
logo_name = "logo.png" if os.path.exists("logo.png") else ("App logo .png" if os.path.exists("App logo .png") else None)

if not logo_name:
    print("Logo file nahi mili. Ensure karein ke 'logo.png' ya 'App logo .png' folder mein mojood hai.")
    exit(1)

with open(logo_name, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")

favicon_tag = f'<link rel="icon" type="image/png" href="data:image/png;base64,{img_b64}">'

with open("web_portal.py", "r", encoding="utf-8") as f:
    code = f.read()

# Inject favicon tag inside HTML <head> if not already present
if 'rel="icon"' not in code:
    code = code.replace("<head>", f"<head>\n    {favicon_tag}")
    with open("web_portal.py", "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✔ Browser Tab Favicon successfully linked using {logo_name}!")
else:
    print("Favicon already configured.")
