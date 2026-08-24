from config.database import get_connection


def get_campaign_progress(campaign_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if campaign_id is not None:

        cursor.execute(
            """
            SELECT
                id,
                name,
                status,
                total_contacts,
                completed_count,
                pending_count,
                failed_count,
                created_at
            FROM campaigns
            WHERE id = ?
            """,
            (campaign_id,)
        )

        row = cursor.fetchone()

        conn.close()

        if not row:
            return None

        (
            campaign_id,
            name,
            status,
            total,
            completed,
            pending,
            failed,
            created_at
        ) = row

        if total > 0:
            progress = int(
                (completed / total) * 100
            )
        else:
            progress = 0

        return {
            "id": campaign_id,
            "name": name,
            "status": status,
            "total": total,
            "completed": completed,
            "pending": pending,
            "failed": failed,
            "progress": progress,
            "created_at": created_at
        }

    cursor.execute(
        """
        SELECT
            id,
            name,
            status,
            total_contacts,
            completed_count,
            pending_count,
            failed_count,
            created_at
        FROM campaigns
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    campaigns = []

    for row in rows:

        (
            campaign_id,
            name,
            status,
            total,
            completed,
            pending,
            failed,
            created_at
        ) = row

        if total > 0:
            progress = int(
                (completed / total) * 100
            )
        else:
            progress = 0

        campaigns.append(
            {
                "id": campaign_id,
                "name": name,
                "status": status,
                "total": total,
                "completed": completed,
                "pending": pending,
                "failed": failed,
                "progress": progress,
                "created_at": created_at
            }
        )

    return campaigns


def show_campaign_progress():

    campaigns = get_campaign_progress()

    print(
        "\n========== CAMPAIGN PROGRESS ==========\n"
    )

    if not campaigns:

        print("No campaigns found.")
        input("\nPress Enter...")
        return

    for campaign in campaigns:

        print(
            f"Campaign #{campaign['id']}"
        )

        print(
            f"Name      : {campaign['name']}"
        )

        print(
            f"Status    : {campaign['status']}"
        )

        print(
            f"Total     : {campaign['total']}"
        )

        print(
            f"Completed : {campaign['completed']}"
        )

        print(
            f"Pending   : {campaign['pending']}"
        )

        print(
            f"Failed    : {campaign['failed']}"
        )

        print(
            f"Progress  : {campaign['progress']}%"
        )

        print(
            f"Created   : {campaign['created_at']}"
        )

        print("----------------------------------------")

    input("\nPress Enter...")