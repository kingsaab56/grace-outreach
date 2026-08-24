"""
Queue Retrieval and Status Updates (Matched Schema)
"""

from config.database import get_connection


def get_pending_queue(campaign_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, contact_email, profile_name, subject, body
            FROM campaign_queue
            WHERE campaign_id = ? AND status = 'pending'
            ORDER BY id ASC
            """,
            (campaign_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def update_queue_status(queue_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE campaign_queue
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_status, queue_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()
