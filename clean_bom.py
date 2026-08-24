with open("web_portal.py", "rb") as f:
    raw_data = f.read()

# Remove UTF-8 BOM if present at beginning
if raw_data.startswith(b'\xef\xbb\xbf'):
    raw_data = raw_data[3:]

# Decode to string and strip invalid zero-width characters
text = raw_data.decode("utf-8", errors="ignore")
text = text.replace('\ufeff', '')

# Save back in standard clean UTF-8 without BOM
with open("web_portal.py", "w", encoding="utf-8", newline='\n') as f:
    f.write(text)

print("✔ Invisible BOM character (U+FEFF) successfully removed!")
