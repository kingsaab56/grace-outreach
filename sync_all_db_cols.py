import sqlite3
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

tables_columns = {
    "gmail_accounts": [("status", "TEXT DEFAULT 'Active'"), ("oauth_connected", "INTEGER DEFAULT 0"), ("token_file", "TEXT")],
    "campaigns": [("status", "TEXT DEFAULT 'Draft'"), ("completed_count", "INTEGER DEFAULT 0"), ("failed_count", "INTEGER DEFAULT 0"), ("pending_count", "INTEGER DEFAULT 0"), ("total_contacts", "INTEGER DEFAULT 0")],
    "campaign_items": [("status", "TEXT DEFAULT 'Pending'"), ("sender_email", "TEXT"), ("draft_id", "TEXT"), ("recipient_email", "TEXT")],
    "contacts": [("status", "TEXT DEFAULT 'Active'")]
}

for table, cols in tables_columns.items():
    cursor.execute(f"PRAGMA table_info({table})")
    existing = [r[1].lower() for r in cursor.fetchall()]
    for col_name, col_def in cols:
        if col_name.lower() not in existing:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                print(f"✔ Added `{col_name}` to `{table}`")
            except Exception as e:
                print(f"Notice on {table}.{col_name}: {e}")

conn.commit()
conn.close()
print("🎉 All database columns permanently synchronized!")
