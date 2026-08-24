import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
                name,
                status,
                total_contacts,
                completed_count,
                pending_count,
                failed_count
            FROM campaigns
            ORDER BY id DESC
            """
        ).fetchall()

        print()
        print("=" * 80)
        print("CAMPAIGNS")
        print("=" * 80)

        if not rows:
            print("No campaigns found.")
        else:
            for row in rows:
                print(row)

        print("=" * 80)

    finally:
        conn.close()


if __name__ == "__main__":
    main()