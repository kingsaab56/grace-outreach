from config.database import get_connection
conn = get_connection()
c = conn.cursor()

print("--- GMAIL_PROFILES COLUMNS & DATA ---")
c.execute("PRAGMA table_info(gmail_profiles)")
print("Columns:", [col[1] for col in c.fetchall()])
c.execute("SELECT * FROM gmail_profiles")
print("Rows:", c.fetchall())

print("\n--- GMAIL_ACCOUNTS COLUMNS & DATA ---")
c.execute("PRAGMA table_info(gmail_accounts)")
print("Columns:", [col[1] for col in c.fetchall()])
c.execute("SELECT * FROM gmail_accounts")
print("Rows:", c.fetchall())

conn.close()
