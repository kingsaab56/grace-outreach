import sqlite3
import hashlib
from config.database import get_connection

def upgrade_v4_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Ensure system_users exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colleague_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            assigned_states TEXT DEFAULT 'Texas (TX)',
            contractor_portfolio TEXT DEFAULT 'Custom Home Builder',
            role TEXT DEFAULT 'Colleague',
            last_seen TEXT,
            is_active_status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check & add missing columns safely
    cursor.execute("PRAGMA table_info(system_users)")
    u_cols = [r[1].lower() for r in cursor.fetchall()]
    if 'last_seen' not in u_cols:
        cursor.execute("ALTER TABLE system_users ADD COLUMN last_seen TEXT")
        cursor.execute("UPDATE system_users SET last_seen = datetime('now')")
    if 'is_active_status' not in u_cols:
        cursor.execute("ALTER TABLE system_users ADD COLUMN is_active_status INTEGER DEFAULT 0")

    # 2. Real-Time Alerts & Notification Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_colleague_id TEXT NOT NULL,
            sender_name TEXT NOT NULL,
            sender_role TEXT NOT NULL,
            message TEXT NOT NULL,
            alert_type TEXT DEFAULT 'warning',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Activity Tracker Table
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

    # 4. Contacts Table columns check
    cursor.execute("PRAGMA table_info(contacts)")
    c_cols = [r[1].lower() for r in cursor.fetchall()]
    if 'client_uid' not in c_cols:
        cursor.execute("ALTER TABLE contacts ADD COLUMN client_uid TEXT")
    if 'state' not in c_cols:
        cursor.execute("ALTER TABLE contacts ADD COLUMN state TEXT DEFAULT 'TX'")
    if 'contractor_category' not in c_cols:
        cursor.execute("ALTER TABLE contacts ADD COLUMN contractor_category TEXT DEFAULT 'General Contractor'")

    # Super Admin Profile
    admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("SELECT id FROM system_users WHERE colleague_id = 'CLG-1001'")
    admin_row = cursor.fetchone()
    if not admin_row:
        cursor.execute("""
            INSERT INTO system_users (colleague_id, full_name, email, password_hash, assigned_states, contractor_portfolio, role, last_seen, is_active_status)
            VALUES ('CLG-1001', 'King Saab (Super Admin)', 'admin@gracearchitectures.com', ?, 'ALL US STATES', 'All Contractor Portfolios', 'Super Admin', datetime('now'), 1)
        """, (admin_pass,))
    else:
        cursor.execute("UPDATE system_users SET role = 'Super Admin' WHERE colleague_id = 'CLG-1001'")

    # HR Profile
    cursor.execute("SELECT id FROM system_users WHERE email = 'hr@gracearchitectures.com'")
    if not cursor.fetchone():
        hr_pass = hashlib.sha256("hr123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO system_users (colleague_id, full_name, email, password_hash, assigned_states, contractor_portfolio, role, last_seen, is_active_status)
            VALUES ('CLG-HR01', 'Grace HR Manager', 'hr@gracearchitectures.com', ?, 'ALL US STATES', 'Management & Supervision', 'HR Manager', datetime('now'), 0)
        """, (hr_pass,))

    conn.commit()
    conn.close()
    print("✔ V4 Enterprise database schema applied successfully!")

if __name__ == "__main__":
    upgrade_v4_db()
