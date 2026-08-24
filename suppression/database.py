from config.database import get_connection
from datetime import datetime


def create_suppression_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS suppression_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            reason TEXT,
            added_on TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def get_suppression_list():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            email,
            reason,
            added_on
        FROM suppression_list
        ORDER BY added_on DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def add_to_suppression(email, reason):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO suppression_list (
            email,
            reason,
            added_on
        )
        VALUES (?, ?, ?)
        """,
        (
            email,
            reason,
            datetime.now().isoformat(
                timespec="seconds"
            )
        )
    )

    conn.commit()
    conn.close()


def remove_from_suppression(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM suppression_list
        WHERE email = ?
        """,
        (email,)
    )

    conn.commit()
    conn.close()