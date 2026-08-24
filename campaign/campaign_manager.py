from campaign.campaign_runner import run_campaign
from engine.campaign_engine import start_campaign_engine
from settings.campaign_settings import get_campaign_settings
from config.database import get_connection


def get_resume_campaigns():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            c.id,
            c.name,
            c.template,
            c.status,
            c.total_contacts,
            c.completed_count,
            c.pending_count,
            c.failed_count,
            c.created_at,
            q.profile_name
        FROM campaigns c
        JOIN campaign_queue q
            ON q.campaign_id = c.id
        WHERE q.status = 'pending'
        GROUP BY c.id, q.profile_name
        ORDER BY c.id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_campaign_details(campaign_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            template,
            status,
            total_contacts,
            draft_limit,
            created_at,
            completed_count,
            pending_count,
            failed_count
        FROM campaigns
        WHERE id = ?
        """,
        (campaign_id,)
    )

    campaign = cursor.fetchone()

    if not campaign:
        conn.close()
        return None, []

    cursor.execute(
        """
        SELECT DISTINCT profile_name
        FROM campaign_queue
        WHERE campaign_id = ?
          AND status = 'pending'
        ORDER BY profile_name
        """,
        (campaign_id,)
    )

    profiles = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return campaign, profiles


def get_campaign_template(campaign_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT subject, body
        FROM campaign_queue
        WHERE campaign_id = ?
        ORDER BY id
        LIMIT 1
        """,
        (campaign_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if not row:
        return None

    return {
        "subject": row[0] or "",
        "body": row[1] or ""
    }


def resume_campaign():
    campaigns = get_resume_campaigns()

    print("\n========== RESUME CAMPAIGN ==========\n")

    if not campaigns:
        print("No campaigns with pending queue items found.")
        input("\nPress Enter...")
        return

    for i, row in enumerate(campaigns, 1):

        (
            campaign_id,
            name,
            template,
            status,
            total,
            completed,
            pending,
            failed,
            created_at,
            profile
        ) = row

        print(
            f"{i}. Campaign #{campaign_id} | {name}"
        )

        print(
            f"   Profile   : {profile}"
        )

        print(
            f"   Status    : {status}"
        )

        print(
            f"   Completed : {completed}"
        )

        print(
            f"   Pending   : {pending}"
        )

        print(
            f"   Failed    : {failed}"
        )

        print(
            f"   Created   : {created_at}"
        )

        print("----------------------------------------")

    try:
        choice = int(
            input("\nSelect Campaign: ").strip()
        )

        if not 1 <= choice <= len(campaigns):
            raise ValueError

        selected = campaigns[choice - 1]

    except (ValueError, IndexError):

        print("\nInvalid Selection.")
        input("\nPress Enter...")
        return

    campaign_id = selected[0]
    profile = selected[9]

    campaign, profiles = get_campaign_details(
        campaign_id
    )

    if not campaign:
        print("\nCampaign not found.")
        input("\nPress Enter...")
        return

    if not profiles:
        print("\nNo pending queue found for this campaign.")
        input("\nPress Enter...")
        return

    template = get_campaign_template(
        campaign_id
    )

    if not template:
        print("\nCampaign template data not found.")
        input("\nPress Enter...")
        return

    print("\n========== RESUME SUMMARY ==========\n")

    print(f"Campaign ID : {campaign_id}")
    print(f"Campaign    : {campaign[1]}")
    print(f"Template    : {campaign[2]}")
    print(f"Profile     : {profile}")
    print(f"Status      : {campaign[3]}")
    print(f"Total       : {campaign[4]}")
    print(f"Completed   : {campaign[7]}")
    print(f"Pending     : {campaign[8]}")
    print(f"Failed      : {campaign[9]}")

    print("\nSubject:")
    print(template["subject"])

    confirm = input(
        "\nResume this campaign? (Y/N): "
    ).strip().lower()

    if confirm != "y":

        print("\nResume Cancelled.")
        input("\nPress Enter...")
        return

    print("\nLoading Campaign Settings...\n")

    settings = get_campaign_settings()

    print("\nResuming Campaign Engine...\n")

    start_campaign_engine(
        profile,
        template,
        settings,
        campaign_id=campaign_id
    )


def show_campaign_progress():
    conn = get_connection()
    cursor = conn.cursor()

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

    campaigns = cursor.fetchall()

    conn.close()

    print("\n========== CAMPAIGN PROGRESS ==========\n")

    if not campaigns:
        print("No campaigns found.")
        input("\nPress Enter...")
        return

    for row in campaigns:

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

        print(f"Campaign #{campaign_id}")
        print(f"Name      : {name}")
        print(f"Status    : {status}")
        print(f"Total     : {total}")
        print(f"Completed : {completed}")
        print(f"Pending   : {pending}")
        print(f"Failed    : {failed}")
        print(f"Progress  : {progress}%")
        print(f"Created   : {created_at}")

        print("----------------------------------------")

    input("\nPress Enter...")


def show_campaign_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            template,
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

    campaigns = cursor.fetchall()

    print("\n========== CAMPAIGN HISTORY ==========\n")

    if not campaigns:

        print("No campaign history found.")

        conn.close()

        input("\nPress Enter...")
        return

    for row in campaigns:

        (
            campaign_id,
            name,
            template,
            status,
            total,
            completed,
            pending,
            failed,
            created_at
        ) = row

        print(f"Campaign #{campaign_id}")
        print(f"Name      : {name}")
        print(f"Template  : {template}")
        print(f"Status    : {status}")
        print(f"Total     : {total}")
        print(f"Completed : {completed}")
        print(f"Pending   : {pending}")
        print(f"Failed    : {failed}")
        print(f"Created   : {created_at}")

        cursor.execute(
            """
            SELECT
                event,
                message,
                time
            FROM campaign_logs
            WHERE campaign_id = ?
            ORDER BY id DESC
            LIMIT 3
            """,
            (campaign_id,)
        )

        logs = cursor.fetchall()

        if logs:

            print("Recent Logs:")

            for event, message, time in logs:

                print(
                    f"  [{time}] "
                    f"{event}: {message}"
                )

        print("----------------------------------------")

    conn.close()

    input("\nPress Enter...")


def show_campaign_settings():
    from settings.campaign_settings import edit_campaign_settings

    edit_campaign_settings()

    print(
        "The current Campaign Settings module "
        "uses interactive input."
    )

    print(
        "\nSettings will be separated into "
        "read/edit functions in Step 3."
    )

    input("\nPress Enter...")


def start_campaign_manager():

    while True:

        print(
            """
========================================
        CAMPAIGN MANAGER
========================================

[1] New Campaign
[2] Resume Campaign
[3] Campaign Progress
[4] Campaign History
[5] Settings
[0] Back

========================================
"""
        )

        choice = input(
            "Select Option: "
        ).strip()

        if choice == "1":

            run_campaign()

        elif choice == "2":

            resume_campaign()

        elif choice == "3":

            show_campaign_progress()

        elif choice == "4":

            show_campaign_history()

        elif choice == "5":

            show_campaign_settings()

        elif choice == "0":

            break

        else:

            print("\nInvalid Option.")
            input("\nPress Enter...")