from automation.gmail_draft import create_draft
from config.database import get_connection
from datetime import datetime


def log_event(campaign_id, event, message):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO campaign_logs (
            campaign_id,
            event,
            message,
            time
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            campaign_id,
            event,
            message,
            datetime.now().isoformat(timespec="seconds")
        )
    )

    conn.commit()
    conn.close()


def update_campaign_counts(campaign_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END)
        FROM campaign_queue
        WHERE campaign_id = ?
        """,
        (campaign_id,)
    )

    completed, pending, failed = cursor.fetchone()

    completed = completed or 0
    pending = pending or 0
    failed = failed or 0

    cursor.execute(
        """
        UPDATE campaigns
        SET
            completed_count = ?,
            pending_count = ?,
            failed_count = ?
        WHERE id = ?
        """,
        (
            completed,
            pending,
            failed,
            campaign_id
        )
    )

    conn.commit()
    conn.close()

    return completed, pending, failed


def mark_campaign_status(campaign_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE campaigns
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            campaign_id
        )
    )

    conn.commit()
    conn.close()


def start_campaign_engine(
    profile,
    template,
    settings,
    campaign_id=None
):

    print("\n====================================")
    print(" Campaign Engine Started")
    print("====================================")

    if campaign_id is None:
        print("\nNo Campaign ID supplied.")
        print("Campaign must be created through Campaign Manager.")
        input("\nPress Enter...")
        return

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            contact_email,
            subject,
            body,
            status,
            attempts
        FROM campaign_queue
        WHERE campaign_id = ?
          AND profile_name = ?
          AND status = 'pending'
        ORDER BY id
        """,
        (
            campaign_id,
            profile
        )
    )

    queue_items = cursor.fetchall()

    conn.close()

    if not queue_items:

        completed, pending, failed = update_campaign_counts(
            campaign_id
        )

        print("\nNo pending queue items found.")

        print(
            f"\nCompleted : {completed}"
            f"\nPending   : {pending}"
            f"\nFailed    : {failed}"
        )

        if pending == 0:
            mark_campaign_status(
                campaign_id,
                "Completed"
            )

        input("\nPress Enter...")
        return

    print(f"\nCampaign ID : {campaign_id}")
    print(f"Profile     : {profile}")
    print(f"Subject     : {template['subject']}")
    print(f"Queue Items : {len(queue_items)}")
    print(
        f"Draft Limit : "
        f"{settings['emails_per_profile']}"
    )
    print(
        f"Delay       : "
        f"{settings['min_delay']} - "
        f"{settings['max_delay']} sec"
    )

    print("\n------------------------------------")
    print("Pending Queue Preview\n")

    for i, row in enumerate(queue_items, start=1):
        print(
            f"{i}. {row[1]} "
            f"[attempts: {row[5]}]"
        )

    print("\n------------------------------------")

    mark_campaign_status(
        campaign_id,
        "Running"
    )

    log_event(
        campaign_id,
        "STARTED",
        f"Campaign engine started for {profile}."
    )

    created = 0

    limit = min(
        settings["emails_per_profile"],
        len(queue_items)
    )

    for row in queue_items[:limit]:

        queue_id = row[0]
        email = row[1]
        subject = row[2] or template["subject"]
        body = row[3] or template["body"]
        attempts = row[5] or 0

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE campaign_queue
            SET
                status = 'processing',
                attempts = ?
            WHERE id = ?
            """,
            (
                attempts + 1,
                queue_id
            )
        )

        conn.commit()
        conn.close()

        try:

            create_draft(
                email,
                subject,
                body
            )

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE campaign_queue
                SET
                    status = 'completed',
                    completed_at = ?
                WHERE id = ?
                """,
                (
                    datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    queue_id
                )
            )

            conn.commit()
            conn.close()

            created += 1

            print(
                f"[{created}/{limit}] "
                f"Draft created -> {email}"
            )

            log_event(
                campaign_id,
                "DRAFT_CREATED",
                f"Draft created for {email}."
            )

        except Exception as error:

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE campaign_queue
                SET status = 'failed'
                WHERE id = ?
                """,
                (queue_id,)
            )

            conn.commit()
            conn.close()

            print(
                f"[ERROR] "
                f"Draft failed -> {email}"
            )

            print(
                f"        {error}"
            )

            log_event(
                campaign_id,
                "DRAFT_FAILED",
                f"{email}: {error}"
            )

    completed, pending, failed = update_campaign_counts(
        campaign_id
    )

    if pending == 0 and failed == 0:

        mark_campaign_status(
            campaign_id,
            "Completed"
        )

        log_event(
            campaign_id,
            "COMPLETED",
            "Campaign completed successfully."
        )

    elif pending == 0 and failed > 0:

        mark_campaign_status(
            campaign_id,
            "Completed With Errors"
        )

        log_event(
            campaign_id,
            "COMPLETED_WITH_ERRORS",
            f"Campaign completed with {failed} failed items."
        )

    else:

        mark_campaign_status(
            campaign_id,
            "Paused"
        )

        log_event(
            campaign_id,
            "PAUSED",
            f"{pending} queue items remain pending."
        )

    print("\n====================================")
    print(" Campaign Engine Result")
    print("====================================")
    print(f"Created   : {created}")
    print(f"Completed : {completed}")
    print(f"Pending   : {pending}")
    print(f"Failed    : {failed}")

    input("\nPress Enter...")