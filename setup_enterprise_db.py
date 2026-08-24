import sqlite3
import hashlib
import random
from config.database import get_connection

def setup_enterprise_schema():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Colleague Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colleague_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            assigned_states TEXT DEFAULT 'ALL',
            contractor_portfolio TEXT DEFAULT 'General Builder',
            role TEXT DEFAULT 'Associate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. User Activity Tracker Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colleague_id TEXT,
            user_name TEXT,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Add Unique Client Reference to Contacts if missing
    cursor.execute("PRAGMA table_info(contacts)")
    cols = [r[1].lower() for r in cursor.fetchall()]
    if 'client_uid' not in cols:
        try:
            cursor.execute("ALTER TABLE contacts ADD COLUMN client_uid TEXT")
            cursor.execute("ALTER TABLE contacts ADD COLUMN state TEXT DEFAULT 'TX'")
            cursor.execute("ALTER TABLE contacts ADD COLUMN contractor_category TEXT DEFAULT 'Home Builder'")
        except Exception as e:
            print(f"Notice: {e}")

    # Generate Unique Client IDs for existing contacts without UID
    cursor.execute("SELECT rowid, id FROM contacts WHERE client_uid IS NULL OR client_uid = ''")
    rows = cursor.fetchall()
    for row in rows:
        uid = f"CLT-{random.randint(100000, 999999)}"
        cursor.execute("UPDATE contacts SET client_uid = ? WHERE rowid = ?", (uid, row[0]))

    # Create Default Admin / King User if empty
    cursor.execute("SELECT COUNT(*) FROM system_users")
    if cursor.fetchone()[0] == 0:
        default_pass = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO system_users (colleague_id, full_name, email, password_hash, assigned_states, contractor_portfolio, role)
            VALUES ('CLG-1001', 'King Saab (Admin)', 'admin@gracearchitectures.com', ?, 'TX, FL, CA, NY', 'Home Builder, Remodeling, Roofing', 'Admin')
        """, (default_pass,))

    conn.commit()
    conn.close()
    print("✔ Enterprise schema, activity logger, and unique client IDs applied!")

if __name__ == "__main__":
    setup_enterprise_schema()
