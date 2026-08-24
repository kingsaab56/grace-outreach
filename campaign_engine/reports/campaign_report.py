from config.database import get_connection


def get_campaign_report(campaign_id):
    """
    Returns complete campaign report.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            total_contacts,
            completed_count,
            pending_count,
            failed_count,
            status,
            created_at
        FROM campaigns
        WHERE id=?
        """,
        (campaign_id,)
    )

    campaign = cursor.fetchone()

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

    queue_status = dict(cursor.fetchall())

    conn.close()

    return {
        "campaign": campaign,
        "queue": {
            "completed": queue_status.get("completed", 0),
            "pending": queue_status.get("pending", 0),
            "failed": queue_status.get("failed", 0)
        }
    }


def print_campaign_report(campaign_id):

    report = get_campaign_report(campaign_id)

    campaign = report["campaign"]

    if not campaign:

        print("\nCampaign not found.")
        return

    print("\n==========================================")
    print("           CAMPAIGN REPORT")
    print("==========================================")

    print(f"Campaign ID     : {campaign[0]}")
    print(f"Campaign Name   : {campaign[1]}")
    print(f"Total Contacts  : {campaign[2]}")
    print(f"Completed       : {campaign[3]}")
    print(f"Pending         : {campaign[4]}")
    print(f"Failed          : {campaign[5]}")
    print(f"Status          : {campaign[6]}")
    print(f"Created         : {campaign[7]}")

    print("\n------------- Queue Summary -------------")

    print(
        f"Completed : {report['queue']['completed']}"
    )

    print(
        f"Pending   : {report['queue']['pending']}"
    )

    print(
        f"Failed    : {report['queue']['failed']}"
    )

    print("==========================================")