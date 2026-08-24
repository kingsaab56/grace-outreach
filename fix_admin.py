import sqlite3
import hashlib
from config.database import get_connection

p_hash = hashlib.sha256("admin56".encode()).hexdigest()
conn = get_connection()
cur = conn.cursor()

cur.execute("DELETE FROM system_users WHERE colleague_id = 'kingsaab56' OR email = 'kingsaab56@gracearchitectures.com'")
cur.execute("""
    INSERT INTO system_users (colleague_id, full_name, email, password_hash, assigned_states, contractor_portfolio, role, last_seen, is_active_status)
    VALUES ('kingsaab56', 'King Saab (Super Admin)', 'kingsaab56@gracearchitectures.com', ?, 'ALL US STATES', 'All Categories', 'Super Admin', datetime('now'), 1)
""", (p_hash,))

conn.commit()
conn.close()
print("✔ Super Admin setup completed: Username: kingsaab56 | Password: admin56")
