import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.database import get_connection


def main():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        print()
        print("=" * 90)
        print("CAMPAIGN QUEUE DIAGNOSTIC")
        print("=" * 90)

        campaign_id = 5

        print(f"\nCampaign ID: {campaign_id}")

        campaign = cursor.execute(
            """
            SELECT
                id,
                name,
                status,
                total_contacts,
                completed_count,
                pending_count,
                failed_count
            FROM campaigns
            WHERE id=?
            """,
            (campaign_id,)
        ).fetchone()

        print("\nCAMPAIGN:")
        print("-" * 90)

        if campaign:
            print(campaign)
        else:
            print("Campaign not found.")
            return

        rows = cursor.execute(
            """
            SELECT
                status,
                COUNT(*)
            FROM campaign_queue
            WHERE campaign_id=?
            GROUP BY status
            """,
            (campaign_id,)
        ).fetchall()

        print("\nQUEUE COUNTS:")
        print("-" * 90)

        if rows:
            for row in rows:
                print(row)
        else:
            print("No queue rows found.")

        total_queue = cursor.execute(
            """
            SELECT COUNT(*)
            FROM campaign_queue
            WHERE campaign_id=?
            """,
            (campaign_id,)
        ).fetchone()[0]

        print("\nTOTAL QUEUE ROWS:")
        print("-" * 90)
        print(total_queue)

        print("\nQUEUE DETAILS:")
        print("-" * 90)

        queue_rows = cursor.execute(
            """
            SELECT
                id,
                contact_email,
                profile_name,
                status,
                attempts
            FROM campaign_queue
            WHERE campaign_id=?
            ORDER BY id
            """,
            (campaign_id,)
        ).fetchall()

        for row in queue_rows:
            print(row)

        print("\n" + "=" * 90)
        print("DIAGNOSTIC COMPLETE")
        print("=" * 90)

    finally:
        conn.close()


if __name__ == "__main__":
    main()