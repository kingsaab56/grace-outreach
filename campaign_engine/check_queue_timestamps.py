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

        rows = cursor.execute(
            """
            SELECT
                id,
                contact_email,
                status,
                created_at
            FROM campaign_queue
            WHERE campaign_id=5
            ORDER BY id
            """
        ).fetchall()

        print()
        print("=" * 100)
        print("CAMPAIGN 5 QUEUE TIMESTAMPS")
        print("=" * 100)

        for row in rows:
            print(row)

        print("=" * 100)
        print(f"TOTAL ROWS: {len(rows)}")
        print("=" * 100)

    finally:
        conn.close()


if __name__ == "__main__":
    main()