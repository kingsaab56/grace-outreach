from datetime import datetime

from config.database import get_connection


def add_campaign_queue(
    campaign_id,
    contacts,
    allocations,
    subject,
    body
):
    """
    Generate campaign queue from validated contacts
    and profile allocations.

    Safety:
    - Never rebuild an existing campaign queue.
    - Never insert the same contact twice.
    - New rows always start as pending.
    - Campaign counters are synchronized with
      the actual newly generated queue.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ---------------------------------------------------------
        # SAFETY CHECK — EXISTING QUEUE
        # ---------------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM campaign_queue
            WHERE campaign_id=?
            """,
            (campaign_id,)
        )

        existing_count = cursor.fetchone()[0]

        if existing_count > 0:

            print("\n==========================================")
            print("       CAMPAIGN QUEUE ALREADY EXISTS")
            print("==========================================")

            print(
                f"Campaign ID    : {campaign_id}"
            )

            print(
                f"Existing Rows  : {existing_count}"
            )

            print(
                "\nQueue generation stopped."
            )

            print(
                "Existing queue was NOT modified."
            )

            print(
                "This prevents duplicate queue generation."
            )

            print("==========================================")

            return 0

        # ---------------------------------------------------------
        # GENERATE QUEUE
        # ---------------------------------------------------------

        index = 0
        total_added = 0

        # Prevent duplicate emails inside this build
        seen_emails = set()

        for allocation in allocations:

            profile = allocation.get("profile")

            count = int(
                allocation.get(
                    "assigned",
                    0
                )
            )

            if not profile:
                continue

            if count <= 0:
                continue

            selected = contacts[
                index:index + count
            ]

            for contact in selected:

                if not contact:
                    continue

                email = str(
                    contact[0]
                ).strip().lower()

                if not email:
                    continue

                # -------------------------------------------------
                # DUPLICATE CONTACT PROTECTION
                # -------------------------------------------------

                if email in seen_emails:

                    print(
                        f"[SKIP] Duplicate contact: {email}"
                    )

                    continue

                seen_emails.add(email)

                # -------------------------------------------------
                # INSERT QUEUE ROW
                # -------------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO campaign_queue
                    (
                        campaign_id,
                        contact_email,
                        profile_name,
                        subject,
                        body,
                        status,
                        attempts,
                        created_at
                    )
                    VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        campaign_id,
                        email,
                        profile,
                        subject,
                        body,
                        "pending",
                        0,
                        datetime.now().isoformat()
                    )
                )

                total_added += 1

            index += count

        # ---------------------------------------------------------
        # VALIDATE
        # ---------------------------------------------------------

        if total_added == 0:

            conn.rollback()

            print(
                "\nNo campaign queue rows were generated."
            )

            return 0

        # ---------------------------------------------------------
        # UPDATE CAMPAIGN SUMMARY
        # ---------------------------------------------------------

        cursor.execute(
            """
            UPDATE campaigns
            SET
                total_contacts=?,
                completed_count=?,
                failed_count=?,
                pending_count=?,
                status=?
            WHERE id=?
            """,
            (
                total_added,
                0,
                0,
                total_added,
                "Created",
                campaign_id
            )
        )

        conn.commit()

        # ---------------------------------------------------------
        # RESULT
        # ---------------------------------------------------------

        print("\n==========================================")
        print("       CAMPAIGN QUEUE GENERATED")
        print("==========================================")

        print(
            f"Campaign ID   : {campaign_id}"
        )

        print(
            f"Queue Created : {total_added}"
        )

        print(
            f"Pending       : {total_added}"
        )

        print(
            "Status        : Created"
        )

        print("==========================================")

        return total_added

    except Exception as e:

        conn.rollback()

        print(
            "\nQueue generation failed."
        )

        print(
            f"Reason: {e}"
        )

        return 0

    finally:

        conn.close()