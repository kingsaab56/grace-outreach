import re

found = False
for file_name in ["main.py.bak", "main_old.py", "main_backup.py"]:
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            print(f"Found {file_name}:")
            for line in f:
                if "import" in line or "elif choice" in line or "def " in line:
                    print(line.rstrip())
        found = True
        break

if not found:
    print("Checking collector/contacts/gmail entry points...")
