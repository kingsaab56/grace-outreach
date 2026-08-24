from config.database import get_connection


def create_followup_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS followup_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            subject TEXT,
            body TEXT,
            days_after INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS followup_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            template_id INTEGER,
            sent_date TEXT,
            opened INTEGER DEFAULT 0,
            replied INTEGER DEFAULT 0,
            unsubscribed INTEGER DEFAULT 0
        )
        """
    )

    cursor.execute(
        "SELECT COUNT(*) FROM followup_templates"
    )

    template_count = cursor.fetchone()[0]

    if template_count == 0:
        cursor.executemany(
            """
            INSERT INTO followup_templates
            (name, subject, body, days_after)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    "Just checking in",
                    "Just checking in",
                    (
                        "Hello,\n\n"
                        "Just following up on my previous email.\n\n"
                        "Thank you."
                    ),
                    3
                ),
                (
                    "Follow-up 2",
                    "Quick follow-up",
                    (
                        "Hello,\n\n"
                        "I wanted to check if you had a chance "
                        "to review my previous email.\n\n"
                        "Thank you."
                    ),
                    7
                ),
                (
                    "Follow-up 3",
                    "Final follow-up",
                    (
                        "Hello,\n\n"
                        "This will be my final follow-up. "
                        "If now isn't the right time, I'd be "
                        "happy to reconnect in the future.\n\n"
                        "Thank you."
                    ),
                    14
                )
            ]
        )

    conn.commit()
    conn.close()


def show_templates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, subject, days_after
        FROM followup_templates
        ORDER BY days_after
        """
    )

    rows = cursor.fetchall()

    conn.close()

    print("\n========== FOLLOW-UP TEMPLATES ==========\n")

    if not rows:
        print("No templates found.")
        return

    for row in rows:
        print(
            f"{row[0]}. {row[1]} "
            f"({row[3]} Days)"
        )
        print(f"   Subject: {row[2]}")


def get_followup_templates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, subject, body, days_after
        FROM followup_templates
        ORDER BY days_after
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_followup_template(template_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, subject, body, days_after
        FROM followup_templates
        WHERE id = ?
        """,
        (template_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def get_pending_followups():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            email,
            template_id,
            sent_date,
            opened,
            replied,
            unsubscribed
        FROM followup_history
        WHERE replied = 0
          AND unsubscribed = 0
        ORDER BY sent_date
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def add_followup_history(
    email,
    template_id,
    sent_date
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO followup_history (
            email,
            template_id,
            sent_date
        )
        VALUES (?, ?, ?)
        """,
        (
            email,
            template_id,
            sent_date
        )
    )

    conn.commit()
    conn.close()


def mark_followup_replied(history_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE followup_history
        SET replied = 1
        WHERE id = ?
        """,
        (history_id,)
    )

    conn.commit()
    conn.close()


def mark_followup_unsubscribed(history_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE followup_history
        SET unsubscribed = 1
        WHERE id = ?
        """,
        (history_id,)
    )

    conn.commit()
    conn.close()