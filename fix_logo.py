import base64
import os
import re

logo_path = 'logo.png'
if not os.path.exists(logo_path):
    logo_path = 'E:\Grace Outreach Assistant\logo.png'

if os.path.exists(logo_path):
    with open(logo_path, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    data_uri = f'data:image/png;base64,{encoded}'
    
    portal_path = 'web_portal.py'
    if not os.path.exists(portal_path):
        portal_path = 'E:\Grace Outreach Assistant\web_portal.py'
        
    with open(portal_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace any logo img tag completely with direct base64 data URI
    new_content = re.sub(r'<img[^>]*class="logo-img"[^>]*>', f'<img src="{data_uri}" class="logo-img" alt="Grace Logo">', content)
    new_content = re.sub(r'<div class="logo-wrap"><img[^>]*></div>', f'<div class="logo-wrap"><img src="{data_uri}" alt="Grace Logo"></div>', new_content)
    
    with open(portal_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS: Logo embedded successfully as Base64!")
else:
    print("ERROR: logo.png not found!")
