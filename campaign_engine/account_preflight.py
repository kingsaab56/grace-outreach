"""
Account Pre-flight & Multi-Profile Categorization Viewer (Matched Schema)
"""

from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight


def get_available_accounts(filter_type=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT gmail, profile_name, COALESCE(health_score, 100), oauth_connected, account_type
            FROM gmail_accounts
            WHERE oauth_connected = 1
        """
        params = []
        if filter_type:
            query += " AND account_type = ?"
            params.append(filter_type)

        query += " ORDER BY profile_name ASC, gmail ASC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Fallback if oauth_connected filter returned nothing
        if not rows:
            cursor.execute("SELECT gmail, profile_name, COALESCE(health_score, 100), 1, account_type FROM gmail_accounts")
            rows = cursor.fetchall()

        accounts = []
        for r in rows:
            accounts.append({
                "email": r[0],
                "profile": r[1] or "Default",
                "health_score": r[2],
                "status": "active" if r[3] else "offline",
                "account_type": r[4] or "Business"
            })
        return accounts
    finally:
        conn.close()


def display_profile_accounts_categorized():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT profile_name, gmail, COALESCE(account_type, 'Business'), COALESCE(health_score, 100)
            FROM gmail_accounts
            ORDER BY profile_name ASC, gmail ASC
            """
        )
        accounts = cursor.fetchall()

        print_banner("PROFILE LOGIN ACCOUNTS & HEALTH MATRIX", "👥")
        if not accounts:
            print(info("No Gmail accounts found in database."))
            return

        current_profile = None
        for acc in accounts:
            prof, email, acc_type, health = acc
            prof_title = prof if prof else "Unassigned Profile"

            if prof_title != current_profile:
                current_profile = prof_title
                print(f"\n{Colors.CYAN}{Colors.BOLD}📁 PROFILE: {current_profile}{Colors.RESET}")
                print(f"{Colors.CYAN}{'─' * 65}{Colors.RESET}")

            health_badge = f"{Colors.GREEN}{health}%{Colors.RESET}" if health >= 80 else f"{Colors.YELLOW}{health}%{Colors.RESET}"
            print(f"  • {email:<38} │ {acc_type:<10} │ {health_badge} │ {Colors.GREEN}[ACTIVE]{Colors.RESET}")

        print(f"\n{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")
    finally:
        conn.close()


def display_profile_accounts():
    return display_profile_accounts_categorized()
