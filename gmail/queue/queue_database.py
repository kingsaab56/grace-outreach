from config.database import get_connection


def create_queue_table():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS draft_queue (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        contact_email TEXT,

        contact_name TEXT DEFAULT '',

        company TEXT DEFAULT '',

        profile_name TEXT,

        subject TEXT,

        body TEXT,

        status TEXT DEFAULT 'pending',

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        sent_at TEXT DEFAULT ''

    )
    """)


    conn.commit()
    conn.close()



def add_to_queue(
    contact_email,
    contact_name,
    company,
    profile_name,
    subject,
    body
):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    INSERT INTO draft_queue(
        contact_email,
        contact_name,
        company,
        profile_name,
        subject,
        body
    )

    VALUES (?,?,?,?,?,?)
    """,
    (
        contact_email,
        contact_name,
        company,
        profile_name,
        subject,
        body
    ))


    conn.commit()
    conn.close()



def get_pending_queue():

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    SELECT
        id,
        contact_email,
        contact_name,
        company,
        profile_name,
        subject,
        body,
        status
    FROM draft_queue
    WHERE status='pending'
    ORDER BY id
    """)


    rows = cursor.fetchall()

    conn.close()

    return rows



def update_queue_status(
    queue_id,
    status
):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute("""
    UPDATE draft_queue
    SET status=?
    WHERE id=?
    """,
    (
        status,
        queue_id
    ))


    conn.commit()
    conn.close()