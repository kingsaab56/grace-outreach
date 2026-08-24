from config.database import get_connection


def get_pending_queue(campaign_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            contact_email,
            profile_name,
            subject,
            body
        FROM campaign_queue
        WHERE campaign_id=?
        AND status='pending'
        ORDER BY id
        """,
        (campaign_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows



def get_queue_stats(campaign_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            status,
            COUNT(*)
        FROM campaign_queue
        WHERE campaign_id=?
        GROUP BY status
        """,
        (campaign_id,)
    )

    stats = dict(cursor.fetchall())

    conn.close()

    return {
        "pending": stats.get("pending", 0),
        "completed": stats.get("completed", 0),
        "failed": stats.get("failed", 0)
    }



def update_queue_status(queue_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE campaign_queue
        SET status=?
        WHERE id=?
        """,
        (
            status,
            queue_id
        )
    )

    conn.commit()
    conn.close()