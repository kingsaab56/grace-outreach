import sqlite3
import hashlib
from config.database import get_connection

def setup_phase_and_recovery_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Add security questions & recovery to system_users
    cursor.execute("PRAGMA table_info(system_users)")
    u_cols = [r[1].lower() for r in cursor.fetchall()]
    if 'security_answer' not in u_cols:
        cursor.execute("ALTER TABLE system_users ADD COLUMN security_answer TEXT DEFAULT 'grace'")

    # 2. Add CRM Lead Deal Pipeline Stages to Contacts
    cursor.execute("PRAGMA table_info(contacts)")
    c_cols = [r[1].lower() for r in cursor.fetchall()]
    if 'deal_stage' not in c_cols:
        cursor.execute("ALTER TABLE contacts ADD COLUMN deal_stage TEXT DEFAULT 'Cold Lead'")
    if 'deal_value' not in c_cols:
        cursor.execute("ALTER TABLE contacts ADD COLUMN deal_value INTEGER DEFAULT 1500")

    # Update Super Admin Recovery
    p_hash = hashlib.sha256("admin56".encode()).hexdigest()
    cursor.execute("""
        UPDATE system_users 
        SET password_hash = ?, security_answer = 'grace' 
        WHERE colleague_id = 'kingsaab56' OR role = 'Super Admin'
    """, (p_hash,))

    conn.commit()
    conn.close()
    print("✔ CRM Deal Stages, AI Pitch Engine & Password Recovery Database Ready!")

if __name__ == "__main__":
    setup_phase_and_recovery_db()
