import sqlite3
import hashlib
from config.database import get_connection

new_user = "kingsaab56"
new_pass = "admin56"
p_hash = hashlib.sha256(new_pass.encode()).hexdigest()

conn = get_connection()
cursor = conn.cursor()

# Update admin row
cursor.execute("""
    UPDATE system_users 
    SET colleague_id = ?, full_name = 'King Saab (Super Admin)', email = 'kingsaab56@gracearchitectures.com', password_hash = ?
    WHERE colleague_id = 'CLG-1001' OR role = 'Super Admin'
""", (new_user, p_hash))

conn.commit()
conn.close()
print("✔ Super Admin updated: Login ID = 'kingsaab56' | Password = 'admin56'")
