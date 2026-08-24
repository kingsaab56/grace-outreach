from config.database import get_connection


def create_reply_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS replies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        subject TEXT,
        received_date TEXT,
        reply_type TEXT,
        action_taken TEXT
    )
    """)

    conn.commit()
    conn.close()