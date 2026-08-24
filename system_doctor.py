import os
import sys
import sqlite3
import py_compile

print("=" * 70)
print("1. CHECKING SQLITE DATABASE TABLES & COLUMNS")
print("=" * 70)

try:
    from config.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    for tbl in tables:
        cursor.execute(f"PRAGMA table_info({tbl});")
        cols = [f"{c[1]} ({c[2]})" for c in cursor.fetchall()]
        print(f"\n[TABLE] {tbl}:")
        print("  -> " + ", ".join(cols))
        
        # Sample row check
        cursor.execute(f"SELECT * FROM {tbl} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"  [Sample Row]: {sample}")
            
    conn.close()
except Exception as e:
    print(f"[DB Error]: {e}")

print("\n" + "=" * 70)
print("2. COMPILING ALL PYTHON FILES IN PROJECT")
print("=" * 70)

error_count = 0
for root, dirs, files in os.walk("."):
    # Ignore virtualenvs or hidden folders
    if ".git" in root or "venv" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            try:
                py_compile.compile(full_path, doraise=True)
                print(f"✔ [OK] {full_path}")
            except Exception as e:
                print(f"✖ [FAILED] {full_path} -> {e}")
                error_count += 1

print("\n" + "=" * 70)
print(f"DIAGNOSTIC FINISHED: {error_count} compile error(s) found.")
print("=" * 70)
