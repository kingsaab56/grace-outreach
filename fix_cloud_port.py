import re

with open("web_portal.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update PORT to dynamic environment variable
content = content.replace("PORT = 8501", "PORT = int(os.environ.get('PORT', 8501))")

# 2. Safely handle webbrowser on headless cloud
old_browser = "webbrowser.open(f\"http://localhost:{PORT}\")"
new_browser = """try:
        if 'PORT' not in os.environ:
            webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass"""
content = content.replace(old_browser, new_browser)

with open("web_portal.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✔ web_portal.py cloud dynamic port fix applied successfully!")
