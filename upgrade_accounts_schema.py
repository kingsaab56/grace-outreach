from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE gmail_accounts ADD COLUMN account_type TEXT DEFAULT 'Business'")
    conn.commit()
except Exception:
    pass

try:
    cursor.execute("ALTER TABLE gmail_accounts ADD COLUMN health_score INTEGER DEFAULT 100")
    conn.commit()
except Exception:
    pass

# Auto-classify based on domain/names
cursor.execute("UPDATE gmail_accounts SET account_type = 'Personal' WHERE gmail LIKE '%waheed%' OR gmail LIKE '%rajpoot%' OR gmail LIKE '%malikshani%'")
cursor.execute("UPDATE gmail_accounts SET account_type = 'Business' WHERE gmail LIKE '%gracearchitectures%'")
conn.commit()
conn.close()
print("Database schema updated with account_type and health_score.")
