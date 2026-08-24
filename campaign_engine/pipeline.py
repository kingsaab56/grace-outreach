"""
Campaign Engine V2 Pipeline, Builder & Dashboard
"""

from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight


def build_campaign(campaign_id, subject, body, limit=None):
    """
    Builds campaign queue by distributing valid contacts across active profiles.
    """
    print_banner("BUILDING CAMPAIGN", "⚙️")
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Fetch valid contacts
        query = "SELECT id, email FROM contacts WHERE status = 'valid'"
        if limit:
            query += f" LIMIT {int(limit)}"
        cursor.execute(query)
        contacts = cursor.fetchall()

        if not contacts:
            print(warning("No valid contacts found in database."))
            return False

        print(f"Loaded {highlight(len(contacts))} valid contact(s).")

        # Fetch active profiles with login accounts
        cursor.execute("SELECT DISTINCT profile_name FROM gmail_accounts WHERE status = 'active'")
        active_profiles = [row[0] for row in cursor.fetchall() if row[0]]

        if not active_profiles:
            active_profiles = ["Default"]

        # Ensure campaign_queue table exists
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS campaign_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                recipient_email TEXT,
                profile_name TEXT,
                subject TEXT,
                body TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Distribute and insert
        queue_count = 0
        for idx, contact in enumerate(contacts):
            cid, email = contact
            assigned_profile = active_profiles[idx % len(active_profiles)]
            cursor.execute(
                """
                INSERT INTO campaign_queue (campaign_id, recipient_email, profile_name, subject, body, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
                """,
                (campaign_id, email, assigned_profile, subject, body)
            )
            queue_count += 1

        # Update campaign record
        cursor.execute(
            """
            UPDATE campaigns 
            SET total_contacts = ?, pending_count = ?, status = 'Ready'
            WHERE id = ?
            """,
            (queue_count, queue_count, campaign_id)
        )
        conn.commit()
        print(success(f"Campaign #{campaign_id} queue generated: {queue_count} draft(s) ready."))
        return True
    except Exception as e:
        print(error(f"Error building campaign: {e}"))
        return False
    finally:
        conn.close()


def display_dashboard(campaign_id):
    """
    Renders real-time visual progress and profile-wise breakdown.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT id, name, status, created_at
            FROM campaigns
            WHERE id = ?
            """,
            (campaign_id,)
        )
        camp = cursor.fetchone()
        if not camp:
            print(error(f"Campaign #{campaign_id} not found."))
            return

        c_id, name, status, created_at = camp

        cursor.execute(
            """
            SELECT 
                COUNT(*),
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END),
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END)
            FROM campaign_queue
            WHERE campaign_id = ?
            """,
            (campaign_id,)
        )
        counts = cursor.fetchone()
        total = counts[0] or 0
        completed = counts[1] or 0
        failed = counts[2] or 0
        pending = counts[3] or 0

        pct = (completed / total * 100) if total > 0 else 0.0
        bar_len = 30
        filled = int((completed / total) * bar_len) if total > 0 else 0
        bar = "█" * filled + "-" * (bar_len - filled)

        print_banner(f"CAMPAIGN PROGRESS DASHBOARD: #{c_id} ({name})", "📊")
        print(f"{Colors.BOLD}{'Status':<17}:{Colors.RESET} {status}")
        print(f"{Colors.BOLD}{'Created At':<17}:{Colors.RESET} {created_at or 'N/A'}")
        print(f"{Colors.BOLD}{'Progress':<17}:{Colors.RESET} [{Colors.GREEN}{bar}{Colors.RESET}] {pct:.1f}% ({completed}/{total})")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")
        print(f"  • {Colors.GREEN}Completed{Colors.RESET}    : {completed}")
        print(f"  • {Colors.RED}Failed{Colors.RESET}       : {failed}")
        print(f"  • {Colors.YELLOW}Pending{Colors.RESET}      : {pending}")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.RESET}")

        cursor.execute("PRAGMA table_info(campaign_queue)")
        cols = [c[1] for c in cursor.fetchall()]
        prof_col = "profile_name" if "profile_name" in cols else ("profile" if "profile" in cols else None)

        if prof_col:
            cursor.execute(
                f"""
                SELECT {prof_col}, 
                       COUNT(*),
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END)
                FROM campaign_queue
                WHERE campaign_id = ?
                GROUP BY {prof_col}
                """,
                (campaign_id,)
            )
            prof_stats = cursor.fetchall()
            if prof_stats:
                print(f"{Colors.BOLD}{'Profile':<18} │ {'Total':<8} │ {'Done':<8} │ {'Fail':<8} │ {'Pend':<8}{Colors.RESET}")
                print(f"{Colors.CYAN}{'─' * 60}{Colors.RESET}")
                for row in prof_stats:
                    pname, ptot, pdone, pfail, ppend = row
                    print(f"{pname or 'Unassigned':<18} │ {ptot or 0:<8} │ {Colors.GREEN}{pdone or 0:<8}{Colors.RESET} │ {Colors.RED}{pfail or 0:<8}{Colors.RESET} │ {ppend or 0:<8}")
                print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}\n")

    finally:
        conn.close()
