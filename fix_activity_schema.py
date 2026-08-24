import sqlite3
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Drop old incompatible table and recreate fresh
cursor.execute("DROP TABLE IF EXISTS activity_logs")
cursor.execute("""
    CREATE TABLE activity_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        colleague_id TEXT DEFAULT 'kingsaab56',
        user_name TEXT DEFAULT 'King Saab',
        action TEXT,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert initial log entry
cursor.execute("""
    INSERT INTO activity_logs (colleague_id, user_name, action, details)
    VALUES ('kingsaab56', 'King Saab (Super Admin)', 'System Initialized', 'Database tables synchronized successfully.')
""")

conn.commit()
conn.close()
print("✔ activity_logs table successfully fixed with colleague_id column!")
