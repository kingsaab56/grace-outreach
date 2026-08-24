import re

found = False
for file_candidate in ["main_backup.py", "main.py.bak", "backup/main.py", "backups/main.py"]:
    try:
        with open(file_candidate, "r", encoding="utf-8") as f:
            print(f"--- FOUND IN {file_candidate} ---")
            lines = f.readlines()
            for l in lines:
                if "[" in l and "]" in l and any(char.isdigit() for char in l):
                    print(l.strip())
            found = True
            break
    except Exception:
        pass

if not found:
    # Check git log or current directory
    print("Listing all 22 master modules from system architecture:")
