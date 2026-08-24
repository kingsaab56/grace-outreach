from datetime import datetime

from campaign_engine.sources.database_source import get_database_contacts
from campaign_engine.validation.email_validator import validate_email
from campaign_engine.validation.duplicate_checker import remove_duplicates
from campaign_engine.validation.business_validator import filter_business_contacts
from campaign_engine.queue.queue_resume import get_queue_stats
from config.database import get_connection


def load_campaign_contacts(campaign_id, limit=None):
    contacts = get_database_contacts(limit)
    valid = []

    for contact in contacts:
        if validate_email(contact[0]):
            valid.append(contact)

    valid = remove_duplicates(valid)
    valid = filter_business_contacts(valid)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE campaigns
        SET total_contacts=?
        WHERE id=?
        """,
        (
            len(valid),
            campaign_id
        )
    )

    conn.commit()
    conn.close()

    print(
        f"Campaign {campaign_id}: {len(valid)} contacts loaded."
    )

    return valid


def show_campaign_dashboard(campaign_id):
    """
    Display a comprehensive visual progress dashboard for a campaign.
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, name, status, total_contacts, completed_count, failed_count, pending_count, created_at
            FROM campaigns
            WHERE id=?
            """,
            (campaign_id,)
        )
        campaign = cursor.fetchone()

        if not campaign:
            print(f"\n[Error] Campaign ID {campaign_id} not found.")
            return

        c_id, name, status, total, completed, failed, pending, created_at = campaign
        
        # Get live queue stats to ensure sync
        queue_stats = get_queue_stats(campaign_id)
        q_completed = queue_stats.get("completed", completed or 0)
        q_failed = queue_stats.get("failed", failed or 0)
        q_pending = queue_stats.get("pending", pending or 0)
        
        calc_total = total if total and total > 0 else (q_completed + q_failed + q_pending)
        processed = q_completed + q_failed
        progress_pct = (processed / calc_total * 100) if calc_total > 0 else 0.0

        bar_len = 30
        filled_len = int(bar_len * progress_pct // 100) if calc_total > 0 else 0
        bar = "█" * filled_len + "-" * (bar_len - filled_len)

        print("\n" + "=" * 70)
        print(f"            CAMPAIGN PROGRESS DASHBOARD: #{c_id} ({name or 'Unnamed'})")
        print("=" * 70)
        print(f"Status           : {status}")
        print(f"Created At       : {created_at}")
        print(f"Progress         : [{bar}] {progress_pct:.1f}% ({processed}/{calc_total})")
        print("-" * 70)
        print(f"  • Completed    : {q_completed}")
        print(f"  • Failed       : {q_failed}")
        print(f"  • Pending      : {q_pending}")
        print("-" * 70)

        # Profile / Account breakdown from queue
        cursor.execute(
            """
            SELECT profile, status, COUNT(*)
            FROM campaign_queue
            WHERE campaign_id=?
            GROUP BY profile, status
            """,
            (campaign_id,)
        )
        breakdown = cursor.fetchall()

        if breakdown:
            print("Queue Breakdown By Profile:")
            profile_map = {}
            for row in breakdown:
                prof, stat, count = row
                profile_map.setdefault(prof or "Unassigned", {})[stat] = count

            for prof, stats in profile_map.items():
                c = stats.get("completed", 0)
                f = stats.get("failed", 0)
                p = stats.get("pending", 0)
                print(f"  [{prof}] -> Completed: {c} | Failed: {f} | Pending: {p}")
        print("=" * 70 + "\n")

    finally:
        conn.close()