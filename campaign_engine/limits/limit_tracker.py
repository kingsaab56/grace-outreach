"""
Account Daily Limits & Quota Tracker
"""

from datetime import datetime
from config.database import get_connection
from campaign_engine.ui_theme import Colors, print_banner, info, success, warning, error, highlight

DEFAULT_DAILY_LIMIT = 50


def get_account_usage(email, profile_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute(
            "SELECT drafts_count, daily_limit FROM account_daily_usage WHERE email = ? AND date = ?",
            (email, today_str)
        )
        row = cursor.fetchone()
        if not row:
            return {"used": 0, "limit": DEFAULT_DAILY_LIMIT, "remaining": DEFAULT_DAILY_LIMIT}
        used, lim = row
        return {"used": used or 0, "limit": lim or DEFAULT_DAILY_LIMIT, "remaining": max(0, (lim or DEFAULT_DAILY_LIMIT) - (used or 0))}
    finally:
        conn.close()


def increment_account_usage(email, profile_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute(
            """
            INSERT INTO account_daily_usage (email, profile, date, drafts_count, daily_limit)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(email, date) DO UPDATE SET drafts_count = drafts_count + 1
            """,
            (email, profile_name or "Default", today_str, DEFAULT_DAILY_LIMIT)
        )
        conn.commit()
    except Exception:
        # Fallback update if unique constraint varies
        try:
            cursor.execute(
                "UPDATE account_daily_usage SET drafts_count = drafts_count + 1 WHERE email = ? AND date = ?",
                (email, today_str)
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    "INSERT INTO account_daily_usage (email, profile, date, drafts_count, daily_limit) VALUES (?, ?, ?, 1, ?)",
                    (email, profile_name or "Default", today_str, DEFAULT_DAILY_LIMIT)
                )
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()


def display_account_limits_summary():
    conn = get_connection()
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    try:
        cursor.execute(
            """
            SELECT g.gmail, g.profile_name, COALESCE(u.drafts_count, 0), COALESCE(u.daily_limit, 50)
            FROM gmail_accounts g
            LEFT JOIN account_daily_usage u ON g.gmail = u.email AND u.date = ?
            ORDER BY g.profile_name ASC, g.gmail ASC
            """,
            (today_str,)
        )
        accounts = cursor.fetchall()

        print_banner("ACCOUNT DAILY QUOTAS & USAGE DASHBOARD", "🛡️")
        if not accounts:
            print(info("No active accounts found."))
            return

        print(f"{'#':<4} │ {'Email':<40} │ {'Profile':<14} │ {'Today Used':<12} │ {'Remaining':<10} │ {'Status'}")
        print(f"{Colors.CYAN}{'─' * 100}{Colors.RESET}")

        for idx, acc in enumerate(accounts, start=1):
            email, prof, used, lim = acc
            rem = max(0, lim - used)
            status = f"{Colors.GREEN}[SAFE]{Colors.RESET}" if rem > 10 else (f"{Colors.YELLOW}[LOW]{Colors.RESET}" if rem > 0 else f"{Colors.RED}[FULL]{Colors.RESET}")
            print(f"{idx:<4} │ {email:<40} │ {prof or 'Default':<14} │ {used:>2}/{lim:<2} drafts  │ {rem:>2} left     │ {status}")

        print(f"{Colors.CYAN}{'═' * 100}{Colors.RESET}\n")
    finally:
        conn.close()
