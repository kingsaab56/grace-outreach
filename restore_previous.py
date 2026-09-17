import os
import shutil
import sys

backup_file = r"E:\Grace Outreach Assistant\backups\main_stable_enterprise_backup.py"
target_file = r"E:\Grace Outreach Assistant\main.py"

if not os.path.exists(backup_file):
    print(f"[ERROR] Backup file not found at: {backup_file}")
    sys.exit(1)

shutil.copy2(backup_file, target_file)
print("=" * 60)
print("✔ SUCCESS: Previous version restored from backup!")
print(f"  Restored {target_file}")
print("=" * 60)
