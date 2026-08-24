import sqlite3
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

tables_to_check = ['contacts', 'campaigns', 'campaign_items']

for table in tables_to_check:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cursor.fetchall()]
    if 'status' not in cols:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN status TEXT DEFAULT 'Active'")
            print(f"✔ Successfully added `status` column to `{table}`")
        except Exception as e:
            print(f"Error altering {table}: {e}")
    else:
        print(f"ℹ `status` column already present in `{table}`")

conn.commit()
conn.close()
print("\n🎉 Database schema updated successfully!")
